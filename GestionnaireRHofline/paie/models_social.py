"""
Module Paie & Charges Sociales - Modèles complémentaires
Cotisations, déclarations CNSS, mutuelles, retraite complémentaire
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur
from employes.models import Employe


class CotisationSociale(models.Model):
    """Définition des cotisations sociales (patronales et salariales)"""
    TYPES_COTISATION = [
        ('cnss_salarie', 'CNSS Salarié'),
        ('cnss_employeur', 'CNSS Employeur'),
        ('vf', 'Versement Forfaitaire'),
        ('ta', 'Taxe d\'Apprentissage'),
        ('onfpp', 'Contribution ONFPP'),
        ('mutuelle_salarie', 'Mutuelle Salarié'),
        ('mutuelle_employeur', 'Mutuelle Employeur'),
        ('retraite_salarie', 'Retraite Complémentaire Salarié'),
        ('retraite_employeur', 'Retraite Complémentaire Employeur'),
        ('prevoyance', 'Prévoyance'),
        ('autre', 'Autre'),
    ]
    BASES_CALCUL = [
        ('brut', 'Salaire brut'),
        ('brut_plafonne', 'Salaire brut plafonné'),
        ('base_cnss', 'Base CNSS'),
        ('net_imposable', 'Net imposable'),
        ('forfait', 'Montant forfaitaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='cotisations_sociales', null=True, blank=True)
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    type_cotisation = models.CharField(max_length=20, choices=TYPES_COTISATION)
    
    # Calcul
    base_calcul = models.CharField(max_length=20, choices=BASES_CALCUL, default='brut')
    taux = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.00'),
                               help_text='Taux en pourcentage')
    montant_forfaitaire = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Plafonds (CNSS Guinée: plancher 550 000 GNF, plafond 2 500 000 GNF)
    plancher = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                   help_text='Plancher de cotisation (SMIG)')
    plafond = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                  help_text='Plafond de cotisation')
    
    # Part
    est_part_salariale = models.BooleanField(default=False)
    est_part_patronale = models.BooleanField(default=False)
    
    # Période de validité
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    
    # Organisme collecteur
    organisme = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'paie_cotisation_sociale'
        verbose_name = 'Cotisation sociale'
        verbose_name_plural = 'Cotisations sociales'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"
    
    def calculer_cotisation(self, base_brute):
        """Calcule le montant de la cotisation"""
        if self.montant_forfaitaire:
            return self.montant_forfaitaire
        
        base = base_brute
        if self.plancher and base < self.plancher:
            base = self.plancher
        if self.plafond and base > self.plafond:
            base = self.plafond
        
        return base * (self.taux / 100)


class DeclarationCNSS(models.Model):
    """Déclarations CNSS/URSSAF"""
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('calcule', 'Calculé'),
        ('valide', 'Validé'),
        ('depose', 'Déposé'),
        ('paye', 'Payé'),
    ]
    TYPES_DECLARATION = [
        ('mensuelle', 'Déclaration mensuelle'),
        ('trimestrielle', 'Déclaration trimestrielle'),
        ('annuelle', 'Déclaration annuelle'),
        ('rectificative', 'Déclaration rectificative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='declarations_cnss')
    
    # Identification
    reference = models.CharField(max_length=50)
    type_declaration = models.CharField(max_length=20, choices=TYPES_DECLARATION, default='mensuelle')
    
    # Période
    annee = models.IntegerField()
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True)
    trimestre = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)], null=True, blank=True)
    
    # Effectifs
    effectif_total = models.IntegerField(default=0)
    effectif_declare = models.IntegerField(default=0)
    
    # Masses salariales
    masse_salariale_brute = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    masse_salariale_plafonnee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Cotisations
    cotisation_salariale = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                               help_text='5% part salariale')
    cotisation_patronale = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                               help_text='18% part patronale')
    total_cotisations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Pénalités
    penalites_retard = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    majorations = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Total à payer
    montant_a_payer = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Dates
    date_limite = models.DateField()
    date_depot = models.DateField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='declarations_cnss_validees')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Fichier
    fichier_declaration = models.FileField(upload_to='paie/declarations_cnss/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'paie_declaration_cnss'
        verbose_name = 'Déclaration CNSS'
        verbose_name_plural = 'Déclarations CNSS'
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        periode = f"{self.mois}/{self.annee}" if self.mois else f"T{self.trimestre}/{self.annee}"
        return f"CNSS {periode} - {self.entreprise.nom}"
    
    def calculer_cotisations(self):
        """Calcule les cotisations CNSS"""
        # Taux CNSS Guinée
        TAUX_SALARIE = Decimal('5.00')
        TAUX_EMPLOYEUR = Decimal('18.00')
        
        self.cotisation_salariale = self.masse_salariale_plafonnee * (TAUX_SALARIE / 100)
        self.cotisation_patronale = self.masse_salariale_plafonnee * (TAUX_EMPLOYEUR / 100)
        self.total_cotisations = self.cotisation_salariale + self.cotisation_patronale
        self.montant_a_payer = self.total_cotisations + self.penalites_retard + self.majorations
        self.save()


class LigneCNSS(models.Model):
    """Détail par salarié de la déclaration CNSS"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    declaration = models.ForeignKey(DeclarationCNSS, on_delete=models.CASCADE,
                                    related_name='lignes')
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                related_name='lignes_cnss')
    
    # Identification
    numero_cnss = models.CharField(max_length=50, blank=True, null=True)
    
    # Salaires
    salaire_brut = models.DecimalField(max_digits=15, decimal_places=2)
    salaire_plafonne = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Cotisations
    cotisation_salariale = models.DecimalField(max_digits=15, decimal_places=2)
    cotisation_patronale = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Jours travaillés
    jours_travailles = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'paie_ligne_cnss'
        verbose_name = 'Ligne CNSS'
        verbose_name_plural = 'Lignes CNSS'
    
    def __str__(self):
        return f"{self.employe} - {self.salaire_brut}"


