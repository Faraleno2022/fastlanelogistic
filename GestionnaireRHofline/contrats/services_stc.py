"""
Service calcul Solde de Tout Compte - Fin de CDD
Conforme au Code du Travail de la République de Guinée
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta


def calculer_solde_tout_compte(contrat, date_fin_effective=None):
    """
    Calcule les indemnités de fin de CDD.

    Éléments calculés :
    - Indemnité de fin de CDD (7% du salaire brut total perçu)
    - Indemnité compensatrice de congés non pris (2,5 j/mois)

    Args:
        contrat: Instance du modèle Contrat
        date_fin_effective: date de fin effective (écrase contrat.date_fin si fournie)

    Returns:
        dict avec le détail complet du calcul
    """
    emp = contrat.employe
    date_fin = date_fin_effective or contrat.date_fin or date.today()
    date_debut = contrat.date_debut

    # === 1. DURÉE DU CONTRAT ===
    delta = relativedelta(date_fin, date_debut)
    duree_mois = max(delta.years * 12 + delta.months, 0)
    duree_jours = max((date_fin - date_debut).days, 0)
    duree_annees = round(duree_jours / 365, 2)

    # === 2. SALAIRE MENSUEL DE RÉFÉRENCE ===
    salaire_mensuel = Decimal('0')

    # Priorité 1 : dernier bulletin de paie validé
    try:
        from paie.models import BulletinPaie
        dernier_bulletin = BulletinPaie.objects.filter(
            employe=emp,
            statut='valide'
        ).order_by('-annee_paie', '-mois_paie').first()
        if dernier_bulletin and dernier_bulletin.salaire_brut:
            salaire_mensuel = Decimal(str(dernier_bulletin.salaire_brut))
    except Exception:
        pass

    # Priorité 2 : salaire de base du contrat
    if salaire_mensuel == 0 and contrat.salaire_base:
        salaire_mensuel = Decimal(str(contrat.salaire_base))

    salaire_journalier = (salaire_mensuel / 26).quantize(
        Decimal('1'), rounding=ROUND_HALF_UP
    ) if salaire_mensuel else Decimal('0')

    # === 3. INDEMNITÉ DE FIN DE CDD ===
    # Art. Code du Travail guinéen : 7% de la rémunération totale brute perçue
    remuneration_totale = salaire_mensuel * Decimal(str(duree_mois))
    indemnite_fin_cdd = (remuneration_totale * Decimal('0.07')).quantize(
        Decimal('1'), rounding=ROUND_HALF_UP
    )

    # === 4. INDEMNITÉ COMPENSATRICE DE CONGÉS NON PRIS ===
    conges_acquis = Decimal('2.5') * Decimal(str(duree_mois))
    conges_pris = Decimal('0')
    conges_restants = Decimal('0')

    try:
        from temps_travail.models import SoldeConge
        solde = SoldeConge.objects.filter(
            employe=emp,
            annee=date_fin.year
        ).first()
        if solde:
            conges_acquis = Decimal(str(solde.conges_acquis or conges_acquis))
            conges_pris = Decimal(str(solde.conges_pris or 0))
            conges_restants = max(
                Decimal(str(getattr(solde, 'conges_restants', 0) or 0)),
                conges_acquis - conges_pris
            )
        else:
            conges_restants = conges_acquis - conges_pris
    except Exception:
        conges_restants = conges_acquis - conges_pris

    indemnite_conges = (conges_restants * salaire_journalier).quantize(
        Decimal('1'), rounding=ROUND_HALF_UP
    )

    # === 5. TOTAUX ===
    total_brut = indemnite_fin_cdd + indemnite_conges
    cnss_employe = (total_brut * Decimal('0.05')).quantize(
        Decimal('1'), rounding=ROUND_HALF_UP
    )
    net_a_payer = total_brut - cnss_employe

    return {
        'employe': emp,
        'contrat': contrat,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'duree_mois': duree_mois,
        'duree_annees': duree_annees,
        'salaire_mensuel': salaire_mensuel,
        'salaire_journalier': salaire_journalier,
        'remuneration_totale': remuneration_totale,
        # Indemnité fin CDD
        'indemnite_fin_cdd': indemnite_fin_cdd,
        'taux_fin_cdd': Decimal('7'),
        # Congés
        'conges_acquis': conges_acquis,
        'conges_pris': conges_pris,
        'conges_restants': conges_restants,
        'indemnite_conges': indemnite_conges,
        # Totaux
        'total_brut': total_brut,
        'cnss_employe': cnss_employe,
        'net_a_payer': net_a_payer,
    }
