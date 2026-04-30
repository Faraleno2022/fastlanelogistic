"""

Vues pour la gestion des missions et déplacements.

"""

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from core.decorators import reauth_required

from django.contrib import messages

from django.db.models import Sum, Count, Q

from django.utils import timezone

from datetime import date

from decimal import Decimal



from .models import Employe

from .models_mission import Mission, FraisMission, BaremeIndemnite





@reauth_required
@login_required

def liste_missions(request):

    """Liste des missions"""

    missions = Mission.objects.filter(

        employe__entreprise=request.user.entreprise

    ).select_related('employe', 'employe__service', 'validee_par')

    

    # Filtres

    employe_id = request.GET.get('employe')

    statut = request.GET.get('statut')

    type_mission = request.GET.get('type')

    annee = request.GET.get('annee', date.today().year)

    

    if employe_id:

        missions = missions.filter(employe_id=employe_id)

    if statut:

        missions = missions.filter(statut=statut)

    if type_mission:

        missions = missions.filter(type_mission=type_mission)

    if annee:

        missions = missions.filter(date_debut__year=int(annee))

    

    # Statistiques

    stats = missions.aggregate(

        nb_planifiees=Count('id', filter=Q(statut='planifiee')),

        nb_en_cours=Count('id', filter=Q(statut='en_cours')),

        nb_terminees=Count('id', filter=Q(statut='terminee')),

        total_budget=Sum('budget_previsionnel'),

        total_depenses=Sum('depenses_reelles'),

    )

    

    employes = Employe.objects.filter(

        entreprise=request.user.entreprise,

    ).order_by('nom', 'prenoms')

    

    return render(request, 'employes/missions/liste.html', {

        'missions': missions[:100],

        'stats': stats,

        'employes': employes,

        'types_mission': Mission.TYPES,

        'statuts': Mission.STATUTS,

        'annee': int(annee),

        'filtre_employe': employe_id,

        'filtre_statut': statut,

        'filtre_type': type_mission,

    })





@reauth_required
@login_required

def creer_mission(request):

    """Créer une nouvelle mission"""

    if request.method == 'POST':

        employe_id = request.POST.get('employe')

        type_mission = request.POST.get('type_mission')

        objet = request.POST.get('objet')

        description = request.POST.get('description', '')

        lieu_depart = request.POST.get('lieu_depart', 'Conakry')

        destination = request.POST.get('destination')

        pays = request.POST.get('pays', 'Guinée')

        date_debut = request.POST.get('date_debut')

        date_fin = request.POST.get('date_fin')

        moyen_transport = request.POST.get('moyen_transport')

        avec_hebergement = request.POST.get('avec_hebergement') == 'on'

        hotel = request.POST.get('hotel', '')

        budget_previsionnel = request.POST.get('budget_previsionnel', '0')

        indemnite_journaliere = request.POST.get('indemnite_journaliere', '0')

        

        employe = get_object_or_404(

            Employe,

            pk=employe_id,

            entreprise=request.user.entreprise

        )

        

        mission = Mission.objects.create(

            employe=employe,

            type_mission=type_mission,

            objet=objet,

            description=description,

            lieu_depart=lieu_depart,

            destination=destination,

            pays=pays,

            date_debut=date_debut,

            date_fin=date_fin,

            moyen_transport=moyen_transport,

            avec_hebergement=avec_hebergement,

            hotel=hotel,

            budget_previsionnel=Decimal(budget_previsionnel) if budget_previsionnel else 0,

            indemnite_journaliere=Decimal(indemnite_journaliere) if indemnite_journaliere else 0,

            statut='planifiee',

        )

        

        messages.success(request, f"Mission {mission.reference} créée")

        return redirect('employes:detail_mission', pk=mission.pk)

    

    employes = Employe.objects.filter(

        entreprise=request.user.entreprise,

    ).order_by('nom', 'prenoms')

    

    # Barèmes pour suggestion

    baremes = BaremeIndemnite.objects.filter(actif=True)

    

    return render(request, 'employes/missions/creer.html', {

        'employes': employes,

        'types_mission': Mission.TYPES,

        'moyens_transport': Mission.MOYENS_TRANSPORT,

        'baremes': baremes,

    })





@reauth_required
@login_required

