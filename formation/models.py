from django.db import models
from decimal import Decimal
from employes.models import Employe
from core.models import Entreprise


class CatalogueFormation(models.Model):
    """Catalogue des formations disponibles"""
    TYPES = (
        ('interne', 'Interne'),
        ('externe', 'Externe'),
        ('en_ligne', 'En ligne'),
        ('certifiante', 'Certifiante'),
    )
    
    DOMAINES = (
        ('technique', 'Technique'),
        ('management', 'Management'),
        ('securite', 'Sécurité'),
        ('informatique', 'Informatique'),
        ('langues', 'Langues'),
        ('soft_skills', 'Soft Skills'),
        ('reglementaire', 'Réglementaire'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='catalogue_formations', null=True, blank=True)
    code_formation = models.CharField(max_length=20, unique=True)
    intitule = models.CharField(max_length=200)
    type_formation = models.CharField(max_length=500)  # Liste déroulante + saisie libre
    domaine = models.CharField(max_length=255)  # Liste déroulante + saisie libre
    description = models.TextField(blank=True, null=True)
    objectifs = models.TextField(blank=True, null=True)
    contenu = models.TextField(blank=True, null=True)
    duree_jours = models.IntegerField(help_text='Durée en jours')
    duree_heures = models.IntegerField(help_text='Durée en heures')
    prerequis = models.TextField(blank=True, null=True)
    organisme_formateur = models.CharField(max_length=200, blank=True, null=True)
    cout_unitaire = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='formations/', blank=True, null=True, help_text="Image de présentation de la formation")
    publiee = models.BooleanField(default=False, help_text="Publier sur la page d'accueil publique")
    date_publication = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'catalogue_formations'
        verbose_name = 'Formation (Catalogue)'
        verbose_name_plural = 'Catalogue des Formations'
        ordering = ['intitule']
    
    def __str__(self):
        return f"{self.code_formation} - {self.intitule}"


class InscriptionFormationPublic(models.Model):
    """Inscriptions publiques aux formations (visiteurs non connectés)"""
    STATUTS = (
        ('en_attente', 'En attente'),
        ('contacte', 'Contacté'),
        ('confirme', 'Confirmé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    )
    
    formation = models.ForeignKey(CatalogueFormation, on_delete=models.CASCADE, related_name='inscriptions_publiques')
    session = models.ForeignKey('SessionFormation', on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions_publiques')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    entreprise = models.CharField(max_length=200, blank=True, null=True)
    fonction = models.CharField(max_length=100, blank=True, null=True)
    motivation = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_inscription = models.DateTimeField(auto_now_add=True)
    notes_admin = models.TextField(blank=True, null=True, help_text="Notes internes")
    
    class Meta:
        db_table = 'inscriptions_formation_public'
        verbose_name = 'Inscription Formation (Public)'
        verbose_name_plural = 'Inscriptions Formation (Public)'
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.formation.intitule}"


class ParticipantFormationCabinet(models.Model):
    """Registre des participants formes au cabinet avec attestation."""
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='participants_formations_cabinet'
    )
    nom_participant = models.CharField(max_length=200)
    titre_formation = models.CharField(max_length=255)
    date_formation = models.DateField()
    numero_identite_attestation = models.CharField(max_length=100)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    observations = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'participants_formations_cabinet'
        verbose_name = 'Participant formation cabinet'
        verbose_name_plural = 'Participants formations cabinet'
        ordering = ['-date_formation', 'nom_participant']
        unique_together = ['entreprise', 'numero_identite_attestation']
        indexes = [
            models.Index(fields=['entreprise', 'date_formation'], name='idx_part_form_cab_date'),
            models.Index(fields=['entreprise', 'numero_identite_attestation'], name='idx_part_form_cab_att'),
        ]

    def __str__(self):
        return f"{self.nom_participant} - {self.titre_formation}"


class SessionFormation(models.Model):
    """Sessions de formation planifiées"""
    STATUTS = (
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    )
    
    formation = models.ForeignKey(CatalogueFormation, on_delete=models.CASCADE, related_name='sessions')
    plan_formation = models.ForeignKey('PlanFormation', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    reference_session = models.CharField(max_length=50, unique=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    lieu = models.CharField(max_length=200)
    formateur = models.CharField(max_length=200, blank=True, null=True)
    nombre_places = models.IntegerField(default=10)
    nombre_inscrits = models.IntegerField(default=0)
    cout_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifiee')
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'sessions_formation'
        verbose_name = 'Session de Formation'
        verbose_name_plural = 'Sessions de Formation'
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['formation', 'statut'], name='idx_session_form_statut'),
            models.Index(fields=['date_debut'], name='idx_session_date_debut'),
        ]
    
    def __str__(self):
        return f"{self.reference_session} - {self.formation.intitule}"
    
    @property
    def places_disponibles(self):
        return self.nombre_places - self.nombre_inscrits


class InscriptionFormation(models.Model):
    """Inscriptions des employés aux formations"""
    STATUTS = (
        ('inscrit', 'Inscrit'),
        ('confirme', 'Confirmé'),
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('annule', 'Annulé'),
    )
    
    session = models.ForeignKey(SessionFormation, on_delete=models.CASCADE, related_name='inscriptions')
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='inscriptions_formation')
    date_inscription = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='inscrit')
    note_evaluation = models.IntegerField(blank=True, null=True, help_text='Note sur 100')
    appreciation = models.CharField(max_length=50, blank=True, null=True)
    certificat_obtenu = models.BooleanField(default=False)
    commentaires = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'inscriptions_formation'
        verbose_name = 'Inscription Formation'
        verbose_name_plural = 'Inscriptions Formation'
        unique_together = ['session', 'employe']
        ordering = ['-date_inscription']
        indexes = [
            models.Index(fields=['session', 'statut'], name='idx_inscription_sess_stat'),
            models.Index(fields=['employe'], name='idx_inscription_employe'),
        ]
    
    def __str__(self):
        return f"{self.employe} - {self.session.formation.intitule}"


