from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, time, datetime, timedelta
import json

from temps_travail.models import Absence, Pointage
from temps_travail.models_extensions import PermissionExceptionnelle
from employes.models import Employe


@login_required
def mes_absences(request):
    """Interface employé pour gérer ses absences et permissions"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    # Absences récentes
    absences_recentes = Absence.objects.filter(
        employe=employe
    ).order_by('-date_absence')[:10]
    
    # Permissions exceptionnelles en cours
    permissions_en_cours = PermissionExceptionnelle.objects.filter(
        employe=employe,
        statut='demandee'
    ).order_by('-date_creation')
    
    # Statistiques du mois
    mois_actuel = date.today().replace(day=1)
    mois_suivant = (mois_actuel + timedelta(days=32)).replace(day=1)
    
    stats_mois = {
        'jours_absence': Absence.objects.filter(
            employe=employe,
            date_absence__gte=mois_actuel,
            date_absence__lt=mois_suivant
        ).count(),
        'heures_permission': sum([
            p.duree_heures for p in PermissionExceptionnelle.objects.filter(
                employe=employe,
                date_permission__gte=mois_actuel,
                date_permission__lt=mois_suivant,
                statut='approuvee'
            )
        ]),
    }
    
    context = {
        'employe': employe,
        'absences_recentes': absences_recentes,
        'permissions_en_cours': permissions_en_cours,
        'stats_mois': stats_mois,
    }
    
    return render(request, 'portail/absences/mes_absences.html', context)


@login_required
def demander_permission(request):
    """Formulaire de demande de permission exceptionnelle"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    if request.method == 'POST':
        try:
            # Récupération des données
            type_permission = request.POST.get('type_permission')
            date_permission = request.POST.get('date_permission')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            motif_detaille = request.POST.get('motif_detaille')
            
            # Validation des données
            date_permission_obj = datetime.strptime(date_permission, '%Y-%m-%d').date()
            heure_debut_obj = datetime.strptime(heure_debut, '%H:%M').time()
            heure_fin_obj = datetime.strptime(heure_fin, '%H:%M').time()
            
            if date_permission_obj < date.today():
                messages.error(request, "La date ne peut pas être dans le passé.")
                return render(request, 'portail/absences/demander_permission.html')
            
            if heure_fin_obj <= heure_debut_obj:
                messages.error(request, "L'heure de fin doit être postérieure à l'heure de début.")
                return render(request, 'portail/absences/demander_permission.html')
            
            # Calcul de la durée
            debut = datetime.combine(date_permission_obj, heure_debut_obj)
            fin = datetime.combine(date_permission_obj, heure_fin_obj)
            duree_heures = (fin - debut).total_seconds() / 3600
            
            # Création de la permission
            permission = PermissionExceptionnelle.objects.create(
                employe=employe,
                type_permission=type_permission,
                date_permission=date_permission_obj,
                heure_debut=heure_debut_obj,
                heure_fin=heure_fin_obj,
                duree_heures=duree_heures,
                motif_detaille=motif_detaille,
                heures_a_recuperer=request.POST.get('heures_a_recuperer') == 'on',
                deduction_salaire=request.POST.get('deduction_salaire') == 'on'
            )
            
            # Gestion de la pièce justificative
            if 'piece_justificative' in request.FILES:
                permission.piece_justificative = request.FILES['piece_justificative']
                permission.save()
            
            messages.success(request, f'Demande de permission créée. Référence: #{permission.id}')
            return redirect('portail:detail_permission', pk=permission.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de la demande : {str(e)}')
    
    context = {
        'employe': employe,
    }
    
    return render(request, 'portail/absences/demander_permission.html', context)


@login_required
def detail_permission(request, pk):
    """Détail d'une permission exceptionnelle"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    permission = get_object_or_404(
        PermissionExceptionnelle,
        pk=pk,
        employe=employe
    )
    
    context = {
        'permission': permission,
    }
    
    return render(request, 'portail/absences/detail_permission.html', context)


@login_required
def declarer_absence(request):
    """Formulaire de déclaration d'absence"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    if request.method == 'POST':
        try:
            # Récupération des données
            type_absence = request.POST.get('type_absence')
            date_absence = request.POST.get('date_absence')
            duree_jours = request.POST.get('duree_jours', '1')
            motif = request.POST.get('motif')
            
            # Validation
            date_absence_obj = datetime.strptime(date_absence, '%Y-%m-%d').date()
            
            # Création de l'absence
            absence = Absence.objects.create(
                employe=employe,
                date_absence=date_absence_obj,
                type_absence=type_absence,
                duree_jours=duree_jours,
                justifie=type_absence in ['maladie', 'accident_travail', 'rendez_vous_medical'],
                observations=motif
            )
            
            # Gestion du justificatif
            if 'justificatif' in request.FILES:
                absence.justificatif = request.FILES['justificatif']
                absence.save()
            
            messages.success(request, f'Absence déclarée avec succès. Référence: #{absence.id}')
            return redirect('portail:mes_absences')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la déclaration : {str(e)}')
    
    context = {
        'employe': employe,
    }
    
    return render(request, 'portail/absences/declarer_absence.html', context)


@login_required
def historique_absences(request):
    """Historique complet des absences"""
    try:
        employe = request.user.employe
    except:
        messages.error(request, "Vous devez être connecté en tant qu'employé.")
        return redirect('core:login')
    
    # Filtres
    annee = request.GET.get('annee', date.today().year)
    type_absence = request.GET.get('type_absence')
    
    absences = Absence.objects.filter(employe=employe)
    
    if annee:
        absences = absences.filter(date_absence__year=annee)
    
    if type_absence:
        absences = absences.filter(type_absence=type_absence)
    
    absences = absences.order_by('-date_absence')
    
    # Permissions exceptionnelles
    permissions = PermissionExceptionnelle.objects.filter(employe=employe)
    
    if annee:
        permissions = permissions.filter(date_permission__year=annee)
    
    permissions = permissions.order_by('-date_permission')
    
    # Années disponibles
    annees_disponibles = list(range(date.today().year - 2, date.today().year + 1))
    
    context = {
        'employe': employe,
        'absences': absences,
        'permissions': permissions,
        'annees_disponibles': annees_disponibles,
        'annee_actuelle': int(annee) if annee else None,
        'type_actuel': type_absence,
    }
    
    return render(request, 'portail/absences/historique.html', context)


@login_required
def calculer_duree_permission(request):
    """API pour calculer la durée d'une permission"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            heure_debut = data.get('heure_debut')
            heure_fin = data.get('heure_fin')
            
            debut_obj = datetime.strptime(heure_debut, '%H:%M').time()
            fin_obj = datetime.strptime(heure_fin, '%H:%M').time()
            
            # Calcul de la durée
            debut = datetime.combine(date.today(), debut_obj)
            fin = datetime.combine(date.today(), fin_obj)
            duree_heures = (fin - debut).total_seconds() / 3600
            
            return JsonResponse({
                'success': True,
                'duree_heures': round(duree_heures, 2)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
