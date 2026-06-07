"""
Module Comptabilité Analytique Avancée
Centres de coûts, sections, imputations, analyses variance, reporting
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur
from .models import ExerciceComptable, PlanComptable, EcritureComptable


class CentreCouts(models.Model):
    """Centres de coûts"""
    TYPES_CENTRE = [
        ('principal', 'Centre principal'),
        ('auxiliaire', 'Centre auxiliaire'),
        ('structure', 'Centre de structure'),
        ('production', 'Centre de production'),
        ('distribution', 'Centre de distribution'),
        ('administration', 'Centre d\'administration'),
    ]
    NATURES = [
        ('operationnel', 'Opérationnel'),
        ('fonctionnel', 'Fonctionnel'),
        ('projet', 'Projet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='centres_couts')
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Classification
    type_centre = models.CharField(max_length=15, choices=TYPES_CENTRE)
    nature = models.CharField(max_length=15, choices=NATURES, default='operationnel')
    
    # Hiérarchie
    centre_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='sous_centres')
    niveau = models.IntegerField(default=1)
    
    # Responsable
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='centres_responsable')
    
    # Budget
    budget_annuel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Unité d'œuvre
    unite_oeuvre = models.CharField(max_length=50, blank=True, null=True,
                                    help_text='Ex: heures machine, m², unités produites')
    cout_unite_oeuvre = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.00'))
    
    # Statut
    est_actif = models.BooleanField(default=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='centres_crees')
    
    class Meta:
        db_table = 'analytique_centre_couts'
        verbose_name = 'Centre de coûts'
        verbose_name_plural = 'Centres de coûts'
        unique_together = ['entreprise', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"


class SectionAnalytique(models.Model):
    """Sections analytiques"""
    TYPES_SECTION = [
        ('produit', 'Produit'),
        ('service', 'Service'),
        ('projet', 'Projet'),
        ('client', 'Client'),
        ('region', 'Région'),
        ('canal', 'Canal de distribution'),
        ('activite', 'Activité'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='sections_analytiques')
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Classification
    type_section = models.CharField(max_length=15, choices=TYPES_SECTION)
    
    # Hiérarchie
    section_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='sous_sections')
    
    # Lien centre de coûts
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='sections')
    
    # Statut
    est_active = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'analytique_section'
        verbose_name = 'Section analytique'
        verbose_name_plural = 'Sections analytiques'
        unique_together = ['entreprise', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"


class CommandeAnalytique(models.Model):
    """Commandes analytiques (ordres internes)"""
    TYPES_COMMANDE = [
        ('investissement', 'Investissement'),
        ('maintenance', 'Maintenance'),
        ('projet', 'Projet'),
        ('marketing', 'Marketing'),
        ('rd', 'R&D'),
        ('formation', 'Formation'),
        ('autre', 'Autre'),
    ]
    STATUTS = [
        ('ouverte', 'Ouverte'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('cloturee', 'Clôturée'),
        ('annulee', 'Annulée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='commandes_analytiques')

    # Identification
    numero = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Classification
    type_commande = models.CharField(max_length=15, choices=TYPES_COMMANDE)

    # Lien centre/section
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='commandes')
    section = models.ForeignKey(SectionAnalytique, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='commandes')

    # Budget
    budget_prevu = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_engage = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_realise = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    # Période
    date_debut = models.DateField()
    date_fin_prevue = models.DateField()
    date_fin_reelle = models.DateField(null=True, blank=True)

    # Responsable
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='commandes_responsable')

    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='ouverte')

    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'analytique_commande'
        verbose_name = 'Commande analytique'
        verbose_name_plural = 'Commandes analytiques'
        unique_together = ['entreprise', 'numero']
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.numero} - {self.libelle}"

    @property
    def ecart_budget(self):
        return self.budget_prevu - self.montant_realise


class ImputationAnalytique(models.Model):
    """Imputations analytiques détaillées"""
    TYPES_IMPUTATION = [
        ('directe', 'Imputation directe'),
        ('indirecte', 'Imputation indirecte'),
        ('repartition', 'Répartition'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='imputations_analytiques')
    
    # Lien écriture comptable
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.CASCADE,
                                 related_name='imputations_analytiques')
    compte = models.ForeignKey(PlanComptable, on_delete=models.CASCADE,
                               related_name='imputations_analytiques')
    
    # Destination analytique
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='imputations')
    section = models.ForeignKey(SectionAnalytique, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='imputations')
    commande = models.ForeignKey(CommandeAnalytique, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='imputations')
    
    # Type
    type_imputation = models.CharField(max_length=15, choices=TYPES_IMPUTATION, default='directe')
    
    # Montants
    montant_debit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_credit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Quantité (pour unités d'œuvre)
    quantite = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    unite = models.CharField(max_length=20, blank=True, null=True)
    
    # Clé de répartition (pour imputations indirectes)
    cle_repartition = models.ForeignKey('CleRepartition', on_delete=models.SET_NULL, null=True, blank=True)
    pourcentage_repartition = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Date
    date_imputation = models.DateField()
    periode = models.CharField(max_length=7, help_text='Format: YYYY-MM')
    
    # Libellé
    libelle = models.CharField(max_length=200)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytique_imputation'
        verbose_name = 'Imputation analytique'
        verbose_name_plural = 'Imputations analytiques'
        ordering = ['-date_imputation']
        indexes = [
            models.Index(fields=['centre_couts', 'periode']),
            models.Index(fields=['section', 'periode']),
        ]
    
    def __str__(self):
        dest = self.centre_couts or self.section or self.commande
        return f"{self.date_imputation} - {dest} - {self.montant_debit - self.montant_credit}"


class CleRepartition(models.Model):
    """Clés de répartition pour charges indirectes"""
    TYPES_CLE = [
        ('fixe', 'Pourcentage fixe'),
        ('variable', 'Variable (unités d\'œuvre)'),
        ('mixte', 'Mixte'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='cles_repartition')
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Type
    type_cle = models.CharField(max_length=10, choices=TYPES_CLE)
    
    # Base de répartition
    base_repartition = models.CharField(max_length=100,
                                        help_text='Ex: effectif, surface, CA, heures')
    
    # Statut
    est_active = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytique_cle_repartition'
        verbose_name = 'Clé de répartition'
        verbose_name_plural = 'Clés de répartition'
        unique_together = ['entreprise', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"


class TauxRepartition(models.Model):
    """Taux de répartition par centre/section"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cle = models.ForeignKey(CleRepartition, on_delete=models.CASCADE,
                            related_name='taux')
    
    # Destination
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                     related_name='taux_repartition')
    
    # Taux
    pourcentage = models.DecimalField(max_digits=6, decimal_places=2,
                                      validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Période de validité
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'analytique_taux_repartition'
        verbose_name = 'Taux de répartition'
        verbose_name_plural = 'Taux de répartition'
    
    def __str__(self):
        return f"{self.cle.code} → {self.centre_couts.code}: {self.pourcentage}%"


class BudgetAnalytique(models.Model):
    """Budget par centre de coûts/section"""
    TYPES_BUDGET = [
        ('initial', 'Budget initial'),
        ('revise', 'Budget révisé'),
        ('previsionnel', 'Prévisionnel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='budgets_analytiques')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='budgets_analytiques')
    
    # Destination
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                     related_name='budgets', null=True, blank=True)
    section = models.ForeignKey(SectionAnalytique, on_delete=models.CASCADE,
                                related_name='budgets', null=True, blank=True)
    
    # Type
    type_budget = models.CharField(max_length=15, choices=TYPES_BUDGET, default='initial')
    
    # Période
    periode = models.CharField(max_length=7, help_text='Format: YYYY-MM')
    
    # Montants
    budget_charges = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    budget_produits = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Détail par nature (JSON)
    detail_par_compte = models.JSONField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytique_budget'
        verbose_name = 'Budget analytique'
        verbose_name_plural = 'Budgets analytiques'
        ordering = ['exercice', 'periode']
    
    def __str__(self):
        dest = self.centre_couts or self.section
        return f"Budget {self.periode} - {dest}"


class AnalyseVariance(models.Model):
    """Analyse des écarts budgétaires"""
    TYPES_ECART = [
        ('volume', 'Écart sur volume'),
        ('prix', 'Écart sur prix'),
        ('rendement', 'Écart sur rendement'),
        ('mix', 'Écart de mix'),
        ('global', 'Écart global'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='analyses_variance')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='analyses_variance')
    
    # Période
    periode = models.CharField(max_length=7)
    
    # Destination
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                     related_name='analyses_variance', null=True, blank=True)
    section = models.ForeignKey(SectionAnalytique, on_delete=models.CASCADE,
                                related_name='analyses_variance', null=True, blank=True)
    
    # Type d'écart
    type_ecart = models.CharField(max_length=15, choices=TYPES_ECART)
    
    # Montants
    montant_budget = models.DecimalField(max_digits=15, decimal_places=2)
    montant_reel = models.DecimalField(max_digits=15, decimal_places=2)
    ecart_montant = models.DecimalField(max_digits=15, decimal_places=2)
    ecart_pourcentage = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Analyse
    favorable = models.BooleanField(default=True)
    explication = models.TextField(blank=True, null=True)
    actions_correctives = models.TextField(blank=True, null=True)
    
    # Audit
    date_analyse = models.DateTimeField(auto_now_add=True)
    analyse_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'analytique_variance'
        verbose_name = 'Analyse de variance'
        verbose_name_plural = 'Analyses de variance'
        ordering = ['-periode', '-ecart_montant']
    
    def __str__(self):
        signe = '+' if self.favorable else '-'
        return f"{self.periode} - {signe}{abs(self.ecart_montant)}"


class ReclassementCharge(models.Model):
    """Reclassement de charges entre centres"""
    MOTIFS = [
        ('erreur', 'Correction d\'erreur'),
        ('reorganisation', 'Réorganisation'),
        ('refacturation', 'Refacturation interne'),
        ('ajustement', 'Ajustement périodique'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('comptabilise', 'Comptabilisé'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='reclassements_charges')
    
    # Identification
    reference = models.CharField(max_length=50)
    date_reclassement = models.DateField()
    motif = models.CharField(max_length=20, choices=MOTIFS)
    
    # Source
    centre_source = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                      related_name='reclassements_sortants')
    
    # Destination
    centre_destination = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                           related_name='reclassements_entrants')
    
    # Montant
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Justification
    libelle = models.CharField(max_length=200)
    justification = models.TextField(blank=True, null=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='brouillon')
    
    # Écriture générée
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reclassements_crees')
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reclassements_valides')
    
    class Meta:
        db_table = 'analytique_reclassement'
        verbose_name = 'Reclassement de charge'
        verbose_name_plural = 'Reclassements de charges'
        ordering = ['-date_reclassement']
    
    def __str__(self):
        return f"{self.reference} - {self.centre_source} → {self.centre_destination}"


class RepriseCharge(models.Model):
    """Reprise de charges (refacturation interne)"""
    TYPES_REPRISE = [
        ('prestation', 'Prestation de service'),
        ('utilisation', 'Utilisation de ressource'),
        ('quote_part', 'Quote-part de frais'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='reprises_charges')
    
    # Identification
    reference = models.CharField(max_length=50)
    date_reprise = models.DateField()
    periode = models.CharField(max_length=7)
    
    # Type
    type_reprise = models.CharField(max_length=15, choices=TYPES_REPRISE)
    
    # Centre fournisseur
    centre_fournisseur = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                           related_name='reprises_fournies')
    
    # Centre bénéficiaire
    centre_beneficiaire = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                            related_name='reprises_recues')
    
    # Calcul
    quantite = models.DecimalField(max_digits=15, decimal_places=4)
    prix_unitaire = models.DecimalField(max_digits=15, decimal_places=4)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Description
    libelle = models.CharField(max_length=200)
    
    # Écriture
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'analytique_reprise_charge'
        verbose_name = 'Reprise de charge'
        verbose_name_plural = 'Reprises de charges'
        ordering = ['-date_reprise']
    
    def __str__(self):
        return f"{self.reference} - {self.montant_total}"


