"""
Vues pour le module Consolidation & Reporting
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date
from decimal import Decimal

from .models import ExerciceComptable, PlanComptable
from .models_consolidation import (
    MatriceConsolidation, ConsolidationFiliales, PerimetreConsolidation,
    EliminationIGF, AjustementConsolidation, AffectationResultat,
    VariationCapitaux, NoteExplicative, DocumentationConsolidation,
    BilanConsolide, CompteResultatConsolide, FluxTresorerieConsolide
)
from core.models import Entreprise, Devise


@reauth_required
@login_required
def dashboard_consolidation(request):
    """Tableau de bord consolidation"""
    entreprise = request.user.entreprise
    
    # Consolidations récentes
    consolidations = ConsolidationFiliales.objects.filter(
        entreprise_mere=entreprise
    ).order_by('-date_consolidation')[:5]
    
    # Matrice de participation
    participations = MatriceConsolidation.objects.filter(
        entreprise_mere=entreprise,
        est_active=True
    ).order_by('-pourcentage_capital')
    
    # Statistiques
    nb_filiales = participations.filter(type_controle='filiale').count()
    nb_participations = participations.filter(type_controle='participation').count()
    
    # Dernière consolidation validée
    derniere_conso = ConsolidationFiliales.objects.filter(
        entreprise_mere=entreprise,
        statut='valide'
    ).order_by('-date_consolidation').first()
    
    context = {
        'consolidations': consolidations,
        'participations': participations,
        'nb_filiales': nb_filiales,
        'nb_participations': nb_participations,
        'derniere_conso': derniere_conso,
    }
    return render(request, 'comptabilite/consolidation/dashboard.html', context)


# ============================================================================
# MATRICE DE CONSOLIDATION
# ============================================================================

@reauth_required
@login_required
def matrice_list(request):
    """Liste des participations (matrice)"""
    entreprise = request.user.entreprise
    participations = MatriceConsolidation.objects.filter(entreprise_mere=entreprise)
    
    context = {
        'participations': participations,
        'types_controle': MatriceConsolidation.TYPES_CONTROLE,
    }
    return render(request, 'comptabilite/consolidation/matrice_list.html', context)


@reauth_required
@login_required
def matrice_create(request):
    """Créer une participation"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        participation = MatriceConsolidation(entreprise_mere=entreprise)
        participation.entreprise_fille_id = request.POST.get('entreprise_fille')
        participation.pourcentage_capital = Decimal(request.POST.get('pourcentage_capital', '0'))
        participation.pourcentage_droits_vote = Decimal(request.POST.get('pourcentage_droits_vote', '0'))
        participation.pourcentage_interet = Decimal(request.POST.get('pourcentage_interet', '0'))
        participation.type_controle = request.POST.get('type_controle')
        participation.date_acquisition = request.POST.get('date_acquisition')
        participation.cout_acquisition = Decimal(request.POST.get('cout_acquisition', '0'))
        participation.goodwill = Decimal(request.POST.get('goodwill', '0'))
        participation.notes = request.POST.get('notes', '')
        participation.cree_par = request.user
        participation.save()
        messages.success(request, "Participation créée avec succès.")
        return redirect('comptabilite:matrice_list')
    
    # Liste des entreprises disponibles
    entreprises = Entreprise.objects.exclude(id=entreprise.id)
    devises = Devise.objects.all()
    
    context = {
        'entreprises': entreprises,
        'devises': devises,
        'types_controle': MatriceConsolidation.TYPES_CONTROLE,
    }
    return render(request, 'comptabilite/consolidation/matrice_form.html', context)


@reauth_required
@login_required
def matrice_detail(request, pk):
    """Détail d'une participation"""
    participation = get_object_or_404(MatriceConsolidation, pk=pk, entreprise_mere=request.user.entreprise)
    return render(request, 'comptabilite/consolidation/matrice_detail.html', {'participation': participation})


@reauth_required
@login_required
def matrice_update(request, pk):
    """Modifier une participation"""
    participation = get_object_or_404(MatriceConsolidation, pk=pk, entreprise_mere=request.user.entreprise)
    
    if request.method == 'POST':
        participation.pourcentage_capital = Decimal(request.POST.get('pourcentage_capital', '0'))
        participation.pourcentage_droits_vote = Decimal(request.POST.get('pourcentage_droits_vote', '0'))
        participation.pourcentage_interet = Decimal(request.POST.get('pourcentage_interet', '0'))
        participation.type_controle = request.POST.get('type_controle')
        participation.goodwill = Decimal(request.POST.get('goodwill', '0'))
        participation.notes = request.POST.get('notes', '')
        participation.save()
        messages.success(request, "Participation modifiée avec succès.")
        return redirect('comptabilite:matrice_detail', pk=pk)
    
    context = {
        'participation': participation,
        'types_controle': MatriceConsolidation.TYPES_CONTROLE,
    }
    return render(request, 'comptabilite/consolidation/matrice_form.html', context)


