from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, date
import random
import string

from .models import CatalogueFormation, SessionFormation, InscriptionFormation, EvaluationFormation, PlanFormation, InscriptionFormationPublic, ParticipantFormationCabinet
from employes.models import Employe
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def formation_home(request):
    """Vue d'accueil du module formation"""
    entreprise = request.user.entreprise

    if request.method == 'POST' and request.POST.get('action') == 'ajouter_participant_cabinet':
        nom_participant = (request.POST.get('nom_participant') or '').strip()
        titre_formation = (request.POST.get('titre_formation') or '').strip()
        date_formation = request.POST.get('date_formation')
        numero_attestation = (request.POST.get('numero_identite_attestation') or '').strip()
        observations = (request.POST.get('observations') or '').strip()

        if not all([nom_participant, titre_formation, date_formation, numero_attestation]):
            messages.error(request, "Nom, formation, date et numero d'attestation sont obligatoires.")
            return redirect('formation:home')

        try:
            ParticipantFormationCabinet.objects.create(
                entreprise=entreprise,
                nom_participant=nom_participant,
                titre_formation=titre_formation,
                date_formation=date.fromisoformat(date_formation),
                numero_identite_attestation=numero_attestation,
                observations=observations,
            )
            messages.success(request, "Participant ajoute dans la base des attestations.")
        except ValueError:
            messages.error(request, "La date de formation est invalide.")
        except IntegrityError:
            messages.error(request, "Ce numero d'attestation existe deja dans la base.")
        return redirect('formation:home')

    # Sessions agrégées en 1 requête au lieu de 2
    session_stats = SessionFormation.objects.filter(
        formation__entreprise=entreprise,
    ).aggregate(
        planifiees=Count('id', filter=Q(statut='planifiee')),
        en_cours=Count('id', filter=Q(statut='en_cours')),
    )

    stats = {
        'total_formations': CatalogueFormation.objects.filter(
            entreprise=entreprise, actif=True
        ).count(),
        'sessions_planifiees': session_stats['planifiees'] or 0,
        'sessions_en_cours': session_stats['en_cours'] or 0,
        'total_participants': InscriptionFormation.objects.filter(
            session__formation__entreprise=entreprise,
            statut__in=['inscrit', 'confirme', 'present']
        ).count(),
        'participants_cabinet': ParticipantFormationCabinet.objects.filter(
            entreprise=entreprise
        ).count(),
    }
    
    # Plan de formation en cours
    annee_actuelle = date.today().year
    plan_actuel = PlanFormation.objects.filter(
        entreprise=request.user.entreprise,
        annee=annee_actuelle
    ).first()
    
    # Prochaines sessions
    prochaines_sessions = SessionFormation.objects.filter(
        date_debut__gte=date.today(),
        statut='planifiee',
        formation__entreprise=request.user.entreprise,
    ).select_related('formation').order_by('date_debut')[:5]
    
    # Formations populaires
    formations_populaires = CatalogueFormation.objects.annotate(
        nb_sessions=Count('sessions')
    ).filter(
        entreprise=request.user.entreprise,
        actif=True
    ).order_by('-nb_sessions')[:5]

    participants_cabinet = ParticipantFormationCabinet.objects.filter(
        entreprise=entreprise
    ).order_by('-date_formation', 'nom_participant')
    
    return render(request, 'formation/home.html', {
        'stats': stats,
        'plan_actuel': plan_actuel,
        'prochaines_sessions': prochaines_sessions,
        'formations_populaires': formations_populaires,
        'participants_cabinet': participants_cabinet,
    })


@login_required
@entreprise_active_required
def supprimer_participant_cabinet(request, pk):
    """Supprime une entree du registre cabinet."""
    participant = get_object_or_404(
        ParticipantFormationCabinet,
        pk=pk,
        entreprise=request.user.entreprise,
    )
    if request.method == 'POST':
        participant.delete()
        messages.success(request, "Participant supprime de la base des attestations.")
    return redirect('formation:home')


# ============= CATALOGUE =============

@login_required
@entreprise_active_required
def liste_catalogue(request):
    """Liste des formations du catalogue"""
    type_formation = request.GET.get('type')
    domaine = request.GET.get('domaine')
    
    formations = CatalogueFormation.objects.filter(
        entreprise=request.user.entreprise
    ).annotate(
        nb_sessions=Count('sessions')
    )
    
    if type_formation:
        formations = formations.filter(type_formation=type_formation)
    if domaine:
        formations = formations.filter(domaine=domaine)
    
    return render(request, 'formation/catalogue/liste.html', {
        'formations': formations
    })


