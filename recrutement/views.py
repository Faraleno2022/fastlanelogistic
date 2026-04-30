from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, date
import random
import string

from .models import OffreEmploi, Candidature, EntretienRecrutement
from core.models import Poste, Service
from core.validators import valider_cv, valider_image_document, valider_image
from employes.models import Employe
from core.decorators import entreprise_active_required


@login_required
@entreprise_active_required
def recrutement_home(request):
    """Vue d'accueil du module recrutement"""
    entreprise = request.user.entreprise

    # Statistiques agrégées — 2 requêtes au lieu de 4
    cand_stats = Candidature.objects.filter(
        offre__entreprise=entreprise,
    ).aggregate(
        recues=Count('id', filter=Q(statut_candidature='recue')),
        retenues=Count('id', filter=Q(statut_candidature='retenue')),
    )
    stats = {
        'offres_ouvertes': OffreEmploi.objects.filter(
            entreprise=entreprise, statut_offre='ouverte'
        ).count(),
        'candidatures_recues': cand_stats['recues'] or 0,
        'candidatures_retenues': cand_stats['retenues'] or 0,
        'entretiens_prevus': EntretienRecrutement.objects.filter(
            candidature__offre__entreprise=entreprise,
            date_entretien__gte=timezone.now()
        ).count(),
    }

    # Offres récentes
    offres_recentes = OffreEmploi.objects.filter(
        entreprise=entreprise, statut_offre='ouverte'
    ).only('id', 'reference_offre', 'intitule_poste', 'date_publication', 'statut_offre')[:5]

    # Candidatures récentes
    candidatures_recentes = Candidature.objects.filter(
        offre__entreprise=entreprise
    ).select_related('offre').only(
        'id', 'numero_candidature', 'nom', 'prenoms', 'date_candidature',
        'statut_candidature', 'offre__intitule_poste'
    )[:5]

    # Prochains entretiens
    prochains_entretiens = EntretienRecrutement.objects.filter(
        candidature__offre__entreprise=entreprise,
        date_entretien__gte=timezone.now()
    ).select_related('candidature', 'candidature__offre').order_by('date_entretien')[:5]
    
    return render(request, 'recrutement/home.html', {
        'stats': stats,
        'offres_recentes': offres_recentes,
        'candidatures_recentes': candidatures_recentes,
        'prochains_entretiens': prochains_entretiens
    })


# ============= OFFRES D'EMPLOI =============

