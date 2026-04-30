"""
Vues pour la gestion des réclamations employés.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date

from .models import Employe
from .models_reclamation import CategorieReclamation, Reclamation, CommentaireReclamation


@reauth_required
@login_required
def liste_reclamations(request):
    """Liste des réclamations"""
    reclamations = Reclamation.objects.filter(
        employe__entreprise=request.user.entreprise
    ).select_related('employe', 'categorie', 'responsable')
    
    # Filtres
    employe_id = request.GET.get('employe')
    statut = request.GET.get('statut')
    categorie_id = request.GET.get('categorie')
    priorite = request.GET.get('priorite')
    
    if employe_id:
        reclamations = reclamations.filter(employe_id=employe_id)
    if statut:
        reclamations = reclamations.filter(statut=statut)
    if categorie_id:
        reclamations = reclamations.filter(categorie_id=categorie_id)
    if priorite:
        reclamations = reclamations.filter(priorite=priorite)
    
    # Statistiques
    stats = Reclamation.objects.filter(
        employe__entreprise=request.user.entreprise
    ).aggregate(
        nb_ouvertes=Count('id', filter=Q(statut='ouverte')),
        nb_en_cours=Count('id', filter=Q(statut='en_cours')),
        nb_en_attente=Count('id', filter=Q(statut='en_attente')),
        nb_resolues=Count('id', filter=Q(statut='resolue')),
    )
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    categories = CategorieReclamation.objects.filter(actif=True)
    
    return render(request, 'employes/reclamations/liste.html', {
        'reclamations': reclamations[:100],
        'stats': stats,
        'employes': employes,
        'categories': categories,
        'statuts': Reclamation.STATUTS,
        'priorites': Reclamation.PRIORITES,
        'filtre_employe': employe_id,
        'filtre_statut': statut,
        'filtre_categorie': categorie_id,
        'filtre_priorite': priorite,
    })


@reauth_required
@login_required
def creer_reclamation(request):
    """Créer une nouvelle réclamation"""
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        categorie_id = request.POST.get('categorie')
        priorite = request.POST.get('priorite', 'normale')
        objet = request.POST.get('objet')
        description = request.POST.get('description')
        confidentiel = request.POST.get('confidentiel') == 'on'
        pieces_jointes = request.FILES.get('pieces_jointes')
        
        employe = get_object_or_404(
            Employe,
            pk=employe_id,
            entreprise=request.user.entreprise
        )
        categorie = get_object_or_404(CategorieReclamation, pk=categorie_id)
        
        reclamation = Reclamation.objects.create(
            employe=employe,
            categorie=categorie,
            priorite=priorite,
            objet=objet,
            description=description,
            confidentiel=confidentiel,
            pieces_jointes=pieces_jointes,
            responsable=categorie.responsable_defaut,
        )
        
        messages.success(request, f"Réclamation {reclamation.reference} créée")
        return redirect('employes:detail_reclamation', pk=reclamation.pk)
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    categories = CategorieReclamation.objects.filter(actif=True)
    
    return render(request, 'employes/reclamations/creer.html', {
        'employes': employes,
        'categories': categories,
        'priorites': Reclamation.PRIORITES,
    })


@reauth_required
@login_required
def detail_reclamation(request, pk):
    """Détail d'une réclamation"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    commentaires = reclamation.commentaires.select_related('auteur').all()
    
    # Responsables potentiels
    responsables = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'employes/reclamations/detail.html', {
        'reclamation': reclamation,
        'commentaires': commentaires,
        'responsables': responsables,
    })


@reauth_required
@login_required
def prendre_en_charge(request, pk):
    """Prendre en charge une réclamation"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if reclamation.statut != 'ouverte':
        messages.error(request, "Cette réclamation est déjà prise en charge")
        return redirect('employes:detail_reclamation', pk=pk)
    
    # Récupérer l'employé connecté
    responsable = Employe.objects.filter(utilisateur=request.user).first()
    
    reclamation.statut = 'en_cours'
    reclamation.responsable = responsable
    reclamation.date_prise_en_charge = timezone.now()
    reclamation.save()
    
    messages.success(request, "Réclamation prise en charge")
    return redirect('employes:detail_reclamation', pk=pk)


@reauth_required
@login_required
def assigner_reclamation(request, pk):
    """Assigner une réclamation à un responsable"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        responsable_id = request.POST.get('responsable')
        responsable = get_object_or_404(Employe, pk=responsable_id)
        
        reclamation.responsable = responsable
        if reclamation.statut == 'ouverte':
            reclamation.statut = 'en_cours'
            reclamation.date_prise_en_charge = timezone.now()
        reclamation.save()
        
        messages.success(request, f"Réclamation assignée à {responsable.nom}")
    
    return redirect('employes:detail_reclamation', pk=pk)


