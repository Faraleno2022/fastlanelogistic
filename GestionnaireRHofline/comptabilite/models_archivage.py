"""
Module Documentation & Archivage Comptable
Archivage documents, pièces justificatives, cycle de vie, rétention, traçabilité
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur
from .models import ExerciceComptable, EcritureComptable, Facture


class ClassementDocument(models.Model):
    """Classification hiérarchique des documents"""
    TYPES_CLASSEMENT = [
        ('comptable', 'Documents comptables'),
        ('fiscal', 'Documents fiscaux'),
        ('social', 'Documents sociaux'),
        ('juridique', 'Documents juridiques'),
        ('commercial', 'Documents commerciaux'),
        ('technique', 'Documents techniques'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='classements_documents')
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    type_classement = models.CharField(max_length=20, choices=TYPES_CLASSEMENT)
    description = models.TextField(blank=True, null=True)
    
    # Hiérarchie
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sous_classements')
    niveau = models.IntegerField(default=1)
    chemin = models.CharField(max_length=500, blank=True, null=True,
                              help_text='Chemin complet: parent/enfant/...')
    
    # Rétention par défaut
    duree_retention_annees = models.IntegerField(default=10)
    
    # Statut
    est_actif = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'archivage_classement'
        verbose_name = 'Classement document'
        verbose_name_plural = 'Classements documents'
        unique_together = ['entreprise', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"


class PolitiqueRetention(models.Model):
    """Politique de rétention des documents"""
    TYPES_DOCUMENT = [
        ('facture_vente', 'Factures de vente'),
        ('facture_achat', 'Factures d\'achat'),
        ('bulletin_paie', 'Bulletins de paie'),
        ('declaration_fiscale', 'Déclarations fiscales'),
        ('declaration_sociale', 'Déclarations sociales'),
        ('contrat', 'Contrats'),
        ('ecriture_comptable', 'Écritures comptables'),
        ('releve_bancaire', 'Relevés bancaires'),
        ('piece_caisse', 'Pièces de caisse'),
        ('inventaire', 'Inventaires'),
        ('rapport_audit', 'Rapports d\'audit'),
        ('correspondance', 'Correspondances'),
        ('autre', 'Autre'),
    ]
    BASES_LEGALES = [
        ('code_commerce', 'Code de Commerce'),
        ('code_travail', 'Code du Travail'),
        ('code_fiscal', 'Code Général des Impôts'),
        ('code_securite_sociale', 'Code Sécurité Sociale'),
        ('reglementation_interne', 'Réglementation interne'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='politiques_retention')
    
    # Type de document
    type_document = models.CharField(max_length=30, choices=TYPES_DOCUMENT)
    description = models.TextField(blank=True, null=True)
    
    # Durée de conservation
    duree_conservation_annees = models.IntegerField(default=10)
    base_legale = models.CharField(max_length=30, choices=BASES_LEGALES)
    reference_legale = models.CharField(max_length=200, blank=True, null=True,
                                        help_text='Article de loi ou référence')
    
    # Actions à échéance
    action_expiration = models.CharField(max_length=20, choices=[
        ('archiver', 'Archiver définitivement'),
        ('detruire', 'Détruire'),
        ('reviser', 'Réviser'),
    ], default='archiver')
    
    # Notification
    alerte_avant_expiration_jours = models.IntegerField(default=90)
    
    # Statut
    est_actif = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'archivage_politique_retention'
        verbose_name = 'Politique de rétention'
        verbose_name_plural = 'Politiques de rétention'
        unique_together = ['entreprise', 'type_document']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.duree_conservation_annees} ans"


class ArchiveDocument(models.Model):
    """Documents archivés"""
    STATUTS = [
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
        ('a_detruire', 'À détruire'),
        ('detruit', 'Détruit'),
    ]
    FORMATS = [
        ('pdf', 'PDF'),
        ('image', 'Image (JPG, PNG)'),
        ('excel', 'Excel'),
        ('word', 'Word'),
        ('xml', 'XML'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='archives_documents')
    
    # Classification
    classement = models.ForeignKey(ClassementDocument, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='documents')
    politique_retention = models.ForeignKey(PolitiqueRetention, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='documents')
    
    # Identification
    reference = models.CharField(max_length=100)
    titre = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    
    # Fichier
    fichier = models.FileField(upload_to='archives/%Y/%m/')
    format_fichier = models.CharField(max_length=10, choices=FORMATS)
    taille_octets = models.BigIntegerField(default=0)
    hash_fichier = models.CharField(max_length=64, blank=True, null=True,
                                    help_text='SHA-256 pour intégrité')
    
    # Métadonnées
    date_document = models.DateField()
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='documents_archives')
    
    # Liens optionnels
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='documents_archives')
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='documents_archives')
    
    # Rétention
    date_archivage = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='actif')
    
    # Confidentialité
    niveau_confidentialite = models.CharField(max_length=15, choices=[
        ('public', 'Public'),
        ('interne', 'Interne'),
        ('confidentiel', 'Confidentiel'),
        ('secret', 'Secret'),
    ], default='interne')
    
    # Audit
    archive_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='documents_archives')
    
    class Meta:
        db_table = 'archivage_document'
        verbose_name = 'Document archivé'
        verbose_name_plural = 'Documents archivés'
        ordering = ['-date_archivage']
        indexes = [
            models.Index(fields=['entreprise', 'statut']),
            models.Index(fields=['date_expiration']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class MatricePiecesJustificatives(models.Model):
    """Matrice des pièces justificatives requises par type d'opération"""
    TYPES_OPERATION = [
        ('achat', 'Achat'),
        ('vente', 'Vente'),
        ('encaissement', 'Encaissement'),
        ('decaissement', 'Décaissement'),
        ('paie', 'Paie'),
        ('immobilisation', 'Immobilisation'),
        ('stock', 'Stock'),
        ('od', 'Opération diverse'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='matrices_pieces')
    
    # Type d'opération
    type_operation = models.CharField(max_length=20, choices=TYPES_OPERATION)
    description = models.TextField(blank=True, null=True)
    
    # Pièces requises
    pieces_obligatoires = models.JSONField(default=list,
                                           help_text='Liste des pièces obligatoires')
    pieces_optionnelles = models.JSONField(default=list,
                                           help_text='Liste des pièces optionnelles')
    
    # Seuils
    seuil_montant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        help_text='Seuil au-delà duquel pièces supplémentaires requises')
    pieces_supplementaires_seuil = models.JSONField(default=list)
    
    # Validation
    validation_requise = models.BooleanField(default=True)
    niveaux_validation = models.IntegerField(default=1)
    
    # Statut
    est_actif = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'archivage_matrice_pieces'
        verbose_name = 'Matrice pièces justificatives'
        verbose_name_plural = 'Matrices pièces justificatives'
        unique_together = ['entreprise', 'type_operation']
    
    def __str__(self):
        return f"Matrice {self.get_type_operation_display()}"


