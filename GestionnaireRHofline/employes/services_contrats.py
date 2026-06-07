from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from django.utils import timezone


def _texte(valeur, defaut='Non renseigne'):
    if valeur is None:
        return defaut
    valeur = str(valeur).strip()
    return valeur or defaut


def _date(valeur):
    return valeur.strftime('%d/%m/%Y') if valeur else 'Non renseignee'


def _montant(valeur):
    try:
        montant = Decimal(str(valeur or 0))
    except Exception:
        montant = Decimal('0')
    return f"{montant:,.0f}".replace(',', ' ') + " GNF"


def _libelle_choice(instance, champ):
    getter = getattr(instance, f'get_{champ}_display', None)
    if callable(getter):
        return getter()
    return _texte(getattr(instance, champ, None))


class PremierBulletinManquant(ValueError):
    pass


def _premier_bulletin_contrat(contrat):
    from paie.models import BulletinPaie

    bulletins = BulletinPaie.objects.filter(
        employe=contrat.employe,
        statut_bulletin__in=['calcule', 'valide', 'paye'],
        salaire_brut__gt=0,
    )

    if contrat.date_debut:
        bulletins = bulletins.filter(
            annee_paie__gt=contrat.date_debut.year
        ) | bulletins.filter(
            annee_paie=contrat.date_debut.year,
            mois_paie__gte=contrat.date_debut.month,
        )

    bulletin = (
        bulletins.select_related('periode')
        .prefetch_related('lignes__rubrique')
        .order_by('annee_paie', 'mois_paie', 'id')
        .first()
    )

    if not bulletin:
        raise PremierBulletinManquant(
            "Le contrat sera genere apres le calcul du premier bulletin de salaire de cet employe."
        )
    return bulletin


def _elements_remuneration_depuis_bulletin(bulletin):
    salaire_base = Decimal(str(bulletin.salaire_base or 0))
    accessoires = []

    for ligne in bulletin.lignes.all():
        rubrique = ligne.rubrique
        montant = Decimal(str(ligne.montant or 0))
        code = (rubrique.code_rubrique or '').upper()
        categorie = rubrique.categorie_rubrique
        est_base = categorie == 'salaire_base' or 'SAL_BASE' in code
        if est_base or rubrique.type_rubrique != 'gain' or montant <= 0:
            continue
        libelle = ligne.libelle_personnalise or rubrique.libelle_rubrique
        accessoires.append((libelle, montant))

    return salaire_base, accessoires, Decimal(str(bulletin.salaire_brut or 0))


def _clause_type_contrat(contrat):
    type_contrat = contrat.type_contrat
    if type_contrat == 'CDI':
        return (
            "Le present contrat est conclu pour une duree indeterminee. "
            "Il prend effet a compter de la date de debut indiquee ci-dessus."
        )
    if type_contrat == 'CDD':
        return (
            "Le present contrat est conclu pour une duree determinee. "
            f"Il prendra fin le {_date(contrat.date_fin)}, sauf renouvellement ou rupture conforme a la legislation applicable."
        )
    if type_contrat == 'CDImp':
        return (
            "Le present contrat est conclu pour une duree imprecise liee a l'execution de la mission ou de l'activite indiquee. "
            "Sa fin interviendra conformement aux conditions prevues par le Code du Travail."
        )
    if type_contrat == 'CTI':
        return (
            "Le present contrat est un contrat de travail intermittent. "
            "Les periodes travaillees sont organisees selon les besoins de l'activite et les conditions convenues entre les parties."
        )
    if type_contrat == 'stage':
        return (
            "Le present document formalise une convention de stage. "
            "Le stagiaire intervient dans un objectif de formation pratique et d'acquisition d'experience professionnelle."
        )
    if type_contrat == 'apprentissage':
        return (
            "Le present document formalise un contrat d'apprentissage. "
            "L'apprenti beneficie d'une formation pratique au poste et d'un encadrement professionnel."
        )
    if type_contrat == 'temporaire':
        return (
            "Le present contrat est conclu pour un besoin temporaire de main-d'oeuvre. "
            "Il est limite a la periode et aux missions prevues dans le present document."
        )
    return "Le present contrat est etabli selon le type de contrat selectionne dans le dossier du travailleur."


def _paragraph(texte, bold=False, size=22):
    texte = escape(str(texte))
    bold_xml = '<w:b/>' if bold else ''
    return (
        '<w:p><w:r><w:rPr>'
        f'{bold_xml}<w:sz w:val="{size}"/>'
        '</w:rPr>'
        f'<w:t xml:space="preserve">{texte}</w:t>'
        '</w:r></w:p>'
    )


def _empty_paragraph():
    return '<w:p/>'


