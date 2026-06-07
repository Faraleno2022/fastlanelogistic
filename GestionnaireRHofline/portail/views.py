"""
Portail Employé - Self-service.
Permet aux employés de consulter leurs bulletins, congés, et faire des demandes.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, Http404
from decimal import Decimal
from datetime import date

from employes.models import Employe
from paie.models import BulletinPaie, ElementSalaire
from paie.models_pret import Pret, EcheancePret
from temps_travail.models import Conge, SoldeConge, HeureSupplementaire


def get_employe_connecte(request):
    """Récupère l'employé connecté à partir de l'utilisateur"""
    if hasattr(request.user, 'employe'):
        return request.user.employe
    
    # Chercher par email professionnel ou personnel
    try:
        from django.db.models import Q
        return Employe.objects.get(
            Q(email_professionnel=request.user.email) | Q(email_personnel=request.user.email),
            entreprise=request.user.entreprise,
            statut_employe='actif'
        )
    except Employe.DoesNotExist:
        return None


@login_required
def portail_accueil(request):
    """Page d'accueil du portail employé"""
    employe = get_employe_connecte(request)
    
    if not employe:
        messages.warning(request, "Votre compte n'est pas lié à un profil employé.")
        return redirect('core:index')
    
    aujourd_hui = date.today()
    
    # Dernier bulletin
    dernier_bulletin = BulletinPaie.objects.filter(
        employe=employe,
        statut_bulletin__in=['valide', 'paye']
    ).order_by('-periode__annee', '-periode__mois').first()
    
    # Solde congés
    solde_conges = SoldeConge.objects.filter(
        employe=employe,
        annee=aujourd_hui.year
    ).first()
    
    # Congés en cours
    conge_en_cours = Conge.objects.filter(
        employe=employe,
        date_debut__lte=aujourd_hui,
        date_fin__gte=aujourd_hui,
        statut_demande='approuve'
    ).first()
    
    # Demandes en attente
    demandes_conges = Conge.objects.filter(
        employe=employe,
        statut_demande='en_attente'
    ).count()
    
    # Prêts en cours
    prets_en_cours = Pret.objects.filter(
        employe=employe,
        statut='en_cours'
    )
    solde_prets = prets_en_cours.aggregate(total=Sum('solde_restant'))['total'] or Decimal('0')
    
    # Heures sup du mois
    hs_mois = HeureSupplementaire.objects.filter(
        employe=employe,
        date_hs__year=aujourd_hui.year,
        date_hs__month=aujourd_hui.month,
        statut='valide'
    ).aggregate(
        heures=Sum('nombre_heures'),
        montant=Sum('montant_hs')
    )
    
    context = {
        'employe': employe,
        'dernier_bulletin': dernier_bulletin,
        'solde_conges': solde_conges,
        'conge_en_cours': conge_en_cours,
        'demandes_conges': demandes_conges,
        'prets_en_cours': prets_en_cours.count(),
        'solde_prets': solde_prets,
        'hs_heures': hs_mois['heures'] or Decimal('0'),
        'hs_montant': hs_mois['montant'] or Decimal('0'),
    }
    
    return render(request, 'portail/accueil.html', context)


@login_required
def mes_bulletins(request):
    """Liste des bulletins de paie de l'employé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    annee = request.GET.get('annee', date.today().year)
    
    bulletins = BulletinPaie.objects.filter(
        employe=employe,
        periode__annee=int(annee),
        statut_bulletin__in=['valide', 'paye']
    ).order_by('-periode__mois')
    
    # Années disponibles
    annees = BulletinPaie.objects.filter(
        employe=employe,
        statut_bulletin__in=['valide', 'paye']
    ).values_list('periode__annee', flat=True).distinct().order_by('-periode__annee')
    
    # Totaux annuels
    totaux = bulletins.aggregate(
        brut=Sum('salaire_brut'),
        net=Sum('net_a_payer'),
        cnss=Sum('cnss_employe'),
        rts=Sum('irg')
    )
    
    return render(request, 'portail/mes_bulletins.html', {
        'employe': employe,
        'bulletins': bulletins,
        'annee': int(annee),
        'annees': annees,
        'totaux': totaux,
    })


@login_required
def detail_bulletin(request, pk):
    """Détail d'un bulletin de paie"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    bulletin = get_object_or_404(
        BulletinPaie,
        pk=pk,
        employe=employe,
        statut_bulletin__in=['valide', 'paye']
    )
    
    return render(request, 'portail/detail_bulletin.html', {
        'employe': employe,
        'bulletin': bulletin,
    })


