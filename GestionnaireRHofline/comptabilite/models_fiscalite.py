"""
Module Déclarations Fiscales Avancées
IRPP, IS, CAT, CVAE, Liasses fiscales, Documentation fiscale
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur
from .models import ExerciceComptable, PlanComptable, Tiers


class DossierFiscalComplet(models.Model):
    """Dossier fiscal centralisé par exercice"""
    STATUTS = [
        ('en_preparation', 'En préparation'),
        ('en_cours', 'En cours de validation'),
        ('valide', 'Validé'),
        ('depose', 'Déposé'),
        ('controle', 'En contrôle fiscal'),
        ('cloture', 'Clôturé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='dossiers_fiscaux')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='dossiers_fiscaux')
    
    # Identification
    reference = models.CharField(max_length=50, verbose_name='Référence dossier')
    annee_fiscale = models.IntegerField()
    
    # Dates clés
    date_ouverture = models.DateField()
    date_cloture_exercice = models.DateField()
    date_limite_depot = models.DateField()
    date_depot_effectif = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_preparation')
    
    # Montants récapitulatifs
    resultat_comptable = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_fiscal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_impots_dus = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_impots_payes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='dossiers_fiscaux_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Notes
    observations = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='dossiers_fiscaux_crees')
    
    class Meta:
        db_table = 'fiscalite_dossier_complet'
        verbose_name = 'Dossier fiscal complet'
        verbose_name_plural = 'Dossiers fiscaux complets'
        unique_together = ['entreprise', 'annee_fiscale']
        ordering = ['-annee_fiscale']
    
    def __str__(self):
        return f"Dossier fiscal {self.annee_fiscale} - {self.entreprise.nom}"


class DeclarationIS(models.Model):
    """Déclaration Impôt sur les Sociétés"""
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('calcule', 'Calculé'),
        ('valide', 'Validé'),
        ('depose', 'Déposé'),
        ('paye', 'Payé'),
        ('rectifie', 'Rectifié'),
    ]
    TYPES_DECLARATION = [
        ('principale', 'Déclaration principale'),
        ('rectificative', 'Déclaration rectificative'),
        ('complementaire', 'Déclaration complémentaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.CASCADE,
                                       related_name='declarations_is')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='declarations_is')
    
    # Identification
    reference = models.CharField(max_length=50)
    type_declaration = models.CharField(max_length=20, choices=TYPES_DECLARATION, default='principale')
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    
    # Résultat comptable
    resultat_comptable_brut = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Réintégrations fiscales
    reintegrations_amortissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reintegrations_provisions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reintegrations_amendes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reintegrations_dons_excessifs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_reintegrations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_reintegrations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Déductions fiscales
    deductions_dividendes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deductions_plus_values = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deductions_provisions_reglementees = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat fiscal
    resultat_fiscal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    deficits_anterieurs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    base_imposable = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Calcul IS
    taux_is = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('25.00'))
    is_brut = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    credits_impot = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_net = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Acomptes
    acomptes_verses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    solde_a_payer = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Minimum fiscal
    minimum_fiscal = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_minimum_applicable = models.BooleanField(default=False)
    
    # Statut et dates
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_depot = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='declarations_is_validees')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'fiscalite_declaration_is'
        verbose_name = 'Déclaration IS'
        verbose_name_plural = 'Déclarations IS'
        ordering = ['-periode_fin']
    
    def __str__(self):
        return f"IS {self.periode_fin.year} - {self.entreprise.nom}"
    
    def calculer_is(self):
        """Calcule l'IS automatiquement"""
        self.total_reintegrations = (
            self.reintegrations_amortissements + self.reintegrations_provisions +
            self.reintegrations_amendes + self.reintegrations_dons_excessifs +
            self.autres_reintegrations
        )
        self.total_deductions = (
            self.deductions_dividendes + self.deductions_plus_values +
            self.deductions_provisions_reglementees + self.autres_deductions
        )
        self.resultat_fiscal = self.resultat_comptable_brut + self.total_reintegrations - self.total_deductions
        self.base_imposable = max(Decimal('0'), self.resultat_fiscal - self.deficits_anterieurs)
        self.is_brut = self.base_imposable * (self.taux_is / 100)
        self.is_net = max(self.is_brut - self.credits_impot, self.minimum_fiscal if self.is_minimum_applicable else Decimal('0'))
        self.solde_a_payer = self.is_net - self.acomptes_verses
        self.save()


