"""
Module Consolidation & Reporting - Modèles critiques
Consolidation filiales, éliminations IGF, affectation résultat, états consolidés
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur, Devise
from .models import ExerciceComptable, PlanComptable, EcritureComptable


class MatriceConsolidation(models.Model):
    """Matrice de pourcentage de participation entre entités"""
    TYPES_CONTROLE = [
        ('filiale', 'Filiale (contrôle exclusif >50%)'),
        ('participation', 'Participation (influence notable 20-50%)'),
        ('minoritaire', 'Participation minoritaire (<20%)'),
        ('conjointe', 'Entreprise conjointe (contrôle conjoint)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise_mere = models.ForeignKey(Entreprise, on_delete=models.CASCADE, 
                                        related_name='participations_detenues')
    entreprise_fille = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                         related_name='participations_recues')
    
    # Participation
    pourcentage_capital = models.DecimalField(max_digits=6, decimal_places=2,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)],
                                              verbose_name='% du capital')
    pourcentage_droits_vote = models.DecimalField(max_digits=6, decimal_places=2,
                                                  validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                  verbose_name='% droits de vote')
    pourcentage_interet = models.DecimalField(max_digits=6, decimal_places=2,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)],
                                              verbose_name='% d\'intérêt')
    
    # Type de contrôle
    type_controle = models.CharField(max_length=20, choices=TYPES_CONTROLE)
    
    # Dates
    date_acquisition = models.DateField(verbose_name='Date d\'acquisition')
    date_fin = models.DateField(null=True, blank=True, verbose_name='Date de cession')
    
    # Valeur d'acquisition
    cout_acquisition = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    devise = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Goodwill
    goodwill = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                   help_text='Écart d\'acquisition (survaleur)')
    badwill = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                  help_text='Écart d\'acquisition négatif')
    
    # Statut
    est_active = models.BooleanField(default=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'consolidation_matrice'
        verbose_name = 'Matrice de consolidation'
        verbose_name_plural = 'Matrices de consolidation'
        unique_together = ['entreprise_mere', 'entreprise_fille']
        ordering = ['-pourcentage_capital']
    
    def __str__(self):
        return f"{self.entreprise_mere.nom} → {self.entreprise_fille.nom} ({self.pourcentage_capital}%)"


class ConsolidationFiliales(models.Model):
    """Consolidation des filiales - processus de consolidation"""
    METHODES_CONSOLIDATION = [
        ('integration_globale', 'Intégration globale (IG)'),
        ('integration_proportionnelle', 'Intégration proportionnelle (IP)'),
        ('mise_equivalence', 'Mise en équivalence (MEE)'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('cloture', 'Clôturé'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise_mere = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                        related_name='consolidations_groupe')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='consolidations_filiales')
    
    # Identification
    reference = models.CharField(max_length=50, verbose_name='Référence consolidation')
    libelle = models.CharField(max_length=200)
    
    # Période
    date_consolidation = models.DateField()
    date_debut_periode = models.DateField()
    date_fin_periode = models.DateField()
    
    # Méthode
    methode_consolidation = models.CharField(max_length=30, choices=METHODES_CONSOLIDATION,
                                             default='integration_globale')
    
    # Devise de consolidation
    devise_consolidation = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='consolidations_validees')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='consolidations_creees')
    
    class Meta:
        db_table = 'consolidation_filiales'
        verbose_name = 'Consolidation filiales'
        verbose_name_plural = 'Consolidations filiales'
        ordering = ['-date_consolidation']
        unique_together = ['entreprise_mere', 'exercice', 'reference']
    
    def __str__(self):
        return f"{self.reference} - {self.exercice.libelle}"


class PerimetreConsolidation(models.Model):
    """Périmètre de consolidation - entités incluses"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='perimetre')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    matrice = models.ForeignKey(MatriceConsolidation, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Méthode pour cette entité
    methode = models.CharField(max_length=30, choices=ConsolidationFiliales.METHODES_CONSOLIDATION)
    
    # Pourcentages appliqués
    pourcentage_integration = models.DecimalField(max_digits=6, decimal_places=2,
                                                  validators=[MinValueValidator(0), MaxValueValidator(100)])
    pourcentage_interet = models.DecimalField(max_digits=6, decimal_places=2,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Taux de change
    taux_change_cloture = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'))
    taux_change_moyen = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'))
    
    # Statut
    est_incluse = models.BooleanField(default=True)
    motif_exclusion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'consolidation_perimetre'
        verbose_name = 'Périmètre de consolidation'
        verbose_name_plural = 'Périmètres de consolidation'
        unique_together = ['consolidation', 'entreprise']
    
    def __str__(self):
        return f"{self.entreprise.nom} - {self.get_methode_display()}"


class EliminationIGF(models.Model):
    """Éliminations intercompagnies (Intra-Groupe Financier)"""
    TYPES_ELIMINATION = [
        ('creance_dette', 'Créances/Dettes réciproques'),
        ('produit_charge', 'Produits/Charges réciproques'),
        ('dividende', 'Dividendes intra-groupe'),
        ('marge_stock', 'Marges sur stocks'),
        ('plus_value', 'Plus-values sur cessions internes'),
        ('provision', 'Provisions intra-groupe'),
        ('capital', 'Titres de participation/Capital'),
    ]
    STATUTS = [
        ('identifie', 'Identifié'),
        ('valide', 'Validé'),
        ('comptabilise', 'Comptabilisé'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='eliminations')
    
    # Type d'élimination
    type_elimination = models.CharField(max_length=20, choices=TYPES_ELIMINATION)
    
    # Entités concernées
    entreprise_source = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                          related_name='eliminations_source')
    entreprise_destination = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                               related_name='eliminations_destination')
    
    # Montants
    montant_brut = models.DecimalField(max_digits=15, decimal_places=2)
    montant_elimine = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Comptes
    compte_debit = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='eliminations_debit')
    compte_credit = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='eliminations_credit')
    
    # Écriture de consolidation
    ecriture_consolidation = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL,
                                               null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='identifie')
    
    # Description
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'consolidation_elimination_igf'
        verbose_name = 'Élimination IGF'
        verbose_name_plural = 'Éliminations IGF'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_elimination_display()} - {self.montant_elimine}"


