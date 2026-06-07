from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import uuid

from .models import TypeContrat, Contrat, AlerteContrat, AvantageContrat, DisponibiliteEmploye
from employes.models import Employe
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def contrats_dashboard(request):
    """Dashboard principal du module contrats"""
    entreprise = request.user.entreprise
    
    # Statistiques
    stats = {
        'contrats_actifs': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif'
        ).count(),
        'contrats_expire_bientot': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif',
            date_fin__lte=date.today() + timedelta(days=30),
            date_fin__gte=date.today()
        ).count(),
        'periode_essai_en_cours': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif',
            date_fin_periode_essai__gte=date.today()
        ).count(),
        'alertes_actives': AlerteContrat.objects.filter(
            contrat__employe__entreprise=entreprise,
            statut='active'
        ).count(),
    }
    
    # Contrats expirant bientôt
    contrats_expirants = Contrat.objects.filter(
        employe__entreprise=entreprise,
        statut='actif',
        date_fin__lte=date.today() + timedelta(days=30),
        date_fin__gte=date.today()
    )[:5]
    
    # Alertes récentes
    alertes_recentes = AlerteContrat.objects.filter(
        contrat__employe__entreprise=entreprise,
        statut='active'
    ).order_by('date_echeance')[:5]
    
    context = {
        'stats': stats,
        'contrats_expirants': contrats_expirants,
        'alertes_recentes': alertes_recentes,
    }
    
    return render(request, 'contrats/dashboard.html', context)


@login_required
@entreprise_active_required
def liste_contrats(request):
    """Liste des contrats avec filtres"""
    entreprise = request.user.entreprise
    
    contrats = Contrat.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe', 'type_contrat')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        contrats = contrats.filter(statut=statut)
    
    type_contrat = request.GET.get('type_contrat')
    if type_contrat:
        contrats = contrats.filter(type_contrat_id=type_contrat)
    
    search = request.GET.get('search')
    if search:
        contrats = contrats.filter(
            Q(employe__nom__icontains=search) |
            Q(employe__prenoms__icontains=search) |
            Q(numero_contrat__icontains=search)
        )
    
    # Types de contrats pour le filtre
    types_contrats = TypeContrat.objects.filter(entreprise=entreprise, actif=True)
    
    context = {
        'contrats': contrats,
        'types_contrats': types_contrats,
        'statut_actuel': statut,
        'type_actuel': type_contrat,
        'search_actuel': search,
    }
    
    return render(request, 'contrats/liste.html', context)


@login_required
@entreprise_active_required
def creer_contrat(request):
    """Créer un nouveau contrat"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        try:
            # Récupération des données
            employe_id = request.POST.get('employe')
            type_contrat_id = request.POST.get('type_contrat')
            numero_contrat = request.POST.get('numero_contrat')
            date_debut = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin') or None
            salaire_base = request.POST.get('salaire_base')
            heures_semaine = request.POST.get('heures_semaine', '40.0')
            lieu_travail = request.POST.get('lieu_travail')
            
            # Validation
            employe = get_object_or_404(Employe, id=employe_id, entreprise=entreprise)
            type_contrat = get_object_or_404(TypeContrat, id=type_contrat_id, entreprise=entreprise)
            
            # Calcul de la date de fin de période d'essai
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin_periode_essai = date_debut_obj + timedelta(days=type_contrat.duree_periode_essai_jours)
            
            # Création du contrat
            contrat = Contrat.objects.create(
                employe=employe,
                type_contrat=type_contrat,
                numero_contrat=numero_contrat,
                date_debut=date_debut_obj,
                date_fin=datetime.strptime(date_fin, '%Y-%m-%d').date() if date_fin else None,
                date_fin_periode_essai=date_fin_periode_essai,
                salaire_base=salaire_base,
                heures_semaine=heures_semaine,
                lieu_travail=lieu_travail,
                cree_par=request.user.employe if hasattr(request.user, 'employe') else None
            )
            
            messages.success(request, f'Contrat {numero_contrat} créé avec succès.')
            return redirect('contrats:detail', pk=contrat.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Données pour le formulaire
    employes = Employe.objects.filter(entreprise=entreprise).order_by('nom', 'prenoms')
    types_contrats = TypeContrat.objects.filter(entreprise=entreprise, actif=True)
    
    context = {
        'employes': employes,
        'types_contrats': types_contrats,
    }
    
    return render(request, 'contrats/creer.html', context)


@login_required
@entreprise_active_required
def detail_contrat(request, pk):
    """Détail d'un contrat"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    # Avantages du contrat
    avantages = contrat.avantages.filter(actif=True)
    
    # Alertes liées au contrat
    alertes = contrat.alertes.filter(statut='active')
    
    context = {
        'contrat': contrat,
        'avantages': avantages,
        'alertes': alertes,
    }
    
    return render(request, 'contrats/detail.html', context)