@login_required
@entreprise_active_required
def creer_formation(request):
    """Créer une formation"""
    if request.method == 'POST':
        try:
            # Générer un code unique
            code = f"FORM-{''.join(random.choices(string.digits, k=3))}"
            
            # Vérifier si publiée
            publiee = request.POST.get('publiee') == 'on'
            
            formation = CatalogueFormation.objects.create(
                entreprise=request.user.entreprise,
                code_formation=code,
                intitule=request.POST.get('intitule'),
                type_formation=request.POST.get('type_formation'),
                domaine=request.POST.get('domaine'),
                description=request.POST.get('description'),
                objectifs=request.POST.get('objectifs'),
                contenu=request.POST.get('contenu'),
                duree_jours=request.POST.get('duree_jours'),
                duree_heures=request.POST.get('duree_heures'),
                prerequis=request.POST.get('prerequis'),
                organisme_formateur=request.POST.get('organisme'),
                cout_unitaire=request.POST.get('cout') if request.POST.get('cout') else None,
                image=request.FILES.get('image') if 'image' in request.FILES else None,
                publiee=publiee,
                date_publication=date.today() if publiee else None,
                actif=True
            )
            
            messages.success(request, f'Formation {code} créée avec succès.')
            return redirect('formation:detail_formation', pk=formation.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'formation/catalogue/creer.html')


@login_required
@entreprise_active_required
def detail_formation(request, pk):
    """Détail d'une formation"""
    formation = get_object_or_404(CatalogueFormation, pk=pk, entreprise=request.user.entreprise)
    sessions = formation.sessions.all().annotate(
        nb_inscrits=Count('inscriptions')
    )
    # Récupérer les candidatures/inscriptions publiques
    inscriptions_publiques = formation.inscriptions_publiques.all().order_by('-date_inscription')
    
    return render(request, 'formation/catalogue/detail.html', {
        'formation': formation,
        'sessions': sessions,
        'inscriptions_publiques': inscriptions_publiques
    })


