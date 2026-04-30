"""
Vues du module Congés
Interface dédiée pour la gestion des congés
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date

from temps_travail.models import Conge, SoldeConge
from employes.models import Employe
from paie.models import ConfigurationPaieEntreprise


@reauth_required
@login_required
def liste_conges(request):
    """Liste des demandes de congés"""
    entreprise = request.user.entreprise
    
    # Filtres
    statut = request.GET.get('statut', '')
    type_conge = request.GET.get('type', '')
    employe_id = request.GET.get('employe', '')
    
    conges = Conge.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe', 'approbateur')
    
    if statut:
        conges = conges.filter(statut_demande=statut)
    if type_conge:
        conges = conges.filter(type_conge=type_conge)
    if employe_id:
        conges = conges.filter(employe_id=employe_id)
    
    # Config entreprise pour afficher les règles
    config = ConfigurationPaieEntreprise.get_ou_creer(entreprise)
    
    employes = Employe.objects.filter(entreprise=entreprise).order_by('nom', 'prenoms')
    
    return render(request, 'conges/liste.html', {
        'conges': conges,
        'employes': employes,
        'config': config,
        'types_conge': Conge.TYPES,
        'statuts': Conge.STATUTS,
        'statut_filter': statut,
        'type_filter': type_conge,
        'employe_filter': employe_id,
    })


@reauth_required
@login_required
def soldes_conges(request):
    """Afficher les soldes de congés par employé"""
    entreprise = request.user.entreprise
    annee = int(request.GET.get('annee', date.today().year))
    
    soldes = SoldeConge.objects.filter(
        employe__entreprise=entreprise,
        annee=annee
    ).select_related('employe')
    
    # Config entreprise
    config = ConfigurationPaieEntreprise.get_ou_creer(entreprise)
    
    return render(request, 'conges/soldes.html', {
        'soldes': soldes,
        'annee': annee,
        'config': config,
    })


@reauth_required
@login_required
def demander_conge(request):
    """Formulaire de demande de congé"""
    entreprise = request.user.entreprise
    
    if request.method == 'POST':
        try:
            employe = get_object_or_404(Employe, pk=request.POST.get('employe'), entreprise=entreprise)
            
            conge = Conge.objects.create(
                employe=employe,
                type_conge=request.POST.get('type_conge'),
                date_debut=request.POST.get('date_debut'),
                date_fin=request.POST.get('date_fin'),
                nombre_jours=int(request.POST.get('nombre_jours', 1)),
                motif=request.POST.get('motif', ''),
                annee_reference=date.today().year,
            )
            
            if request.FILES.get('justificatif'):
                conge.justificatif = request.FILES['justificatif']
                conge.save()
            
            messages.success(request, 'Demande de congé soumise avec succès.')
            return redirect('conges:liste')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    employes = Employe.objects.filter(entreprise=entreprise).order_by('nom', 'prenoms')
    config = ConfigurationPaieEntreprise.get_ou_creer(entreprise)
    
    return render(request, 'conges/demander.html', {
        'employes': employes,
        'types_conge': Conge.TYPES,
        'config': config,
    })


@reauth_required
@login_required
def approuver_conge(request, pk):
    """Approuver ou rejeter une demande de congé"""
    entreprise = request.user.entreprise
    conge = get_object_or_404(Conge, pk=pk, employe__entreprise=entreprise)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approuver':
            conge.statut_demande = 'approuve'
            conge.date_approbation = date.today()
            # Mettre à jour le solde
            solde, _ = SoldeConge.objects.get_or_create(
                employe=conge.employe,
                annee=conge.annee_reference or date.today().year
            )
            solde.conges_pris += conge.nombre_jours
            solde.conges_restants = solde.conges_acquis - solde.conges_pris + solde.conges_reports
            solde.save()
            messages.success(request, 'Congé approuvé.')
        elif action == 'rejeter':
            conge.statut_demande = 'rejete'
            messages.warning(request, 'Congé rejeté.')
        
        conge.commentaire_approbateur = request.POST.get('commentaire', '')
        conge.save()
        
        return redirect('conges:liste')
    
    return render(request, 'conges/approuver.html', {
        'conge': conge,
    })
