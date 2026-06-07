"""
Vues pour la conformité inspection du travail
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import date, timedelta

from core.models import RegistreObligatoire, VisiteInspection
from core.views import log_activity


@login_required
def inspection_dashboard(request):
    """Tableau de bord conformité inspection du travail"""
    entreprise = request.user.entreprise
    
    # Registres obligatoires
    registres = RegistreObligatoire.objects.filter(
        entreprise=entreprise
    )
    
    registres_a_jour = registres.filter(vise_inspection=True).count()
    registres_total = registres.count()
    
    # Dernières visites
    visites = VisiteInspection.objects.filter(
        entreprise=entreprise
    ).order_by('-date_visite')[:5]
    
    # Dernier rapport (simplifié - pas de modèle RapportConformite)
    dernier_rapport = None
    
    # Score de conformité
    if registres_total > 0:
        score_conformite = int((registres_a_jour / registres_total) * 100)
    else:
        score_conformite = 0
    
    return render(request, 'core/inspection/dashboard.html', {
        'registres': registres,
        'registres_a_jour': registres_a_jour,
        'registres_total': registres_total,
        'score_conformite': score_conformite,
        'visites': visites,
        'dernier_rapport': dernier_rapport,
    })


@login_required
def registres_liste(request):
    """Liste des registres obligatoires"""
    registres = RegistreObligatoire.objects.filter(
        entreprise=request.user.entreprise
    ).order_by('type_registre')
    
    return render(request, 'core/inspection/registres_liste.html', {
        'registres': registres,
    })


@login_required
def registre_ajouter(request):
    """Ajouter un registre obligatoire"""
    if request.method == 'POST':
        registre = RegistreObligatoire.objects.create(
            entreprise=request.user.entreprise,
            type_registre=request.POST.get('type_registre', 'personnel'),
            annee=request.POST.get('annee') or date.today().year,
            numero_registre=request.POST.get('numero_registre', ''),
            date_ouverture=request.POST.get('date_ouverture') or date.today(),
            date_cloture=request.POST.get('date_cloture') or None,
            vise_inspection=request.POST.get('vise_inspection') == 'on',
            date_visa=request.POST.get('date_visa') or None,
            numero_visa=request.POST.get('numero_visa', ''),
            observations=request.POST.get('observations', ''),
        )
        
        log_activity(request, f"Ajout registre {registre.get_type_registre_display()}", 'core')
        messages.success(request, 'Registre ajouté')
        return redirect('core:registres_liste')
    
    return render(request, 'core/inspection/registre_form.html', {})


@login_required
def registre_modifier(request, pk):
    """Modifier un registre"""
    registre = get_object_or_404(
        RegistreObligatoire,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        registre.type_registre = request.POST.get('type_registre', 'personnel')
        registre.annee = request.POST.get('annee') or registre.annee
        registre.numero_registre = request.POST.get('numero_registre', '')
        registre.date_ouverture = request.POST.get('date_ouverture') or registre.date_ouverture
        registre.date_cloture = request.POST.get('date_cloture') or None
        registre.vise_inspection = request.POST.get('vise_inspection') == 'on'
        registre.date_visa = request.POST.get('date_visa') or None
        registre.numero_visa = request.POST.get('numero_visa', '')
        registre.observations = request.POST.get('observations', '')
        registre.save()
        
        log_activity(request, f"Modification registre {registre.numero_registre}", 'core')
        messages.success(request, 'Registre modifié')
        return redirect('core:registres_liste')
    
    return render(request, 'core/inspection/registre_form.html', {
        'registre': registre,
        'modification': True,
    })


@login_required
def visites_liste(request):
    """Liste des visites d'inspection"""
    visites = VisiteInspection.objects.filter(
        entreprise=request.user.entreprise
    ).order_by('-date_visite')
    
    return render(request, 'core/inspection/visites_liste.html', {
        'visites': visites,
    })


@login_required
def visite_ajouter(request):
    """Enregistrer une visite d'inspection"""
    if request.method == 'POST':
        visite = VisiteInspection.objects.create(
            entreprise=request.user.entreprise,
            date_visite=request.POST.get('date_visite') or date.today(),
            type_visite=request.POST.get('type_visite', 'routine'),
            inspecteur=request.POST.get('inspecteur', ''),
            motif=request.POST.get('motif', ''),
            observations=request.POST.get('observations', ''),
            actions_requises=request.POST.get('actions_requises', ''),
            date_limite_actions=request.POST.get('date_limite_actions') or None,
            statut=request.POST.get('statut', 'en_cours'),
        )
        
        log_activity(request, f"Enregistrement visite inspection {visite.date_visite}", 'core')
        messages.success(request, 'Visite enregistrée')
        return redirect('core:visites_liste')
    
    return render(request, 'core/inspection/visite_form.html', {})


@login_required
def visite_detail(request, pk):
    """Détail d'une visite d'inspection"""
    visite = get_object_or_404(
        VisiteInspection,
        pk=pk,
        entreprise=request.user.entreprise
    )
    
    return render(request, 'core/inspection/visite_detail.html', {
        'visite': visite,
    })


@login_required
def checklist_conformite(request):
    """Checklist de conformité inspection du travail"""
    from core.services.conformite import ConformiteService
    
    entreprise = request.user.entreprise
    service = ConformiteService(entreprise)
    
    # Traitement des validations manuelles
    if request.method == 'POST':
        from core.models import ParametreConformite
        code = request.POST.get('code')
        valide = request.POST.get('valide') == 'true'
        
        if code:
            param, created = ParametreConformite.objects.get_or_create(
                entreprise=entreprise,
                code=code,
                defaults={'valide': valide}
            )
            if not created:
                param.valide = valide
                if valide:
                    param.date_validation = date.today()
                    param.validateur = request.user.get_full_name() or request.user.username
                param.save()
            
            messages.success(request, f"{'✓ Validé' if valide else '✗ Non conforme'}: {param.get_code_display()}")
            return redirect('core:checklist_conformite')
    
    # Obtenir la checklist avec évaluation automatique
    data = service.get_checklist_complete()
    
    return render(request, 'core/inspection/checklist.html', {
        'checklist': data['checklist'],
        'score': data['score'],
        'score_obligatoire': data['score_obligatoire'],
        'items_conformes': data['items_conformes'],
        'total_items': data['total_items'],
        'obligatoires_conformes': data['obligatoires_conformes'],
        'items_obligatoires': data['items_obligatoires'],
    })


@login_required
def generer_rapport_conformite(request):
    """Générer un rapport de conformité (affichage simplifié)"""
    from core.services.conformite import ConformiteService
    
    entreprise = request.user.entreprise
    service = ConformiteService(entreprise)
    data = service.get_checklist_complete()
    
    score = data['score']
    
    if request.method == 'POST':
        log_activity(request, f"Génération rapport conformité - Score {score}%", 'core')
        messages.success(request, f'Rapport généré - Score: {score}%')
        return redirect('core:inspection_dashboard')
    
    return render(request, 'core/inspection/generer_rapport.html', {
        'score': score,
        'items_conformes': data['items_conformes'],
        'total_items': data['total_items'],
        'checklist': data['checklist'],
    })