def detail_mission(request, pk):

    """Détail d'une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    frais = mission.frais.all()

    total_frais = frais.aggregate(total=Sum('montant'))['total'] or 0

    

    return render(request, 'employes/missions/detail.html', {

        'mission': mission,

        'frais': frais,

        'total_frais': total_frais,

    })





@reauth_required
@login_required

def modifier_mission(request, pk):

    """Modifier une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if mission.statut not in ['planifiee']:

        messages.error(request, "Cette mission ne peut plus être modifiée")

        return redirect('employes:detail_mission', pk=pk)

    

    if request.method == 'POST':

        mission.objet = request.POST.get('objet')

        mission.description = request.POST.get('description', '')

        mission.destination = request.POST.get('destination')

        mission.pays = request.POST.get('pays', 'Guinée')

        mission.date_debut = request.POST.get('date_debut')

        mission.date_fin = request.POST.get('date_fin')

        mission.moyen_transport = request.POST.get('moyen_transport')

        mission.avec_hebergement = request.POST.get('avec_hebergement') == 'on'

        mission.hotel = request.POST.get('hotel', '')

        

        budget = request.POST.get('budget_previsionnel', '0')

        indemnite = request.POST.get('indemnite_journaliere', '0')

        mission.budget_previsionnel = Decimal(budget) if budget else 0

        mission.indemnite_journaliere = Decimal(indemnite) if indemnite else 0

        

        mission.save()

        

        messages.success(request, "Mission mise à jour")

        return redirect('employes:detail_mission', pk=pk)

    

    return render(request, 'employes/missions/modifier.html', {

        'mission': mission,

        'types_mission': Mission.TYPES,

        'moyens_transport': Mission.MOYENS_TRANSPORT,

    })





@reauth_required
@login_required

def demarrer_mission(request, pk):

    """Démarrer une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if mission.statut != 'planifiee':

        messages.error(request, "Cette mission ne peut pas être démarrée")

        return redirect('employes:detail_mission', pk=pk)

    

    mission.statut = 'en_cours'

    mission.save()

    

    messages.success(request, f"Mission {mission.reference} démarrée")

    return redirect('employes:detail_mission', pk=pk)





@reauth_required
@login_required

def terminer_mission(request, pk):

    """Terminer une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if mission.statut != 'en_cours':

        messages.error(request, "Cette mission n'est pas en cours")

        return redirect('employes:detail_mission', pk=pk)

    

    if request.method == 'POST':

        mission.rapport_mission = request.POST.get('rapport_mission', '')

        mission.objectifs_atteints = request.POST.get('objectifs_atteints') == 'on'

        mission.statut = 'terminee'

        

        # Calculer les dépenses réelles

        total_frais = mission.frais.aggregate(total=Sum('montant'))['total'] or 0

        mission.depenses_reelles = total_frais + mission.total_indemnites

        

        mission.save()

        

        messages.success(request, f"Mission {mission.reference} terminée")

        return redirect('employes:detail_mission', pk=pk)

    

    return render(request, 'employes/missions/terminer.html', {

        'mission': mission,

    })





@reauth_required
@login_required

def annuler_mission(request, pk):

    """Annuler une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if mission.statut not in ['planifiee', 'en_cours']:

        messages.error(request, "Cette mission ne peut pas être annulée")

        return redirect('employes:detail_mission', pk=pk)

    

    mission.statut = 'annulee'

    mission.save()

    

    messages.warning(request, f"Mission {mission.reference} annulée")

    return redirect('employes:liste_missions')





@reauth_required
@login_required

def supprimer_mission(request, pk):

    """Supprimer une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if request.method == 'POST':

        reference = mission.reference

        mission.delete()

        messages.success(request, f"Mission {reference} supprimée avec succès.")

        return redirect('employes:liste_missions')

    

    return redirect('employes:detail_mission', pk=pk)





@reauth_required
@login_required

def ajouter_frais_mission(request, pk):

    """Ajouter des frais à une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if mission.statut not in ['planifiee', 'en_cours']:

        messages.error(request, "Impossible d'ajouter des frais à cette mission")

        return redirect('employes:detail_mission', pk=pk)

    

    if request.method == 'POST':

        type_frais = request.POST.get('type_frais')

        date_depense = request.POST.get('date_depense')

        description = request.POST.get('description')

        montant = request.POST.get('montant')

        justificatif = request.FILES.get('justificatif')

        

        FraisMission.objects.create(

            mission=mission,

            type_frais=type_frais,

            date_depense=date_depense,

            description=description,

            montant=Decimal(montant),

            justificatif=justificatif,

        )

        

        messages.success(request, "Frais ajouté")

    

    return redirect('employes:detail_mission', pk=pk)





@reauth_required
@login_required

def supprimer_frais_mission(request, pk, frais_pk):

    """Supprimer un frais de mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    frais = get_object_or_404(FraisMission, pk=frais_pk, mission=mission)

    frais.delete()

    

    messages.success(request, "Frais supprimé")

    return redirect('employes:detail_mission', pk=pk)





