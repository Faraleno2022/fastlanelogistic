from django.db import models
from django.utils import timezone
from datetime import date, timedelta
import uuid

from .models import DecisionEmbauche
from employes.models import Employe


class ProcessusIntegration(models.Model):
    """Processus d'intégration des nouveaux employés"""
    ETAPES = (
        ('documents_pre_embauche', 'Documents pré-embauche'),
        ('signature_contrat', 'Signature contrat'),
        ('accueil_premier_jour', 'Accueil premier jour'),
        ('formation_securite', 'Formation sécurité'),
        ('presentation_equipe', 'Présentation équipe'),
        ('formation_poste', 'Formation au poste'),
        ('evaluation_periode_essai', 'Évaluation période d\'essai'),
        ('integration_terminee', 'Intégration terminée'),
    )
    
    STATUTS_ETAPE = (
        ('a_faire', 'À faire'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('bloquee', 'Bloquée'),
    )
    
    decision_embauche = models.OneToOneField(DecisionEmbauche, on_delete=models.CASCADE, related_name='processus_integration')
    employe_cree = models.OneToOneField(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='processus_integration')
    
    # Responsables
    responsable_integration = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='integrations_gerees')
    tuteur_assigne = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutorats')
    
    # Dates importantes
    date_debut_prevue = models.DateField()
    date_debut_effective = models.DateField(null=True, blank=True)
    date_fin_prevue = models.DateField()
    date_fin_effective = models.DateField(null=True, blank=True)
    
    # Suivi
    etape_actuelle = models.CharField(max_length=30, choices=ETAPES, default='documents_pre_embauche')
    pourcentage_completion = models.IntegerField(default=0)
    
    # Évaluation
    note_integration = models.IntegerField(null=True, blank=True, help_text="Note sur 10")
    commentaires_integration = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'processus_integration'
        verbose_name = 'Processus d\'intégration'
        verbose_name_plural = 'Processus d\'intégration'
    
    def __str__(self):
        nom_candidat = f"{self.decision_embauche.candidature.nom} {self.decision_embauche.candidature.prenoms}"
        return f"Intégration - {nom_candidat}"
    
    def calculer_pourcentage(self):
        """Calcule le pourcentage de completion basé sur les étapes terminées"""
        etapes_terminees = self.etapes_integration.filter(statut='terminee').count()
        total_etapes = self.etapes_integration.count()
        if total_etapes > 0:
            self.pourcentage_completion = int((etapes_terminees / total_etapes) * 100)
            self.save()
        return self.pourcentage_completion


class EtapeIntegration(models.Model):
    """Étapes individuelles du processus d'intégration"""
    processus = models.ForeignKey(ProcessusIntegration, on_delete=models.CASCADE, related_name='etapes_integration')
    nom_etape = models.CharField(max_length=30, choices=ProcessusIntegration.ETAPES)
    description = models.TextField()
    
    # Planning
    date_prevue = models.DateField()
    date_realisation = models.DateField(null=True, blank=True)
    duree_estimee_heures = models.IntegerField(default=1)
    
    # Responsabilité
    responsable = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True)
    statut = models.CharField(max_length=20, choices=ProcessusIntegration.STATUTS_ETAPE, default='a_faire')
    
    # Documents et validation
    documents_requis = models.TextField(blank=True, null=True)
    documents_fournis = models.BooleanField(default=False)
    validation_requise = models.BooleanField(default=False)
    validee_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='etapes_validees')
    
    # Suivi
    commentaires = models.TextField(blank=True, null=True)
    ordre = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'etapes_integration'
        verbose_name = 'Étape d\'intégration'
        verbose_name_plural = 'Étapes d\'intégration'
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.processus} - {self.get_nom_etape_display()}"
    
    def marquer_terminee(self, employe_validateur=None):
        """Marque l'étape comme terminée"""
        self.statut = 'terminee'
        self.date_realisation = date.today()
        if employe_validateur:
            self.validee_par = employe_validateur
        self.save()
        
        # Mettre à jour le pourcentage du processus
        self.processus.calculer_pourcentage()


class AlerteIntegration(models.Model):
    """Alertes liées au processus d'intégration"""
    TYPES_ALERTE = (
        ('retard_etape', 'Retard sur étape'),
        ('document_manquant', 'Document manquant'),
        ('validation_requise', 'Validation requise'),
        ('fin_periode_essai', 'Fin période d\'essai'),
    )
    
    processus = models.ForeignKey(ProcessusIntegration, on_delete=models.CASCADE, related_name='alertes')
    type_alerte = models.CharField(max_length=30, choices=TYPES_ALERTE)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    
    date_alerte = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField()
    
    # Traitement
    traitee = models.BooleanField(default=False)
    traitee_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alertes_integration'
        verbose_name = 'Alerte intégration'
        verbose_name_plural = 'Alertes intégration'
        ordering = ['date_echeance']
    
    def __str__(self):
        return f"{self.processus} - {self.titre}"