# ============================================================================
# CONSOLIDATION FILIALES
# ============================================================================

@reauth_required
@login_required
def consolidation_list(request):
    """Liste des consolidations"""
    entreprise = request.user.entreprise
    consolidations = ConsolidationFiliales.objects.filter(entreprise_mere=entreprise)
    
    statut = request.GET.get('statut')
    exercice_id = request.GET.get('exercice')
    
    if statut:
        consolidations = consolidations.filter(statut=statut)
    if exercice_id:
        consolidations = consolidations.filter(exercice_id=exercice_id)
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'consolidations': consolidations,
        'exercices': exercices,
        'statuts': ConsolidationFiliales.STATUTS,
    }
    return render(request, 'comptabilite/consolidation/consolidation_list.html', context)


@reauth_required
@login_required
def consolidation_create(request):
    """Créer une consolidation"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        conso = ConsolidationFiliales(entreprise_mere=entreprise)
        conso.exercice_id = request.POST.get('exercice')
        conso.reference = request.POST.get('reference')
        conso.libelle = request.POST.get('libelle')
        conso.date_consolidation = request.POST.get('date_consolidation')
        conso.date_debut_periode = request.POST.get('date_debut_periode')
        conso.date_fin_periode = request.POST.get('date_fin_periode')
        conso.methode_consolidation = request.POST.get('methode_consolidation')
        conso.notes = request.POST.get('notes', '')
        conso.cree_par = request.user
        conso.save()
        
        # Créer automatiquement le périmètre à partir de la matrice
        participations = MatriceConsolidation.objects.filter(
            entreprise_mere=entreprise,
            est_active=True
        )
        for p in participations:
            methode = 'integration_globale' if p.type_controle == 'filiale' else \
                      'integration_proportionnelle' if p.type_controle == 'conjointe' else \
                      'mise_equivalence'
            PerimetreConsolidation.objects.create(
                consolidation=conso,
                entreprise=p.entreprise_fille,
                matrice=p,
                methode=methode,
                pourcentage_integration=p.pourcentage_capital,
                pourcentage_interet=p.pourcentage_interet,
            )
        
        messages.success(request, "Consolidation créée avec succès. Périmètre initialisé.")
        return redirect('comptabilite:consolidation_detail', pk=conso.pk)
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise, statut='ouvert')
    devises = Devise.objects.all()
    
    context = {
        'exercices': exercices,
        'devises': devises,
        'methodes': ConsolidationFiliales.METHODES_CONSOLIDATION,
    }
    return render(request, 'comptabilite/consolidation/consolidation_form.html', context)


@reauth_required
@login_required
def consolidation_detail(request, pk):
    """Détail d'une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=pk, entreprise_mere=request.user.entreprise)
    
    perimetre = conso.perimetre.all()
    eliminations = conso.eliminations.all()
    ajustements = conso.ajustements.all()
    
    context = {
        'consolidation': conso,
        'perimetre': perimetre,
        'eliminations': eliminations,
        'ajustements': ajustements,
    }
    return render(request, 'comptabilite/consolidation/consolidation_detail.html', context)


@reauth_required
@login_required
def consolidation_valider(request, pk):
    """Valider une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=pk, entreprise_mere=request.user.entreprise)
    
    if request.method == 'POST':
        conso.statut = 'valide'
        conso.valide_par = request.user
        conso.date_validation = timezone.now()
        conso.save()
        messages.success(request, "Consolidation validée.")
    
    return redirect('comptabilite:consolidation_detail', pk=pk)


# ============================================================================
# ÉLIMINATIONS IGF
# ============================================================================

@reauth_required
@login_required
def elimination_list(request, consolidation_pk):
    """Liste des éliminations d'une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk, 
                              entreprise_mere=request.user.entreprise)
    eliminations = conso.eliminations.all()
    
    context = {
        'consolidation': conso,
        'eliminations': eliminations,
        'types': EliminationIGF.TYPES_ELIMINATION,
    }
    return render(request, 'comptabilite/consolidation/elimination_list.html', context)