class AjustementConsolidation(models.Model):
    """Ajustements de consolidation"""
    TYPES_AJUSTEMENT = [
        ('retraitement', 'Retraitement d\'homogénéité'),
        ('conversion', 'Écart de conversion'),
        ('impot_differe', 'Impôts différés'),
        ('goodwill', 'Amortissement goodwill'),
        ('minoritaires', 'Intérêts minoritaires'),
        ('autre', 'Autre ajustement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='ajustements')
    
    # Type
    type_ajustement = models.CharField(max_length=20, choices=TYPES_AJUSTEMENT)
    
    # Entité concernée
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    
    # Montants
    montant_debit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_credit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Comptes
    compte_debit = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='ajustements_debit')
    compte_credit = models.ForeignKey(PlanComptable, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='ajustements_credit')
    
    # Écriture
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Description
    libelle = models.CharField(max_length=200)
    justification = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'consolidation_ajustement'
        verbose_name = 'Ajustement de consolidation'
        verbose_name_plural = 'Ajustements de consolidation'
    
    def __str__(self):
        return f"{self.get_type_ajustement_display()} - {self.libelle}"


class AffectationResultat(models.Model):
    """Distribution et affectation des résultats"""
    TYPES_AFFECTATION = [
        ('reserve_legale', 'Réserve légale'),
        ('reserve_statutaire', 'Réserve statutaire'),
        ('reserve_facultative', 'Réserve facultative'),
        ('report_nouveau', 'Report à nouveau'),
        ('dividende', 'Dividendes'),
        ('participation', 'Participation salariés'),
        ('autre', 'Autre affectation'),
    ]
    STATUTS = [
        ('proposition', 'Proposition'),
        ('approuve', 'Approuvé AG'),
        ('comptabilise', 'Comptabilisé'),
        ('distribue', 'Distribué'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='affectations_resultat')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='affectations_resultat')
    
    # Résultat à affecter
    resultat_exercice = models.DecimalField(max_digits=15, decimal_places=2)
    report_anterieur = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_a_affecter = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Affectation
    type_affectation = models.CharField(max_length=20, choices=TYPES_AFFECTATION)
    montant_affecte = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Pour dividendes
    montant_par_action = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    date_mise_paiement = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='proposition')
    
    # Approbation AG
    date_ag = models.DateField(null=True, blank=True, verbose_name='Date AG')
    numero_resolution = models.CharField(max_length=50, blank=True, null=True)
    
    # Écriture
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'consolidation_affectation_resultat'
        verbose_name = 'Affectation du résultat'
        verbose_name_plural = 'Affectations du résultat'
        ordering = ['-exercice__date_fin']
    
    def __str__(self):
        return f"{self.exercice.libelle} - {self.get_type_affectation_display()}"