class DeclarationCAT(models.Model):
    """Déclaration Contribution Assistance Technique"""
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('depose', 'Déposé'),
        ('paye', 'Payé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='declarations_cat')
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='declarations_cat')
    
    # Période
    reference = models.CharField(max_length=50)
    annee = models.IntegerField()
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Base de calcul
    montant_prestations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                              verbose_name='Montant prestations techniques')
    taux_cat = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    
    # Calcul
    cat_brute = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    exonerations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cat_nette = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_depot = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'fiscalite_declaration_cat'
        verbose_name = 'Déclaration CAT'
        verbose_name_plural = 'Déclarations CAT'
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"CAT {self.mois}/{self.annee} - {self.entreprise.nom}"
    
    def calculer_cat(self):
        self.cat_brute = self.montant_prestations * (self.taux_cat / 100)
        self.cat_nette = self.cat_brute - self.exonerations
        self.save()


class DeclarationCVAE(models.Model):
    """Déclaration Contribution sur la Valeur Ajoutée des Entreprises"""
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('depose', 'Déposé'),
        ('paye', 'Payé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='declarations_cvae')
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='declarations_cvae')
    
    # Période
    reference = models.CharField(max_length=50)
    annee = models.IntegerField()
    
    # Calcul valeur ajoutée
    chiffre_affaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    achats = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    services_exterieurs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_charges_externes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valeur_ajoutee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Taux et calcul
    taux_cvae = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0075'))
    cvae_brute = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    degrevement = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cvae_nette = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Cotisation minimum
    cotisation_minimum = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_depot = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'fiscalite_declaration_cvae'
        verbose_name = 'Déclaration CVAE'
        verbose_name_plural = 'Déclarations CVAE'
        ordering = ['-annee']
    
    def __str__(self):
        return f"CVAE {self.annee} - {self.entreprise.nom}"
    
    def calculer_cvae(self):
        self.valeur_ajoutee = self.chiffre_affaires - self.achats - self.services_exterieurs - self.autres_charges_externes
        self.cvae_brute = self.valeur_ajoutee * self.taux_cvae
        self.cvae_nette = max(self.cvae_brute - self.degrevement, self.cotisation_minimum)
        self.save()


class LiasseFiscale(models.Model):
    """Liasse fiscale complète"""
    TYPES_LIASSE = [
        ('bic_rn', 'BIC Régime Normal'),
        ('bic_rs', 'BIC Régime Simplifié'),
        ('is', 'Impôt sur les Sociétés'),
    ]
    STATUTS = [
        ('en_cours', 'En cours'),
        ('complete', 'Complète'),
        ('validee', 'Validée'),
        ('deposee', 'Déposée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.CASCADE,
                                       related_name='liasses')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='liasses_fiscales')
    
    # Identification
    reference = models.CharField(max_length=50)
    type_liasse = models.CharField(max_length=10, choices=TYPES_LIASSE)
    annee = models.IntegerField()
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    
    # Données JSON des formulaires
    formulaires_json = models.JSONField(null=True, blank=True,
                                        help_text='Données des formulaires en JSON')
    
    # Fichier généré
    fichier_pdf = models.FileField(upload_to='fiscalite/liasses/', null=True, blank=True)
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_depot = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fiscalite_liasse'
        verbose_name = 'Liasse fiscale'
        verbose_name_plural = 'Liasses fiscales'
        ordering = ['-annee']
    
    def __str__(self):
        return f"Liasse {self.get_type_liasse_display()} {self.annee}"