@reauth_required
@login_required

def accorder_avance(request, pk):

    """Accorder une avance pour une mission"""

    mission = get_object_or_404(

        Mission,

        pk=pk,

        employe__entreprise=request.user.entreprise

    )

    

    if request.method == 'POST':

        montant = request.POST.get('montant_avance', '0')

        mission.avance_accordee = Decimal(montant)

        mission.save()

        

        messages.success(request, f"Avance de {montant} GNF accordée")

    

    return redirect('employes:detail_mission', pk=pk)





@reauth_required
@login_required

def recap_missions(request):

    """Récapitulatif des missions"""

    annee = int(request.GET.get('annee', date.today().year))

    

    # Par employé

    recap_employes = Mission.objects.filter(

        employe__entreprise=request.user.entreprise,

        date_debut__year=annee,

        statut__in=['terminee']

    ).values(

        'employe__nom', 'employe__prenoms', 'employe__matricule'

    ).annotate(

        nb_missions=Count('id'),

        total_depenses=Sum('depenses_reelles'),

        total_avances=Sum('avance_accordee'),

    ).order_by('-nb_missions')

    

    # Par destination

    recap_destinations = Mission.objects.filter(

        employe__entreprise=request.user.entreprise,

        date_debut__year=annee,

        statut__in=['terminee']

    ).values('destination').annotate(

        nb_missions=Count('id'),

        total_depenses=Sum('depenses_reelles'),

    ).order_by('-nb_missions')[:10]

    

    # Totaux

    totaux = Mission.objects.filter(

        employe__entreprise=request.user.entreprise,

        date_debut__year=annee,

        statut__in=['terminee']

    ).aggregate(

        nb_missions=Count('id'),

        total_budget=Sum('budget_previsionnel'),

        total_depenses=Sum('depenses_reelles'),

        total_avances=Sum('avance_accordee'),

    )

    

    return render(request, 'employes/missions/recap.html', {

        'recap_employes': recap_employes,

        'recap_destinations': recap_destinations,

        'totaux': totaux,

        'annee': annee,

    })





@reauth_required
@login_required

def gestion_baremes_indemnites(request):

    """Gestion des barèmes d'indemnités"""

    baremes = BaremeIndemnite.objects.all()

    

    if request.method == 'POST':

        action = request.POST.get('action')

        

        if action == 'creer':

            zone = request.POST.get('zone')

            categorie = request.POST.get('categorie_employe', '')

            indemnite = request.POST.get('indemnite_journaliere')

            plafond_hebergement = request.POST.get('plafond_hebergement')

            plafond_restauration = request.POST.get('plafond_restauration')

            date_debut = request.POST.get('date_debut')

            

            BaremeIndemnite.objects.create(

                zone=zone,

                categorie_employe=categorie,

                indemnite_journaliere=Decimal(indemnite),

                plafond_hebergement=Decimal(plafond_hebergement) if plafond_hebergement else None,

                plafond_restauration=Decimal(plafond_restauration) if plafond_restauration else None,

                date_debut=date_debut,

            )

            messages.success(request, "Barème créé")

        

        elif action == 'supprimer':

            bareme_id = request.POST.get('bareme_id')

            bareme = get_object_or_404(BaremeIndemnite, pk=bareme_id)

            bareme.delete()

            messages.success(request, "Barème supprimé")

        

        return redirect('employes:gestion_baremes_indemnites')

    

    return render(request, 'employes/missions/baremes.html', {

        'baremes': baremes,

        'zones': BaremeIndemnite.ZONES,

        'categories': [

            ('direction', 'Direction'),

            ('cadre_superieur', 'Cadre supérieur'),

            ('cadre', 'Cadre'),

            ('agent_maitrise', 'Agent de maîtrise'),

            ('employe', 'Employé'),

        ],

    })