class VariationCapitaux(models.Model):
    """Tableau de variation des capitaux propres"""
    TYPES_VARIATION = [
        ('capital_initial', 'Capital initial'),
        ('augmentation_capital', 'Augmentation de capital'),
        ('reduction_capital', 'Réduction de capital'),
        ('resultat_exercice', 'Résultat de l\'exercice'),
        ('affectation_resultat', 'Affectation du résultat'),
        ('distribution_dividendes', 'Distribution de dividendes'),
        ('ecart_reevaluation', 'Écart de réévaluation'),
        ('ecart_conversion', 'Écart de conversion'),
        ('variation_perimetre', 'Variation de périmètre'),
        ('autres_variations', 'Autres variations'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='variations_capitaux')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='variations_capitaux')
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='variations_capitaux')
    
    # Type de variation
    type_variation = models.CharField(max_length=30, choices=TYPES_VARIATION)
    
    # Montants par composante
    capital_social = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    primes_emission = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reserves = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    report_nouveau = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_exercice = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ecarts_reevaluation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ecarts_conversion = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    interets_minoritaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Total
    total_capitaux_propres = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Description
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Date
    date_variation = models.DateField()
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consolidation_variation_capitaux'
        verbose_name = 'Variation des capitaux'
        verbose_name_plural = 'Variations des capitaux'
        ordering = ['exercice', 'date_variation']
    
    def __str__(self):
        return f"{self.exercice.libelle} - {self.get_type_variation_display()}"
    
    def calculer_total(self):
        """Calcule le total des capitaux propres"""
        self.total_capitaux_propres = (
            self.capital_social +
            self.primes_emission +
            self.reserves +
            self.report_nouveau +
            self.resultat_exercice +
            self.ecarts_reevaluation +
            self.ecarts_conversion +
            self.interets_minoritaires
        )
        self.save()


class NoteExplicative(models.Model):
    """Notes aux états financiers (annexes)"""
    CATEGORIES = [
        ('principes', 'Principes comptables'),
        ('perimetre', 'Périmètre de consolidation'),
        ('methodes', 'Méthodes de consolidation'),
        ('immobilisations', 'Immobilisations'),
        ('stocks', 'Stocks'),
        ('creances', 'Créances'),
        ('tresorerie', 'Trésorerie'),
        ('capitaux', 'Capitaux propres'),
        ('provisions', 'Provisions'),
        ('dettes', 'Dettes'),
        ('engagements', 'Engagements hors bilan'),
        ('parties_liees', 'Parties liées'),
        ('evenements', 'Événements postérieurs'),
        ('risques', 'Gestion des risques'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='notes_explicatives')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='notes_explicatives')
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='notes_explicatives')
    
    # Identification
    numero_note = models.CharField(max_length=10, verbose_name='N° Note')
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Contenu
    contenu = models.TextField(verbose_name='Contenu de la note')
    
    # Tableaux associés (JSON)
    tableaux_json = models.JSONField(null=True, blank=True,
                                     help_text='Tableaux de données en JSON')
    
    # Ordre d'affichage
    ordre = models.IntegerField(default=0)
    
    # Statut
    est_publie = models.BooleanField(default=False)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    redige_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='notes_redigees')
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='notes_validees')
    
    class Meta:
        db_table = 'consolidation_note_explicative'
        verbose_name = 'Note explicative'
        verbose_name_plural = 'Notes explicatives'
        ordering = ['exercice', 'ordre', 'numero_note']
        unique_together = ['entreprise', 'exercice', 'numero_note']
    
    def __str__(self):
        return f"Note {self.numero_note} - {self.titre}"


