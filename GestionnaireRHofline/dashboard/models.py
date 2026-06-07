from django.db import models
from django.utils import timezone
from core.models import Entreprise, Utilisateur


class DashboardConfig(models.Model):
    """Configuration pour le dashboard"""
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='dashboard_configs', null=True, blank=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='dashboard_configs', null=True, blank=True)
    widgets_actifs = models.JSONField(default=list, help_text="Liste des widgets activés")
    disposition = models.JSONField(default=dict, help_text="Disposition des widgets")
    theme = models.CharField(max_length=20, default='light')
    
    class Meta:
        db_table = 'dashboard_config'
        verbose_name = 'Configuration dashboard'


# ============= INDICATEURS RH =============

class IndicateurRH(models.Model):
    """Indicateurs RH calculés périodiquement"""
    TYPES_INDICATEUR = (
        ('effectif', 'Effectif'),
        ('turnover', 'Turnover'),
        ('absenteisme', 'Absentéisme'),
        ('masse_salariale', 'Masse salariale'),
        ('formation', 'Formation'),
        ('recrutement', 'Recrutement'),
        ('heures_sup', 'Heures supplémentaires'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='indicateurs_rh')
    type_indicateur = models.CharField(max_length=30, choices=TYPES_INDICATEUR)
    annee = models.IntegerField()
    mois = models.IntegerField(null=True, blank=True)
    
    # Valeurs
    valeur = models.DecimalField(max_digits=15, decimal_places=2)
    valeur_precedente = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    variation_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Détails
    details = models.JSONField(default=dict, help_text="Détails du calcul")
    
    date_calcul = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'indicateurs_rh'
        verbose_name = 'Indicateur RH'
        verbose_name_plural = 'Indicateurs RH'
        unique_together = ['entreprise', 'type_indicateur', 'annee', 'mois']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        periode = f"{self.mois}/{self.annee}" if self.mois else str(self.annee)
        return f"{self.get_type_indicateur_display()} - {periode}: {self.valeur}"


class RapportLegal(models.Model):
    """Rapports légaux obligatoires"""
    TYPES_RAPPORT = (
        ('registre_personnel', 'Registre du personnel'),
        ('etat_presence', 'État de présence mensuel'),
        ('bilan_social', 'Bilan social annuel'),
        ('rapport_formation', 'Rapport de formation'),
        ('rapport_accidents', 'Rapport accidents du travail'),
        ('rapport_inspection', 'Rapport inspection du travail'),
        ('das', 'Déclaration Annuelle des Salaires'),
    )
    STATUTS = (
        ('brouillon', 'Brouillon'),
        ('genere', 'Généré'),
        ('valide', 'Validé'),
        ('transmis', 'Transmis'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='rapports_legaux')
    type_rapport = models.CharField(max_length=30, choices=TYPES_RAPPORT)
    annee = models.IntegerField()
    mois = models.IntegerField(null=True, blank=True)
    reference = models.CharField(max_length=50, unique=True)
    
    # Contenu
    donnees = models.JSONField(default=dict, help_text="Données du rapport")
    fichier_rapport = models.FileField(upload_to='rapports/', null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_generation = models.DateTimeField(null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_transmission = models.DateTimeField(null=True, blank=True)
    
    genere_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='rapports_generes')
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'rapports_legaux'
        verbose_name = 'Rapport légal'
        verbose_name_plural = 'Rapports légaux'
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"{self.get_type_rapport_display()} - {self.reference}"


# ============= ARCHIVAGE & CONFORMITÉ =============

class ArchiveDocument(models.Model):
    """Archivage des documents RH"""
    TYPES_DOCUMENT = (
        ('bulletin_paie', 'Bulletin de paie'),
        ('contrat', 'Contrat de travail'),
        ('avenant', 'Avenant'),
        ('declaration', 'Déclaration sociale'),
        ('certificat', 'Certificat'),
        ('attestation', 'Attestation'),
        ('rapport', 'Rapport'),
        ('autre', 'Autre'),
    )
    DUREES_CONSERVATION = (
        (5, '5 ans (paie)'),
        (10, '10 ans (contrats)'),
        (30, '30 ans (accidents)'),
        (50, '50 ans (retraite)'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='archives')
    type_document = models.CharField(max_length=30, choices=TYPES_DOCUMENT)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Fichier
    fichier = models.FileField(upload_to='archives/')
    taille_fichier = models.IntegerField(null=True, blank=True)
    hash_fichier = models.CharField(max_length=64, blank=True, null=True, help_text="Hash SHA256 pour intégrité")
    
    # Dates
    date_document = models.DateField()
    date_archivage = models.DateTimeField(auto_now_add=True)
    duree_conservation_ans = models.IntegerField(default=10)
    date_destruction_prevue = models.DateField(null=True, blank=True)
    
    # Employé concerné (si applicable)
    employe = models.ForeignKey('employes.Employe', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_archives')
    
    archive_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'archives_documents'
        verbose_name = 'Document archivé'
        verbose_name_plural = 'Documents archivés'
        ordering = ['-date_archivage']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.reference}"


class TraceAudit(models.Model):
    """Trace d'audit pour la conformité"""
    ACTIONS = (
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('consultation', 'Consultation'),
        ('export', 'Export'),
        ('impression', 'Impression'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='traces_audit')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    
    action = models.CharField(max_length=20, choices=ACTIONS)
    module = models.CharField(max_length=50, help_text="Module concerné (employes, paie, etc.)")
    table_concernee = models.CharField(max_length=50)
    enregistrement_id = models.IntegerField(null=True, blank=True)
    
    description = models.TextField()
    donnees_avant = models.JSONField(null=True, blank=True)
    donnees_apres = models.JSONField(null=True, blank=True)
    
    date_action = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'traces_audit'
        verbose_name = 'Trace d\'audit'
        verbose_name_plural = 'Traces d\'audit'
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.utilisateur} - {self.get_action_display()} - {self.table_concernee}"
