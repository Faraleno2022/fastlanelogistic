"""
Vues pour la gestion des expatriés (visas, permis de travail)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta

from core.models import Expatrie, PermisVisa
from core.views import log_activity


@login_required
def expatries_liste(request):
    """Liste des expatriés de l'entreprise"""
    expatries = Expatrie.objects.filter(
        employe__entreprise=request.user.entreprise
    ).select_related('employe')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        expatries = expatries.filter(statut=statut)
    
    nationalite = request.GET.get('nationalite')
    if nationalite:
        expatries = expatries.filter(nationalite__icontains=nationalite)
    
    # Alertes (documents expirant dans 60 jours)
    date_alerte = date.today() + timedelta(days=60)
    
    alertes = []
    for exp in expatries:
        permis = exp.permis_visas.filter(
            date_expiration__lte=date_alerte,
            date_expiration__gte=date.today()
        )
        for p in permis:
            jours_restants = (p.date_expiration - date.today()).days
            alertes.append({
                'expatrie': exp,
                'document': p,
                'jours_restants': jours_restants,
                'urgence': 'danger' if jours_restants <= 30 else 'warning'
            })
    
    alertes.sort(key=lambda x: x['jours_restants'])
    
    return render(request, 'core/expatries/liste.html', {
        'expatries': expatries,
        'alertes': alertes[:10],
        'total_alertes': len(alertes),
    })


@login_required
def expatrie_detail(request, pk):
    """Détail d'un expatrié"""
    expatrie = get_object_or_404(
        Expatrie,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    permis_visas = expatrie.permis_visas.all().order_by('-date_expiration')
    
    # Vérifier les expirations
    date_alerte = date.today() + timedelta(days=60)
    
    return render(request, 'core/expatries/detail.html', {
        'expatrie': expatrie,
        'permis_visas': permis_visas,
        'date_alerte': date_alerte,
    })


@login_required
def expatrie_ajouter(request):
    """Ajouter un expatrié"""
    from employes.models import Employe
    
    if request.method == 'POST':
        employe_id = request.POST.get('employe')
        employe = get_object_or_404(
            Employe, 
            pk=employe_id, 
            entreprise=request.user.entreprise
        )
        
        expatrie = Expatrie.objects.create(
            employe=employe,
            type_contrat_expat=request.POST.get('type_contrat_expat', 'expatriation'),
            pays_origine=request.POST.get('pays_origine', ''),
            nationalite=request.POST.get('nationalite', ''),
            date_arrivee=request.POST.get('date_arrivee') or None,
            motif_expatriation=request.POST.get('motif_expatriation', ''),
            duree_prevue_mois=int(request.POST.get('duree_prevue_mois', 0)) or None,
            statut=request.POST.get('statut', 'actif'),
            contact_urgence_pays=request.POST.get('contact_urgence_pays', ''),
            date_debut_mission=request.POST.get('date_debut_mission') or timezone.now().date(),
            date_fin_mission_prevue=request.POST.get('date_fin_mission_prevue') or None,
            observations=request.POST.get('observations', ''),
        )
        
        log_activity(
            request,
            f"Ajout expatrié {employe.nom_complet}",
            'core',
            'expatries',
            expatrie.id
        )
        
        messages.success(request, f'{employe.nom_complet} ajouté comme expatrié')
        return redirect('core:expatrie_detail', pk=expatrie.id)
    
    # Employés non encore expatriés
    employes_ids = Expatrie.objects.filter(
        employe__entreprise=request.user.entreprise
    ).values_list('employe_id', flat=True)
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise
    ).exclude(id__in=employes_ids)
    
    return render(request, 'core/expatries/form.html', {
        'employes': employes,
    })


