from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
import json

from temps_travail.models import Conge, SoldeConge
from temps_travail.models_extensions import DemandeCongePublique, ParametrageConges
from employes.models import Employe


@login_required
def mes_conges(request):
    """Interface employé pour gérer ses congés"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    # Solde de congés actuel
    annee_courante = date.today().year
    solde, created = SoldeConge.objects.get_or_create(
        employe=employe,
        annee=annee_courante,
        defaults={
            'conges_acquis': 18.00,
            'conges_pris': 0,
            'conges_restants': 18.00,
        }
    )
    
    # Mettre à jour automatiquement le solde
    if hasattr(solde, 'mettre_a_jour_solde'):
        solde.mettre_a_jour_solde()
    
    # Historique des congés
    conges_historique = Conge.objects.filter(
        employe=employe
    ).order_by('-date_debut')[:10]
    
    # Demandes en cours
    demandes_en_cours = DemandeCongePublique.objects.filter(
        employe=employe,
        statut__in=['brouillon', 'soumise', 'en_cours']
    ).order_by('-date_creation')
    
    # Prochains congés approuvés
    prochains_conges = Conge.objects.filter(
        employe=employe,
        statut_demande='approuve',
        date_debut__gte=date.today()
    ).order_by('date_debut')[:5]
    
    context = {
        'employe': employe,
        'solde': solde,
        'conges_historique': conges_historique,
        'demandes_en_cours': demandes_en_cours,
        'prochains_conges': prochains_conges,
    }
    
    return render(request, 'portail/conges/mes_conges.html', context)


@login_required
def demander_conge(request):
    """Formulaire de demande de congé"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    if request.method == 'POST':
        try:
            # Récupération des données
            type_conge = request.POST.get('type_conge')
            date_debut = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin')
            motif = request.POST.get('motif')
            
            # Validation des dates
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            
            if date_debut_obj < date.today():
                messages.error(request, "La date de début ne peut pas être dans le passé.")
                return render(request, 'portail/conges/demander.html')
            
            if date_fin_obj < date_debut_obj:
                messages.error(request, "La date de fin doit être postérieure à la date de début.")
                return render(request, 'portail/conges/demander.html')
            
            # Calcul du nombre de jours
            nombre_jours = (date_fin_obj - date_debut_obj).days + 1
            
            # Vérification du solde pour les congés annuels
            if type_conge == 'annuel':
                annee_courante = date.today().year
                solde = SoldeConge.objects.filter(
                    employe=employe,
                    annee=annee_courante
                ).first()
                
                if solde and solde.conges_restants < nombre_jours:
                    messages.error(request, f"Solde insuffisant. Vous avez {solde.conges_restants} jours disponibles.")
                    return render(request, 'portail/conges/demander.html')
            
            # Création de la demande
            demande = DemandeCongePublique.objects.create(
                employe=employe,
                type_conge=type_conge,
                date_debut=date_debut_obj,
                date_fin=date_fin_obj,
                nombre_jours_demandes=nombre_jours,
                motif=motif,
                statut='brouillon'
            )
            
            # Gestion du document justificatif
            if 'document_justificatif' in request.FILES:
                demande.document_justificatif = request.FILES['document_justificatif']
                demande.save()
            
            messages.success(request, f'Demande de congé créée. Référence: #{demande.id}')
            return redirect('portail:detail_demande_conge', pk=demande.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de la demande : {str(e)}')
    
    # Solde actuel pour affichage
    annee_courante = date.today().year
    solde = SoldeConge.objects.filter(
        employe=employe,
        annee=annee_courante
    ).first()
    
    context = {
        'employe': employe,
        'solde': solde,
    }
    
    return render(request, 'portail/conges/demander.html', context)


@login_required
def detail_demande_conge(request, pk):
    """Détail d'une demande de congé"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    demande = get_object_or_404(
        DemandeCongePublique,
        pk=pk,
        employe=employe
    )
    
    context = {
        'demande': demande,
    }
    
    return render(request, 'portail/conges/detail_demande.html', context)


@login_required
def modifier_demande_conge(request, pk):
    """Modifier une demande de congé (si possible)"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    demande = get_object_or_404(
        DemandeCongePublique,
        pk=pk,
        employe=employe
    )
    
    if not demande.peut_etre_modifiee():
        messages.error(request, "Cette demande ne peut plus être modifiée.")
        return redirect('portail:detail_demande_conge', pk=pk)
    
    if request.method == 'POST':
        try:
            # Mise à jour des données
            demande.type_conge = request.POST.get('type_conge')
            demande.motif = request.POST.get('motif')
            
            # Dates
            from datetime import datetime
            date_debut_obj = datetime.strptime(request.POST.get('date_debut'), '%Y-%m-%d').date()
            date_fin_obj = datetime.strptime(request.POST.get('date_fin'), '%Y-%m-%d').date()
            
            demande.date_debut = date_debut_obj
            demande.date_fin = date_fin_obj
            demande.nombre_jours_demandes = (date_fin_obj - date_debut_obj).days + 1
            
            # Document
            if 'document_justificatif' in request.FILES:
                demande.document_justificatif = request.FILES['document_justificatif']
            
            demande.save()
            
            messages.success(request, 'Demande modifiée avec succès.')
            return redirect('portail:detail_demande_conge', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'demande': demande,
    }
    
    return render(request, 'portail/conges/modifier_demande.html', context)