class DocumentationConsolidation(models.Model):
    """Documentation du processus de consolidation"""
    TYPES_DOCUMENT = [
        ('procedure', 'Procédure'),
        ('checklist', 'Checklist'),
        ('rapport', 'Rapport'),
        ('justificatif', 'Justificatif'),
        ('correspondance', 'Correspondance'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='documentation')
    
    # Identification
    type_document = models.CharField(max_length=20, choices=TYPES_DOCUMENT)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Fichier
    fichier = models.FileField(upload_to='consolidation/documentation/')
    
    # Version
    version = models.CharField(max_length=20, default='1.0')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'consolidation_documentation'
        verbose_name = 'Documentation consolidation'
        verbose_name_plural = 'Documentation consolidation'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.titre}"


# ============================================================================
# ÉTATS FINANCIERS CONSOLIDÉS
# ============================================================================

class BilanConsolide(models.Model):
    """Bilan consolidé"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='bilans')
    
    # Date
    date_bilan = models.DateField()
    
    # ACTIF
    # Actif immobilisé
    immobilisations_incorporelles = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    goodwill = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    immobilisations_corporelles = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    immobilisations_financieres = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    participations_mee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                             verbose_name='Participations MEE')
    actifs_impots_differes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_actif_immobilise = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Actif circulant
    stocks = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    creances_clients = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_creances = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tresorerie_actif = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_actif_circulant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    total_actif = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # PASSIF
    # Capitaux propres
    capital_social = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    primes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reserves_consolidees = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ecarts_conversion = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_groupe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    capitaux_propres_groupe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    interets_minoritaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_capitaux_propres = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Passif non courant
    provisions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    emprunts_lt = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                      verbose_name='Emprunts long terme')
    passifs_impots_differes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_passif_non_courant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Passif courant
    dettes_fournisseurs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_dettes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    emprunts_ct = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                      verbose_name='Emprunts court terme')
    tresorerie_passif = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_passif_courant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    total_passif = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Validation
    est_valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consolidation_bilan'
        verbose_name = 'Bilan consolidé'
        verbose_name_plural = 'Bilans consolidés'
        ordering = ['-date_bilan']
    
    def __str__(self):
        return f"Bilan consolidé {self.date_bilan}"
    
    def calculer_totaux(self):
        """Calcule les totaux du bilan"""
        self.total_actif_immobilise = (
            self.immobilisations_incorporelles + self.goodwill +
            self.immobilisations_corporelles + self.immobilisations_financieres +
            self.participations_mee + self.actifs_impots_differes
        )
        self.total_actif_circulant = (
            self.stocks + self.creances_clients + self.autres_creances + self.tresorerie_actif
        )
        self.total_actif = self.total_actif_immobilise + self.total_actif_circulant
        
        self.capitaux_propres_groupe = (
            self.capital_social + self.primes + self.reserves_consolidees +
            self.ecarts_conversion + self.resultat_groupe
        )
        self.total_capitaux_propres = self.capitaux_propres_groupe + self.interets_minoritaires
        
        self.total_passif_non_courant = (
            self.provisions + self.emprunts_lt + self.passifs_impots_differes
        )
        self.total_passif_courant = (
            self.dettes_fournisseurs + self.autres_dettes + self.emprunts_ct + self.tresorerie_passif
        )
        self.total_passif = (
            self.total_capitaux_propres + self.total_passif_non_courant + self.total_passif_courant
        )
        self.save()


class CompteResultatConsolide(models.Model):
    """Compte de résultat consolidé"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='comptes_resultat')
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    # Produits d'exploitation
    chiffre_affaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_produits_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_produits_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Charges d'exploitation
    achats_consommes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    charges_personnel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    dotations_amortissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    dotations_provisions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_charges_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_charges_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat d'exploitation
    resultat_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat financier
    produits_financiers = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    charges_financieres = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_financier = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat courant
    resultat_courant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat exceptionnel
    produits_exceptionnels = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    charges_exceptionnelles = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_exceptionnel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Impôts
    impots_sur_benefices = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    impots_differes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Quote-part MEE
    quote_part_mee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                         verbose_name='Quote-part résultat MEE')
    
    # Résultat net
    resultat_net_ensemble = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_minoritaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_net_groupe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Résultat par action
    resultat_par_action = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    resultat_dilue_par_action = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Validation
    est_valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consolidation_compte_resultat'
        verbose_name = 'Compte de résultat consolidé'
        verbose_name_plural = 'Comptes de résultat consolidés'
        ordering = ['-date_fin']
    
    def __str__(self):
        return f"Compte de résultat consolidé {self.date_debut} - {self.date_fin}"
    
    def calculer_resultats(self):
        """Calcule les résultats intermédiaires"""
        self.total_produits_exploitation = self.chiffre_affaires + self.autres_produits_exploitation
        self.total_charges_exploitation = (
            self.achats_consommes + self.charges_personnel +
            self.dotations_amortissements + self.dotations_provisions +
            self.autres_charges_exploitation
        )
        self.resultat_exploitation = self.total_produits_exploitation - self.total_charges_exploitation
        self.resultat_financier = self.produits_financiers - self.charges_financieres
        self.resultat_courant = self.resultat_exploitation + self.resultat_financier
        self.resultat_exceptionnel = self.produits_exceptionnels - self.charges_exceptionnelles
        self.resultat_net_ensemble = (
            self.resultat_courant + self.resultat_exceptionnel -
            self.impots_sur_benefices - self.impots_differes + self.quote_part_mee
        )
        self.resultat_net_groupe = self.resultat_net_ensemble - self.resultat_minoritaires
        self.save()


