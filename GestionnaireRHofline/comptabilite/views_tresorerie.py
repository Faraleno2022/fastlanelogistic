"""
Vues pour le module Trésorerie Avancée
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import CompteBancaire
from .models_tresorerie import (
    SynchronisationBancaire, EcheancierTresorerie, SituationTresorerie,
    OptimisationTresorerie, LiquiditeSouhaitee, GestionNumeraire,
    AlerteTresorerie, FluxTresorerieJournalier
)


@reauth_required
@login_required
def dashboard_tresorerie(request):
    """Tableau de bord trésorerie avancée"""
    entreprise = request.user.entreprise
    today = date.today()
    
    # Situation consolidée
    situation_jour = SituationTresorerie.objects.filter(
        entreprise=entreprise,
        date_situation=today,
        compte_bancaire__isnull=True
    ).first()
    
    # Comptes bancaires avec soldes
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    # Alertes actives
    alertes_actives = AlerteTresorerie.objects.filter(
        entreprise=entreprise,
        statut='active'
    ).order_by('-niveau', '-date_creation')[:10]
    
    # Échéances à venir (7 jours)
    echeances_proches = EcheancierTresorerie.objects.filter(
        entreprise=entreprise,
        statut__in=['prevu', 'confirme'],
        date_echeance__gte=today,
        date_echeance__lte=today + timedelta(days=7)
    ).order_by('date_echeance')[:15]
    
    # Totaux échéances
    encaissements_prevus = EcheancierTresorerie.objects.filter(
        entreprise=entreprise,
        type_flux='encaissement',
        statut__in=['prevu', 'confirme'],
        date_echeance__gte=today,
        date_echeance__lte=today + timedelta(days=30)
    ).aggregate(total=Sum('montant_prevu'))['total'] or Decimal('0.00')
    
    decaissements_prevus = EcheancierTresorerie.objects.filter(
        entreprise=entreprise,
        type_flux='decaissement',
        statut__in=['prevu', 'confirme'],
        date_echeance__gte=today,
        date_echeance__lte=today + timedelta(days=30)
    ).aggregate(total=Sum('montant_prevu'))['total'] or Decimal('0.00')
    
    # Synchronisations en erreur
    syncs_erreur = SynchronisationBancaire.objects.filter(
        entreprise=entreprise,
        statut='erreur'
    ).count()
    
    context = {
        'situation_jour': situation_jour,
        'comptes': comptes,
        'alertes_actives': alertes_actives,
        'echeances_proches': echeances_proches,
        'encaissements_prevus': encaissements_prevus,
        'decaissements_prevus': decaissements_prevus,
        'syncs_erreur': syncs_erreur,
        'nb_alertes': alertes_actives.count(),
    }
    return render(request, 'comptabilite/tresorerie/dashboard.html', context)


@reauth_required
@login_required
def situation_tresorerie_list(request):
    """Liste des situations de trésorerie"""
    entreprise = request.user.entreprise
    situations = SituationTresorerie.objects.filter(entreprise=entreprise)
    
    # Filtres
    periodicite = request.GET.get('periodicite')
    compte_id = request.GET.get('compte')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if periodicite:
        situations = situations.filter(periodicite=periodicite)
    if compte_id:
        situations = situations.filter(compte_bancaire_id=compte_id)
    if date_debut:
        situations = situations.filter(date_situation__gte=date_debut)
    if date_fin:
        situations = situations.filter(date_situation__lte=date_fin)
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'situations': situations[:100],
        'comptes': comptes,
    }
    return render(request, 'comptabilite/tresorerie/situation_list.html', context)


@reauth_required
@login_required
def situation_tresorerie_detail(request, pk):
    """Détail d'une situation de trésorerie"""
    situation = get_object_or_404(SituationTresorerie, pk=pk, entreprise=request.user.entreprise)
    return render(request, 'comptabilite/tresorerie/situation_detail.html', {'situation': situation})