@reauth_required
@login_required
def elimination_create(request, consolidation_pk):
    """Créer une élimination"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    if request.method == 'POST':
        elim = EliminationIGF(consolidation=conso)
        elim.type_elimination = request.POST.get('type_elimination')
        elim.entreprise_source_id = request.POST.get('entreprise_source')
        elim.entreprise_destination_id = request.POST.get('entreprise_destination')
        elim.montant_brut = Decimal(request.POST.get('montant_brut', '0'))
        elim.montant_elimine = Decimal(request.POST.get('montant_elimine', '0'))
        elim.libelle = request.POST.get('libelle')
        elim.description = request.POST.get('description', '')
        elim.save()
        messages.success(request, "Élimination créée avec succès.")
        return redirect('comptabilite:elimination_list', consolidation_pk=consolidation_pk)
    
    # Entreprises du périmètre
    entreprises = [p.entreprise for p in conso.perimetre.filter(est_incluse=True)]
    comptes = PlanComptable.objects.filter(entreprise=request.user.entreprise)
    
    context = {
        'consolidation': conso,
        'entreprises': entreprises,
        'comptes': comptes,
        'types': EliminationIGF.TYPES_ELIMINATION,
    }
    return render(request, 'comptabilite/consolidation/elimination_form.html', context)


# ============================================================================
# AJUSTEMENTS
# ============================================================================

@reauth_required
@login_required
def ajustement_list(request, consolidation_pk):
    """Liste des ajustements d'une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    ajustements = conso.ajustements.all()
    
    context = {
        'consolidation': conso,
        'ajustements': ajustements,
        'types': AjustementConsolidation.TYPES_AJUSTEMENT,
    }
    return render(request, 'comptabilite/consolidation/ajustement_list.html', context)


@reauth_required
@login_required
def ajustement_create(request, consolidation_pk):
    """Créer un ajustement"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    if request.method == 'POST':
        ajust = AjustementConsolidation(consolidation=conso)
        ajust.type_ajustement = request.POST.get('type_ajustement')
        ajust.entreprise_id = request.POST.get('entreprise')
        ajust.montant_debit = Decimal(request.POST.get('montant_debit', '0'))
        ajust.montant_credit = Decimal(request.POST.get('montant_credit', '0'))
        ajust.libelle = request.POST.get('libelle')
        ajust.justification = request.POST.get('justification', '')
        ajust.cree_par = request.user
        ajust.save()
        messages.success(request, "Ajustement créé avec succès.")
        return redirect('comptabilite:ajustement_list', consolidation_pk=consolidation_pk)
    
    entreprises = [p.entreprise for p in conso.perimetre.filter(est_incluse=True)]
    comptes = PlanComptable.objects.filter(entreprise=request.user.entreprise)
    
    context = {
        'consolidation': conso,
        'entreprises': entreprises,
        'comptes': comptes,
        'types': AjustementConsolidation.TYPES_AJUSTEMENT,
    }
    return render(request, 'comptabilite/consolidation/ajustement_form.html', context)


# ============================================================================
# AFFECTATION DU RÉSULTAT
# ============================================================================

@reauth_required
@login_required
def affectation_list(request):
    """Liste des affectations de résultat"""
    entreprise = request.user.entreprise
    affectations = AffectationResultat.objects.filter(entreprise=entreprise)
    
    context = {
        'affectations': affectations,
    }
    return render(request, 'comptabilite/consolidation/affectation_list.html', context)


@reauth_required
@login_required
def affectation_create(request):
    """Créer une affectation de résultat"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        aff = AffectationResultat(entreprise=entreprise)
        aff.exercice_id = request.POST.get('exercice')
        aff.resultat_exercice = Decimal(request.POST.get('resultat_exercice', '0'))
        aff.report_anterieur = Decimal(request.POST.get('report_anterieur', '0'))
        aff.montant_a_affecter = Decimal(request.POST.get('montant_a_affecter', '0'))
        aff.type_affectation = request.POST.get('type_affectation')
        aff.montant_affecte = Decimal(request.POST.get('montant_affecte', '0'))
        aff.date_ag = request.POST.get('date_ag') or None
        aff.cree_par = request.user
        aff.save()
        messages.success(request, "Affectation créée avec succès.")
        return redirect('comptabilite:affectation_list')
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'exercices': exercices,
        'types': AffectationResultat.TYPES_AFFECTATION,
    }
    return render(request, 'comptabilite/consolidation/affectation_form.html', context)


# ============================================================================
# VARIATION DES CAPITAUX
# ============================================================================

