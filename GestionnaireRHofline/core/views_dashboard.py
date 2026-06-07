"""
Tableau de bord RH avec KPIs et statistiques.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from employes.models import Employe
from paie.models import BulletinPaie, PeriodePaie
from paie.models_pret import Pret
from temps_travail.models import Conge, HeureSupplementaire, Absence
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def tableau_bord_rh(request):
    """Tableau de bord RH avec KPIs"""
    entreprise = request.user.entreprise
    aujourd_hui = date.today()
    mois_courant = aujourd_hui.month
    annee_courante = aujourd_hui.year
    
    # ============ EFFECTIFS ============
    employes_actifs = Employe.objects.filter(
        entreprise=entreprise,
        statut_employe='actif'
    )
    
    effectifs = {
        'total': employes_actifs.count(),
        'hommes': employes_actifs.filter(sexe='M').count(),
        'femmes': employes_actifs.filter(sexe='F').count(),
        'cdi': employes_actifs.filter(type_contrat='cdi').count(),
        'cdd': employes_actifs.filter(type_contrat='cdd').count(),
        'stage': employes_actifs.filter(type_contrat__in=['stage', 'apprentissage']).count(),
    }
    
    # Répartition par département
    repartition_dept = employes_actifs.values('departement__nom').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Ancienneté moyenne
    employes_avec_date = employes_actifs.exclude(date_embauche__isnull=True)
    if employes_avec_date.exists():
        total_jours = sum((aujourd_hui - e.date_embauche).days for e in employes_avec_date)
        anciennete_moyenne = total_jours / employes_avec_date.count() / 365
    else:
        anciennete_moyenne = 0
    
    effectifs['anciennete_moyenne'] = round(anciennete_moyenne, 1)
    
    # ============ MASSE SALARIALE ============
    # Mois courant
    bulletins_mois = BulletinPaie.objects.filter(
        employe__entreprise=entreprise,
        periode__annee=annee_courante,
        periode__mois=mois_courant,
        statut_bulletin__in=['valide', 'paye']
    )
    
    masse_salariale_mois = bulletins_mois.aggregate(
        brut=Sum('salaire_brut'),
        net=Sum('net_a_payer'),
        cnss_employe=Sum('cnss_employe'),
        cnss_employeur=Sum('cnss_employeur'),
        rts=Sum('irg'),
    )
    
    # Année courante
    bulletins_annee = BulletinPaie.objects.filter(
        employe__entreprise=entreprise,
        periode__annee=annee_courante,
        statut_bulletin__in=['valide', 'paye']
    )
    
    masse_salariale_annee = bulletins_annee.aggregate(
        brut=Sum('salaire_brut'),
        net=Sum('net_a_payer'),
    )
    
    # Évolution sur 6 mois
    evolution_masse = []
    for i in range(5, -1, -1):
        date_mois = aujourd_hui - relativedelta(months=i)
        total = BulletinPaie.objects.filter(
            employe__entreprise=entreprise,
            periode__annee=date_mois.year,
            periode__mois=date_mois.month,
            statut_bulletin__in=['valide', 'paye']
        ).aggregate(total=Sum('salaire_brut'))['total'] or 0
        
        evolution_masse.append({
            'mois': date_mois.strftime('%b %Y'),
            'montant': float(total),
        })
    
    paie = {
        'brut_mois': masse_salariale_mois['brut'] or Decimal('0'),
        'net_mois': masse_salariale_mois['net'] or Decimal('0'),
        'cnss_employe': masse_salariale_mois['cnss_employe'] or Decimal('0'),
        'cnss_employeur': masse_salariale_mois['cnss_employeur'] or Decimal('0'),
        'rts': masse_salariale_mois['rts'] or Decimal('0'),
        'brut_annee': masse_salariale_annee['brut'] or Decimal('0'),
        'net_annee': masse_salariale_annee['net'] or Decimal('0'),
        'evolution': evolution_masse,
    }
    
    # Salaire moyen
    if effectifs['total'] > 0 and paie['brut_mois'] > 0:
        paie['salaire_moyen'] = paie['brut_mois'] / effectifs['total']
    else:
        paie['salaire_moyen'] = Decimal('0')
    
    # ============ CONGÉS ============
    conges_en_cours = Conge.objects.filter(
        employe__entreprise=entreprise,
        date_debut__lte=aujourd_hui,
        date_fin__gte=aujourd_hui,
        statut_demande='approuve'
    ).count()
    
    conges_en_attente = Conge.objects.filter(
        employe__entreprise=entreprise,
        statut_demande='en_attente'
    ).count()
    
    conges_mois = Conge.objects.filter(
        employe__entreprise=entreprise,
        date_debut__year=annee_courante,
        date_debut__month=mois_courant,
        statut_demande='approuve'
    ).aggregate(total=Sum('nombre_jours'))['total'] or 0
    
    conges = {
        'en_cours': conges_en_cours,
        'en_attente': conges_en_attente,
        'jours_mois': conges_mois,
    }
    
    # ============ HEURES SUPPLÉMENTAIRES ============
    hs_mois = HeureSupplementaire.objects.filter(
        employe__entreprise=entreprise,
        date_hs__year=annee_courante,
        date_hs__month=mois_courant,
        statut='valide'
    ).aggregate(
        heures=Sum('nombre_heures'),
        montant=Sum('montant_hs')
    )
    
    heures_sup = {
        'heures_mois': hs_mois['heures'] or Decimal('0'),
        'montant_mois': hs_mois['montant'] or Decimal('0'),
    }
    
    # ============ PRÊTS ============
    prets_en_cours = Pret.objects.filter(
        employe__entreprise=entreprise,
        statut='en_cours'
    )
    
    prets = {
        'nb_en_cours': prets_en_cours.count(),
        'solde_total': prets_en_cours.aggregate(total=Sum('solde_restant'))['total'] or Decimal('0'),
        'en_attente': Pret.objects.filter(employe__entreprise=entreprise, statut='en_attente').count(),
    }
    
    # ============ ABSENCES ============
    absences_mois = Absence.objects.filter(
        employe__entreprise=entreprise,
        date_absence__year=annee_courante,
        date_absence__month=mois_courant
    ).aggregate(
        total=Sum('duree_jours'),
        count=Count('id')
    )
    
    absences = {
        'jours_mois': absences_mois['total'] or 0,
        'nb_absences': absences_mois['count'] or 0,
    }
    
    # ============ ALERTES ============
    alertes = []
    
    # Contrats expirant dans 30 jours
    date_limite = aujourd_hui + timedelta(days=30)
    contrats_expirant = Employe.objects.filter(
        entreprise=entreprise,
        statut_employe='actif',
        date_fin_contrat__lte=date_limite,
        date_fin_contrat__gte=aujourd_hui
    ).count()
    
    if contrats_expirant > 0:
        alertes.append({
            'type': 'warning',
            'message': f'{contrats_expirant} contrat(s) expirant dans les 30 jours',
            'icon': 'fa-file-contract'
        })
    
    # Congés en attente
    if conges['en_attente'] > 0:
        alertes.append({
            'type': 'info',
            'message': f'{conges["en_attente"]} demande(s) de congé en attente',
            'icon': 'fa-calendar-alt'
        })
    
    # Prêts en attente
    if prets['en_attente'] > 0:
        alertes.append({
            'type': 'info',
            'message': f'{prets["en_attente"]} demande(s) de prêt en attente',
            'icon': 'fa-hand-holding-usd'
        })
    
    # ============ TOP 5 SALAIRES ============
    top_salaires = bulletins_mois.order_by('-salaire_brut')[:5]
    
    context = {
        'effectifs': effectifs,
        'paie': paie,
        'conges': conges,
        'heures_sup': heures_sup,
        'prets': prets,
        'absences': absences,
        'alertes': alertes,
        'repartition_dept': list(repartition_dept),
        'top_salaires': top_salaires,
        'mois_courant': mois_courant,
        'annee_courante': annee_courante,
    }
    
    return render(request, 'core/tableau_bord_rh.html', context)
