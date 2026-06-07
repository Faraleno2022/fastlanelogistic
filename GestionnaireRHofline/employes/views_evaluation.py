"""
Vues pour la gestion des évaluations de performance.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import date
from decimal import Decimal

from .models import Employe
from .models_evaluation import CampagneEvaluation, Evaluation, ObjectifEvaluation, CompetenceEvaluation


@reauth_required
@login_required
def liste_campagnes(request):
    """Liste des campagnes d'évaluation"""
    campagnes = CampagneEvaluation.objects.filter(
        entreprise=request.user.entreprise
    ).annotate(
        nb_evaluations=Count('evaluations'),
        nb_terminees=Count('evaluations', filter=Q(evaluations__statut='validee'))
    )
    
    return render(request, 'employes/evaluations/liste_campagnes.html', {
        'campagnes': campagnes,
    })


@reauth_required
@login_required
def creer_campagne(request):
    """Créer une nouvelle campagne d'évaluation"""
    if request.method == 'POST':
        annee = int(request.POST.get('annee', date.today().year))
        titre = request.POST.get('titre', f'Évaluation annuelle {annee}')
        description = request.POST.get('description', '')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        # Vérifier si une campagne existe déjà pour cette année
        if CampagneEvaluation.objects.filter(
            entreprise=request.user.entreprise,
            annee=annee
        ).exists():
            messages.error(request, f"Une campagne existe déjà pour l'année {annee}")
            return redirect('employes:liste_campagnes')
        
        campagne = CampagneEvaluation.objects.create(
            entreprise=request.user.entreprise,
            annee=annee,
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
        )
        
        messages.success(request, f"Campagne '{titre}' créée avec succès")
        return redirect('employes:detail_campagne', pk=campagne.pk)
    
    return render(request, 'employes/evaluations/creer_campagne.html', {
        'annee_courante': date.today().year,
    })