@login_required
@entreprise_active_required
def liste_alertes(request):
    """Liste des alertes contrats"""
    entreprise = request.user.entreprise
    
    alertes = AlerteContrat.objects.filter(
        contrat__employe__entreprise=entreprise
    ).select_related('contrat__employe').order_by('date_echeance')
    
    # Filtres
    statut = request.GET.get('statut', 'active')
    if statut:
        alertes = alertes.filter(statut=statut)
    
    type_alerte = request.GET.get('type_alerte')
    if type_alerte:
        alertes = alertes.filter(type_alerte=type_alerte)
    
    context = {
        'alertes': alertes,
        'statut_actuel': statut,
        'type_actuel': type_alerte,
    }
    
    return render(request, 'contrats/alertes.html', context)


@login_required
@entreprise_active_required
def generer_alertes(request):
    """Génère automatiquement les alertes pour les contrats"""
    if request.method == 'POST':
        from django.core.management import call_command
        try:
            call_command('generer_alertes_contrats')
            messages.success(request, 'Alertes générées avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la génération des alertes : {str(e)}')
    
    return redirect('contrats:alertes')


@login_required
@entreprise_active_required
def liste_types_contrats(request):
    """Liste des types de contrats"""
    entreprise = request.user.entreprise
    types_contrats = TypeContrat.objects.filter(entreprise=entreprise)
    
    context = {
        'types_contrats': types_contrats,
    }
    
    return render(request, 'contrats/types.html', context)


@login_required
@entreprise_active_required
def creer_type_contrat(request):
    """Créer un nouveau type de contrat"""
    if request.method == 'POST':
        try:
            TypeContrat.objects.create(
                entreprise=request.user.entreprise,
                nom=request.POST.get('nom'),
                categorie=request.POST.get('categorie'),
                duree_periode_essai_jours=request.POST.get('duree_periode_essai_jours', 90),
                renouvelable=request.POST.get('renouvelable') == 'on',
                duree_max_mois=request.POST.get('duree_max_mois') or None,
            )
            messages.success(request, 'Type de contrat créé avec succès.')
            return redirect('contrats:types')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    return render(request, 'contrats/creer_type.html')


@login_required
@entreprise_active_required
def modifier_type_contrat(request, pk):
    """Modifier un type de contrat"""
    type_contrat = get_object_or_404(
        TypeContrat,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            type_contrat.nom = request.POST.get('nom')
            type_contrat.categorie = request.POST.get('categorie')
            type_contrat.duree_periode_essai_jours = request.POST.get('duree_periode_essai_jours', 90)
            type_contrat.renouvelable = request.POST.get('renouvelable') == 'on'
            type_contrat.duree_max_mois = request.POST.get('duree_max_mois') or None
            type_contrat.actif = request.POST.get('actif') == 'on'
            type_contrat.save()
            
            messages.success(request, 'Type de contrat modifié avec succès.')
            return redirect('contrats:types')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'type_contrat': type_contrat,
    }
    
    return render(request, 'contrats/modifier_type.html', context)


