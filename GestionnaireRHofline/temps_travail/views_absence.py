"""
Vues pour la gestion des absences.
Utilise le modèle Absence existant avec date_absence et duree_jours.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date
from decimal import Decimal

from employes.models import Employe
from .models import Absence


@login_required
def liste_absences(request):
    """Liste des absences avec filtres"""
    absences = Absence.objects.filter(
        employe__entreprise=request.user.entreprise
    ).select_related('employe', 'employe__service')
    
    # Filtres
    employe_id = request.GET.get('employe')
    type_absence = request.GET.get('type')
    mois = request.GET.get('mois')
    annee = request.GET.get('annee', date.today().year)
    justifie = request.GET.get('justifie')
    
    if employe_id:
        absences = absences.filter(employe_id=employe_id)
    if type_absence:
        absences = absences.filter(type_absence=type_absence)
    if mois:
        absences = absences.filter(date_absence__month=int(mois))
    if annee:
        absences = absences.filter(date_absence__year=int(annee))
    if justifie == '1':
        absences = absences.filter(justifie=True)
    elif justifie == '0':
        absences = absences.filter(justifie=False)
    
    # Statistiques
    stats = absences.aggregate(
        total_jours=Sum('duree_jours'),
        nb_absences=Count('id'),
        nb_justifiees=Count('id', filter=Q(justifie=True)),
        nb_non_justifiees=Count('id', filter=Q(justifie=False)),
    )
    
    # Employés pour le filtre
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'temps_travail/absences/liste.html', {
        'absences': absences[:100],
        'stats': stats,
        'employes': employes,
        'types_absence': Absence.TYPES,
        'annee': int(annee),
        'mois': mois,
        'filtre_employe': employe_id,
        'filtre_type': type_absence,
        'filtre_justifie': justifie,
    })


@login_required
def declarer_absence(request):
    """Déclarer une nouvelle absence"""
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        type_absence = request.POST.get('type_absence')
        date_absence = request.POST.get('date_absence')
        duree_jours = request.POST.get('duree_jours', '1')
        observations = request.POST.get('observations', '')
        
        employe = get_object_or_404(
            Employe,
            pk=employe_id,
            entreprise=request.user.entreprise
        )
        
        # Déterminer l'impact paie
        impact_paie = 'paye'
        if type_absence == 'absence_injustifiee':
            impact_paie = 'non_paye'
        
        absence = Absence.objects.create(
            employe=employe,
            type_absence=type_absence,
            date_absence=date_absence,
            duree_jours=Decimal(duree_jours),
            impact_paie=impact_paie,
            observations=observations,
        )
        
        messages.success(request, f"Absence déclarée: {absence.duree_jours} jour(s)")
        return redirect('temps_travail:liste_absences')
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'temps_travail/absences/declarer.html', {
        'employes': employes,
        'types_absence': Absence.TYPES,
    })


@login_required
def detail_absence(request, pk):
    """Détail d'une absence"""
    absence = get_object_or_404(
        Absence,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    return render(request, 'temps_travail/absences/detail.html', {
        'absence': absence,
    })


@login_required
def justifier_absence(request, pk):
    """Justifier une absence"""
    absence = get_object_or_404(
        Absence,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        justificatif = request.FILES.get('justificatif')
        observations = request.POST.get('observations', '')
        
        absence.justifie = True
        if observations:
            absence.observations = observations
        
        if justificatif:
            absence.justificatif = justificatif
        
        absence.save()
        
        messages.success(request, "Absence justifiée")
        return redirect('temps_travail:detail_absence', pk=pk)
    
    return render(request, 'temps_travail/absences/justifier.html', {
        'absence': absence,
    })


@login_required
def marquer_non_justifiee(request, pk):
    """Marquer une absence comme non justifiée"""
    absence = get_object_or_404(
        Absence,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    absence.justifie = False
    absence.impact_paie = 'non_paye'
    absence.save()
    
    messages.warning(request, "Absence marquée comme non justifiée (retenue applicable)")
    return redirect('temps_travail:detail_absence', pk=pk)


@login_required
def prolonger_absence(request, pk):
    """Prolonger une absence - crée une nouvelle entrée"""
    absence_initiale = get_object_or_404(
        Absence,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        date_absence = request.POST.get('date_absence')
        duree_jours = request.POST.get('duree_jours', '1')
        observations = request.POST.get('observations', '')
        
        # Créer la prolongation comme nouvelle absence
        prolongation = Absence.objects.create(
            employe=absence_initiale.employe,
            type_absence=absence_initiale.type_absence,
            date_absence=date_absence,
            duree_jours=Decimal(duree_jours),
            impact_paie=absence_initiale.impact_paie,
            observations=f"Prolongation: {observations}",
        )
        
        messages.success(request, f"Prolongation créée: {prolongation.duree_jours} jour(s) supplémentaires")
        return redirect('temps_travail:detail_absence', pk=prolongation.pk)
    
    return render(request, 'temps_travail/absences/prolonger.html', {
        'absence': absence_initiale,
    })


@login_required
def supprimer_absence(request, pk):
    """Supprimer une absence"""
    absence = get_object_or_404(
        Absence,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    absence.delete()
    
    messages.success(request, "Absence supprimée")
    return redirect('temps_travail:liste_absences')


@login_required
def recap_absences(request):
    """Récapitulatif des absences par employé"""
    annee = request.GET.get('annee', date.today().year)
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    recap = []
    for employe in employes:
        absences = Absence.objects.filter(
            employe=employe,
            date_absence__year=int(annee)
        )
        
        totaux = absences.aggregate(
            total=Sum('duree_jours'),
            maladie=Sum('duree_jours', filter=Q(type_absence='maladie')),
            accident=Sum('duree_jours', filter=Q(type_absence='accident_travail')),
            injustifie=Sum('duree_jours', filter=Q(type_absence='absence_injustifiee')),
            autres=Sum('duree_jours', filter=Q(type_absence='permission')),
        )
        
        if totaux['total']:
            recap.append({
                'employe': employe,
                'total': totaux['total'] or 0,
                'maladie': totaux['maladie'] or 0,
                'accident': totaux['accident'] or 0,
                'injustifie': totaux['injustifie'] or 0,
                'autres': totaux['autres'] or 0,
            })
    
    # Trier par total décroissant
    recap.sort(key=lambda x: x['total'], reverse=True)
    
    # Statistiques globales
    stats_globales = Absence.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_absence__year=int(annee)
    ).aggregate(
        total_jours=Sum('duree_jours'),
        nb_absences=Count('id'),
        nb_employes=Count('employe', distinct=True),
    )
    
    return render(request, 'temps_travail/absences/recap.html', {
        'recap': recap,
        'stats': stats_globales,
        'annee': int(annee),
    })


@login_required
def calendrier_absences(request):
    """Vue calendrier des absences"""
    mois = int(request.GET.get('mois', date.today().month))
    annee = int(request.GET.get('annee', date.today().year))
    
    # Absences du mois
    absences = Absence.objects.filter(
        employe__entreprise=request.user.entreprise,
        date_absence__year=annee,
        date_absence__month=mois
    ).select_related('employe')
    
    # Préparer les données pour le calendrier
    events = []
    for absence in absences:
        events.append({
            'title': f"{absence.employe.nom} - {absence.get_type_absence_display()}",
            'start': absence.date_absence.isoformat(),
            'color': get_couleur_absence(absence.type_absence),
        })
    
    return render(request, 'temps_travail/absences/calendrier.html', {
        'events': events,
        'mois': mois,
        'annee': annee,
    })


def get_couleur_absence(type_absence):
    """Retourne la couleur selon le type d'absence"""
    couleurs = {
        'maladie': '#ffc107',
        'accident_travail': '#dc3545',
        'absence_injustifiee': '#343a40',
        'permission': '#17a2b8',
    }
    return couleurs.get(type_absence, '#6c757d')