class FluxTresorerieConsolide(models.Model):
    """Tableau des flux de trésorerie consolidé"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consolidation = models.ForeignKey(ConsolidationFiliales, on_delete=models.CASCADE,
                                      related_name='flux_tresorerie')
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    # Flux d'exploitation
    resultat_net = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    amortissements_provisions = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    variation_bfr = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                        verbose_name='Variation BFR')
    autres_flux_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    flux_exploitation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Flux d'investissement
    acquisitions_immobilisations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cessions_immobilisations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    acquisitions_filiales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cessions_filiales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_flux_investissement = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    flux_investissement = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Flux de financement
    augmentation_capital = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    dividendes_verses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    emprunts_nouveaux = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    remboursements_emprunts = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_flux_financement = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    flux_financement = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Variation de trésorerie
    variation_tresorerie = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    effet_change = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tresorerie_ouverture = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tresorerie_cloture = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Validation
    est_valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consolidation_flux_tresorerie'
        verbose_name = 'Flux de trésorerie consolidé'
        verbose_name_plural = 'Flux de trésorerie consolidés'
        ordering = ['-date_fin']
    
    def __str__(self):
        return f"Flux trésorerie consolidé {self.date_debut} - {self.date_fin}"
    
    def calculer_flux(self):
        """Calcule les flux de trésorerie"""
        self.flux_exploitation = (
            self.resultat_net + self.amortissements_provisions -
            self.variation_bfr + self.autres_flux_exploitation
        )
        self.flux_investissement = (
            -self.acquisitions_immobilisations + self.cessions_immobilisations -
            self.acquisitions_filiales + self.cessions_filiales + self.autres_flux_investissement
        )
        self.flux_financement = (
            self.augmentation_capital - self.dividendes_verses +
            self.emprunts_nouveaux - self.remboursements_emprunts + self.autres_flux_financement
        )
        self.variation_tresorerie = self.flux_exploitation + self.flux_investissement + self.flux_financement
        self.tresorerie_cloture = self.tresorerie_ouverture + self.variation_tresorerie + self.effet_change
        self.save()