@login_required
@entreprise_active_required
def modifier_formation(request, pk):
    """Modifier une formation"""
    formation = get_object_or_404(CatalogueFormation, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        try:
            formation.intitule = request.POST.get('intitule')
            formation.type_formation = request.POST.get('type_formation')
            formation.domaine = request.POST.get('domaine')
            formation.description = request.POST.get('description')
            formation.objectifs = request.POST.get('objectifs')
            formation.contenu = request.POST.get('contenu')
            formation.duree_jours = request.POST.get('duree_jours')
            formation.duree_heures = request.POST.get('duree_heures')
            formation.prerequis = request.POST.get('prerequis')
            formation.organisme_formateur = request.POST.get('organisme')
            formation.cout_unitaire = request.POST.get('cout') if request.POST.get('cout') else None
            formation.actif = request.POST.get('actif') == 'on'
            
            # Gestion de la publication
            publiee = request.POST.get('publiee') == 'on'
            if publiee and not formation.publiee:
                formation.date_publication = date.today()
            elif not publiee:
                formation.date_publication = None
            formation.publiee = publiee
            
            # Gestion de l'image
            if request.POST.get('supprimer_image') == 'on':
                formation.image = None
            elif 'image' in request.FILES:
                formation.image = request.FILES['image']
            
            formation.save()
            
            messages.success(request, 'Formation modifiée avec succès.')
            return redirect('formation:detail_formation', pk=formation.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'formation/catalogue/modifier.html', {
        'formation': formation
    })


@login_required
@entreprise_active_required
def supprimer_formation(request, pk):
    """Supprimer une formation du catalogue"""
    formation = get_object_or_404(CatalogueFormation, pk=pk, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        code = formation.code_formation
        intitule = formation.intitule
        nb_sessions = formation.sessions.count()
        
        if nb_sessions > 0:
            messages.warning(
                request,
                f"La formation {code} a été supprimée avec {nb_sessions} session(s) associée(s)."
            )
        else:
            messages.success(request, f"La formation {code} - {intitule} a été supprimée avec succès.")
        
        formation.delete()
        return redirect('formation:catalogue')
    
    return redirect('formation:detail_formation', pk=pk)


# ============= SESSIONS =============

@login_required
@entreprise_active_required
def liste_sessions(request):
    """Liste des sessions"""
    statut = request.GET.get('statut')
    
    sessions = SessionFormation.objects.filter(
        formation__entreprise=request.user.entreprise
    ).select_related('formation').annotate(
        nb_inscrits=Count('inscriptions')
    )
    
    if statut:
        sessions = sessions.filter(statut=statut)
    
    return render(request, 'formation/sessions/liste.html', {
        'sessions': sessions
    })


@login_required
@entreprise_active_required
def planifier_session(request):
    """Planifier une session"""
    if request.method == 'POST':
        try:
            # Générer une référence unique
            reference = f"SESS-{date.today().year}-{''.join(random.choices(string.digits, k=3))}"
            
            formation = get_object_or_404(
                CatalogueFormation,
                pk=request.POST.get('formation'),
                entreprise=request.user.entreprise,
            )

            session = SessionFormation.objects.create(
                formation=formation,
                reference_session=reference,
                date_debut=request.POST.get('date_debut'),
                date_fin=request.POST.get('date_fin'),
                lieu=request.POST.get('lieu'),
                formateur=request.POST.get('formateur'),
                nombre_places=request.POST.get('nombre_places', 10),
                cout_total=request.POST.get('cout_total') if request.POST.get('cout_total') else None,
                statut='planifiee'
            )
            
            messages.success(request, f'Session {reference} planifiée avec succès.')
            return redirect('formation:detail_session', pk=session.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    formations = CatalogueFormation.objects.filter(
        entreprise=request.user.entreprise,
        actif=True
    )
    
    return render(request, 'formation/sessions/planifier.html', {
        'formations': formations
    })


@login_required
@entreprise_active_required
def detail_session(request, pk):
    """Détail d'une session"""
    session = get_object_or_404(SessionFormation, pk=pk, formation__entreprise=request.user.entreprise)
    
    # Récupérer les inscriptions des employés
    inscriptions_employes = session.inscriptions.all().select_related('employe')
    
    # Récupérer les inscriptions publiques pour cette session
    inscriptions_publiques = session.inscriptions_publiques.all()
    
    # Combiner les deux types d'inscriptions pour l'affichage
    tous_participants = []
    
    # Ajouter les inscriptions des employés
    for inscription in inscriptions_employes:
        tous_participants.append({
            'type': 'employe',
            'nom': inscription.employe.nom,
            'prenom': inscription.employe.prenom,
            'email': inscription.employe.email,
            'telephone': inscription.employe.telephone,
            'entreprise': inscription.employe.entreprise.nom if inscription.employe.entreprise else '',
            'fonction': inscription.employe.poste,
            'statut': inscription.statut,
            'date_inscription': inscription.date_inscription,
            'pk': inscription.pk
        })
    
    # Ajouter les inscriptions publiques
    for inscription in inscriptions_publiques:
        tous_participants.append({
            'type': 'public',
            'nom': inscription.nom,
            'prenom': inscription.prenom,
            'email': inscription.email,
            'telephone': inscription.telephone,
            'entreprise': inscription.entreprise or '',
            'fonction': inscription.fonction or '',
            'statut': inscription.statut,
            'date_inscription': inscription.date_inscription,
            'pk': inscription.pk
        })
    
    # Trier par date d'inscription
    tous_participants.sort(key=lambda x: x['date_inscription'], reverse=True)
    
    return render(request, 'formation/sessions/detail.html', {
        'session': session,
        'inscriptions': inscriptions_employes,
        'inscriptions_publiques': inscriptions_publiques,
        'tous_participants': tous_participants
    })


@login_required
@entreprise_active_required
def modifier_session(request, pk):
    """Modifier une session existante"""
    session = get_object_or_404(SessionFormation, pk=pk, formation__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            session.date_debut = request.POST.get('date_debut')
            session.date_fin = request.POST.get('date_fin')
            session.lieu = request.POST.get('lieu')
            session.formateur = request.POST.get('formateur')
            session.nombre_places = request.POST.get('nombre_places')
            session.observations = request.POST.get('observations')
            
            # Valider les dates
            if session.date_debut > session.date_fin:
                messages.error(request, 'La date de début doit être antérieure à la date de fin.')
                return redirect('formation:modifier_session', pk=pk)
            
            session.save()
            messages.success(request, 'Session modifiée avec succès.')
            return redirect('formation:detail_session', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {e}')
    
    return render(request, 'formation/sessions/modifier.html', {
        'session': session
    })


@login_required
@entreprise_active_required
def inscrire_employe(request, session_id):
    """Inscrire un employé à une session"""
    session = get_object_or_404(SessionFormation, pk=session_id, formation__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        try:
            employe_id = request.POST.get('employe')
            employe = get_object_or_404(Employe, pk=employe_id, entreprise=request.user.entreprise)
            
            # Vérifier les places disponibles
            if session.nombre_inscrits >= session.nombre_places:
                messages.error(request, 'Plus de places disponibles.')
                return redirect('formation:detail_session', pk=session.pk)
            
            # Créer l'inscription
            inscription = InscriptionFormation.objects.create(
                session=session,
                employe=employe,
                statut='inscrit'
            )
            
            # Mettre à jour le nombre d'inscrits
            session.nombre_inscrits += 1
            session.save()
            
            messages.success(request, 'Employé inscrit avec succès.')
            return redirect('formation:detail_session', pk=session.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'formation/inscriptions/inscrire.html', {
        'session': session,
        'employes': employes
    })


# ============= INSCRIPTIONS =============

@login_required
@entreprise_active_required
def liste_inscriptions(request):
    """Liste des inscriptions"""
    inscriptions = InscriptionFormation.objects.filter(
        session__formation__entreprise=request.user.entreprise,
        employe__entreprise=request.user.entreprise,
    ).select_related(
        'employe', 'session', 'session__formation'
    )
    
    return render(request, 'formation/inscriptions/liste.html', {
        'inscriptions': inscriptions
    })


@login_required
@entreprise_active_required
def evaluer_participant(request, pk):
    """Évaluer un participant"""
    inscription = get_object_or_404(
        InscriptionFormation,
        pk=pk,
        session__formation__entreprise=request.user.entreprise,
        employe__entreprise=request.user.entreprise,
    )
    
    if request.method == 'POST':
        try:
            inscription.note_evaluation = request.POST.get('note') if request.POST.get('note') else None
            inscription.appreciation = request.POST.get('appreciation')
            inscription.certificat_obtenu = request.POST.get('certificat') == 'on'
            inscription.commentaires = request.POST.get('commentaires')
            inscription.statut = 'present'
            inscription.save()
            
            messages.success(request, 'Évaluation enregistrée avec succès.')
            return redirect('formation:detail_session', pk=inscription.session.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'formation/inscriptions/evaluer.html', {
        'inscription': inscription
    })


# ============= ÉVALUATIONS =============

@login_required
@entreprise_active_required
def formulaire_evaluation(request, inscription_id):
    """Formulaire d'évaluation de la formation"""
    inscription = get_object_or_404(
        InscriptionFormation,
        pk=inscription_id,
        session__formation__entreprise=request.user.entreprise,
        employe__entreprise=request.user.entreprise,
    )
    
    if request.method == 'POST':
        try:
            evaluation = EvaluationFormation.objects.create(
                inscription=inscription,
                note_contenu=request.POST.get('note_contenu'),
                note_formateur=request.POST.get('note_formateur'),
                note_organisation=request.POST.get('note_organisation'),
                note_moyens=request.POST.get('note_moyens'),
                note_globale=request.POST.get('note_globale'),
                points_forts=request.POST.get('points_forts'),
                points_ameliorer=request.POST.get('points_ameliorer'),
                suggestions=request.POST.get('suggestions'),
                competences_acquises=request.POST.get('competences'),
                application_travail=request.POST.get('application') == 'on',
                recommandation=request.POST.get('recommandation') == 'on'
            )
            
            messages.success(request, 'Évaluation enregistrée. Merci pour votre retour !')
            return redirect('formation:home')
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'formation/evaluations/formulaire.html', {
        'inscription': inscription
    })


@login_required
@entreprise_active_required
def liste_evaluations(request):
    """Liste des évaluations"""
    evaluations = EvaluationFormation.objects.filter(
        inscription__session__formation__entreprise=request.user.entreprise,
        inscription__employe__entreprise=request.user.entreprise,
    ).select_related(
        'inscription', 'inscription__employe', 'inscription__session__formation'
    )
    
    return render(request, 'formation/evaluations/liste.html', {
        'evaluations': evaluations
    })


# ============= PLAN DE FORMATION =============

@login_required
@entreprise_active_required
def liste_plans(request):
    """Liste des plans de formation"""
    plans = PlanFormation.objects.filter(entreprise=request.user.entreprise)
    
    return render(request, 'formation/plan/liste.html', {
        'plans': plans
    })


@login_required
@entreprise_active_required
def creer_plan(request):
    """Créer un plan de formation"""
    if request.method == 'POST':
        try:
            plan = PlanFormation.objects.create(
                entreprise=request.user.entreprise,
                annee=request.POST.get('annee'),
                budget_total=request.POST.get('budget_total'),
                objectifs=request.POST.get('objectifs'),
                statut='brouillon'
            )
            
            messages.success(request, f'Plan de formation {plan.annee} créé avec succès.')
            return redirect('formation:detail_plan', annee=plan.annee)
            
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'formation/plan/creer.html')


@login_required
@entreprise_active_required
def detail_plan(request, annee):
    """Détail d'un plan de formation"""
    plan = get_object_or_404(PlanFormation, annee=annee, entreprise=request.user.entreprise)
    
    # Sessions de l'année
    sessions = SessionFormation.objects.filter(
        date_debut__year=annee,
        formation__entreprise=request.user.entreprise,
    ).select_related('formation')
    
    return render(request, 'formation/plan/detail.html', {
        'plan': plan,
        'sessions': sessions
    })


# ============================================
# VUES PUBLIQUES (sans authentification)
# ============================================

def formation_public(request, pk):
    """Vue publique des détails d'une formation"""
    formation = get_object_or_404(CatalogueFormation, pk=pk, publiee=True, actif=True)
    
    # Récupérer les prochaines sessions disponibles
    sessions_disponibles = SessionFormation.objects.filter(
        formation=formation,
        statut='planifiee',
        date_debut__gte=date.today()
    ).order_by('date_debut')
    
    return render(request, 'formation/public/detail.html', {
        'formation': formation,
        'sessions': sessions_disponibles,
    })


def inscription_formation_public(request, pk):
    """Inscription publique à une formation"""
    formation = get_object_or_404(CatalogueFormation, pk=pk, publiee=True, actif=True)
    
    # Récupérer les sessions disponibles
    sessions_disponibles = SessionFormation.objects.filter(
        formation=formation,
        statut='planifiee',
        date_debut__gte=date.today()
    ).order_by('date_debut')
    
    if request.method == 'POST':
        try:
            inscription = InscriptionFormationPublic.objects.create(
                formation=formation,
                session_id=request.POST.get('session') if request.POST.get('session') else None,
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                email=request.POST.get('email'),
                telephone=request.POST.get('telephone'),
                entreprise=request.POST.get('entreprise'),
                fonction=request.POST.get('fonction'),
                motivation=request.POST.get('motivation'),
            )
            
            messages.success(request, f'Votre inscription à la formation "{formation.intitule}" a été enregistrée. Nous vous contacterons prochainement.')
            return redirect('formation:formation_public', pk=formation.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'inscription : {str(e)}')
    
    return render(request, 'formation/public/inscription.html', {
        'formation': formation,
        'sessions': sessions_disponibles,
    })


@login_required
@entreprise_active_required
def liste_candidatures(request):
    """Liste de toutes les candidatures publiques"""
    candidatures = InscriptionFormationPublic.objects.filter(
        formation__entreprise=request.user.entreprise
    ).select_related('formation', 'session').order_by('-date_inscription')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        candidatures = candidatures.filter(statut=statut)
    
    formation_id = request.GET.get('formation')
    if formation_id:
        candidatures = candidatures.filter(formation_id=formation_id)
    
    formations = CatalogueFormation.objects.filter(
        entreprise=request.user.entreprise,
        actif=True
    )
    
    return render(request, 'formation/candidatures/liste.html', {
        'candidatures': candidatures,
        'formations': formations,
        'statut_filtre': statut,
        'formation_filtre': formation_id,
    })


@login_required
@entreprise_active_required
def gerer_candidature(request, pk):
    """Gérer une candidature (changer statut, ajouter notes)"""
    candidature = get_object_or_404(
        InscriptionFormationPublic,
        pk=pk,
        formation__entreprise=request.user.entreprise
    )
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        notes = request.POST.get('notes_admin')
        
        if nouveau_statut:
            candidature.statut = nouveau_statut
        if notes is not None:
            candidature.notes_admin = notes
        
        candidature.save()
        messages.success(request, f'Candidature de {candidature.prenom} {candidature.nom} mise à jour.')
        return redirect('formation:detail_formation', pk=candidature.formation.pk)
    
    return render(request, 'formation/candidatures/gerer.html', {
        'candidature': candidature,
    })