class ValidationDocument(models.Model):
    """Validation des documents"""
    STATUTS = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('a_completer', 'À compléter'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(ArchiveDocument, on_delete=models.CASCADE,
                                 related_name='validations')
    
    # Validation
    niveau_validation = models.IntegerField(default=1)
    statut = models.CharField(max_length=15, choices=STATUTS, default='en_attente')
    
    # Validateur
    validateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='validations_documents')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Commentaires
    commentaire = models.TextField(blank=True, null=True)
    motif_rejet = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'archivage_validation'
        verbose_name = 'Validation document'
        verbose_name_plural = 'Validations documents'
        ordering = ['niveau_validation']
    
    def __str__(self):
        return f"Validation niveau {self.niveau_validation} - {self.document.reference}"


class VerificationSignature(models.Model):
    """Vérification des signatures sur documents"""
    TYPES_SIGNATURE = [
        ('manuscrite', 'Signature manuscrite'),
        ('electronique', 'Signature électronique'),
        ('cachet', 'Cachet/Tampon'),
    ]
    STATUTS = [
        ('a_verifier', 'À vérifier'),
        ('valide', 'Valide'),
        ('invalide', 'Invalide'),
        ('non_applicable', 'Non applicable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(ArchiveDocument, on_delete=models.CASCADE,
                                 related_name='verifications_signature')
    
    # Signature
    type_signature = models.CharField(max_length=15, choices=TYPES_SIGNATURE)
    signataire_attendu = models.CharField(max_length=200)
    fonction_signataire = models.CharField(max_length=100, blank=True, null=True)
    
    # Vérification
    statut = models.CharField(max_length=15, choices=STATUTS, default='a_verifier')
    date_verification = models.DateTimeField(null=True, blank=True)
    verifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Observations
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'archivage_verification_signature'
        verbose_name = 'Vérification signature'
        verbose_name_plural = 'Vérifications signatures'
    
    def __str__(self):
        return f"Signature {self.signataire_attendu} - {self.get_statut_display()}"


class FluxDocument(models.Model):
    """Workflow de traitement des documents"""
    STATUTS_ETAPE = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(ArchiveDocument, on_delete=models.CASCADE,
                                 related_name='flux')
    
    # Étape
    numero_etape = models.IntegerField()
    nom_etape = models.CharField(max_length=100)
    description_etape = models.TextField(blank=True, null=True)
    
    # Responsable
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='etapes_flux_documents')
    
    # Dates
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    delai_prevu_jours = models.IntegerField(default=1)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS_ETAPE, default='en_attente')
    
    # Commentaires
    commentaire = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'archivage_flux_document'
        verbose_name = 'Flux document'
        verbose_name_plural = 'Flux documents'
        ordering = ['document', 'numero_etape']
    
    def __str__(self):
        return f"Étape {self.numero_etape}: {self.nom_etape}"


