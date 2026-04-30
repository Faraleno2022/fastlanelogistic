"""
Vues pour la gestion des heures supplémentaires.
Conforme au Code du Travail guinéen.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models import HeureSupplementaire
from employes.models import Employe
from paie.models import ElementSalaire
from core.decorators import entreprise_active_required


def calculer_taux_horaire(employe):
    """Calcule le taux horaire de base d'un employé"""
    # Récupérer le salaire de base
    element_base = ElementSalaire.objects.filter(
        employe=employe,
        rubrique__code_rubrique='SALAIRE_BASE',
        actif=True
    ).first()
    
    if element_base and element_base.montant:
        # Taux horaire = Salaire mensuel / 173.33 heures (40h x 52 / 12)
        return (element_base.montant / Decimal('173.33')).quantize(Decimal('1'))
    
    return Decimal('0')


@login_required
@entreprise_active_required
def liste_heures_supplementaires(request):
    """Liste des heures supplémentaires"""
    entreprise = request.user.entreprise
    
    # Filtres
    annee = request.GET.get('annee', date.today().year)
    mois = request.GET.get('mois', date.today().month)
    employe_id = request.GET.get('employe', '')
    statut = request.GET.get('statut', '')
    
    # Base query
    hs_list = HeureSupplementaire.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe')
    
    # Appliquer les filtres
    if annee:
        hs_list = hs_list.filter(date_hs__year=int(annee))
    if mois:
        hs_list = hs_list.filter(date_hs__month=int(mois))
    if employe_id:
        hs_list = hs_list.filter(employe_id=employe_id)
    if statut:
        hs_list = hs_list.filter(statut=statut)
    
    hs_list = hs_list.order_by('-date_hs', 'employe__nom')
    
    # Statistiques
    stats = hs_list.aggregate(
        total_heures=Sum('nombre_heures'),
        total_montant=Sum('montant_hs'),
    )
    stats['total_heures'] = stats['total_heures'] or Decimal('0')
    stats['total_montant'] = stats['total_montant'] or Decimal('0')
    stats['nb_hs'] = hs_list.count()
    
    # Listes pour les filtres
    employes = Employe.objects.filter(
        entreprise=entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'temps_travail/heures_supplementaires/liste.html', {
        'hs_list': hs_list,
        'stats': stats,
        'employes': employes,
        'annee': int(annee) if annee else date.today().year,
        'mois': int(mois) if mois else date.today().month,
        'employe_selectionne': int(employe_id) if employe_id else None,
        'statut_selectionne': statut,
        'types_hs': HeureSupplementaire.TYPES_HS,
        'statuts': HeureSupplementaire.STATUTS,
    })


@login_required
@entreprise_active_required
def ajouter_heure_supplementaire(request):
    """Ajouter des heures supplémentaires"""
    entreprise = request.user.entreprise
    
    employes = Employe.objects.filter(
        entreprise=entreprise,
    ).order_by('nom', 'prenoms')
    
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        date_hs = request.POST.get('date_hs')
        type_hs = request.POST.get('type_hs')
        nombre_heures = request.POST.get('nombre_heures')
        motif = request.POST.get('motif', '')
        
        try:
            employe = Employe.objects.get(pk=employe_id, entreprise=entreprise)
            nombre_heures = Decimal(nombre_heures.replace(',', '.'))
            
            # Calculer le taux horaire
            taux_horaire = calculer_taux_horaire(employe)
            if taux_horaire == 0:
                messages.warning(request, f"Taux horaire non défini pour {employe.nom}. Veuillez définir le salaire de base.")
            
            # Récupérer le taux de majoration
            taux_majoration = HeureSupplementaire.get_taux_majoration(type_hs)
            
            # Créer l'enregistrement
            hs = HeureSupplementaire(
                employe=employe,
                date_hs=date_hs,
                type_hs=type_hs,
                nombre_heures=nombre_heures,
                taux_majoration=taux_majoration,
                taux_horaire_base=taux_horaire,
                montant_hs=Decimal('0'),
                motif=motif,
            )
            hs.calculer_montant()
            hs.save()
            
            messages.success(request, f'Heures supplémentaires ajoutées: {nombre_heures}h pour {employe.nom} = {hs.montant_hs:,.0f} GNF')
            return redirect('temps_travail:liste_heures_supplementaires')
            
        except Employe.DoesNotExist:
            messages.error(request, "Employé non trouvé")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'temps_travail/heures_supplementaires/ajouter.html', {
        'employes': employes,
        'types_hs': HeureSupplementaire.TYPES_HS,
    })