class AnnexeFiscale(models.Model):
    """Annexes requises pour les déclarations fiscales"""
    TYPES_ANNEXE = [
        ('2050', 'Bilan Actif'),
        ('2051', 'Bilan Passif'),
        ('2052', 'Compte de résultat (charges)'),
        ('2053', 'Compte de résultat (produits)'),
        ('2054', 'Immobilisations'),
        ('2055', 'Amortissements'),
        ('2056', 'Provisions'),
        ('2057', 'État des échéances'),
        ('2058A', 'Détermination résultat fiscal'),
        ('2058B', 'Déficits et provisions'),
        ('2058C', 'Tableau affectation résultat'),
        ('2059A', 'Plus-values'),
        ('2059B', 'Affectation plus-values'),
        ('autre', 'Autre annexe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    liasse = models.ForeignKey(LiasseFiscale, on_delete=models.CASCADE,
                               related_name='annexes')
    
    # Identification
    type_annexe = models.CharField(max_length=10, choices=TYPES_ANNEXE)
    numero_formulaire = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    
    # Données
    donnees_json = models.JSONField(null=True, blank=True)
    
    # Statut
    est_complete = models.BooleanField(default=False)
    est_obligatoire = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fiscalite_annexe'
        verbose_name = 'Annexe fiscale'
        verbose_name_plural = 'Annexes fiscales'
        ordering = ['type_annexe']
    
    def __str__(self):
        return f"{self.numero_formulaire} - {self.libelle}"


class DocumentationFiscale(models.Model):
    """Documentation fiscale détaillée"""
    TYPES_DOCUMENT = [
        ('justificatif', 'Justificatif'),
        ('calcul', 'Note de calcul'),
        ('correspondance', 'Correspondance administration'),
        ('avis', 'Avis d\'imposition'),
        ('quittance', 'Quittance de paiement'),
        ('controle', 'Document contrôle fiscal'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.CASCADE,
                                       related_name='documentation')
    
    # Identification
    type_document = models.CharField(max_length=20, choices=TYPES_DOCUMENT)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Fichier
    fichier = models.FileField(upload_to='fiscalite/documentation/')
    
    # Référence à une déclaration spécifique
    declaration_is = models.ForeignKey(DeclarationIS, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='documents')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'fiscalite_documentation'
        verbose_name = 'Documentation fiscale'
        verbose_name_plural = 'Documentation fiscale'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.titre}"


class RobustesseControleFiscal(models.Model):
    """Sécurité et robustesse pour contrôle fiscal"""
    NIVEAUX_RISQUE = [
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('eleve', 'Élevé'),
        ('critique', 'Critique'),
    ]
    STATUTS = [
        ('identifie', 'Identifié'),
        ('en_cours', 'En cours de traitement'),
        ('resolu', 'Résolu'),
        ('accepte', 'Risque accepté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier_fiscal = models.ForeignKey(DossierFiscalComplet, on_delete=models.CASCADE,
                                       related_name='controles_robustesse')
    
    # Identification du risque
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    
    # Évaluation
    niveau_risque = models.CharField(max_length=10, choices=NIVEAUX_RISQUE)
    impact_financier_estime = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    probabilite = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                      help_text='1=Très faible, 5=Très élevée')
    
    # Contrôle
    point_controle = models.TextField(verbose_name='Point de contrôle')
    justification = models.TextField(blank=True, null=True)
    documents_support = models.TextField(blank=True, null=True,
                                         help_text='Liste des documents justificatifs')
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='identifie')
    
    # Actions correctives
    actions_correctives = models.TextField(blank=True, null=True)
    date_resolution = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    identifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='risques_fiscaux_identifies')
    resolu_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='risques_fiscaux_resolus')
    
    class Meta:
        db_table = 'fiscalite_robustesse_controle'
        verbose_name = 'Contrôle robustesse fiscale'
        verbose_name_plural = 'Contrôles robustesse fiscale'
        ordering = ['-niveau_risque', '-date_creation']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class HistoriqueDeclaration(models.Model):
    """Historique des modifications des déclarations fiscales"""
    TYPES_MODIFICATION = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('validation', 'Validation'),
        ('depot', 'Dépôt'),
        ('rectification', 'Rectification'),
        ('annulation', 'Annulation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Référence à la déclaration (générique)
    type_declaration = models.CharField(max_length=20)  # 'is', 'irpp', 'cat', 'cvae'
    declaration_id = models.UUIDField()
    
    # Modification
    type_modification = models.CharField(max_length=20, choices=TYPES_MODIFICATION)
    description = models.TextField()
    
    # Valeurs avant/après (JSON)
    valeurs_avant = models.JSONField(null=True, blank=True)
    valeurs_apres = models.JSONField(null=True, blank=True)
    
    # Audit
    date_modification = models.DateTimeField(auto_now_add=True)
    modifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'fiscalite_historique_declaration'
        verbose_name = 'Historique déclaration'
        verbose_name_plural = 'Historique déclarations'
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.type_declaration} - {self.get_type_modification_display()}"


class RegleFiscale(models.Model):
    """Règles fiscales complexes pour validation automatique"""
    TYPES_REGLE = [
        ('limite', 'Limite/Plafond'),
        ('taux', 'Taux applicable'),
        ('condition', 'Condition d\'éligibilité'),
        ('calcul', 'Règle de calcul'),
        ('delai', 'Délai'),
    ]
    NIVEAUX_SEVERITE = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur bloquante'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identification
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=200)
    description = models.TextField()
    
    # Type et application
    type_regle = models.CharField(max_length=20, choices=TYPES_REGLE)
    impot_concerne = models.CharField(max_length=20)  # 'is', 'irpp', 'tva', etc.
    
    # Paramètres
    valeur_seuil = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    taux = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    formule = models.TextField(blank=True, null=True, help_text='Expression de calcul')
    
    # Validation
    niveau_severite = models.CharField(max_length=10, choices=NIVEAUX_SEVERITE, default='warning')
    message_erreur = models.TextField()
    
    # Période de validité
    date_debut_validite = models.DateField()
    date_fin_validite = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    
    # Référence légale
    reference_legale = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'fiscalite_regle'
        verbose_name = 'Règle fiscale'
        verbose_name_plural = 'Règles fiscales'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"
