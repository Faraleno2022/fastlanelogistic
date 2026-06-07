from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError
from datetime import date, timedelta

from .models import Candidature, DecisionEmbauche
from .models_integration import ProcessusIntegration, EtapeIntegration, AlerteIntegration
from employes.models import Employe
from core.models import Poste, Service
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def liste_decisions(request):
    """Liste des décisions d'embauche"""
    decisions = DecisionEmbauche.objects.filter(
        candidature__offre__entreprise=request.user.entreprise
    ).select_related('candidature', 'candidature__offre', 'poste_propose')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        decisions = decisions.filter(statut_integration=statut)
    
    decision_type = request.GET.get('decision')
    if decision_type:
        decisions = decisions.filter(decision=decision_type)
    
    context = {
        'decisions': decisions,
        'statut_actuel': statut,
        'decision_actuelle': decision_type,
    }
    
    return render(request, 'recrutement/decisions/liste.html', context)


@login_required
@entreprise_active_required
def creer_decision(request, candidature_id):
    """Créer une décision d'embauche pour une candidature"""
    candidature = get_object_or_404(
        Candidature,
        pk=candidature_id,
        offre__entreprise=request.user.entreprise
    )
    
    # Vérifier qu'il n'y a pas déjà une décision
    if hasattr(candidature, 'decision_embauche'):
        messages.warning(request, 'Une décision existe déjà pour cette candidature.')
        return redirect('recrutement:detail_decision', pk=candidature.decision_embauche.pk)
    
    if request.method == 'POST':
        try:
            decision = DecisionEmbauche.objects.create(
                candidature=candidature,
                decision=request.POST.get('decision'),
                date_decision=date.today(),
                poste_propose_id=request.POST.get('poste') or None,
                service_affectation_id=request.POST.get('service') or None,
                type_contrat=request.POST.get('type_contrat'),
                date_embauche_prevue=request.POST.get('date_embauche') or None,
                salaire_propose=request.POST.get('salaire') or None,
                valide_par_id=request.POST.get('valide_par') or None,
                observations=request.POST.get('observations'),
            )
            
            # Mettre à jour le statut de la candidature
            if decision.decision == 'embauche':
                candidature.statut_candidature = 'retenue'
                decision.statut_integration = 'offre_envoyee'
                decision.date_envoi_offre = date.today()
            elif decision.decision == 'refus':
                candidature.statut_candidature = 'rejetee'
                decision.motif_refus = request.POST.get('motif_refus')
            
            candidature.save()
            decision.save()
            
            messages.success(request, 'Décision d\'embauche enregistrée avec succès.')
            return redirect('recrutement:detail_decision', pk=decision.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
    
    postes = Poste.objects.filter(entreprise=request.user.entreprise, actif=True)
    services = Service.objects.filter(
        entreprise=request.user.entreprise,
        actif=True,
    )
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    context = {
        'candidature': candidature,
        'postes': postes,
        'services': services,
        'employes': employes,
    }
    
    return render(request, 'recrutement/decisions/creer.html', context)


@login_required
@entreprise_active_required
def detail_decision(request, pk):
    """Détail d'une décision d'embauche"""
    decision = get_object_or_404(
        DecisionEmbauche,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise
    )
    
    # Vérifier si un processus d'intégration existe
    processus = None
    if hasattr(decision, 'processus_integration'):
        processus = decision.processus_integration
    
    context = {
        'decision': decision,
        'processus': processus,
    }
    
    return render(request, 'recrutement/decisions/detail.html', context)


@login_required
@entreprise_active_required
def accepter_offre(request, pk):
    """Marquer l'offre comme acceptée par le candidat"""
    decision = get_object_or_404(
        DecisionEmbauche,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            decision.statut_integration = 'offre_acceptee'
            decision.date_reponse_candidat = date.today()
            decision.save()
            
            # Mettre à jour le statut de la candidature
            decision.candidature.statut_candidature = 'embauche'
            decision.candidature.save()
            
            messages.success(request, 'Offre acceptée ! Vous pouvez maintenant démarrer le processus d\'intégration.')
            return redirect('recrutement:demarrer_integration', pk=decision.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return redirect('recrutement:detail_decision', pk=pk)


@login_required
@entreprise_active_required
def refuser_offre(request, pk):
    """Marquer l'offre comme refusée par le candidat"""
    decision = get_object_or_404(
        DecisionEmbauche,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        decision.statut_integration = 'offre_refusee'
        decision.date_reponse_candidat = date.today()
        decision.observations = request.POST.get('motif_refus', '')
        decision.save()
        
        messages.info(request, 'Offre refusée par le candidat.')
    
    return redirect('recrutement:detail_decision', pk=pk)


@login_required
@entreprise_active_required
def demarrer_integration(request, pk):
    """Démarrer le processus d'intégration"""
    decision = get_object_or_404(
        DecisionEmbauche,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise
    )
    
    # Vérifier que l'offre a été acceptée
    if decision.statut_integration != 'offre_acceptee':
        messages.warning(request, 'L\'offre doit d\'abord être acceptée par le candidat.')
        return redirect('recrutement:detail_decision', pk=pk)
    
    # Vérifier qu'un processus n'existe pas déjà
    if hasattr(decision, 'processus_integration'):
        messages.info(request, 'Un processus d\'intégration existe déjà.')
        return redirect('recrutement:detail_integration', pk=decision.processus_integration.pk)
    
    if request.method == 'POST':
        try:
            # Créer le processus d'intégration
            date_debut = decision.date_embauche_prevue or date.today()
            processus = ProcessusIntegration.objects.create(
                decision_embauche=decision,
                responsable_integration_id=request.POST.get('responsable') or None,
                tuteur_assigne_id=request.POST.get('tuteur') or None,
                date_debut_prevue=date_debut,
                date_fin_prevue=date_debut + timedelta(days=90),  # 3 mois par défaut
            )
            
            # Créer les étapes d'intégration par défaut
            etapes_defaut = [
                ('documents_pre_embauche', 'Collecte des documents pré-embauche', 0),
                ('signature_contrat', 'Signature du contrat de travail', 1),
                ('accueil_premier_jour', 'Accueil le premier jour', 7),
                ('formation_securite', 'Formation sécurité et règlement intérieur', 14),
                ('presentation_equipe', 'Présentation à l\'équipe', 7),
                ('formation_poste', 'Formation au poste de travail', 30),
                ('evaluation_periode_essai', 'Évaluation fin de période d\'essai', 90),
            ]
            
            for i, (nom, description, jours_offset) in enumerate(etapes_defaut, 1):
                EtapeIntegration.objects.create(
                    processus=processus,
                    nom_etape=nom,
                    description=description,
                    date_prevue=date_debut + timedelta(days=jours_offset),
                    ordre=i,
                )
            
            # Mettre à jour le statut
            decision.statut_integration = 'integration_cours'
            decision.date_debut_integration = date.today()
            decision.save()
            
            messages.success(request, 'Processus d\'intégration démarré avec succès.')
            return redirect('recrutement:detail_integration', pk=processus.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    context = {
        'decision': decision,
        'employes': employes,
    }
    
    return render(request, 'recrutement/integration/demarrer.html', context)


@login_required
@entreprise_active_required
def liste_integrations(request):
    """Liste des processus d'intégration en cours"""
    integrations = ProcessusIntegration.objects.filter(
        decision_embauche__candidature__offre__entreprise=request.user.entreprise
    ).select_related('decision_embauche', 'decision_embauche__candidature')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut == 'en_cours':
        integrations = integrations.filter(date_fin_effective__isnull=True)
    elif statut == 'terminees':
        integrations = integrations.filter(date_fin_effective__isnull=False)
    
    context = {
        'integrations': integrations,
        'statut_actuel': statut,
    }
    
    return render(request, 'recrutement/integration/liste.html', context)


@login_required
@entreprise_active_required
def detail_integration(request, pk):
    """Détail d'un processus d'intégration"""
    processus = get_object_or_404(
        ProcessusIntegration,
        pk=pk,
        decision_embauche__candidature__offre__entreprise=request.user.entreprise
    )
    
    etapes = processus.etapes_integration.all()
    alertes = processus.alertes.filter(traitee=False)
    
    context = {
        'processus': processus,
        'etapes': etapes,
        'alertes': alertes,
    }
    
    return render(request, 'recrutement/integration/detail.html', context)


@login_required
@entreprise_active_required
def valider_etape(request, pk):
    """Valider une étape d'intégration"""
    etape = get_object_or_404(
        EtapeIntegration,
        pk=pk,
        processus__decision_embauche__candidature__offre__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            # Récupérer l'employé connecté
            employe = Employe.objects.filter(
                utilisateur=request.user,
                entreprise=request.user.entreprise
            ).first()
            
            etape.marquer_terminee(employe)
            etape.commentaires = request.POST.get('commentaires', '')
            etape.documents_fournis = request.POST.get('documents_fournis') == 'on'
            etape.save()
            
            messages.success(request, f'Étape "{etape.get_nom_etape_display()}" validée.')
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return redirect('recrutement:detail_integration', pk=etape.processus.pk)


@login_required
@entreprise_active_required
def liste_alertes_recrutement(request):
    """Liste des alertes de recrutement et d'intégration"""
    alertes = AlerteIntegration.objects.filter(
        processus__decision_embauche__candidature__offre__entreprise=request.user.entreprise,
        traitee=False
    ).select_related('processus', 'processus__decision_embauche__candidature')
    
    context = {
        'alertes': alertes,
    }
    
    return render(request, 'recrutement/alertes/liste.html', context)


@login_required
@entreprise_active_required
def traiter_alerte_recrutement(request, pk):
    """Traiter une alerte de recrutement"""
    alerte = get_object_or_404(
        AlerteIntegration,
        pk=pk,
        processus__decision_embauche__candidature__offre__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        try:
            employe = Employe.objects.filter(
                utilisateur=request.user,
                entreprise=request.user.entreprise
            ).first()
            
            alerte.traitee = True
            alerte.traitee_par = employe
            alerte.date_traitement = timezone.now()
            alerte.save()
            
            messages.success(request, 'Alerte traitée.')
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return redirect('recrutement:alertes')


@login_required
@entreprise_active_required
def creer_employe_depuis_candidat(request, pk):
    """Créer un employé à partir d'un candidat embauché"""
    decision = get_object_or_404(
        DecisionEmbauche,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise
    )
    
    candidature = decision.candidature
    
    # Vérifier que le candidat n'a pas déjà été converti
    if candidature.employe_cree:
        messages.info(request, 'Un employé a déjà été créé pour ce candidat.')
        return redirect('employes:detail', pk=candidature.employe_cree.pk)
    
    if request.method == 'POST':
        try:
            # Générer un matricule unique (vérification globale)
            annee = date.today().year
            dernier = Employe.objects.filter(
                matricule__startswith=f'EMP{annee}'
            ).order_by('-matricule').first()
            if dernier:
                try:
                    numero = int(dernier.matricule[-4:]) + 1
                except (ValueError, IndexError):
                    numero = 1
            else:
                numero = 1
            matricule = f'EMP{annee}{numero:04d}'
            
            # Créer l'employé
            employe = Employe.objects.create(
                entreprise=request.user.entreprise,
                matricule=matricule,
                nom=candidature.nom,
                prenoms=candidature.prenoms,
                civilite=candidature.civilite,
                date_naissance=candidature.date_naissance,
                nationalite=candidature.nationalite,
                telephone=candidature.telephone,
                email=candidature.email,
                adresse=candidature.adresse,
                poste=decision.poste_propose,
                service=decision.service_affectation,
                date_embauche=decision.date_embauche_prevue or date.today(),
                salaire_base=decision.salaire_propose or 0,
                type_contrat=decision.type_contrat,
                statut_employe='actif',
            )
            
            # Lier l'employé à la candidature
            candidature.employe_cree = employe
            candidature.save()
            
            # Mettre à jour le processus d'intégration si existant
            if hasattr(decision, 'processus_integration'):
                decision.processus_integration.employe_cree = employe
                decision.processus_integration.save()
            
            messages.success(request, f'Employé {matricule} créé avec succès.')
            return redirect('employes:detail', pk=employe.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'decision': decision,
        'candidature': candidature,
    }
    
    return render(request, 'recrutement/integration/creer_employe.html', context)