@reauth_required
@login_required
def ajouter_commentaire(request, pk):
    """Ajouter un commentaire à une réclamation"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        interne = request.POST.get('interne') == 'on'
        piece_jointe = request.FILES.get('piece_jointe')
        
        auteur = Employe.objects.filter(utilisateur=request.user).first()
        
        CommentaireReclamation.objects.create(
            reclamation=reclamation,
            auteur=auteur,
            contenu=contenu,
            interne=interne,
            piece_jointe=piece_jointe,
        )
        
        messages.success(request, "Commentaire ajouté")
    
    return redirect('employes:detail_reclamation', pk=pk)


@reauth_required
@login_required
def resoudre_reclamation(request, pk):
    """Résoudre une réclamation"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if reclamation.statut in ['resolue', 'rejetee', 'fermee']:
        messages.error(request, "Cette réclamation est déjà traitée")
        return redirect('employes:detail_reclamation', pk=pk)
    
    if request.method == 'POST':
        reponse = request.POST.get('reponse')
        
        reclamation.reponse = reponse
        reclamation.statut = 'resolue'
        reclamation.date_resolution = timezone.now()
        reclamation.save()
        
        messages.success(request, f"Réclamation {reclamation.reference} résolue")
        return redirect('employes:liste_reclamations')
    
    return render(request, 'employes/reclamations/resoudre.html', {
        'reclamation': reclamation,
    })


@reauth_required
@login_required
def rejeter_reclamation(request, pk):
    """Rejeter une réclamation"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        motif = request.POST.get('motif_rejet')
        
        reclamation.motif_rejet = motif
        reclamation.statut = 'rejetee'
        reclamation.date_resolution = timezone.now()
        reclamation.save()
        
        messages.warning(request, f"Réclamation {reclamation.reference} rejetée")
    
    return redirect('employes:detail_reclamation', pk=pk)


@reauth_required
@login_required
def fermer_reclamation(request, pk):
    """Fermer une réclamation résolue"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if reclamation.statut not in ['resolue', 'rejetee']:
        messages.error(request, "Seules les réclamations résolues ou rejetées peuvent être fermées")
        return redirect('employes:detail_reclamation', pk=pk)
    
    reclamation.statut = 'fermee'
    reclamation.date_fermeture = timezone.now()
    reclamation.save()
    
    messages.success(request, f"Réclamation {reclamation.reference} fermée")
    return redirect('employes:liste_reclamations')


@reauth_required
@login_required
def noter_satisfaction(request, pk):
    """Noter la satisfaction pour une réclamation résolue"""
    reclamation = get_object_or_404(
        Reclamation,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        satisfaction = request.POST.get('satisfaction')
        commentaire = request.POST.get('commentaire_satisfaction', '')
        
        reclamation.satisfaction = int(satisfaction)
        reclamation.commentaire_satisfaction = commentaire
        reclamation.save()
        
        messages.success(request, "Merci pour votre retour")
    
    return redirect('employes:detail_reclamation', pk=pk)


@reauth_required
@login_required
def recap_reclamations(request):
    """Récapitulatif des réclamations"""
    annee = int(request.GET.get('annee', date.today().year))
    
    # Par catégorie
    recap_categories = Reclamation.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_ouverture__year=annee
    ).values('categorie__libelle').annotate(
        total=Count('id'),
        resolues=Count('id', filter=Q(statut='resolue')),
        rejetees=Count('id', filter=Q(statut='rejetee')),
    ).order_by('-total')
    
    # Par mois
    recap_mois = Reclamation.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_ouverture__year=annee
    ).values('date_ouverture__month').annotate(
        total=Count('id')
    ).order_by('date_ouverture__month')
    
    # Totaux
    totaux = Reclamation.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_ouverture__year=annee
    ).aggregate(
        total=Count('id'),
        resolues=Count('id', filter=Q(statut='resolue')),
        rejetees=Count('id', filter=Q(statut='rejetee')),
        en_cours=Count('id', filter=Q(statut__in=['ouverte', 'en_cours', 'en_attente'])),
    )
    
    # Taux de résolution
    if totaux['total'] > 0:
        totaux['taux_resolution'] = round((totaux['resolues'] / totaux['total']) * 100, 1)
    else:
        totaux['taux_resolution'] = 0
    
    return render(request, 'employes/reclamations/recap.html', {
        'recap_categories': recap_categories,
        'recap_mois': recap_mois,
        'totaux': totaux,
        'annee': annee,
    })


@reauth_required
@login_required
def gestion_categories_reclamations(request):
    """Gestion des catégories de réclamations"""
    categories = CategorieReclamation.objects.all()
    
    responsables = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'creer':
            code = request.POST.get('code')
            libelle = request.POST.get('libelle')
            description = request.POST.get('description', '')
            delai = request.POST.get('delai_traitement_jours', 5)
            responsable_id = request.POST.get('responsable_defaut')
            
            responsable = None
            if responsable_id:
                responsable = Employe.objects.filter(pk=responsable_id).first()
            
            CategorieReclamation.objects.create(
                code=code,
                libelle=libelle,
                description=description,
                delai_traitement_jours=int(delai),
                responsable_defaut=responsable,
            )
            messages.success(request, f"Catégorie '{libelle}' créée")
        
        elif action == 'supprimer':
            cat_id = request.POST.get('categorie_id')
            cat = get_object_or_404(CategorieReclamation, pk=cat_id)
            if cat.reclamations.exists():
                messages.error(request, "Cette catégorie est utilisée")
            else:
                cat.delete()
                messages.success(request, "Catégorie supprimée")
        
        return redirect('employes:gestion_categories_reclamations')
    
    return render(request, 'employes/reclamations/categories.html', {
        'categories': categories,
        'responsables': responsables,
    })