@login_required
def soumettre_demande_conge(request, pk):
    """Soumettre une demande de congé pour validation"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    demande = get_object_or_404(
        DemandeCongePublique,
        pk=pk,
        employe=employe
    )
    
    if demande.statut != 'brouillon':
        messages.error(request, "Cette demande a déjà été soumise.")
        return redirect('portail:detail_demande_conge', pk=pk)
    
    if request.method == 'POST':
        demande.soumettre()
        messages.success(request, 'Demande soumise avec succès. Elle sera traitée par votre responsable.')
        return redirect('portail:mes_conges')
    
    context = {
        'demande': demande,
    }
    
    return render(request, 'portail/conges/soumettre_demande.html', context)


@login_required
def annuler_demande_conge(request, pk):
    """Annuler une demande de congé"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    demande = get_object_or_404(
        DemandeCongePublique,
        pk=pk,
        employe=employe
    )
    
    if demande.statut not in ['brouillon', 'soumise']:
        messages.error(request, "Cette demande ne peut plus être annulée.")
        return redirect('portail:detail_demande_conge', pk=pk)
    
    if request.method == 'POST':
        demande.delete()
        messages.success(request, 'Demande annulée avec succès.')
        return redirect('portail:mes_conges')
    
    context = {
        'demande': demande,
    }
    
    return render(request, 'portail/conges/annuler_demande.html', context)


@login_required
def calculer_jours_conges(request):
    """API pour calculer le nombre de jours de congés"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_debut = data.get('date_debut')
            date_fin = data.get('date_fin')
            
            from datetime import datetime
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            
            # Calcul simple (peut être amélioré pour exclure les weekends et jours fériés)
            nombre_jours = (date_fin_obj - date_debut_obj).days + 1
            
            return JsonResponse({
                'success': True,
                'nombre_jours': nombre_jours
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})


@login_required
def historique_conges(request):
    """Historique complet des congés de l'employé"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    # Filtres
    annee = request.GET.get('annee', date.today().year)
    type_conge = request.GET.get('type_conge')
    
    conges = Conge.objects.filter(employe=employe)
    
    if annee:
        conges = conges.filter(annee_reference=annee)
    
    if type_conge:
        conges = conges.filter(type_conge=type_conge)
    
    conges = conges.order_by('-date_debut')
    
    # Années disponibles pour le filtre
    annees_disponibles = Conge.objects.filter(
        employe=employe
    ).values_list('annee_reference', flat=True).distinct().order_by('-annee_reference')
    
    context = {
        'employe': employe,
        'conges': conges,
        'annees_disponibles': annees_disponibles,
        'annee_actuelle': int(annee) if annee else None,
        'type_actuel': type_conge,
    }
    
    return render(request, 'portail/conges/historique.html', context)