def _document_xml(paragraphes):
    body = ''.join(paragraphes)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>'''


def _build_docx(document_xml):
    buffer = BytesIO()
    with ZipFile(buffer, 'w', ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
        docx.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        docx.writestr('word/document.xml', document_xml)
    buffer.seek(0)
    return buffer


def generer_contrat_employe_docx(contrat):
    employe = contrat.employe
    entreprise = employe.entreprise
    poste = employe.poste
    service = employe.service
    etablissement = employe.etablissement
    bulletin = _premier_bulletin_contrat(contrat)
    salaire_base, accessoires, remuneration_totale = _elements_remuneration_depuis_bulletin(bulletin)

    type_contrat = _libelle_choice(contrat, 'type_contrat')
    categorie_poste = _libelle_choice(poste, 'categorie_professionnelle') if poste else 'Non renseignee'
    mode_paiement = _libelle_choice(employe, 'mode_paiement')

    paragraphes = [
        _paragraph(f"CONTRAT DE TRAVAIL - {type_contrat.upper()}", bold=True, size=32),
        _paragraph(f"Numero de contrat: {_texte(contrat.num_contrat)}", bold=True),
        _empty_paragraph(),
        _paragraph("1. Parties au contrat", bold=True, size=26),
        _paragraph(f"Employeur: {_texte(getattr(entreprise, 'nom_entreprise', None))}"),
        _paragraph(f"Adresse employeur: {_texte(getattr(entreprise, 'adresse', None))}"),
        _paragraph(f"NIF: {_texte(getattr(entreprise, 'nif', None))} | CNSS: {_texte(getattr(entreprise, 'num_cnss', None))}"),
        _paragraph(f"Travailleur: {_texte(employe.civilite, '')} {_texte(employe.nom, '')} {_texte(employe.prenoms, '')}"),
        _paragraph(f"Matricule: {_texte(employe.matricule)} | Nationalite: {_texte(employe.nationalite)}"),
        _paragraph(f"Piece d'identite: {_texte(employe.type_piece_identite)} N° {_texte(employe.numero_piece_identite)}"),
        _paragraph(f"Adresse du travailleur: {_texte(employe.adresse_actuelle)}"),
        _empty_paragraph(),
        _paragraph("2. Nature et duree du contrat", bold=True, size=26),
        _paragraph(f"Type de contrat: {type_contrat}"),
        _paragraph(f"Date de debut: {_date(contrat.date_debut)}"),
        _paragraph(f"Date de fin: {_date(contrat.date_fin)}"),
        _paragraph(f"Duree prevue: {_texte(contrat.duree_mois)} mois"),
        _paragraph(_clause_type_contrat(contrat)),
        _empty_paragraph(),
        _paragraph("3. Poste, affectation et missions", bold=True, size=26),
        _paragraph(f"Poste: {_texte(getattr(poste, 'intitule_poste', None))}"),
        _paragraph(f"Categorie professionnelle: {categorie_poste}"),
        _paragraph(f"Classification: {_texte(getattr(poste, 'classification', None))}"),
        _paragraph(f"Service: {_texte(getattr(service, 'nom_service', None))}"),
        _paragraph(f"Etablissement: {_texte(getattr(etablissement, 'nom_etablissement', None))}"),
        _paragraph(f"Lieu de travail: {_texte(getattr(etablissement, 'ville', None), _texte(getattr(entreprise, 'ville', None)))}"),
    ]

    responsabilites = _texte(getattr(poste, 'responsabilites', None), '')
    if responsabilites:
        paragraphes.append(_paragraph(f"Responsabilites principales: {responsabilites}"))
    description = _texte(getattr(poste, 'description_poste', None), '')
    if description:
        paragraphes.append(_paragraph(f"Description du poste: {description}"))

    paragraphes.extend([
        _empty_paragraph(),
        _paragraph("4. Remuneration et avantages", bold=True, size=26),
        _paragraph(f"Source de remuneration: premier bulletin calcule {_texte(bulletin.numero_bulletin)} ({bulletin.mois_paie:02d}/{bulletin.annee_paie})"),
        _paragraph(f"Salaire de base mensuel: {_montant(salaire_base)}"),
        _paragraph(f"Salaire brut mensuel retenu: {_montant(remuneration_totale)}"),
        _paragraph(f"Net a payer du premier bulletin: {_montant(bulletin.net_a_payer)}"),
    ])
    if accessoires:
        paragraphes.append(_paragraph("Autres elements fixes pris en compte:", bold=True))
        for libelle, montant in accessoires:
            paragraphes.append(_paragraph(f"- {libelle}: {_montant(montant)}"))
    else:
        paragraphes.append(_paragraph("Autres elements fixes pris en compte: aucun element actif renseigne."))

    paragraphes.extend([
        _paragraph(f"Mode de paiement: {mode_paiement}"),
        _empty_paragraph(),
        _paragraph("5. Periode d'essai", bold=True, size=26),
        _paragraph(f"Duree de la periode d'essai: {_texte(contrat.periode_essai_mois, '0')} mois"),
        _paragraph(f"Fin de periode d'essai: {_date(contrat.date_fin_essai)}"),
        _empty_paragraph(),
        _paragraph("6. Obligations generales", bold=True, size=26),
        _paragraph("Le travailleur s'engage a executer ses fonctions avec diligence, discretion et respect des procedures internes."),
        _paragraph("L'employeur s'engage a fournir les conditions normales d'execution du travail et a respecter les obligations sociales et fiscales applicables."),
        _paragraph("Les parties conviennent que le present contrat reste soumis au Code du Travail de la Republique de Guinee et aux textes applicables."),
        _empty_paragraph(),
        _paragraph("7. Signature", bold=True, size=26),
        _paragraph(f"Fait a {_texte(getattr(entreprise, 'ville', None), 'Conakry')}, le {_date(contrat.date_signature or timezone.now().date())}"),
        _empty_paragraph(),
        _paragraph("Pour l'employeur: ______________________________"),
        _empty_paragraph(),
        _paragraph("Le travailleur: ______________________________"),
    ])

    return _build_docx(_document_xml(paragraphes))