@reauth_required
@login_required
def variation_capitaux_list(request):
    """Tableau de variation des capitaux propres"""
    entreprise = request.user.entreprise
    variations = VariationCapitaux.objects.filter(entreprise=entreprise)
    
    exercice_id = request.GET.get('exercice')
    if exercice_id:
        variations = variations.filter(exercice_id=exercice_id)
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'variations': variations,
        'exercices': exercices,
    }
    return render(request, 'comptabilite/consolidation/variation_capitaux_list.html', context)


@reauth_required
@login_required
def variation_capitaux_create(request):
    """Créer une variation de capitaux"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        var = VariationCapitaux(entreprise=entreprise)
        var.exercice_id = request.POST.get('exercice')
        var.type_variation = request.POST.get('type_variation')
        var.libelle = request.POST.get('libelle')
        var.date_variation = request.POST.get('date_variation')
        var.capital_social = Decimal(request.POST.get('capital_social', '0'))
        var.primes_emission = Decimal(request.POST.get('primes_emission', '0'))
        var.reserves = Decimal(request.POST.get('reserves', '0'))
        var.report_nouveau = Decimal(request.POST.get('report_nouveau', '0'))
        var.resultat_exercice = Decimal(request.POST.get('resultat_exercice', '0'))
        var.save()
        var.calculer_total()
        messages.success(request, "Variation créée avec succès.")
        return redirect('comptabilite:variation_capitaux_list')
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'exercices': exercices,
        'types': VariationCapitaux.TYPES_VARIATION,
    }
    return render(request, 'comptabilite/consolidation/variation_capitaux_form.html', context)


# ============================================================================
# NOTES EXPLICATIVES
# ============================================================================

@reauth_required
@login_required
def notes_list(request):
    """Liste des notes explicatives"""
    entreprise = request.user.entreprise
    notes = NoteExplicative.objects.filter(entreprise=entreprise)
    
    exercice_id = request.GET.get('exercice')
    categorie = request.GET.get('categorie')
    
    if exercice_id:
        notes = notes.filter(exercice_id=exercice_id)
    if categorie:
        notes = notes.filter(categorie=categorie)
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'notes': notes,
        'exercices': exercices,
        'categories': NoteExplicative.CATEGORIES,
    }
    return render(request, 'comptabilite/consolidation/notes_list.html', context)


@reauth_required
@login_required
def note_create(request):
    """Créer une note explicative"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        note = NoteExplicative(entreprise=entreprise)
        note.exercice_id = request.POST.get('exercice')
        note.numero_note = request.POST.get('numero_note')
        note.titre = request.POST.get('titre')
        note.categorie = request.POST.get('categorie')
        note.contenu = request.POST.get('contenu')
        note.ordre = int(request.POST.get('ordre', 0))
        note.redige_par = request.user
        note.save()
        messages.success(request, "Note créée avec succès.")
        return redirect('comptabilite:notes_list')
    
    exercices = ExerciceComptable.objects.filter(entreprise=entreprise)
    
    context = {
        'exercices': exercices,
        'categories': NoteExplicative.CATEGORIES,
    }
    return render(request, 'comptabilite/consolidation/note_form.html', context)


@reauth_required
@login_required
def note_detail(request, pk):
    """Détail d'une note"""
    note = get_object_or_404(NoteExplicative, pk=pk, entreprise=request.user.entreprise)
    return render(request, 'comptabilite/consolidation/note_detail.html', {'note': note})


