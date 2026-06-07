"""
Vues pour la gestion des prêts employés.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models_pret import Pret, EcheancePret
from employes.models import Employe
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def liste_prets(request):
    """Liste des prêts"""
    entreprise = request.user.entreprise
    
    # Filtres
    statut = request.GET.get('statut', '')
    employe_id = request.GET.get('employe', '')
    type_pret = request.GET.get('type', '')
    
    # Base query
    prets = Pret.objects.filter(
        employe__entreprise=entreprise
    ).select_related('employe')
    
    # Appliquer les filtres
    if statut:
        prets = prets.filter(statut=statut)
    if employe_id:
        prets = prets.filter(employe_id=employe_id)
    if type_pret:
        prets = prets.filter(type_pret=type_pret)
    
    prets = prets.order_by('-date_demande')
    
    # Statistiques
    stats = {
        'total_prets': prets.count(),
        'montant_total': prets.aggregate(total=Sum('montant_pret'))['total'] or Decimal('0'),
        'en_cours': prets.filter(statut='en_cours').count(),
        'solde_restant': prets.filter(statut='en_cours').aggregate(total=Sum('solde_restant'))['total'] or Decimal('0'),
    }
    
    # Listes pour les filtres
    employes = Employe.objects.filter(
        entreprise=entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'paie/prets/liste.html', {
        'prets': prets,
        'stats': stats,
        'employes': employes,
        'statut_selectionne': statut,
        'employe_selectionne': int(employe_id) if employe_id else None,
        'type_selectionne': type_pret,
        'types_pret': Pret.TYPES_PRET,
        'statuts': Pret.STATUTS,
    })


@login_required
@entreprise_active_required
def creer_pret(request):
    """Créer un nouveau prêt"""
    entreprise = request.user.entreprise
    
    employes = Employe.objects.filter(
        entreprise=entreprise,
    ).order_by('nom', 'prenoms')
    
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        type_pret = request.POST.get('type_pret')
        montant = request.POST.get('montant', '0')
        taux_interet = request.POST.get('taux_interet', '0')
        nombre_echeances = request.POST.get('nombre_echeances', '1')
        date_debut = request.POST.get('date_debut')
        motif = request.POST.get('motif', '')
        
        try:
            employe = Employe.objects.get(pk=employe_id, entreprise=entreprise)
            montant = Decimal(montant.replace(' ', '').replace(',', '.'))
            taux_interet = Decimal(taux_interet.replace(',', '.') or '0')
            nombre_echeances = int(nombre_echeances)
            
            # Créer le prêt
            pret = Pret(
                employe=employe,
                type_pret=type_pret,
                montant_pret=montant,
                taux_interet=taux_interet,
                nombre_echeances=nombre_echeances,
                date_debut_remboursement=date_debut,
                motif=motif,
            )
            pret.save()
            
            messages.success(request, f'Prêt {pret.numero_pret} créé: {montant:,.0f} GNF en {nombre_echeances} échéances de {pret.montant_echeance:,.0f} GNF')
            return redirect('paie:detail_pret', pk=pret.pk)
            
        except Employe.DoesNotExist:
            messages.error(request, "Employé non trouvé")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'paie/prets/creer.html', {
        'employes': employes,
        'types_pret': Pret.TYPES_PRET,
    })


@login_required
@entreprise_active_required
def detail_pret(request, pk):
    """Détail d'un prêt avec échéancier"""
    pret = get_object_or_404(Pret, pk=pk, employe__entreprise=request.user.entreprise)
    
    # Générer l'échéancier si nécessaire
    if pret.echeances.count() == 0 and pret.statut in ['approuve', 'en_cours']:
        pret.generer_echeancier()
    
    echeances = pret.echeances.all().order_by('numero_echeance')
    
    # Mettre à jour les échéances en retard
    for ech in echeances:
        ech.est_en_retard()
    
    return render(request, 'paie/prets/detail.html', {
        'pret': pret,
        'echeances': echeances,
    })


@login_required
@entreprise_active_required
def approuver_pret(request, pk):
    """Approuver un prêt"""
    pret = get_object_or_404(Pret, pk=pk, employe__entreprise=request.user.entreprise)
    
    if pret.statut == 'en_attente':
        pret.statut = 'approuve'
        pret.date_approbation = date.today()
        if hasattr(request.user, 'employe'):
            pret.approbateur = request.user.employe
        pret.save()
        
        # Générer l'échéancier
        pret.generer_echeancier()
        
        # Passer en cours si date de début atteinte
        if pret.date_debut_remboursement <= date.today():
            pret.statut = 'en_cours'
            pret.save()
        
        messages.success(request, f'Prêt {pret.numero_pret} approuvé')
    
    return redirect('paie:detail_pret', pk=pk)


@login_required
@entreprise_active_required
def rejeter_pret(request, pk):
    """Rejeter un prêt"""
    pret = get_object_or_404(Pret, pk=pk, employe__entreprise=request.user.entreprise)
    
    if pret.statut == 'en_attente':
        pret.statut = 'annule'
        pret.save()
        messages.warning(request, f'Prêt {pret.numero_pret} rejeté')
    
    return redirect('paie:liste_prets')


@login_required
@entreprise_active_required
def enregistrer_remboursement(request, pk):
    """Enregistrer un remboursement manuel"""
    pret = get_object_or_404(Pret, pk=pk, employe__entreprise=request.user.entreprise)
    
    if request.method == 'POST' and pret.statut == 'en_cours':
        montant = request.POST.get('montant', '0')
        try:
            montant = Decimal(montant.replace(' ', '').replace(',', '.'))
            if pret.enregistrer_remboursement(montant):
                messages.success(request, f'Remboursement de {montant:,.0f} GNF enregistré')
            else:
                messages.warning(request, "Aucune échéance à payer")
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return redirect('paie:detail_pret', pk=pk)


@login_required
@entreprise_active_required
def prets_a_prelever(request):
    """Liste des prêts à prélever pour le mois en cours"""
    entreprise = request.user.entreprise
    annee = request.GET.get('annee', date.today().year)
    mois = request.GET.get('mois', date.today().month)
    
    # Échéances du mois
    echeances = EcheancePret.objects.filter(
        pret__employe__entreprise=entreprise,
        pret__statut='en_cours',
        date_echeance__year=int(annee),
        date_echeance__month=int(mois),
        statut__in=['en_attente', 'en_retard']
    ).select_related('pret', 'pret__employe').order_by('pret__employe__nom', 'date_echeance')
    
    # Totaux
    totaux = echeances.aggregate(
        total_montant=Sum('montant_echeance'),
        nb_echeances=Sum('pret_id')  # Juste pour avoir un count
    )
    totaux['nb_echeances'] = echeances.count()
    
    return render(request, 'paie/prets/a_prelever.html', {
        'echeances': echeances,
        'totaux': totaux,
        'annee': int(annee),
        'mois': int(mois),
    })