@reauth_required
@login_required
def detail_campagne(request, pk):
    """Détail d'une campagne avec ses évaluations"""
    campagne = get_object_or_404(
        CampagneEvaluation,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    evaluations = campagne.evaluations.select_related('employe', 'evaluateur')
    
    # Statistiques
    stats = {
        'total': evaluations.count(),
        'terminees': evaluations.filter(statut='validee').count(),
        'en_cours': evaluations.exclude(statut__in=['validee', 'annulee']).count(),
        'note_moyenne': evaluations.filter(note_globale__isnull=False).aggregate(
            moy=Avg('note_globale')
        )['moy'] or 0,
    }
    
    return render(request, 'employes/evaluations/detail_campagne.html', {
        'campagne': campagne,
        'evaluations': evaluations,
        'stats': stats,
    })


@reauth_required
@login_required
def lancer_campagne(request, pk):
    """Lancer une campagne et créer les évaluations pour tous les employés"""
    campagne = get_object_or_404(
        CampagneEvaluation,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    if campagne.statut != 'preparation':
        messages.error(request, "Cette campagne a déjà été lancée")
        return redirect('employes:detail_campagne', pk=pk)
    
    # Récupérer tous les employés actifs
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
        statut_employe='actif'
    )
    
    # Créer une évaluation pour chaque employé
    nb_crees = 0
    for employe in employes:
        # Trouver l'évaluateur (responsable du département ou manager)
        evaluateur = None
        if employe.departement and hasattr(employe.departement, 'responsable'):
            evaluateur = employe.departement.responsable
        
        Evaluation.objects.get_or_create(
            campagne=campagne,
            employe=employe,
            defaults={
                'evaluateur': evaluateur,
                'statut': 'auto_evaluation',
            }
        )
        nb_crees += 1
    
    # Mettre à jour le statut de la campagne
    campagne.statut = 'en_cours'
    campagne.save()
    
    messages.success(request, f"Campagne lancée: {nb_crees} évaluations créées")
    return redirect('employes:detail_campagne', pk=pk)


@reauth_required
@login_required
def detail_evaluation(request, pk):
    """Détail d'une évaluation individuelle"""
    evaluation = get_object_or_404(
        Evaluation,
        pk=pk,
        campagne__entreprise=request.user.entreprise
    )
    
    objectifs = evaluation.objectifs.all()
    competences = evaluation.competences.all()
    
    return render(request, 'employes/evaluations/detail_evaluation.html', {
        'evaluation': evaluation,
        'objectifs': objectifs,
        'competences': competences,
    })


@reauth_required
@login_required
def modifier_evaluation(request, pk):
    """Modifier une évaluation"""
    evaluation = get_object_or_404(
        Evaluation,
        pk=pk,
        campagne__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        # Notes
        evaluation.note_objectifs = request.POST.get('note_objectifs') or None
        evaluation.note_competences = request.POST.get('note_competences') or None
        evaluation.note_comportement = request.POST.get('note_comportement') or None
        
        # Commentaires
        evaluation.points_forts = request.POST.get('points_forts', '')
        evaluation.axes_amelioration = request.POST.get('axes_amelioration', '')
        evaluation.commentaire_evaluateur = request.POST.get('commentaire_evaluateur', '')
        
        # Plan de développement
        evaluation.plan_developpement = request.POST.get('plan_developpement', '')
        evaluation.besoins_formation = request.POST.get('besoins_formation', '')
        
        # Évolution
        evaluation.souhait_evolution = request.POST.get('souhait_evolution', '')
        augmentation = request.POST.get('proposition_augmentation', '')
        if augmentation:
            evaluation.proposition_augmentation = Decimal(augmentation)
        
        # Date entretien
        date_entretien = request.POST.get('date_entretien')
        if date_entretien:
            evaluation.date_entretien = date_entretien
        
        # Calculer note globale
        evaluation.calculer_note_globale()
        
        # Statut
        action = request.POST.get('action', 'save')
        if action == 'valider':
            evaluation.statut = 'validee'
            evaluation.date_validation = timezone.now()
        elif action == 'entretien':
            evaluation.statut = 'entretien'
        else:
            evaluation.statut = 'evaluation_manager'
        
        evaluation.save()
        
        messages.success(request, "Évaluation mise à jour")
        return redirect('employes:detail_evaluation', pk=pk)
    
    return render(request, 'employes/evaluations/modifier_evaluation.html', {
        'evaluation': evaluation,
    })


@reauth_required
@login_required
def ajouter_objectif(request, evaluation_id):
    """Ajouter un objectif à une évaluation"""
    evaluation = get_object_or_404(
        Evaluation,
        pk=evaluation_id,
        campagne__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        ObjectifEvaluation.objects.create(
            evaluation=evaluation,
            intitule=request.POST.get('intitule'),
            description=request.POST.get('description', ''),
            indicateurs=request.POST.get('indicateurs', ''),
            priorite=request.POST.get('priorite', 'moyenne'),
            poids=int(request.POST.get('poids', 100)),
            date_echeance=request.POST.get('date_echeance') or None,
        )
        messages.success(request, "Objectif ajouté")
    
    return redirect('employes:detail_evaluation', pk=evaluation_id)


@reauth_required
@login_required
def evaluer_objectif(request, pk):
    """Évaluer un objectif"""
    objectif = get_object_or_404(ObjectifEvaluation, pk=pk)
    
    if request.method == 'POST':
        objectif.statut = request.POST.get('statut', 'en_cours')
        objectif.taux_realisation = int(request.POST.get('taux_realisation', 0))
        objectif.commentaire_evaluateur = request.POST.get('commentaire_evaluateur', '')
        objectif.save()
        messages.success(request, "Objectif évalué")
    
    return redirect('employes:detail_evaluation', pk=objectif.evaluation.pk)


@reauth_required
@login_required
def ajouter_competence(request, evaluation_id):
    """Ajouter une compétence à évaluer"""
    evaluation = get_object_or_404(
        Evaluation,
        pk=evaluation_id,
        campagne__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        CompetenceEvaluation.objects.create(
            evaluation=evaluation,
            competence=request.POST.get('competence'),
            categorie=request.POST.get('categorie', ''),
            niveau_requis=int(request.POST.get('niveau_requis', 3)),
            niveau_actuel=request.POST.get('niveau_actuel') or None,
            commentaire=request.POST.get('commentaire', ''),
        )
        messages.success(request, "Compétence ajoutée")
    
    return redirect('employes:detail_evaluation', pk=evaluation_id)


@reauth_required
@login_required
def synthese_evaluations(request):
    """Synthèse des évaluations de l'entreprise"""
    annee = request.GET.get('annee', date.today().year)
    
    campagne = CampagneEvaluation.objects.filter(
        entreprise=request.user.entreprise,
        annee=int(annee)
    ).first()
    
    if not campagne:
        messages.info(request, f"Aucune campagne pour l'année {annee}")
        return redirect('employes:liste_campagnes')
    
    evaluations = campagne.evaluations.filter(statut='validee').select_related(
        'employe', 'employe__service'
    )
    
    # Statistiques par service
    stats_dept = evaluations.values(
        'employe__service__nom_service'
    ).annotate(
        nb=Count('id'),
        note_moy=Avg('note_globale')
    ).order_by('-note_moy')
    
    # Distribution des notes
    distribution = {
        'excellent': evaluations.filter(note_globale__gte=4.5).count(),
        'bon': evaluations.filter(note_globale__gte=3.5, note_globale__lt=4.5).count(),
        'satisfaisant': evaluations.filter(note_globale__gte=2.5, note_globale__lt=3.5).count(),
        'ameliorer': evaluations.filter(note_globale__gte=1.5, note_globale__lt=2.5).count(),
        'insuffisant': evaluations.filter(note_globale__lt=1.5).count(),
    }
    
    # Top performers
    top_performers = evaluations.order_by('-note_globale')[:10]
    
    return render(request, 'employes/evaluations/synthese.html', {
        'campagne': campagne,
        'evaluations': evaluations,
        'stats_dept': stats_dept,
        'distribution': distribution,
        'top_performers': top_performers,
        'annee': int(annee),
    })