@reauth_required
@login_required
def note_update(request, pk):
    """Modifier une note"""
    note = get_object_or_404(NoteExplicative, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        note.titre = request.POST.get('titre')
        note.categorie = request.POST.get('categorie')
        note.contenu = request.POST.get('contenu')
        note.ordre = int(request.POST.get('ordre', 0))
        note.save()
        messages.success(request, "Note modifiée avec succès.")
        return redirect('comptabilite:note_detail', pk=pk)
    
    context = {
        'note': note,
        'categories': NoteExplicative.CATEGORIES,
    }
    return render(request, 'comptabilite/consolidation/note_form.html', context)


# ============================================================================
# ÉTATS FINANCIERS CONSOLIDÉS
# ============================================================================

@reauth_required
@login_required
def bilan_consolide(request, consolidation_pk):
    """Bilan consolidé"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    bilan = conso.bilans.first()
    if not bilan:
        # Créer un bilan vide
        bilan = BilanConsolide.objects.create(
            consolidation=conso,
            date_bilan=conso.date_fin_periode
        )
    
    context = {
        'consolidation': conso,
        'bilan': bilan,
    }
    return render(request, 'comptabilite/consolidation/bilan_consolide.html', context)


@reauth_required
@login_required
def compte_resultat_consolide(request, consolidation_pk):
    """Compte de résultat consolidé"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    cr = conso.comptes_resultat.first()
    if not cr:
        cr = CompteResultatConsolide.objects.create(
            consolidation=conso,
            date_debut=conso.date_debut_periode,
            date_fin=conso.date_fin_periode
        )
    
    context = {
        'consolidation': conso,
        'compte_resultat': cr,
    }
    return render(request, 'comptabilite/consolidation/compte_resultat_consolide.html', context)


@reauth_required
@login_required
def flux_tresorerie_consolide(request, consolidation_pk):
    """Tableau des flux de trésorerie consolidé"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    flux = conso.flux_tresorerie.first()
    if not flux:
        flux = FluxTresorerieConsolide.objects.create(
            consolidation=conso,
            date_debut=conso.date_debut_periode,
            date_fin=conso.date_fin_periode
        )
    
    context = {
        'consolidation': conso,
        'flux': flux,
    }
    return render(request, 'comptabilite/consolidation/flux_tresorerie_consolide.html', context)


@reauth_required
@login_required
def tableau_capitaux_consolide(request, consolidation_pk):
    """Tableau de variation des capitaux propres consolidés"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    variations = conso.variations_capitaux.all()
    
    context = {
        'consolidation': conso,
        'variations': variations,
    }
    return render(request, 'comptabilite/consolidation/tableau_capitaux_consolide.html', context)


@reauth_required
@login_required
def annexes_consolidees(request, consolidation_pk):
    """Annexes détaillées consolidées"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    notes = conso.notes_explicatives.filter(est_publie=True).order_by('ordre', 'numero_note')
    
    context = {
        'consolidation': conso,
        'notes': notes,
    }
    return render(request, 'comptabilite/consolidation/annexes_consolidees.html', context)


# ============================================================================
# DOCUMENTATION
# ============================================================================

@reauth_required
@login_required
def documentation_list(request, consolidation_pk):
    """Liste de la documentation d'une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    docs = conso.documentation.all()
    
    context = {
        'consolidation': conso,
        'documents': docs,
        'types': DocumentationConsolidation.TYPES_DOCUMENT,
    }
    return render(request, 'comptabilite/consolidation/documentation_list.html', context)


@reauth_required
@login_required
def documentation_upload(request, consolidation_pk):
    """Uploader un document"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    if request.method == 'POST' and request.FILES.get('fichier'):
        doc = DocumentationConsolidation(consolidation=conso)
        doc.type_document = request.POST.get('type_document')
        doc.titre = request.POST.get('titre')
        doc.description = request.POST.get('description', '')
        doc.fichier = request.FILES['fichier']
        doc.cree_par = request.user
        doc.save()
        messages.success(request, "Document uploadé avec succès.")
        return redirect('comptabilite:documentation_list', consolidation_pk=consolidation_pk)
    
    context = {
        'consolidation': conso,
        'types': DocumentationConsolidation.TYPES_DOCUMENT,
    }
    return render(request, 'comptabilite/consolidation/documentation_form.html', context)


# ============================================================================
# API JSON
# ============================================================================

@reauth_required
@login_required
def api_perimetre_consolidation(request, consolidation_pk):
    """API pour le périmètre de consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    perimetre = []
    for p in conso.perimetre.filter(est_incluse=True):
        perimetre.append({
            'id': str(p.id),
            'entreprise': p.entreprise.nom,
            'methode': p.get_methode_display(),
            'pourcentage_integration': float(p.pourcentage_integration),
            'pourcentage_interet': float(p.pourcentage_interet),
        })
    
    return JsonResponse({'perimetre': perimetre})


@reauth_required
@login_required
def api_synthese_consolidation(request, consolidation_pk):
    """API pour la synthèse d'une consolidation"""
    conso = get_object_or_404(ConsolidationFiliales, pk=consolidation_pk,
                              entreprise_mere=request.user.entreprise)
    
    data = {
        'reference': conso.reference,
        'statut': conso.get_statut_display(),
        'nb_entites': conso.perimetre.filter(est_incluse=True).count(),
        'nb_eliminations': conso.eliminations.count(),
        'nb_ajustements': conso.ajustements.count(),
        'total_eliminations': float(conso.eliminations.aggregate(
            total=Sum('montant_elimine'))['total'] or 0),
    }
    
    return JsonResponse(data)