class EvaluationFormation(models.Model):
    """Évaluation des formations par les participants"""
    inscription = models.OneToOneField(InscriptionFormation, on_delete=models.CASCADE, related_name='evaluation')
    date_evaluation = models.DateField(auto_now_add=True)
    
    # Évaluation du contenu
    note_contenu = models.IntegerField(help_text='Note sur 5')
    note_formateur = models.IntegerField(help_text='Note sur 5')
    note_organisation = models.IntegerField(help_text='Note sur 5')
    note_moyens = models.IntegerField(help_text='Note sur 5')
    note_globale = models.IntegerField(help_text='Note sur 5')
    
    # Commentaires
    points_forts = models.TextField(blank=True, null=True)
    points_ameliorer = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    
    # Utilité
    competences_acquises = models.TextField(blank=True, null=True)
    application_travail = models.BooleanField(default=True)
    recommandation = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'evaluations_formation'
        verbose_name = 'Évaluation Formation'
        verbose_name_plural = 'Évaluations Formation'
        ordering = ['-date_evaluation']
    
    def __str__(self):
        return f"Évaluation - {self.inscription.employe} - {self.inscription.session.formation.intitule}"


class PlanFormation(models.Model):
    """Plan de formation annuel"""
    STATUTS = (
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('en_cours', 'En cours'),
        ('cloture', 'Clôturé'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='plans_formation', null=True, blank=True)
    annee = models.IntegerField()
    budget_total = models.DecimalField(max_digits=15, decimal_places=2)
    budget_consomme = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    objectifs = models.TextField(blank=True, null=True)
    date_validation = models.DateField(blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'plans_formation'
        verbose_name = 'Plan de Formation'
        verbose_name_plural = 'Plans de Formation'
        unique_together = ['entreprise', 'annee']
        ordering = ['-annee']
    
    def __str__(self):
        return f"Plan de Formation {self.annee}"
    
    @property
    def budget_restant(self):
        return self.budget_total - self.budget_consomme
    
    @property
    def taux_consommation(self):
        if self.budget_total > 0:
            return round((self.budget_consomme / self.budget_total) * 100, 2)
        return 0
