"""
Tableau de bord des absences / congés.
Utilise le modèle Conge de temps_travail.
"""
import io
import json
import calendar
from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q

from temps_travail.models import Conge
from employes.models import Employe
from core.models import Service
from core.decorators import reauth_required, entreprise_active_required

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

MOIS_FR = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

# Coût journalier moyen estimé (utilisé si on ne peut pas le calculer depuis BulletinPaie)
COUT_JOURNALIER_DEFAUT = Decimal('50000')  # GNF


def _cout_journalier_moyen(entreprise, annee, mois):
    """Calcule le coût journalier moyen depuis les bulletins du mois."""
    try:
        from paie.models import BulletinPaie
        agg = BulletinPaie.objects.filter(
            employe__entreprise=entreprise,
            annee_paie=annee,
            mois_paie=mois,
            statut_bulletin__in=['calcule', 'valide', 'paye'],
        ).aggregate(total_brut=Sum('salaire_brut'), nb=Count('id'))
        if agg['nb'] and agg['total_brut']:
            return agg['total_brut'] / agg['nb'] / 22  # 22 jours ouvrables
    except Exception:
        pass
    return COUT_JOURNALIER_DEFAUT


@reauth_required
@login_required
@entreprise_active_required
@reauth_required
def tableau_bord_absences(request):
    """Tableau de bord mensuel des absences."""
    entreprise = request.user.entreprise
    today = date.today()

    annee = int(request.GET.get('annee', today.year))
    mois = int(request.GET.get('mois', today.month))
    service_id = request.GET.get('service', '')

    # Services
    services = Service.objects.filter(
        entreprise=entreprise,
        actif=True,
    ).order_by('nom_service')

    # Nombre de jours dans le mois
    _, nb_jours_mois = calendar.monthrange(annee, mois)
    premier_jour = date(annee, mois, 1)
    dernier_jour = date(annee, mois, nb_jours_mois)

    # Queryset de base des congés du mois
    conges_qs = Conge.objects.filter(
        employe__entreprise=entreprise,
        date_debut__lte=dernier_jour,
        date_fin__gte=premier_jour,
    ).select_related('employe__service', 'employe')

    if service_id:
        conges_qs = conges_qs.filter(employe__service_id=service_id)

    # Employés actifs de l'entreprise
    employes_actifs = Employe.objects.filter(
        entreprise=entreprise,
        statut_employe='actif',
    )
    if service_id:
        employes_actifs = employes_actifs.filter(service_id=service_id)
    nb_employes = employes_actifs.count()

    # --- Indicateurs globaux du mois ---
    total_jours_absences = sum(c.nombre_jours for c in conges_qs)
    taux_absenteisme = 0
    if nb_employes and nb_jours_mois:
        taux_absenteisme = total_jours_absences / (nb_employes * nb_jours_mois) * 100

    cout_journalier = _cout_journalier_moyen(entreprise, annee, mois)
    cout_estime = total_jours_absences * cout_journalier

    # --- Absences par employé (pour alertes) ---
    absences_par_employe = defaultdict(lambda: {'nom': '', 'nb_absences': 0, 'jours': 0, 'non_justifiees': 0})
    for c in conges_qs:
        emp_id = c.employe_id
        absences_par_employe[emp_id]['nom'] = f"{c.employe.nom} {c.employe.prenoms}"
        absences_par_employe[emp_id]['matricule'] = c.employe.matricule
        absences_par_employe[emp_id]['service'] = str(c.employe.service) if c.employe.service else '-'
        absences_par_employe[emp_id]['nb_absences'] += 1
        absences_par_employe[emp_id]['jours'] += c.nombre_jours
        # Absence non justifiée = statut en_attente ou rejeté
        if c.statut_demande in ('en_attente', 'rejete'):
            absences_par_employe[emp_id]['non_justifiees'] += 1

    # Alertes: employés avec >= 3 absences non justifiées dans le mois
    alertes = [
        emp for emp in absences_par_employe.values()
        if emp['non_justifiees'] >= 3
    ]

    # --- Calendrier mensuel des absences ---
    # Structure: {jour: [{'employe': str, 'type': str, 'statut': str}]}
    calendrier = {j: [] for j in range(1, nb_jours_mois + 1)}
    COULEURS_TYPE = {
        'annuel': 'success',
        'maladie': 'danger',
        'maternite': 'info',
        'paternite': 'info',
        'sans_solde': 'secondary',
        'formation': 'warning',
    }
    for c in conges_qs:
        debut = max(c.date_debut, premier_jour)
        fin = min(c.date_fin, dernier_jour)
        current = debut
        while current <= fin:
            j = current.day
            if j in calendrier:
                calendrier[j].append({
                    'employe': f"{c.employe.nom} {c.employe.prenoms}",
                    'matricule': c.employe.matricule,
                    'type': c.get_type_conge_display(),
                    'type_code': c.type_conge,
                    'couleur': COULEURS_TYPE.get(c.type_conge, 'primary'),
                    'statut': c.get_statut_demande_display(),
                })
            current += timedelta(days=1)

    # Jours de la semaine pour le calendrier
    premier_semaine = premier_jour.weekday()  # 0=lundi
    jours_semaine = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

    # --- Répartition par type d'absence ---
    par_type = defaultdict(lambda: {'label': '', 'nb': 0, 'jours': 0})
    for c in conges_qs:
        par_type[c.type_conge]['label'] = c.get_type_conge_display()
        par_type[c.type_conge]['nb'] += 1
        par_type[c.type_conge]['jours'] += c.nombre_jours

    par_type_list = sorted(par_type.values(), key=lambda x: -x['jours'])

    # --- Répartition par service ---
    par_service = defaultdict(lambda: {'nom': '', 'nb': 0, 'jours': 0})
    for c in conges_qs:
        svc = c.employe.service
        svc_key = svc.pk if svc else 0
        par_service[svc_key]['nom'] = str(svc) if svc else 'Sans service'
        par_service[svc_key]['nb'] += 1
        par_service[svc_key]['jours'] += c.nombre_jours

    par_service_list = sorted(par_service.values(), key=lambda x: -x['jours'])

    # Données Chart.js pour répartition par type
    chart_labels = json.dumps([t['label'] for t in par_type_list])
    chart_jours = json.dumps([t['jours'] for t in par_type_list])
    chart_couleurs = json.dumps([
        '#dc3545', '#0dcaf0', '#198754', '#ffc107', '#6c757d', '#0d6efd', '#fd7e14'
    ][:len(par_type_list)])

    # Années disponibles
    annees_dispo = list(range(today.year - 2, today.year + 2))

    # Calendrier JSON pour JS
    calendrier_json = json.dumps({str(j): v for j, v in calendrier.items()})

    context = {
        'annee': annee,
        'mois': mois,
        'mois_label': MOIS_FR[mois],
        'service_id': service_id,
        'services': services,
        'nb_employes': nb_employes,
        'nb_jours_mois': nb_jours_mois,
        'total_jours_absences': total_jours_absences,
        'taux_absenteisme': taux_absenteisme,
        'cout_estime': cout_estime,
        'alertes': alertes,
        'absences_par_employe': sorted(absences_par_employe.values(), key=lambda x: -x['jours']),
        'calendrier': calendrier,
        'calendrier_json': calendrier_json,
        'premier_semaine': premier_semaine,
        'jours_semaine': jours_semaine,
        'par_type': par_type_list,
        'par_service': par_service_list,
        'chart_labels': chart_labels,
        'chart_jours': chart_jours,
        'chart_couleurs': chart_couleurs,
        'annees_dispo': annees_dispo,
        'mois_liste': list(range(1, 13)),
        'mois_fr': MOIS_FR,
    }
    return render(request, 'employes/tableau_bord_absences.html', context)


