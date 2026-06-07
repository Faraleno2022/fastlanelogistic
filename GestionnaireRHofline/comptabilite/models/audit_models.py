# ============================================================================
# AUDIT & CONFORMITÉ (Phase 2 Week 2)
# ============================================================================

class RapportAudit(models.Model):
    """Rapports d'audit comptable"""
    
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('PUBLIE', 'Publié'),
    ]
    
    RISQUE_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYEN', 'Moyen'),
        ('ELEVE', 'Élevé'),
        ('CRITIQUE', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='rapports_audit')
    
    # Informations générales
    code = models.CharField(max_length=50, unique=True)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    date_publication = models.DateField(null=True, blank=True)
    
    # Contenu
    objectifs = models.TextField(help_text='Objectifs de l\'audit')
    perimetre = models.TextField(help_text='Périmètre de l\'audit')
    resultats = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    recommandations = models.TextField(blank=True)
    
    # Méta
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PLANIFIE')
    niveau_risque_global = models.CharField(max_length=20, choices=RISQUE_CHOICES, default='MOYEN')
    auditeur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='rapports_audites')
    responsable_correction = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='corrections_audit')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='rapports_audit_crees')
    
    class Meta:
        db_table = 'comptabilite_rapport_audit'
        verbose_name = 'Rapport d\'audit'
        verbose_name_plural = 'Rapports d\'audit'
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['entreprise', 'statut']),
            models.Index(fields=['date_debut']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"Audit {self.code}: {self.titre}"


class AlerteNonConformite(models.Model):
    """Alertes de non-conformité détectées lors des audits"""
    
    SEVERITE_CHOICES = [
        ('MINEURE', 'Mineure'),
        ('MAJEURE', 'Majeure'),
        ('CRITIQUE', 'Critique'),
    ]
    
    STATUT_CHOICES = [
        ('DETECTEE', 'Détectée'),
        ('EN_CORRECTION', 'En correction'),
        ('CORRIGEE', 'Corrigée'),
        ('VERIFIEE', 'Vérifiée'),
        ('ACCEPTEE', 'Acceptée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='alertes_non_conformite')
    rapport = models.ForeignKey(RapportAudit, on_delete=models.CASCADE, related_name='alertes')
    
    # Identifiant
    numero_alerte = models.CharField(max_length=50)
    titre = models.CharField(max_length=255)
    description = models.TextField()
    
    # Gravité
    severite = models.CharField(max_length=20, choices=SEVERITE_CHOICES)
    domaine = models.CharField(max_length=100, help_text='Domaine affecté: TVA, Comptabilité, etc.')
    
    # Correction
    plan_action = models.TextField(blank=True)
    date_correction_prevue = models.DateField(null=True, blank=True)
    date_correction_reelle = models.DateField(null=True, blank=True)
    
    # Suivi
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DETECTEE')
    responsable_correction = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    observations = models.TextField(blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comptabilite_alerte_non_conformite'
        verbose_name = 'Alerte de non-conformité'
        verbose_name_plural = 'Alertes de non-conformité'
        ordering = ['-date_creation']
        unique_together = ['rapport', 'numero_alerte']
        indexes = [
            models.Index(fields=['entreprise', 'severite']),
            models.Index(fields=['statut']),
            models.Index(fields=['date_correction_prevue']),
        ]
    
    def __str__(self):
        return f"Alerte {self.numero_alerte}: {self.titre}"


class ReglesConformite(models.Model):
    """Règles de conformité à vérifier régulièrement"""
    
    PERIODICITE_CHOICES = [
        ('MENSUELLE', 'Mensuelle'),
        ('TRIMESTRIELLE', 'Trimestrielle'),
        ('SEMESTRIELLE', 'Semestrielle'),
        ('ANNUELLE', 'Annuelle'),
        ('A_LA_DEMANDE', 'À la demande'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='regles_conformite')
    
    # Identification
    code = models.CharField(max_length=50)
    nom = models.CharField(max_length=255)
    description = models.TextField()
    
    # Contenu
    critere_conformite = models.TextField(help_text='Critère exact à vérifier')
    consequence_non_conformite = models.TextField()
    documentation_requise = models.TextField(blank=True)
    
    # Paramètres
    periodicite = models.CharField(max_length=20, choices=PERIODICITE_CHOICES)
    module_concerne = models.CharField(max_length=100, help_text='TVA, Paie, Temps, etc.')
    criticite = models.CharField(max_length=20, choices=[
        ('FAIBLE', 'Faible'),
        ('MOYEN', 'Moyen'),
        ('ELEVE', 'Élevé'),
        ('CRITIQUE', 'Critique'),
    ])
    
    # Statut
    actif = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='regles_conformite_creees')
    
    class Meta:
        db_table = 'comptabilite_regles_conformite'
        verbose_name = 'Règle de conformité'
        verbose_name_plural = 'Règles de conformité'
        ordering = ['module_concerne', 'code']
        unique_together = ['entreprise', 'code']
        indexes = [
            models.Index(fields=['entreprise', 'module_concerne']),
            models.Index(fields=['actif']),
        ]
    
    def __str__(self):
        return f"{self.code}: {self.nom}"


class HistoriqueModification(models.Model):
    """Historique détaillé des modifications comptables"""
    
    TYPE_OBJET_CHOICES = [
        ('DECLARATION_TVA', 'Déclaration TVA'),
        ('LIGNE_TVA', 'Ligne déclaration TVA'),
        ('ECRITURE', 'Écriture comptable'),
        ('FACTURE', 'Facture'),
        ('REGLEMENT', 'Règlement'),
        ('RAPPORT_AUDIT', 'Rapport d\'audit'),
        ('ALERTE', 'Alerte non-conformité'),
        ('AUTRE', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='historiques_modification')
    
    # Objet modifié
    type_objet = models.CharField(max_length=50, choices=TYPE_OBJET_CHOICES)
    id_objet = models.CharField(max_length=100, help_text='UUID ou ID de l\'objet modifié')
    nom_objet = models.CharField(max_length=255, help_text='Nom/libellé de l\'objet')
    
    # Modification
    action = models.CharField(max_length=20, choices=[
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('APPROVE', 'Approbation'),
        ('REJECT', 'Rejet'),
        ('REOPEN', 'Réouverture'),
    ])
    
    # Contenu
    champ_modifie = models.CharField(max_length=100, blank=True, help_text='Champ spécifique modifié')
    valeur_ancienne = models.TextField(blank=True)
    valeur_nouvelle = models.TextField(blank=True)
    description_modification = models.TextField(blank=True)
    
    # Justification
    motif = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text='Référence: N° ticket, N° demande, etc.')
    
    # Utilisateur
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='modifications_historique')
    
    # Date
    date_modification = models.DateTimeField(auto_now_add=True)
    
    # Audit
    ip_adresse = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'comptabilite_historique_modification'
        verbose_name = 'Historique de modification'
        verbose_name_plural = 'Historiques de modification'
        ordering = ['-date_modification']
        indexes = [
            models.Index(fields=['entreprise', 'type_objet']),
            models.Index(fields=['utilisateur', 'date_modification']),
            models.Index(fields=['id_objet']),
            models.Index(fields=['date_modification']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} {self.nom_objet} ({self.date_modification.strftime('%d/%m/%Y %H:%M')})"