@reauth_required
@login_required
def generer_situation_journaliere(request):
    """Génère la situation de trésorerie du jour"""
    entreprise = request.user.entreprise
    today = date.today()
    
    if request.method == 'GET':
        # Afficher le formulaire de confirmation
        comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
        solde_total = sum(c.solde_initial for c in comptes)
        context = {
            'date': today,
            'comptes': comptes,
            'solde_total': solde_total,
        }
        return render(request, 'comptabilite/tresorerie/generer_situation.html', context)
    
    # Vérifier si déjà générée
    if SituationTresorerie.objects.filter(
        entreprise=entreprise, 
        date_situation=today,
        compte_bancaire__isnull=True
    ).exists():
        messages.warning(request, "La situation du jour existe déjà.")
        return redirect('comptabilite:tresorerie_dashboard')
    
    # Calculer les soldes
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    solde_total = sum(c.solde_initial for c in comptes)  # Simplification
    
    # Créer la situation consolidée
    situation = SituationTresorerie.objects.create(
        entreprise=entreprise,
        date_situation=today,
        periodicite='quotidien',
        compte_bancaire=None,
        solde_debut=solde_total,
        solde_fin=solde_total,
    )
    
    # Calculer les prévisions
    situation.calculer_previsions()
    
    messages.success(request, "Situation de trésorerie générée avec succès.")
    return redirect('comptabilite:tresorerie_dashboard')


# ============================================================================
# ÉCHÉANCIER
# ============================================================================

@reauth_required
@login_required
def echeancier_list(request):
    """Liste de l'échéancier de trésorerie"""
    entreprise = request.user.entreprise
    echeances = EcheancierTresorerie.objects.filter(entreprise=entreprise)
    
    # Filtres
    type_flux = request.GET.get('type_flux')
    statut = request.GET.get('statut')
    origine = request.GET.get('origine')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if type_flux:
        echeances = echeances.filter(type_flux=type_flux)
    if statut:
        echeances = echeances.filter(statut=statut)
    if origine:
        echeances = echeances.filter(origine=origine)
    if date_debut:
        echeances = echeances.filter(date_echeance__gte=date_debut)
    if date_fin:
        echeances = echeances.filter(date_echeance__lte=date_fin)
    
    context = {
        'echeances': echeances[:200],
        'types_flux': EcheancierTresorerie.TYPES_FLUX,
        'statuts': EcheancierTresorerie.STATUTS,
        'origines': EcheancierTresorerie.ORIGINES,
    }
    return render(request, 'comptabilite/tresorerie/echeancier_list.html', context)


@reauth_required
@login_required
def echeancier_create(request):
    """Créer une échéance"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        echeance = EcheancierTresorerie(entreprise=entreprise)
        echeance.reference = request.POST.get('reference')
        echeance.libelle = request.POST.get('libelle')
        echeance.type_flux = request.POST.get('type_flux')
        echeance.origine = request.POST.get('origine')
        echeance.montant_prevu = Decimal(request.POST.get('montant_prevu', '0'))
        echeance.date_echeance = request.POST.get('date_echeance')
        echeance.priorite = request.POST.get('priorite', 'normale')
        echeance.notes = request.POST.get('notes', '')
        
        compte_id = request.POST.get('compte_bancaire')
        if compte_id:
            echeance.compte_bancaire_id = compte_id
        
        tiers_id = request.POST.get('tiers')
        if tiers_id:
            echeance.tiers_id = tiers_id
        
        echeance.save()
        messages.success(request, "Échéance créée avec succès.")
        return redirect('comptabilite:echeancier_list')
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    from .models import Tiers
    tiers = Tiers.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'comptes': comptes,
        'tiers': tiers,
        'types_flux': EcheancierTresorerie.TYPES_FLUX,
        'origines': EcheancierTresorerie.ORIGINES,
        'priorites': EcheancierTresorerie.PRIORITES,
    }
    return render(request, 'comptabilite/tresorerie/echeancier_form.html', context)


@reauth_required
@login_required
def echeancier_detail(request, pk):
    """Détail d'une échéance"""
    echeance = get_object_or_404(EcheancierTresorerie, pk=pk, entreprise=request.user.entreprise)
    return render(request, 'comptabilite/tresorerie/echeancier_detail.html', {'echeance': echeance})