@login_required
@entreprise_active_required
def liste_offres(request):
    """Liste des offres d'emploi"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    statut = request.GET.get('statut')
    service_id = request.GET.get('service')
    
    offres = OffreEmploi.objects.filter(
        entreprise=request.user.entreprise
    ).select_related('poste', 'service', 'responsable_recrutement').order_by('-date_publication')
    
    if statut:
        offres = offres.filter(statut_offre=statut)
    if service_id:
        offres = offres.filter(service_id=service_id)
    
    # Ajouter le nombre de candidatures pour chaque offre
    offres = offres.annotate(nb_candidatures=Count('candidatures'))
    
    # Pagination - 50 par page
    paginator = Paginator(offres, 50)
    page = request.GET.get('page')
    try:
        offres_page = paginator.page(page)
    except PageNotAnInteger:
        offres_page = paginator.page(1)
    except EmptyPage:
        offres_page = paginator.page(paginator.num_pages)
    
    services = Service.objects.filter(
        entreprise=request.user.entreprise
    )

    return render(request, 'recrutement/offres/liste.html', {
        'offres': offres_page,
        'services': services,
        'total_offres': paginator.count,
    })


@login_required
@entreprise_active_required
def creer_offre(request):
    """Créer une offre d'emploi"""
    if request.method == 'POST':
        try:
            # Générer une référence unique
            reference = f"OFF-{date.today().year}-{''.join(random.choices(string.digits, k=4))}"
            
            # Valider les fichiers avant création
            image_file = None
            pdf_file = None
            if 'image' in request.FILES:
                try:
                    valider_image(request.FILES['image'])
                    image_file = request.FILES['image']
                except ValidationError as e:
                    messages.error(request, f'Image : {e.message}')
                    raise
            if 'document_pdf' in request.FILES:
                try:
                    valider_cv(request.FILES['document_pdf'])
                    pdf_file = request.FILES['document_pdf']
                except ValidationError as e:
                    messages.error(request, f'Document PDF : {e.message}')
                    raise

            offre = OffreEmploi.objects.create(
                entreprise=request.user.entreprise,
                reference_offre=reference,
                reference_poste=request.POST.get('reference_poste') if request.POST.get('reference_poste') else None,
                intitule_poste=request.POST.get('intitule_poste'),
                secteur_activite=request.POST.get('secteur_activite') if request.POST.get('secteur_activite') else None,
                poste_id=request.POST.get('poste') if request.POST.get('poste') else None,
                poste_texte=request.POST.get('poste_texte') if request.POST.get('poste_texte') else None,
                service_id=request.POST.get('service') if request.POST.get('service') else None,
                service_texte=request.POST.get('service_texte') if request.POST.get('service_texte') else None,
                type_contrat=request.POST.get('type_contrat'),
                responsable_texte=request.POST.get('responsable_texte') if request.POST.get('responsable_texte') else None,
                nombre_postes=request.POST.get('nombre_postes', 1),
                date_limite_candidature=request.POST.get('date_limite') if request.POST.get('date_limite') else None,
                description_poste=request.POST.get('description'),
                profil_recherche=request.POST.get('profil'),
                competences_requises=request.POST.get('competences'),
                experience_requise=request.POST.get('experience') if request.POST.get('experience') else None,
                formation_requise=request.POST.get('formation'),
                salaire_propose_min=request.POST.get('salaire_min') if request.POST.get('salaire_min') else None,
                salaire_propose_max=request.POST.get('salaire_max') if request.POST.get('salaire_max') else None,
                avantages=request.POST.get('avantages'),
                image=image_file,
                document_pdf=pdf_file,
                responsable_recrutement_id=request.POST.get('responsable') if request.POST.get('responsable') else None,
                statut_offre='ouverte'
            )
            
            messages.success(request, f'Offre {reference} créée avec succès.')
            return redirect('recrutement:detail_offre', offre_uuid=offre.uuid)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    postes = Poste.objects.filter(entreprise=request.user.entreprise, actif=True)
    services = Service.objects.filter(
        entreprise=request.user.entreprise,
        actif=True,
    )
    employes = Employe.objects.filter(
        entreprise=request.user.entreprise,
    ).order_by('nom', 'prenoms')
    
    return render(request, 'recrutement/offres/creer.html', {
        'postes': postes,
        'services': services,
        'employes': employes
    })


@login_required
@entreprise_active_required
def detail_offre(request, offre_uuid):
    """Détail d'une offre d'emploi"""
    offre = get_object_or_404(OffreEmploi, uuid=offre_uuid, entreprise=request.user.entreprise)
    candidatures = offre.candidatures.all()
    
    # Statistiques des candidatures
    stats_candidatures = {
        'total': candidatures.count(),
        'recues': candidatures.filter(statut_candidature='recue').count(),
        'preselectionnes': candidatures.filter(statut_candidature='preselectionne').count(),
        'entretien': candidatures.filter(statut_candidature='entretien').count(),
        'retenues': candidatures.filter(statut_candidature='retenue').count(),
        'rejetees': candidatures.filter(statut_candidature='rejetee').count(),
    }
    
    return render(request, 'recrutement/offres/detail.html', {
        'offre': offre,
        'candidatures': candidatures,
        'stats': stats_candidatures
    })