@login_required
@entreprise_active_required
def modifier_contrat(request, pk):
    """Modifier un contrat existant"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            # Mise à jour des champs modifiables
            contrat.salaire_base = request.POST.get('salaire_base')
            contrat.heures_semaine = request.POST.get('heures_semaine')
            contrat.lieu_travail = request.POST.get('lieu_travail')
            contrat.statut = request.POST.get('statut')
            
            if request.POST.get('date_fin'):
                from datetime import datetime
                contrat.date_fin = datetime.strptime(request.POST.get('date_fin'), '%Y-%m-%d').date()
            
            contrat.save()
            messages.success(request, 'Contrat modifié avec succès.')
            return redirect('contrats:detail', pk=contrat.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'contrat': contrat,
    }
    
    return render(request, 'contrats/modifier.html', context)


@login_required
@entreprise_active_required
def terminer_contrat(request, pk):
    """Terminer un contrat"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            from datetime import datetime
            contrat.statut = 'termine'
            contrat.date_fin_effective = datetime.strptime(request.POST.get('date_fin_effective'), '%Y-%m-%d').date()
            contrat.motif_fin = request.POST.get('motif_fin')
            contrat.commentaire_fin = request.POST.get('commentaire_fin')
            contrat.save()
            
            messages.success(request, 'Contrat terminé avec succès.')
            return redirect('contrats:detail', pk=contrat.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la terminaison : {str(e)}')
    
    context = {
        'contrat': contrat,
    }
    
    return render(request, 'contrats/terminer.html', context)


@login_required
@entreprise_active_required
def traiter_alerte(request, pk):
    """Traiter une alerte"""
    alerte = get_object_or_404(
        AlerteContrat,
        pk=pk,
        contrat__employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        alerte.statut = request.POST.get('statut', 'traitee')
        alerte.traitee_par = request.user.employe if hasattr(request.user, 'employe') else None
        alerte.date_traitement = timezone.now()
        alerte.save()
        
        messages.success(request, 'Alerte traitée avec succès.')
        return redirect('contrats:alertes')
    
    context = {
        'alerte': alerte,
    }
    
    return render(request, 'contrats/traiter_alerte.html', context)


@login_required
@entreprise_active_required
def liste_disponibilites(request):
    """Liste des disponibilités employés"""
    entreprise = request.user.entreprise
    
    disponibilites = DisponibiliteEmploye.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe').order_by('-date_debut')
    
    context = {
        'disponibilites': disponibilites,
    }
    
    return render(request, 'contrats/disponibilites.html', context)


@login_required
@entreprise_active_required
def creer_disponibilite(request):
    """Créer une nouvelle disponibilité"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        try:
            employe_id = request.POST.get('employe')
            employe = get_object_or_404(Employe, id=employe_id, entreprise=entreprise)
            
            from datetime import datetime
            DisponibiliteEmploye.objects.create(
                employe=employe,
                type_disponibilite=request.POST.get('type_disponibilite'),
                date_debut=datetime.strptime(request.POST.get('date_debut'), '%Y-%m-%d').date(),
                date_fin=datetime.strptime(request.POST.get('date_fin'), '%Y-%m-%d').date(),
                commentaire=request.POST.get('commentaire'),
            )
            
            messages.success(request, 'Disponibilité créée avec succès.')
            return redirect('contrats:disponibilites')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    employes = Employe.objects.filter(entreprise=entreprise).order_by('nom', 'prenoms')
    
    context = {
        'employes': employes,
    }
    
    return render(request, 'contrats/creer_disponibilite.html', context)


@login_required
@entreprise_active_required
def approuver_disponibilite(request, pk):
    """Approuver une disponibilité"""
    disponibilite = get_object_or_404(
        DisponibiliteEmploye,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        disponibilite.approuve = True
        disponibilite.approuve_par = request.user.employe if hasattr(request.user, 'employe') else None
        disponibilite.save()
        
        messages.success(request, 'Disponibilité approuvée avec succès.')
        return redirect('contrats:disponibilites')
    
    context = {
        'disponibilite': disponibilite,
    }
    
    return render(request, 'contrats/approuver_disponibilite.html', context)


@login_required
@entreprise_active_required
def rapports_contrats(request):
    """Rapports et statistiques des contrats"""
    entreprise = request.user.entreprise
    
    # Statistiques par type de contrat
    stats_types = TypeContrat.objects.filter(entreprise=entreprise).annotate(
        nb_contrats=Count('contrat')
    )
    
    # Statistiques par statut
    from django.db.models import Count
    stats_statuts = Contrat.objects.filter(
        employe__entreprise=entreprise
    ).values('statut').annotate(count=Count('id'))
    
    context = {
        'stats_types': stats_types,
        'stats_statuts': stats_statuts,
    }
    
    return render(request, 'contrats/rapports.html', context)


@login_required
@entreprise_active_required
def rapport_expirations(request):
    """Rapport des contrats arrivant à expiration"""
    entreprise = request.user.entreprise
    
    # Contrats expirant dans les 30, 60, 90 jours
    today = date.today()
    
    expirations = {
        '30_jours': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif',
            date_fin__lte=today + timedelta(days=30),
            date_fin__gte=today
        ),
        '60_jours': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif',
            date_fin__lte=today + timedelta(days=60),
            date_fin__gte=today + timedelta(days=30)
        ),
        '90_jours': Contrat.objects.filter(
            employe__entreprise=entreprise,
            statut='actif',
            date_fin__lte=today + timedelta(days=90),
            date_fin__gte=today + timedelta(days=60)
        ),
    }
    
    context = {
        'expirations': expirations,
    }
    
    return render(request, 'contrats/rapport_expirations.html', context)


@login_required
@entreprise_active_required
def renouveler_contrat(request, pk):
    """Renouveler un contrat"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            from datetime import datetime
            
            # Créer un nouveau contrat basé sur l'ancien
            nouveau_contrat = Contrat.objects.create(
                employe=contrat.employe,
                type_contrat=contrat.type_contrat,
                numero_contrat=request.POST.get('numero_contrat'),
                date_debut=datetime.strptime(request.POST.get('date_debut'), '%Y-%m-%d').date(),
                date_fin=datetime.strptime(request.POST.get('date_fin'), '%Y-%m-%d').date() if request.POST.get('date_fin') else None,
                salaire_base=request.POST.get('salaire_base'),
                heures_semaine=request.POST.get('heures_semaine'),
                lieu_travail=request.POST.get('lieu_travail'),
                cree_par=request.user.employe if hasattr(request.user, 'employe') else None
            )
            
            # Marquer l'ancien contrat comme terminé
            contrat.statut = 'termine'
            contrat.date_fin_effective = nouveau_contrat.date_debut
            contrat.motif_fin = 'renouvellement'
            contrat.save()
            
            messages.success(request, f'Contrat renouvelé avec succès. Nouveau contrat: {nouveau_contrat.numero_contrat}')
            return redirect('contrats:detail', pk=nouveau_contrat.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors du renouvellement : {str(e)}')
    
    context = {
        'contrat': contrat,
    }
    
    return render(request, 'contrats/renouveler.html', context)


@login_required
@entreprise_active_required
def imprimer_contrat(request, pk):
    """Imprimer un contrat"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    # Avantages du contrat
    avantages = contrat.avantages.filter(actif=True)
    
    context = {
        'contrat': contrat,
        'avantages': avantages,
        'entreprise': request.user.entreprise,
    }
    
    return render(request, 'contrats/imprimer.html', context)


@login_required
@entreprise_active_required
def solde_tout_compte(request, pk):
    """Calcul et affichage du Solde de Tout Compte pour fin de CDD"""
    contrat = get_object_or_404(
        Contrat,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )

    from .services_stc import calculer_solde_tout_compte
    from datetime import datetime

    # Date de fin personnalisée (paramètre GET optionnel)
    date_fin_str = request.GET.get('date_fin')
    date_fin = None
    if date_fin_str:
        try:
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    calcul = calculer_solde_tout_compte(contrat, date_fin)

    context = {
        'contrat': contrat,
        'calcul': calcul,
        'entreprise': request.user.entreprise,
        'date_fin_str': (date_fin or calcul['date_fin']).strftime('%Y-%m-%d'),
    }
    return render(request, 'contrats/solde_tout_compte.html', context)