class SuppressionDocument(models.Model):
    """Gestion de la suppression/destruction des documents"""
    TYPES_SUPPRESSION = [
        ('logique', 'Suppression logique'),
        ('physique', 'Destruction physique'),
        ('anonymisation', 'Anonymisation'),
    ]
    STATUTS = [
        ('planifiee', 'Planifiée'),
        ('en_attente_validation', 'En attente validation'),
        ('validee', 'Validée'),
        ('executee', 'Exécutée'),
        ('annulee', 'Annulée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='suppressions_documents')
    
    # Document concerné
    document = models.ForeignKey(ArchiveDocument, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='demandes_suppression')
    
    # Suppression
    type_suppression = models.CharField(max_length=15, choices=TYPES_SUPPRESSION)
    motif = models.TextField()
    reference_legale = models.CharField(max_length=200, blank=True, null=True)
    
    # Planification
    date_planifiee = models.DateField()
    statut = models.CharField(max_length=25, choices=STATUTS, default='planifiee')
    
    # Validation
    validee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='suppressions_validees')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Exécution
    executee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='suppressions_executees')
    date_execution = models.DateTimeField(null=True, blank=True)
    
    # Certificat de destruction
    certificat_destruction = models.FileField(upload_to='archives/certificats/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'archivage_suppression'
        verbose_name = 'Suppression document'
        verbose_name_plural = 'Suppressions documents'
        ordering = ['-date_planifiee']
    
    def __str__(self):
        return f"Suppression {self.get_type_suppression_display()} - {self.date_planifiee}"


class TraceAccesDocument(models.Model):
    """Traçabilité des accès aux documents"""
    TYPES_ACCES = [
        ('consultation', 'Consultation'),
        ('telechargement', 'Téléchargement'),
        ('impression', 'Impression'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(ArchiveDocument, on_delete=models.CASCADE,
                                 related_name='traces_acces')
    
    # Accès
    type_acces = models.CharField(max_length=15, choices=TYPES_ACCES)
    date_acces = models.DateTimeField(auto_now_add=True)
    
    # Utilisateur
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contexte
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    
    # Résultat
    succes = models.BooleanField(default=True)
    motif_echec = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'archivage_trace_acces'
        verbose_name = 'Trace accès document'
        verbose_name_plural = 'Traces accès documents'
        ordering = ['-date_acces']
        indexes = [
            models.Index(fields=['document', 'date_acces']),
            models.Index(fields=['utilisateur', 'date_acces']),
        ]
    
    def __str__(self):
        return f"{self.get_type_acces_display()} - {self.document.reference}"


class AlerteArchivage(models.Model):
    """Alertes liées à l'archivage"""
    TYPES_ALERTE = [
        ('expiration', 'Document expirant'),
        ('retention', 'Fin de rétention'),
        ('validation', 'Validation en attente'),
        ('integrite', 'Problème d\'intégrité'),
        ('espace', 'Espace stockage'),
    ]
    NIVEAUX = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('critical', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='alertes_archivage')
    
    # Document concerné
    document = models.ForeignKey(ArchiveDocument, on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='alertes')
    
    # Alerte
    type_alerte = models.CharField(max_length=15, choices=TYPES_ALERTE)
    niveau = models.CharField(max_length=10, choices=NIVEAUX, default='warning')
    message = models.TextField()
    
    # Dates
    date_alerte = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    
    # Statut
    est_lue = models.BooleanField(default=False)
    est_traitee = models.BooleanField(default=False)
    traitee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'archivage_alerte'
        verbose_name = 'Alerte archivage'
        verbose_name_plural = 'Alertes archivage'
        ordering = ['-date_alerte']
    
    def __str__(self):
        return f"{self.get_type_alerte_display()} - {self.get_niveau_display()}"


class RapportArchivage(models.Model):
    """Rapports sur l'archivage"""
    TYPES_RAPPORT = [
        ('inventaire', 'Inventaire documents'),
        ('retention', 'État rétention'),
        ('acces', 'Statistiques accès'),
        ('conformite', 'Conformité archivage'),
        ('destruction', 'Documents détruits'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='rapports_archivage')
    
    # Rapport
    type_rapport = models.CharField(max_length=15, choices=TYPES_RAPPORT)
    titre = models.CharField(max_length=200)
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    # Contenu
    resume = models.TextField(blank=True, null=True)
    donnees = models.JSONField(null=True, blank=True)
    fichier_rapport = models.FileField(upload_to='archives/rapports/', null=True, blank=True)
    
    # Statistiques
    nombre_documents = models.IntegerField(default=0)
    taille_totale_mo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Audit
    date_generation = models.DateTimeField(auto_now_add=True)
    genere_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'archivage_rapport'
        verbose_name = 'Rapport archivage'
        verbose_name_plural = 'Rapports archivage'
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"{self.get_type_rapport_display()} - {self.titre}"