@reauth_required
@login_required
@entreprise_active_required
@reauth_required
def tableau_bord_absences_pdf(request):
    """Export PDF du rapport mensuel d'absences."""
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("ReportLab non disponible", status=500)

    entreprise = request.user.entreprise
    today = date.today()
    annee = int(request.GET.get('annee', today.year))
    mois = int(request.GET.get('mois', today.month))
    service_id = request.GET.get('service', '')

    _, nb_jours_mois = calendar.monthrange(annee, mois)
    premier_jour = date(annee, mois, 1)
    dernier_jour = date(annee, mois, nb_jours_mois)

    conges_qs = Conge.objects.filter(
        employe__entreprise=entreprise,
        date_debut__lte=dernier_jour,
        date_fin__gte=premier_jour,
    ).select_related('employe__service', 'employe').order_by('employe__nom', 'date_debut')

    if service_id:
        conges_qs = conges_qs.filter(employe__service_id=service_id)

    nb_employes = Employe.objects.filter(
        entreprise=entreprise, statut_employe='actif'
    ).count()
    total_jours = sum(c.nombre_jours for c in conges_qs)
    taux = (total_jours / (nb_employes * nb_jours_mois) * 100) if nb_employes and nb_jours_mois else 0
    cout_journalier = _cout_journalier_moyen(entreprise, annee, mois)
    cout_estime = total_jours * cout_journalier

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16,
                                  spaceAfter=4, alignment=TA_CENTER)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10,
                                spaceAfter=12, alignment=TA_CENTER)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=12,
                                    fontName='Helvetica-Bold', spaceAfter=6, spaceBefore=10)

    elements.append(Paragraph(f"RAPPORT MENSUEL DES ABSENCES", title_style))
    elements.append(Paragraph(f"{MOIS_FR[mois]} {annee} - Généré le {today.strftime('%d/%m/%Y')}", sub_style))

    # Indicateurs
    elements.append(Paragraph("Indicateurs du mois", section_style))
    indic_data = [
        ['Indicateur', 'Valeur'],
        ['Employés actifs', str(nb_employes)],
        ['Total jours d\'absence', str(total_jours)],
        ['Taux d\'absentéisme', f"{taux:.2f}%"],
        ['Coût estimé des absences', f"{cout_estime:,.0f} GNF"],
    ]
    t_indic = Table(indic_data, colWidths=[9*cm, 6*cm])
    t_indic.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EBF3FF')]),
    ]))
    elements.append(t_indic)
    elements.append(Spacer(1, 0.5*cm))

    # Liste des absences
    elements.append(Paragraph("Détail des absences", section_style))
    headers = ['Employé', 'Matricule', 'Service', 'Type', 'Début', 'Fin', 'Jours', 'Statut']
    rows = [headers]
    for c in conges_qs:
        rows.append([
            f"{c.employe.nom} {c.employe.prenoms}",
            c.employe.matricule,
            str(c.employe.service) if c.employe.service else '-',
            c.get_type_conge_display()[:20],
            c.date_debut.strftime('%d/%m/%Y'),
            c.date_fin.strftime('%d/%m/%Y'),
            str(c.nombre_jours),
            c.get_statut_demande_display(),
        ])

    if len(rows) > 1:
        col_widths = [4*cm, 2.5*cm, 3*cm, 3*cm, 2.2*cm, 2.2*cm, 1.5*cm, 2.5*cm]
        t_abs = Table(rows, colWidths=col_widths, repeatRows=1)
        t_abs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EBF3FF')]),
            ('ALIGN', (6, 0), (6, -1), 'CENTER'),
        ]))
        elements.append(t_abs)
    else:
        elements.append(Paragraph("Aucune absence enregistrée pour cette période.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="absences_{annee}_{mois:02d}.pdf"'
    return response