@login_required
def mes_conges(request):
    """Gestion des congés de l'employé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    aujourd_hui = date.today()
    
    # Solde congés
    solde = SoldeConge.objects.filter(
        employe=employe,
        annee=aujourd_hui.year
    ).first()
    
    # Historique des congés
    conges = Conge.objects.filter(
        employe=employe
    ).order_by('-date_demande')[:20]
    
    return render(request, 'portail/mes_conges.html', {
        'employe': employe,
        'solde': solde,
        'conges': conges,
    })


@login_required
def demander_conge(request):
    """Formulaire de demande de congé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    if request.method == 'POST':
        type_conge = request.POST.get('type_conge', 'conge_paye')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        motif = request.POST.get('motif', '')
        
        try:
            from datetime import datetime
            d_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            d_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            
            if d_fin < d_debut:
                messages.error(request, "La date de fin doit être après la date de début")
                return redirect('portail:demander_conge')
            
            # Calculer le nombre de jours (hors weekends)
            nb_jours = 0
            current = d_debut
            while current <= d_fin:
                if current.weekday() < 5:  # Lundi à vendredi
                    nb_jours += 1
                current += timedelta(days=1)
            
            conge = Conge.objects.create(
                employe=employe,
                type_conge=type_conge,
                date_debut=d_debut,
                date_fin=d_fin,
                nombre_jours=nb_jours,
                motif=motif,
                statut_demande='en_attente',
            )
            
            messages.success(request, f'Demande de congé soumise: {nb_jours} jour(s) du {date_debut} au {date_fin}')
            return redirect('portail:mes_conges')
            
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    # Types de congés disponibles
    types_conges = [
        ('conge_paye', 'Congé payé'),
        ('conge_maladie', 'Congé maladie'),
        ('conge_maternite', 'Congé maternité'),
        ('conge_paternite', 'Congé paternité'),
        ('conge_sans_solde', 'Congé sans solde'),
        ('evenement_familial', 'Événement familial'),
    ]
    
    return render(request, 'portail/demander_conge.html', {
        'employe': employe,
        'types_conges': types_conges,
    })


@login_required
def annuler_conge(request, pk):
    """Annuler une demande de congé en attente"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    conge = get_object_or_404(Conge, pk=pk, employe=employe, statut_demande='en_attente')
    conge.statut_demande = 'annule'
    conge.save()
    
    messages.success(request, "Demande de congé annulée")
    return redirect('portail:mes_conges')


@login_required
def mes_prets(request):
    """Liste des prêts de l'employé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    prets = Pret.objects.filter(employe=employe).order_by('-date_demande')
    
    # Totaux
    en_cours = prets.filter(statut='en_cours')
    solde_total = en_cours.aggregate(total=Sum('solde_restant'))['total'] or Decimal('0')
    
    return render(request, 'portail/mes_prets.html', {
        'employe': employe,
        'prets': prets,
        'solde_total': solde_total,
    })


@login_required
def detail_pret(request, pk):
    """Détail d'un prêt avec échéancier"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    pret = get_object_or_404(Pret, pk=pk, employe=employe)
    echeances = pret.echeances.all().order_by('numero_echeance')
    
    return render(request, 'portail/detail_pret.html', {
        'employe': employe,
        'pret': pret,
        'echeances': echeances,
    })


@login_required
def demander_pret(request):
    """Formulaire de demande de prêt"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    if request.method == 'POST':
        type_pret = request.POST.get('type_pret')
        montant = request.POST.get('montant', '0')
        nombre_echeances = request.POST.get('nombre_echeances', '1')
        motif = request.POST.get('motif', '')
        
        try:
            montant = Decimal(montant.replace(' ', '').replace(',', '.'))
            nombre_echeances = int(nombre_echeances)
            
            # Date de début: mois suivant
            from dateutil.relativedelta import relativedelta
            date_debut = date.today().replace(day=1) + relativedelta(months=1)
            
            pret = Pret(
                employe=employe,
                type_pret=type_pret,
                montant_pret=montant,
                nombre_echeances=nombre_echeances,
                date_debut_remboursement=date_debut,
                motif=motif,
            )
            pret.save()
            
            messages.success(request, f'Demande de prêt soumise: {montant:,.0f} GNF en {nombre_echeances} échéances')
            return redirect('portail:mes_prets')
            
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return render(request, 'portail/demander_pret.html', {
        'employe': employe,
        'types_pret': Pret.TYPES_PRET,
    })


@login_required
def mes_heures_sup(request):
    """Liste des heures supplémentaires de l'employé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    annee = request.GET.get('annee', date.today().year)
    
    heures = HeureSupplementaire.objects.filter(
        employe=employe,
        date_hs__year=int(annee)
    ).order_by('-date_hs')
    
    # Totaux
    totaux = heures.filter(statut='valide').aggregate(
        heures=Sum('nombre_heures'),
        montant=Sum('montant_hs')
    )
    
    return render(request, 'portail/mes_heures_sup.html', {
        'employe': employe,
        'heures': heures,
        'annee': int(annee),
        'totaux': totaux,
    })


@login_required
def mon_profil(request):
    """Profil de l'employé"""
    employe = get_employe_connecte(request)
    if not employe:
        return redirect('core:index')
    
    # Éléments de salaire
    elements = ElementSalaire.objects.filter(
        employe=employe,
        actif=True
    ).select_related('rubrique')
    
    return render(request, 'portail/mon_profil.html', {
        'employe': employe,
        'elements': elements,
    })


# Import manquant
from datetime import timedelta