@reauth_required
@login_required
def echeancier_update(request, pk):
    """Modifier une échéance"""
    echeance = get_object_or_404(EcheancierTresorerie, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        echeance.libelle = request.POST.get('libelle')
        echeance.montant_prevu = Decimal(request.POST.get('montant_prevu', '0'))
        echeance.date_echeance = request.POST.get('date_echeance')
        echeance.statut = request.POST.get('statut')
        echeance.priorite = request.POST.get('priorite')
        echeance.notes = request.POST.get('notes', '')
        echeance.save()
        messages.success(request, "Échéance modifiée avec succès.")
        return redirect('comptabilite:echeancier_detail', pk=pk)
    
    comptes = CompteBancaire.objects.filter(entreprise=request.user.entreprise, est_actif=True)
    
    context = {
        'echeance': echeance,
        'comptes': comptes,
        'types_flux': EcheancierTresorerie.TYPES_FLUX,
        'statuts': EcheancierTresorerie.STATUTS,
        'priorites': EcheancierTresorerie.PRIORITES,
    }
    return render(request, 'comptabilite/tresorerie/echeancier_form.html', context)


@reauth_required
@login_required
def echeancier_realiser(request, pk):
    """Marquer une échéance comme réalisée"""
    echeance = get_object_or_404(EcheancierTresorerie, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        echeance.statut = 'realise'
        echeance.date_realisation = date.today()
        echeance.montant_realise = Decimal(request.POST.get('montant_realise', echeance.montant_prevu))
        echeance.save()
        messages.success(request, "Échéance marquée comme réalisée.")
    
    return redirect('comptabilite:echeancier_list')


# ============================================================================
# SYNCHRONISATION BANCAIRE
# ============================================================================

@reauth_required
@login_required
def synchronisation_list(request):
    """Liste des synchronisations bancaires"""
    entreprise = request.user.entreprise
    syncs = SynchronisationBancaire.objects.filter(entreprise=entreprise)
    
    context = {
        'synchronisations': syncs,
    }
    return render(request, 'comptabilite/tresorerie/synchronisation_list.html', context)


@reauth_required
@login_required
def synchronisation_create(request):
    """Créer une synchronisation bancaire"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        sync = SynchronisationBancaire(entreprise=entreprise)
        sync.compte_bancaire_id = request.POST.get('compte_bancaire')
        sync.nom_connexion = request.POST.get('nom_connexion')
        sync.protocole = request.POST.get('protocole')
        sync.frequence_sync = request.POST.get('frequence_sync')
        sync.url_api = request.POST.get('url_api') or None
        sync.identifiant_api = request.POST.get('identifiant_api') or None
        sync.reconciliation_auto = request.POST.get('reconciliation_auto') == 'on'
        sync.cree_par = request.user
        sync.save()
        messages.success(request, "Synchronisation créée avec succès.")
        return redirect('comptabilite:synchronisation_list')
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'comptes': comptes,
        'protocoles': SynchronisationBancaire.PROTOCOLES,
        'frequences': SynchronisationBancaire.FREQUENCES,
    }
    return render(request, 'comptabilite/tresorerie/synchronisation_form.html', context)


@reauth_required
@login_required
def synchronisation_executer(request, pk):
    """Exécuter une synchronisation"""
    sync = get_object_or_404(SynchronisationBancaire, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        # Simulation de synchronisation
        sync.statut = 'en_cours'
        sync.save()
        
        # TODO: Implémenter la vraie logique de synchronisation
        # Pour l'instant, on simule un succès
        sync.statut = 'active'
        sync.derniere_sync = timezone.now()
        sync.prochaine_sync = timezone.now() + timedelta(hours=24)
        sync.derniere_erreur = None
        sync.save()
        
        messages.success(request, f"Synchronisation '{sync.nom_connexion}' exécutée avec succès.")
    
    return redirect('comptabilite:synchronisation_list')


# ============================================================================
# ALERTES TRÉSORERIE
# ============================================================================

@reauth_required
@login_required
def alertes_tresorerie_list(request):
    """Liste des alertes de trésorerie"""
    entreprise = request.user.entreprise
    alertes = AlerteTresorerie.objects.filter(entreprise=entreprise)
    
    statut = request.GET.get('statut')
    niveau = request.GET.get('niveau')
    
    if statut:
        alertes = alertes.filter(statut=statut)
    if niveau:
        alertes = alertes.filter(niveau=niveau)
    
    context = {
        'alertes': alertes[:100],
        'statuts': AlerteTresorerie.STATUTS,
        'niveaux': AlerteTresorerie.NIVEAUX,
    }
    return render(request, 'comptabilite/tresorerie/alertes_list.html', context)


@reauth_required
@login_required
def alerte_acquitter(request, pk):
    """Acquitter une alerte"""
    alerte = get_object_or_404(AlerteTresorerie, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        alerte.statut = 'acquittee'
        alerte.acquittee_par = request.user
        alerte.date_acquittement = timezone.now()
        alerte.commentaire_traitement = request.POST.get('commentaire', '')
        alerte.save()
        messages.success(request, "Alerte acquittée.")
    
    return redirect('comptabilite:alertes_tresorerie_list')


# ============================================================================
# SEUILS DE LIQUIDITÉ
# ============================================================================

@reauth_required
@login_required
def seuils_liquidite_list(request):
    """Liste des seuils de liquidité"""
    entreprise = request.user.entreprise
    seuils = LiquiditeSouhaitee.objects.filter(entreprise=entreprise)
    
    context = {
        'seuils': seuils,
    }
    return render(request, 'comptabilite/tresorerie/seuils_list.html', context)


@reauth_required
@login_required
def seuil_liquidite_create(request):
    """Créer un seuil de liquidité"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        seuil = LiquiditeSouhaitee(entreprise=entreprise)
        compte_id = request.POST.get('compte_bancaire')
        if compte_id:
            seuil.compte_bancaire_id = compte_id
        seuil.type_seuil = request.POST.get('type_seuil')
        seuil.montant_seuil = Decimal(request.POST.get('montant_seuil', '0'))
        seuil.alerte_active = request.POST.get('alerte_active') == 'on'
        seuil.destinataires_alerte = request.POST.get('destinataires_alerte', '')
        seuil.justification = request.POST.get('justification', '')
        seuil.cree_par = request.user
        seuil.save()
        messages.success(request, "Seuil de liquidité créé avec succès.")
        return redirect('comptabilite:seuils_liquidite_list')
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'comptes': comptes,
        'types_seuil': LiquiditeSouhaitee.TYPES_SEUIL,
    }
    return render(request, 'comptabilite/tresorerie/seuil_form.html', context)


# ============================================================================
# GESTION NUMÉRAIRE
# ============================================================================

@reauth_required
@login_required
def numeraire_list(request):
    """Liste des mouvements de numéraire"""
    entreprise = request.user.entreprise
    mouvements = GestionNumeraire.objects.filter(entreprise=entreprise)
    
    type_mvt = request.GET.get('type_mouvement')
    statut = request.GET.get('statut')
    
    if type_mvt:
        mouvements = mouvements.filter(type_mouvement=type_mvt)
    if statut:
        mouvements = mouvements.filter(statut=statut)
    
    context = {
        'mouvements': mouvements[:100],
        'types_mouvement': GestionNumeraire.TYPES_MOUVEMENT,
        'statuts': GestionNumeraire.STATUTS,
    }
    return render(request, 'comptabilite/tresorerie/numeraire_list.html', context)


@reauth_required
@login_required
def numeraire_create(request):
    """Créer un mouvement de numéraire"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        mvt = GestionNumeraire(entreprise=entreprise)
        mvt.reference = request.POST.get('reference')
        mvt.date_mouvement = request.POST.get('date_mouvement')
        mvt.type_mouvement = request.POST.get('type_mouvement')
        mvt.montant = Decimal(request.POST.get('montant', '0'))
        mvt.motif = request.POST.get('motif')
        
        caisse_source = request.POST.get('caisse_source')
        if caisse_source:
            mvt.caisse_source_id = caisse_source
        
        caisse_dest = request.POST.get('caisse_destination')
        if caisse_dest:
            mvt.caisse_destination_id = caisse_dest
        
        mvt.effectue_par = request.user
        mvt.save()
        messages.success(request, "Mouvement de numéraire créé avec succès.")
        return redirect('comptabilite:numeraire_list')
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'comptes': comptes,
        'types_mouvement': GestionNumeraire.TYPES_MOUVEMENT,
    }
    return render(request, 'comptabilite/tresorerie/numeraire_form.html', context)


@reauth_required
@login_required
def numeraire_valider(request, pk):
    """Valider un mouvement de numéraire"""
    mvt = get_object_or_404(GestionNumeraire, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        mvt.statut = 'valide'
        mvt.valide_par = request.user
        mvt.date_validation = timezone.now()
        mvt.save()
        messages.success(request, "Mouvement validé.")
    
    return redirect('comptabilite:numeraire_list')


# ============================================================================
# OPTIMISATION TRÉSORERIE
# ============================================================================

@reauth_required
@login_required
def optimisation_list(request):
    """Liste des stratégies d'optimisation"""
    entreprise = request.user.entreprise
    optimisations = OptimisationTresorerie.objects.filter(entreprise=entreprise)
    
    context = {
        'optimisations': optimisations,
    }
    return render(request, 'comptabilite/tresorerie/optimisation_list.html', context)


@reauth_required
@login_required
def optimisation_create(request):
    """Créer une stratégie d'optimisation"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        opt = OptimisationTresorerie(entreprise=entreprise)
        opt.reference = request.POST.get('reference')
        opt.titre = request.POST.get('titre')
        opt.type_strategie = request.POST.get('type_strategie')
        opt.description = request.POST.get('description')
        opt.situation_actuelle = request.POST.get('situation_actuelle')
        opt.objectif = request.POST.get('objectif')
        opt.actions_proposees = request.POST.get('actions_proposees')
        opt.gain_estime = Decimal(request.POST.get('gain_estime', '0'))
        opt.cout_mise_en_oeuvre = Decimal(request.POST.get('cout_mise_en_oeuvre', '0'))
        opt.niveau_risque = request.POST.get('niveau_risque', 'moyen')
        opt.priorite = request.POST.get('priorite', 'normale')
        opt.cree_par = request.user
        opt.save()
        messages.success(request, "Stratégie d'optimisation créée avec succès.")
        return redirect('comptabilite:optimisation_list')
    
    context = {
        'types_strategie': OptimisationTresorerie.TYPES_STRATEGIE,
        'priorites': OptimisationTresorerie.PRIORITES,
    }
    return render(request, 'comptabilite/tresorerie/optimisation_form.html', context)


@reauth_required
@login_required
def optimisation_detail(request, pk):
    """Détail d'une stratégie d'optimisation"""
    opt = get_object_or_404(OptimisationTresorerie, pk=pk, entreprise=request.user.entreprise)
    return render(request, 'comptabilite/tresorerie/optimisation_detail.html', {'optimisation': opt})


# ============================================================================
# FLUX JOURNALIERS
# ============================================================================

@reauth_required
@login_required
def flux_journaliers_list(request):
    """Liste des flux journaliers"""
    entreprise = request.user.entreprise
    flux = FluxTresorerieJournalier.objects.filter(entreprise=entreprise)
    
    compte_id = request.GET.get('compte')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if compte_id:
        flux = flux.filter(compte_bancaire_id=compte_id)
    if date_debut:
        flux = flux.filter(date_flux__gte=date_debut)
    if date_fin:
        flux = flux.filter(date_flux__lte=date_fin)
    
    comptes = CompteBancaire.objects.filter(entreprise=entreprise, est_actif=True)
    
    context = {
        'flux': flux[:100],
        'comptes': comptes,
    }
    return render(request, 'comptabilite/tresorerie/flux_journaliers_list.html', context)


@reauth_required
@login_required
def flux_journalier_detail(request, pk):
    """Détail d'un flux journalier"""
    flux = get_object_or_404(FluxTresorerieJournalier, pk=pk, entreprise=request.user.entreprise)
    return render(request, 'comptabilite/tresorerie/flux_journalier_detail.html', {'flux': flux})


# ============================================================================
# API JSON pour graphiques
# ============================================================================

@reauth_required
@login_required
def api_previsions_tresorerie(request):
    """API pour les prévisions de trésorerie (graphiques)"""
    entreprise = request.user.entreprise
    today = date.today()
    
    # Récupérer la dernière situation
    situation = SituationTresorerie.objects.filter(
        entreprise=entreprise,
        compte_bancaire__isnull=True
    ).order_by('-date_situation').first()
    
    if not situation:
        return JsonResponse({'error': 'Aucune situation disponible'}, status=404)
    
    data = {
        'date_situation': situation.date_situation.isoformat(),
        'solde_actuel': float(situation.solde_fin),
        'previsions': {
            'J+1': float(situation.prevision_j1),
            'J+3': float(situation.prevision_j3),
            'J+5': float(situation.prevision_j5),
            'J+7': float(situation.prevision_j7),
            'J+30': float(situation.prevision_j30),
        }
    }
    return JsonResponse(data)


@reauth_required
@login_required
def api_echeances_calendrier(request):
    """API pour le calendrier des échéances"""
    entreprise = request.user.entreprise
    
    date_debut = request.GET.get('start', date.today().isoformat())
    date_fin = request.GET.get('end', (date.today() + timedelta(days=30)).isoformat())
    
    echeances = EcheancierTresorerie.objects.filter(
        entreprise=entreprise,
        date_echeance__gte=date_debut,
        date_echeance__lte=date_fin
    )
    
    events = []
    for e in echeances:
        color = '#28a745' if e.type_flux == 'encaissement' else '#dc3545'
        if e.statut == 'realise':
            color = '#6c757d'
        
        events.append({
            'id': str(e.id),
            'title': f"{e.libelle} ({e.montant_prevu})",
            'start': e.date_echeance.isoformat(),
            'color': color,
            'extendedProps': {
                'type_flux': e.type_flux,
                'montant': float(e.montant_prevu),
                'statut': e.statut,
            }
        })
    
    return JsonResponse(events, safe=False)
