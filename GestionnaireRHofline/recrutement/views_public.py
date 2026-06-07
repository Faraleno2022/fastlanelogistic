"""
Vues publiques pour les candidatures - accessibles sans authentification
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
import uuid

from .models import OffreEmploi, Candidature
from core.validators import valider_cv, valider_image_document


def offre_detail_public(request, offre_uuid):
    """Détail d'une offre d'emploi - vue publique"""
    offre = get_object_or_404(OffreEmploi, uuid=offre_uuid, statut_offre='ouverte')
    
    # Vérifier si l'offre est expirée (pour affichage conditionnel)
    est_expiree = offre.date_limite_candidature and offre.date_limite_candidature < date.today()
    
    return render(request, 'recrutement/public/offre_detail.html', {
        'offre': offre,
        'est_expiree': est_expiree,
    })


def postuler(request, offre_uuid):
    """Formulaire de candidature publique"""
    offre = get_object_or_404(OffreEmploi, uuid=offre_uuid, statut_offre='ouverte')
    
    # Vérifier si la date limite n'est pas dépassée
    if offre.date_limite_candidature and offre.date_limite_candidature < date.today():
        messages.error(request, "La date limite de candidature est dépassée.")
        return redirect('recrutement:offre_public', offre_uuid=offre_uuid)
    
    if request.method == 'POST':
        # Générer un numéro de candidature unique
        numero = f"CAND-{offre.reference_offre}-{uuid.uuid4().hex[:6].upper()}"
        
        # Valider les fichiers uploadés avant de créer la candidature
        erreurs_fichiers = []
        fichiers = {}
        
        if 'cv_fichier' in request.FILES:
            try:
                valider_cv(request.FILES['cv_fichier'])
                fichiers['cv_fichier'] = request.FILES['cv_fichier']
            except ValidationError as e:
                erreurs_fichiers.append(f"CV : {e.message}")
        
        if 'lettre_motivation' in request.FILES:
            try:
                valider_cv(request.FILES['lettre_motivation'])
                fichiers['lettre_motivation'] = request.FILES['lettre_motivation']
            except ValidationError as e:
                erreurs_fichiers.append(f"Lettre de motivation : {e.message}")
        
        if 'autres_documents' in request.FILES:
            try:
                valider_image_document(request.FILES['autres_documents'])
                fichiers['autres_documents'] = request.FILES['autres_documents']
            except ValidationError as e:
                erreurs_fichiers.append(f"Autre document : {e.message}")
        
        if erreurs_fichiers:
            for err in erreurs_fichiers:
                messages.error(request, err)
            return render(request, 'recrutement/public/postuler.html', {'offre': offre})
        
        # Créer la candidature
        candidature = Candidature(
            offre=offre,
            numero_candidature=numero,
            civilite=request.POST.get('civilite', ''),
            nom=request.POST.get('nom', ''),
            prenoms=request.POST.get('prenoms', ''),
            email=request.POST.get('email', ''),
            telephone=request.POST.get('telephone', ''),
            date_naissance=request.POST.get('date_naissance') or None,
            nationalite=request.POST.get('nationalite', ''),
            adresse=request.POST.get('adresse', ''),
            formation_niveau=request.POST.get('formation_niveau', ''),
            experience_annees=request.POST.get('experience_annees') or None,
            statut_candidature='recue',
        )
        
        # Assigner les fichiers validés
        for champ, fichier in fichiers.items():
            setattr(candidature, champ, fichier)
        
        candidature.save()
        
        messages.success(
            request, 
            f"Votre candidature a été enregistrée avec succès! "
            f"Référence: {numero}. L'entreprise {offre.entreprise.nom_entreprise} vous contactera."
        )
        return redirect('recrutement:candidature_confirmee', numero=numero)
    
    return render(request, 'recrutement/public/postuler.html', {
        'offre': offre,
    })


def candidature_confirmee(request, numero):
    """Page de confirmation après candidature"""
    candidature = get_object_or_404(Candidature, numero_candidature=numero)
    
    return render(request, 'recrutement/public/confirmation.html', {
        'candidature': candidature,
    })