@login_required
def expatrie_modifier(request, pk):
    """Modifier un expatrié"""
    expatrie = get_object_or_404(
        Expatrie,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        expatrie.type_contrat_expat = request.POST.get('type_contrat_expat', expatrie.type_contrat_expat)
        expatrie.nationalite = request.POST.get('nationalite', '')
        expatrie.pays_origine = request.POST.get('pays_origine', '')
        expatrie.date_arrivee = request.POST.get('date_arrivee') or None
        expatrie.motif_expatriation = request.POST.get('motif_expatriation', '')
        expatrie.duree_prevue_mois = int(request.POST.get('duree_prevue_mois', 0)) or None
        expatrie.statut = request.POST.get('statut', 'actif')
        expatrie.contact_urgence_pays = request.POST.get('contact_urgence_pays', '')
        expatrie.date_debut_mission = request.POST.get('date_debut_mission') or expatrie.date_debut_mission
        expatrie.date_fin_mission_prevue = request.POST.get('date_fin_mission_prevue') or None
        expatrie.observations = request.POST.get('observations', '')
        expatrie.save()
        
        log_activity(request, f"Modification expatrié {expatrie.employe.nom_complet}", 'core')
        messages.success(request, 'Expatrié modifié')
        return redirect('core:expatrie_detail', pk=pk)
    
    return render(request, 'core/expatries/form.html', {
        'expatrie': expatrie,
        'modification': True,
    })


@login_required
def expatrie_supprimer(request, pk):
    """Supprimer un expatrié"""
    expatrie = get_object_or_404(
        Expatrie,
        pk=pk,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        nom_complet = expatrie.employe.nom_complet
        expatrie.delete()
        
        log_activity(request, f"Suppression expatrié {nom_complet}", 'core')
        messages.success(request, f'Expatrié {nom_complet} supprimé avec succès')
        return redirect('core:expatries_liste')
    
    return render(request, 'core/expatries/confirmer_suppression.html', {
        'expatrie': expatrie,
    })


@login_required
def permis_ajouter(request, expatrie_id):
    """Ajouter un permis/visa à un expatrié"""
    expatrie = get_object_or_404(
        Expatrie,
        pk=expatrie_id,
        employe__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        permis = PermisVisa.objects.create(
            expatrie=expatrie,
            type_document=request.POST.get('type_document', 'visa_travail'),
            numero_document=request.POST.get('numero_document', ''),
            date_emission=request.POST.get('date_emission') or None,
            date_expiration=request.POST.get('date_expiration') or None,
            autorite_emission=request.POST.get('autorite_emission', ''),
            statut=request.POST.get('statut', 'en_cours'),
            observations=request.POST.get('notes', ''),
        )
        
        log_activity(
            request,
            f"Ajout {permis.get_type_document_display()} pour {expatrie.employe.nom_complet}",
            'core'
        )
        
        messages.success(request, 'Document ajouté')
        return redirect('core:expatrie_detail', pk=expatrie_id)
    
    return render(request, 'core/expatries/permis_form.html', {
        'expatrie': expatrie,
    })


@login_required
def permis_modifier(request, pk):
    """Modifier un permis/visa"""
    permis = get_object_or_404(PermisVisa, pk=pk)
    expatrie = permis.expatrie
    
    # Vérifier l'accès
    if expatrie.employe.entreprise != request.user.entreprise:
        messages.error(request, 'Accès non autorisé')
        return redirect('core:expatries_liste')
    
    if request.method == 'POST':
        permis.type_document = request.POST.get('type_document', 'visa_travail')
        permis.numero_document = request.POST.get('numero_document', '')
        permis.date_emission = request.POST.get('date_emission') or None
        permis.date_expiration = request.POST.get('date_expiration') or None
        permis.autorite_emission = request.POST.get('autorite_emission', '')
        permis.statut = request.POST.get('statut', 'en_cours')
        permis.observations = request.POST.get('notes', '')
        permis.save()
        
        log_activity(request, f"Modification document {permis.numero_document}", 'core')
        messages.success(request, 'Document modifié')
        return redirect('core:expatrie_detail', pk=expatrie.id)
    
    return render(request, 'core/expatries/permis_form.html', {
        'expatrie': expatrie,
        'permis': permis,
        'modification': True,
    })


@login_required
def alertes_expatries(request):
    """Liste des alertes pour documents expirant"""
    date_limite = date.today() + timedelta(days=90)
    
    permis_expirants = PermisVisa.objects.filter(
        expatrie__employe__entreprise=request.user.entreprise,
        date_expiration__lte=date_limite,
        date_expiration__gte=date.today(),
        statut='en_cours'
    ).select_related('expatrie', 'expatrie__employe').order_by('date_expiration')
    
    alertes = []
    for p in permis_expirants:
        jours = (p.date_expiration - date.today()).days
        alertes.append({
            'permis': p,
            'jours_restants': jours,
            'urgence': 'danger' if jours <= 30 else 'warning' if jours <= 60 else 'info'
        })
    
    return render(request, 'core/expatries/alertes.html', {
        'alertes': alertes,
    })