class MutuelleEntreprise(models.Model):
    """Mutuelles d'entreprise"""
    TYPES_COUVERTURE = [
        ('base', 'Couverture de base'),
        ('etendue', 'Couverture étendue'),
        ('famille', 'Couverture famille'),
        ('premium', 'Couverture premium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='mutuelles')
    
    # Identification
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=200)
    organisme = models.CharField(max_length=200)
    numero_contrat = models.CharField(max_length=50)
    
    # Type de couverture
    type_couverture = models.CharField(max_length=15, choices=TYPES_COUVERTURE)
    
    # Cotisations
    cotisation_salarie = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cotisation_employeur = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cotisation_conjoint = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cotisation_enfant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    
    # Contact
    contact_nom = models.CharField(max_length=100, blank=True, null=True)
    contact_telephone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    class Meta:
        db_table = 'paie_mutuelle'
        verbose_name = 'Mutuelle entreprise'
        verbose_name_plural = 'Mutuelles entreprise'
    
    def __str__(self):
        return f"{self.nom} - {self.organisme}"


class AffiliationMutuelle(models.Model):
    """Affiliation des salariés à la mutuelle"""
    STATUTS = [
        ('active', 'Active'),
        ('suspendue', 'Suspendue'),
        ('resiliee', 'Résiliée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mutuelle = models.ForeignKey(MutuelleEntreprise, on_delete=models.CASCADE,
                                 related_name='affiliations')
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                related_name='affiliations_mutuelle')
    
    # Affiliation
    date_affiliation = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=15, choices=STATUTS, default='active')
    
    # Bénéficiaires
    inclut_conjoint = models.BooleanField(default=False)
    nombre_enfants = models.IntegerField(default=0)
    
    # Cotisation mensuelle
    cotisation_mensuelle = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        db_table = 'paie_affiliation_mutuelle'
        verbose_name = 'Affiliation mutuelle'
        verbose_name_plural = 'Affiliations mutuelle'
        unique_together = ['mutuelle', 'employe']
    
    def __str__(self):
        return f"{self.employe} - {self.mutuelle.nom}"


class RetraiteComplementaire(models.Model):
    """Régimes de retraite complémentaire"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='retraites_complementaires')
    
    # Identification
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=200)
    organisme = models.CharField(max_length=200)
    numero_contrat = models.CharField(max_length=50)
    
    # Cotisations
    taux_salarie = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    taux_employeur = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    plafond = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'paie_retraite_complementaire'
        verbose_name = 'Retraite complémentaire'
        verbose_name_plural = 'Retraites complémentaires'
    
    def __str__(self):
        return f"{self.nom} - {self.organisme}"


class AffiliationRetraite(models.Model):
    """Affiliation des salariés à la retraite complémentaire"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retraite = models.ForeignKey(RetraiteComplementaire, on_delete=models.CASCADE,
                                 related_name='affiliations')
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                related_name='affiliations_retraite')
    
    # Affiliation
    date_affiliation = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    
    # Numéro adhérent
    numero_adherent = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'paie_affiliation_retraite'
        verbose_name = 'Affiliation retraite'
        verbose_name_plural = 'Affiliations retraite'
        unique_together = ['retraite', 'employe']
    
    def __str__(self):
        return f"{self.employe} - {self.retraite.nom}"