@login_required
@entreprise_active_required
def modifier_offre(request, offre_uuid):
    """Modifier une offre d'emploi"""
    offre = get_object_or_404(OffreEmploi, uuid=offre_uuid, entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        try:
            offre.reference_poste = request.POST.get('reference_poste') if request.POST.get('reference_poste') else None
            offre.intitule_poste = request.POST.get('intitule_poste')
            offre.secteur_activite = request.POST.get('secteur_activite') if request.POST.get('secteur_activite') else None
            offre.poste_id = request.POST.get('poste') if request.POST.get('poste') else None
            offre.poste_texte = request.POST.get('poste_texte') if request.POST.get('poste_texte') else None
            offre.service_id = request.POST.get('service') if request.POST.get('service') else None
            offre.service_texte = request.POST.get('service_texte') if request.POST.get('service_texte') else None
            offre.type_contrat = request.POST.get('type_contrat')
            offre.nombre_postes = request.POST.get('nombre_postes', 1)
            offre.date_limite_candidature = request.POST.get('date_limite') if request.POST.get('date_limite') else None
            offre.description_poste = request.POST.get('description')
            offre.profil_recherche = request.POST.get('profil')
            offre.competences_requises = request.POST.get('competences')
            offre.experience_requise = request.POST.get('experience') if request.POST.get('experience') else None
            offre.formation_requise = request.POST.get('formation')
            offre.salaire_propose_min = request.POST.get('salaire_min') if request.POST.get('salaire_min') else None
            offre.salaire_propose_max = request.POST.get('salaire_max') if request.POST.get('salaire_max') else None
            offre.avantages = request.POST.get('avantages')
            offre.statut_offre = request.POST.get('statut')
            offre.responsable_recrutement_id = request.POST.get('responsable') if request.POST.get('responsable') else None
            offre.responsable_texte = request.POST.get('responsable_texte') if request.POST.get('responsable_texte') else None
            
            if 'image' in request.FILES:
                valider_image(request.FILES['image'])
                offre.image = request.FILES['image']
            if 'document_pdf' in request.FILES:
                valider_cv(request.FILES['document_pdf'])
                offre.document_pdf = request.FILES['document_pdf']
            offre.save()
            
            messages.success(request, 'Offre modifiée avec succès.')
            return redirect('recrutement:detail_offre', offre_uuid=offre.uuid)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    postes = Poste.objects.filter(entreprise=request.user.entreprise, actif=True)
    services = Service.objects.filter(entreprise=request.user.entreprise, actif=True)
    employes = Employe.objects.filter(entreprise=request.user.entreprise).order_by('nom', 'prenoms')
    
    return render(request, 'recrutement/offres/modifier.html', {
        'offre': offre,
        'postes': postes,
        'services': services,
        'employes': employes
    })


@login_required
@entreprise_active_required
def supprimer_offre(request, offre_uuid):
    """Supprimer une offre d'emploi"""
    try:
        offre = OffreEmploi.objects.get(uuid=offre_uuid, entreprise=request.user.entreprise)
    except OffreEmploi.DoesNotExist:
        messages.error(request, "L'offre d'emploi n'existe pas ou a déjà été supprimée.")
        return redirect('recrutement:offres')
    
    if request.method == 'POST':
        reference = offre.reference_offre
        intitule = offre.intitule_poste
        
        # Vérifier s'il y a des candidatures liées
        nb_candidatures = offre.candidatures.count()
        if nb_candidatures > 0:
            messages.warning(
                request, 
                f"L'offre {reference} a été supprimée avec {nb_candidatures} candidature(s) associée(s)."
            )
        else:
            messages.success(request, f"L'offre {reference} - {intitule} a été supprimée avec succès.")
        
        offre.delete()
        return redirect('recrutement:offres')
    
    # GET request - afficher une confirmation
    return render(request, 'recrutement/offres/confirmer_suppression.html', {
        'offre': offre
    })


# ============= CANDIDATURES =============

@login_required
@entreprise_active_required
def liste_candidatures(request):
    """Liste des candidatures"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    statut = request.GET.get('statut')
    offre_id = request.GET.get('offre')
    
    candidatures = Candidature.objects.filter(
        offre__entreprise=request.user.entreprise
    ).select_related('offre').order_by('-date_candidature')
    
    if statut:
        candidatures = candidatures.filter(statut_candidature=statut)
    if offre_id:
        candidatures = candidatures.filter(offre_id=offre_id)
    
    # Pagination - 50 par page
    paginator = Paginator(candidatures, 50)
    page = request.GET.get('page')
    try:
        candidatures_page = paginator.page(page)
    except PageNotAnInteger:
        candidatures_page = paginator.page(1)
    except EmptyPage:
        candidatures_page = paginator.page(paginator.num_pages)
    
    offres = OffreEmploi.objects.filter(
        entreprise=request.user.entreprise,
        statut_offre='ouverte'
    )
    
    return render(request, 'recrutement/candidatures/liste.html', {
        'candidatures': candidatures_page,
        'offres': offres,
        'total_candidatures': paginator.count,
    })


@login_required
@entreprise_active_required
def creer_candidature(request):
    """Créer une candidature"""
    if request.method == 'POST':
        try:
            # Générer un numéro unique
            numero = f"CAND-{date.today().year}-{''.join(random.choices(string.digits, k=5))}"

            offre = get_object_or_404(
                OffreEmploi,
                pk=request.POST.get('offre'),
                entreprise=request.user.entreprise,
            )
            
            candidature = Candidature.objects.create(
                offre=offre,
                numero_candidature=numero,
                civilite=request.POST.get('civilite'),
                nom=request.POST.get('nom'),
                prenoms=request.POST.get('prenoms'),
                date_naissance=request.POST.get('date_naissance') if request.POST.get('date_naissance') else None,
                nationalite=request.POST.get('nationalite'),
                telephone=request.POST.get('telephone'),
                email=request.POST.get('email'),
                adresse=request.POST.get('adresse'),
                formation_niveau=request.POST.get('formation'),
                experience_annees=request.POST.get('experience') if request.POST.get('experience') else None,
                statut_candidature='recue'
            )
            
            # Gérer les fichiers avec validation
            if request.FILES.get('cv'):
                try:
                    valider_cv(request.FILES['cv'])
                    candidature.cv_fichier = request.FILES['cv']
                except ValidationError as e:
                    messages.error(request, f'CV : {e.message}')
                    return redirect('recrutement:creer_candidature')
            if request.FILES.get('lettre'):
                try:
                    valider_cv(request.FILES['lettre'])
                    candidature.lettre_motivation = request.FILES['lettre']
                except ValidationError as e:
                    messages.error(request, f'Lettre : {e.message}')
                    return redirect('recrutement:creer_candidature')
            candidature.save()
            
            messages.success(request, f'Candidature {numero} enregistrée avec succès.')
            return redirect('recrutement:detail_candidature', pk=candidature.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
    
    offres = OffreEmploi.objects.filter(
        entreprise=request.user.entreprise,
        statut_offre='ouverte'
    )
    
    return render(request, 'recrutement/candidatures/creer.html', {
        'offres': offres
    })


@login_required
@entreprise_active_required
def detail_candidature(request, pk):
    """Détail d'une candidature"""
    candidature = get_object_or_404(Candidature, pk=pk, offre__entreprise=request.user.entreprise)
    entretiens = candidature.entretiens.all()
    
    return render(request, 'recrutement/candidatures/detail.html', {
        'candidature': candidature,
        'entretiens': entretiens
    })


@login_required
@entreprise_active_required
def supprimer_document_candidature(request, pk):
    """Supprimer un document d'une candidature (CV, lettre, autres)"""
    candidature = get_object_or_404(Candidature, pk=pk, offre__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        file_field = request.POST.get('file_field')
        
        if file_field == 'cv_fichier' and candidature.cv_fichier:
            candidature.cv_fichier.delete(save=False)
            candidature.cv_fichier = None
            candidature.save()
            messages.success(request, 'CV supprimé avec succès.')
        elif file_field == 'lettre_motivation' and candidature.lettre_motivation:
            candidature.lettre_motivation.delete(save=False)
            candidature.lettre_motivation = None
            candidature.save()
            messages.success(request, 'Lettre de motivation supprimée avec succès.')
        elif file_field == 'autres_documents' and candidature.autres_documents:
            candidature.autres_documents.delete(save=False)
            candidature.autres_documents = None
            candidature.save()
            messages.success(request, 'Document supprimé avec succès.')
        else:
            messages.error(request, 'Fichier non trouvé.')
    
    return redirect('recrutement:detail_candidature', pk=pk)


@login_required
@entreprise_active_required
def evaluer_candidature(request, pk):
    """Évaluer une candidature"""
    candidature = get_object_or_404(Candidature, pk=pk, offre__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'preselectionner':
            candidature.statut_candidature = 'preselectionne'
            messages.success(request, 'Candidature présélectionnée.')
        elif action == 'convoquer':
            candidature.statut_candidature = 'entretien'
            messages.success(request, 'Candidat convoqué en entretien.')
        elif action == 'retenir':
            candidature.statut_candidature = 'retenue'
            messages.success(request, 'Candidature retenue.')
        elif action == 'rejeter':
            candidature.statut_candidature = 'rejetee'
            messages.success(request, 'Candidature rejetée.')
        
        candidature.score_evaluation = request.POST.get('score') if request.POST.get('score') else None
        candidature.commentaires = request.POST.get('commentaires')
        candidature.save()
        
        return redirect('recrutement:detail_candidature', pk=candidature.pk)
    
    return render(request, 'recrutement/candidatures/evaluer.html', {
        'candidature': candidature
    })


# ============= ENTRETIENS =============

@login_required
@entreprise_active_required
def liste_entretiens(request):
    """Liste des entretiens"""
    entretiens = EntretienRecrutement.objects.filter(
        candidature__offre__entreprise=request.user.entreprise
    ).select_related('candidature', 'candidature__offre')
    
    return render(request, 'recrutement/entretiens/liste.html', {
        'entretiens': entretiens
    })


@login_required
@entreprise_active_required
def creer_entretien(request, candidature_id):
    """Planifier un entretien"""
    candidature = get_object_or_404(Candidature, pk=candidature_id, offre__entreprise=request.user.entreprise)
    
    if request.method == 'POST':
        try:
            entretien = EntretienRecrutement.objects.create(
                candidature=candidature,
                type_entretien=request.POST.get('type_entretien'),
                date_entretien=request.POST.get('date_entretien'),
                lieu_entretien=request.POST.get('lieu'),
                intervieweurs=request.POST.get('intervieweurs'),
                duree_minutes=request.POST.get('duree') if request.POST.get('duree') else None
            )
            
            # Mettre à jour le statut de la candidature
            candidature.statut_candidature = 'entretien'
            candidature.date_entretien = request.POST.get('date_entretien')
            candidature.save()
            
            messages.success(request, 'Entretien planifié avec succès.')
            return redirect('recrutement:detail_entretien', pk=entretien.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la planification : {str(e)}')
    
    return render(request, 'recrutement/entretiens/creer.html', {
        'candidature': candidature
    })


@login_required
@entreprise_active_required
def detail_entretien(request, pk):
    """Détail d'un entretien"""
    entretien = get_object_or_404(
        EntretienRecrutement,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise,
    )
    
    return render(request, 'recrutement/entretiens/detail.html', {
        'entretien': entretien
    })


@login_required
@entreprise_active_required
def evaluer_entretien(request, pk):
    """Évaluer un entretien"""
    entretien = get_object_or_404(
        EntretienRecrutement,
        pk=pk,
        candidature__offre__entreprise=request.user.entreprise,
    )
    
    if request.method == 'POST':
        try:
            entretien.evaluation_technique = request.POST.get('eval_technique') if request.POST.get('eval_technique') else None
            entretien.evaluation_comportementale = request.POST.get('eval_comportementale') if request.POST.get('eval_comportementale') else None
            entretien.evaluation_motivation = request.POST.get('eval_motivation') if request.POST.get('eval_motivation') else None
            
            # Calculer la note globale
            if all([entretien.evaluation_technique, entretien.evaluation_comportementale, entretien.evaluation_motivation]):
                entretien.note_globale = round(
                    (int(entretien.evaluation_technique) + 
                     int(entretien.evaluation_comportementale) + 
                     int(entretien.evaluation_motivation)) / 3
                )
            
            entretien.decision = request.POST.get('decision')
            entretien.commentaires = request.POST.get('commentaires')
            entretien.recommandations = request.POST.get('recommandations')
            entretien.save()
            
            messages.success(request, 'Évaluation enregistrée avec succès.')
            return redirect('recrutement:detail_entretien', pk=entretien.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'évaluation : {str(e)}')
    
    return render(request, 'recrutement/entretiens/evaluer.html', {
        'entretien': entretien
    })


# ============= TÉLÉCHARGEMENT SÉCURISÉ =============

@login_required
@entreprise_active_required
def telecharger_document_candidature(request, pk, type_doc):
    """Téléchargement sécurisé des documents de candidature (CV, lettre, autres)."""
    import os
    from django.http import FileResponse, Http404

    candidature = get_object_or_404(Candidature, pk=pk, offre__entreprise=request.user.entreprise)

    champs = {
        'cv': ('cv_fichier', f"CV_{candidature.nom}_{candidature.prenoms}"),
        'lettre': ('lettre_motivation', f"Lettre_{candidature.nom}_{candidature.prenoms}"),
        'autre': ('autres_documents', f"Doc_{candidature.nom}_{candidature.prenoms}"),
    }

    if type_doc not in champs:
        raise Http404("Type de document invalide.")

    champ, nom_base = champs[type_doc]
    fichier_field = getattr(candidature, champ)

    if not fichier_field:
        raise Http404("Aucun fichier disponible.")

    chemin = fichier_field.path
    if not os.path.exists(chemin):
        raise Http404("Fichier introuvable sur le serveur.")

    ext = os.path.splitext(chemin)[1]
    return FileResponse(
        open(chemin, 'rb'),
        as_attachment=True,
        filename=f"{nom_base}{ext}",
    )