@login_required
@entreprise_active_required
def valider_heure_supplementaire(request, pk):
    """Valider une heure supplémentaire"""
    hs = get_object_or_404(HeureSupplementaire, pk=pk, employe__entreprise=request.user.entreprise)
    
    if hs.statut == 'en_attente':
        hs.statut = 'valide'
        hs.valideur = request.user.employe if hasattr(request.user, 'employe') else None
        hs.date_validation = timezone.now()
        hs.save()
        messages.success(request, f'Heures supplémentaires validées pour {hs.employe.nom}')
    
    return redirect('temps_travail:liste_heures_supplementaires')


@login_required
@entreprise_active_required
def rejeter_heure_supplementaire(request, pk):
    """Rejeter une heure supplémentaire"""
    hs = get_object_or_404(HeureSupplementaire, pk=pk, employe__entreprise=request.user.entreprise)
    
    if hs.statut == 'en_attente':
        hs.statut = 'rejete'
        hs.save()
        messages.warning(request, f'Heures supplémentaires rejetées pour {hs.employe.nom}')
    
    return redirect('temps_travail:liste_heures_supplementaires')


@login_required
@entreprise_active_required
def supprimer_heure_supplementaire(request, pk):
    """Supprimer une heure supplémentaire"""
    hs = get_object_or_404(HeureSupplementaire, pk=pk, employe__entreprise=request.user.entreprise)
    
    if hs.statut not in ['paye']:
        employe_nom = hs.employe.nom
        hs.delete()
        messages.success(request, f'Heures supplémentaires supprimées pour {employe_nom}')
    else:
        messages.error(request, "Impossible de supprimer des heures déjà payées")
    
    return redirect('temps_travail:liste_heures_supplementaires')


@login_required
@entreprise_active_required
def recap_heures_supplementaires(request):
    """Récapitulatif des heures supplémentaires par employé"""
    entreprise = request.user.entreprise
    annee = request.GET.get('annee', date.today().year)
    mois = request.GET.get('mois', date.today().month)
    
    # Récapitulatif par employé
    recap = HeureSupplementaire.objects.filter(
        employe__entreprise=entreprise,
        date_hs__year=int(annee),
        date_hs__month=int(mois),
        statut='valide'
    ).values(
        'employe__matricule',
        'employe__nom',
        'employe__prenoms',
        'employe_id'
    ).annotate(
        total_heures=Sum('nombre_heures'),
        total_montant=Sum('montant_hs')
    ).order_by('employe__nom')
    
    # Détail par type
    detail_types = HeureSupplementaire.objects.filter(
        employe__entreprise=entreprise,
        date_hs__year=int(annee),
        date_hs__month=int(mois),
        statut='valide'
    ).values('type_hs').annotate(
        total_heures=Sum('nombre_heures'),
        total_montant=Sum('montant_hs')
    )
    
    # Totaux
    totaux = HeureSupplementaire.objects.filter(
        employe__entreprise=entreprise,
        date_hs__year=int(annee),
        date_hs__month=int(mois),
        statut='valide'
    ).aggregate(
        total_heures=Sum('nombre_heures'),
        total_montant=Sum('montant_hs')
    )
    
    return render(request, 'temps_travail/heures_supplementaires/recap.html', {
        'recap': recap,
        'detail_types': detail_types,
        'totaux': totaux,
        'annee': int(annee),
        'mois': int(mois),
        'types_hs': dict(HeureSupplementaire.TYPES_HS),
    })