class RapportAnalytique(models.Model):
    """Rapports de comptabilité analytique"""
    TYPES_RAPPORT = [
        ('resultat_centre', 'Résultat par centre'),
        ('resultat_section', 'Résultat par section'),
        ('profitabilite', 'Analyse de profitabilité'),
        ('variance', 'Analyse des écarts'),
        ('cout_revient', 'Coût de revient'),
        ('tableau_bord', 'Tableau de bord'),
    ]
    PERIODICITES = [
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('annuel', 'Annuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='rapports_analytiques')
    exercice = models.ForeignKey(ExerciceComptable, on_delete=models.CASCADE,
                                 related_name='rapports_analytiques')
    
    # Identification
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    type_rapport = models.CharField(max_length=20, choices=TYPES_RAPPORT)
    periodicite = models.CharField(max_length=15, choices=PERIODICITES)
    
    # Période
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    
    # Périmètre
    centres_inclus = models.ManyToManyField(CentreCouts, related_name='rapports', blank=True)
    sections_incluses = models.ManyToManyField(SectionAnalytique, related_name='rapports', blank=True)
    
    # Données (JSON)
    donnees_json = models.JSONField(null=True, blank=True)
    
    # Indicateurs clés
    total_charges = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_produits = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat_analytique = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    marge_brute = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'),
                                      help_text='En pourcentage')
    
    # Fichier
    fichier_rapport = models.FileField(upload_to='analytique/rapports/', null=True, blank=True)
    
    # Audit
    date_generation = models.DateTimeField(auto_now_add=True)
    genere_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'analytique_rapport'
        verbose_name = 'Rapport analytique'
        verbose_name_plural = 'Rapports analytiques'
        ordering = ['-periode_fin']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class TableauBordAnalytique(models.Model):
    """Tableau de bord analytique avec KPIs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='tableaux_bord_analytiques')
    
    # Période
    periode = models.CharField(max_length=7)
    
    # Centre/Section
    centre_couts = models.ForeignKey(CentreCouts, on_delete=models.CASCADE,
                                     related_name='tableaux_bord', null=True, blank=True)
    
    # KPIs
    charges_directes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    charges_indirectes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_charges = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    produits = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    resultat = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Comparaison budget
    budget_periode = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ecart_budget = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    taux_realisation = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Comparaison N-1
    charges_n1 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    evolution_n1 = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Audit
    date_calcul = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytique_tableau_bord'
        verbose_name = 'Tableau de bord analytique'
        verbose_name_plural = 'Tableaux de bord analytiques'
        unique_together = ['entreprise', 'periode', 'centre_couts']
        ordering = ['-periode']
    
    def __str__(self):
        return f"TB {self.periode} - {self.centre_couts}"
