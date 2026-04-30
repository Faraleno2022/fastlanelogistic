"""
Vues pour la gestion des visites medicales.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta

from .models import Employe, VisiteMedicale


@reauth_required
@login_required
def liste_visites_medicales(request):
    visites = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise
    ).select_related('employe', 'employe__service')
    
    employe_id = request.GET.get('employe')
    aptitude = request.GET.get('aptitude')
    type_visite = request.GET.get('type')
    annee = request.GET.get('annee', date.today().year)
    
    if employe_id:
        visites = visites.filter(employe_id=employe_id)
    if aptitude:
        visites = visites.filter(aptitude=aptitude)
    if type_visite:
        visites = visites.filter(type_visite=type_visite)
    if annee:
        visites = visites.filter(date_visite__year=int(annee))
    
    stats = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise
    ).aggregate(
        nb_total=Count('id'),
        nb_aptes=Count('id', filter=Q(aptitude='apte')),
        nb_reserves=Count('id', filter=Q(aptitude='apte_reserves')),
        nb_en_attente=Count('id', filter=Q(aptitude='en_attente')),
    )
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'employes/medical/liste.html', {
        'visites': visites[:100],
        'stats': stats,
        'employes': employes,
        'types_visite': VisiteMedicale.TYPES_VISITE,
        'aptitudes': VisiteMedicale.APTITUDES,
        'annee': int(annee),
        'filtre_employe': employe_id,
        'filtre_aptitude': aptitude,
        'filtre_type': type_visite,
    })


@reauth_required
@login_required
def planifier_visite(request):
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        type_visite = request.POST.get('type_visite')
        date_visite = request.POST.get('date_visite')
        medecin = request.POST.get('medecin', '')
        centre_medical = request.POST.get('centre_medical', '')
        
        employe = get_object_or_404(Employe, pk=employe_id, entreprise=request.user.entreprise)
        
        visite = VisiteMedicale.objects.create(
            employe=employe,
            type_visite=type_visite,
            date_visite=date_visite,
            medecin=medecin,
            centre_medical=centre_medical,
            aptitude='en_attente',
        )
        
        messages.success(request, f"Visite medicale planifiee pour {employe.nom}")
        return redirect('employes:detail_visite', pk=visite.pk)
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'employes/medical/planifier.html', {
        'employes': employes,
        'types_visite': VisiteMedicale.TYPES_VISITE,
    })


@reauth_required
@login_required
def detail_visite(request, pk):
    visite = get_object_or_404(VisiteMedicale, pk=pk, employe__entreprise=request.user.entreprise)
    historique = VisiteMedicale.objects.filter(employe=visite.employe).exclude(pk=pk).order_by('-date_visite')[:5]
    
    return render(request, 'employes/medical/detail.html', {
        'visite': visite,
        'historique': historique,
        'aptitudes': VisiteMedicale.APTITUDES,
    })


@reauth_required
@login_required
def enregistrer_resultat(request, pk):
    visite = get_object_or_404(VisiteMedicale, pk=pk, employe__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        visite.aptitude = request.POST.get('aptitude')
        visite.reserves = request.POST.get('reserves', '')
        visite.recommandations = request.POST.get('recommandations', '')
        visite.date_prochaine_visite = request.POST.get('date_prochaine_visite') or None
        if request.FILES.get('fichier_certificat'):
            visite.fichier_certificat = request.FILES.get('fichier_certificat')
        visite.save()
        
        messages.success(request, "Resultat de la visite enregistre")
        return redirect('employes:detail_visite', pk=pk)
    
    return render(request, 'employes/medical/resultat.html', {
        'visite': visite,
        'aptitudes': VisiteMedicale.APTITUDES,
    })


@reauth_required
@login_required
def supprimer_visite(request, pk):
    visite = get_object_or_404(VisiteMedicale, pk=pk, employe__entreprise=request.user.entreprise)
    visite.delete()
    messages.success(request, "Visite supprimee")
    return redirect('employes:liste_visites_medicales')


@reauth_required
@login_required
def tableau_bord_medical(request):
    today = date.today()
    
    visites_a_venir = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_prochaine_visite__isnull=False,
        date_prochaine_visite__gte=today,
        date_prochaine_visite__lte=today + timedelta(days=60)
    ).select_related('employe').order_by('date_prochaine_visite')[:10]
    
    visites_en_attente = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise,
        aptitude='en_attente'
    ).select_related('employe').order_by('-date_visite')[:10]
    
    employes_restrictions = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise,
        aptitude='apte_reserves'
    ).select_related('employe').order_by('-date_visite')[:10]
    
    stats_aptitude = VisiteMedicale.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_visite__year=today.year
    ).values('aptitude').annotate(count=Count('id'))
    
    return render(request, 'employes/medical/tableau_bord.html', {
        'visites_a_venir': visites_a_venir,
        'visites_en_attente': visites_en_attente,
        'employes_restrictions': employes_restrictions,
        'stats_aptitude': stats_aptitude,
    })


@reauth_required
@login_required
def suivi_medical_employe(request, employe_id):
    employe = get_object_or_404(Employe, pk=employe_id, entreprise=request.user.entreprise)
    visites = VisiteMedicale.objects.filter(employe=employe).order_by('-date_visite')
    
    return render(request, 'employes/medical/suivi_employe.html', {
        'employe': employe,
        'visites': visites,
    })