class AffiliationSecuriteSociale(models.Model):
    """Affiliations à la sécurité sociale (CNSS)"""
    STATUTS = [
        ('en_cours', 'En cours d\'immatriculation'),
        ('active', 'Active'),
        ('suspendue', 'Suspendue'),
        ('radiee', 'Radiée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.OneToOneField(Employe, on_delete=models.CASCADE,
                                   related_name='affiliation_cnss')
    
    # Numéro CNSS
    numero_cnss = models.CharField(max_length=50, unique=True)
    
    # Dates
    date_immatriculation = models.DateField()
    date_affiliation_entreprise = models.DateField()
    date_radiation = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='active')
    
    # Documents
    carte_cnss = models.FileField(upload_to='paie/cartes_cnss/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paie_affiliation_securite_sociale'
        verbose_name = 'Affiliation sécurité sociale'
        verbose_name_plural = 'Affiliations sécurité sociale'
    
    def __str__(self):
        return f"{self.employe} - CNSS {self.numero_cnss}"


class DossierPaie(models.Model):
    """Dossier de paie centralisé par période"""
    STATUTS = [
        ('ouvert', 'Ouvert'),
        ('en_calcul', 'En calcul'),
        ('calcule', 'Calculé'),
        ('valide', 'Validé'),
        ('paye', 'Payé'),
        ('cloture', 'Clôturé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='dossiers_paie')
    
    # Période
    annee = models.IntegerField()
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    # Effectifs
    effectif_total = models.IntegerField(default=0)
    effectif_paye = models.IntegerField(default=0)
    
    # Totaux
    masse_salariale_brute = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_cotisations_salariales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_cotisations_patronales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_rts = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_net_a_payer = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Charges patronales détaillées
    total_cnss_employeur = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_vf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_ta = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='ouvert')
    
    # Dates
    date_calcul = models.DateTimeField(null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_paiement = models.DateField(null=True, blank=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    
    # Validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='dossiers_paie_valides')
    cloture_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='dossiers_paie_clotures')
    
    # Observations
    observations = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'paie_dossier'
        verbose_name = 'Dossier de paie'
        verbose_name_plural = 'Dossiers de paie'
        unique_together = ['entreprise', 'annee', 'mois']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"Dossier paie {self.mois}/{self.annee}"


class BilanPaie(models.Model):
    """Bilan de paie mensuel/annuel"""
    TYPES_BILAN = [
        ('mensuel', 'Bilan mensuel'),
        ('trimestriel', 'Bilan trimestriel'),
        ('annuel', 'Bilan annuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='bilans_paie')
    
    # Type et période
    type_bilan = models.CharField(max_length=15, choices=TYPES_BILAN)
    annee = models.IntegerField()
    mois = models.IntegerField(null=True, blank=True)
    trimestre = models.IntegerField(null=True, blank=True)
    
    # Effectifs
    effectif_moyen = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    entrees = models.IntegerField(default=0)
    sorties = models.IntegerField(default=0)
    
    # Masses salariales
    masse_salariale_brute = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    masse_salariale_nette = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Cotisations
    cotisations_salariales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    cotisations_patronales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Impôts
    rts_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Coût total employeur
    cout_total_employeur = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Comparaison N-1
    masse_salariale_n1 = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    evolution_pourcentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Fichier
    fichier_bilan = models.FileField(upload_to='paie/bilans/', null=True, blank=True)
    
    # Audit
    date_generation = models.DateTimeField(auto_now_add=True)
    genere_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'paie_bilan'
        verbose_name = 'Bilan de paie'
        verbose_name_plural = 'Bilans de paie'
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        if self.type_bilan == 'mensuel':
            return f"Bilan paie {self.mois}/{self.annee}"
        elif self.type_bilan == 'trimestriel':
            return f"Bilan paie T{self.trimestre}/{self.annee}"
        return f"Bilan paie annuel {self.annee}"
