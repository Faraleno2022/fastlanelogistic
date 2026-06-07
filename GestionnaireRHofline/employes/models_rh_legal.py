"""
Modèles pour les fonctionnalités RH légales guinéennes.
- Indemnités de licenciement (Code du travail Art. 172)
- Gestion des préavis (Code du travail Art. 172)
- Congé maternité (Code du travail Art. 153)
- Allocations familiales CNSS
- Accidents du travail
- Jours fériés légaux
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta


class FinContrat(models.Model):
    """Gestion des fins de contrat (licenciement, démission, retraite)"""
    MOTIFS_FIN = (
        ('licenciement_economique', 'Licenciement économique'),
        ('licenciement_faute_simple', 'Licenciement pour faute simple'),
        ('licenciement_faute_grave', 'Licenciement pour faute grave'),
        ('licenciement_faute_lourde', 'Licenciement pour faute lourde'),
        ('licenciement_inaptitude', 'Licenciement pour inaptitude'),
        ('demission', 'Démission'),
        ('rupture_conventionnelle', 'Rupture conventionnelle'),
        ('fin_cdd', 'Fin de CDD'),
        ('fin_periode_essai', 'Fin de période d\'essai'),
        ('retraite', 'Départ à la retraite'),
        ('deces', 'Décès'),
    )
    
    STATUTS = (
        ('en_cours', 'En cours'),
        ('preavis', 'En préavis'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    )
    
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE, related_name='fins_contrat')
    motif = models.CharField(max_length=50, choices=MOTIFS_FIN)
    date_notification = models.DateField(help_text="Date de notification de la fin de contrat")
    date_debut_preavis = models.DateField(blank=True, null=True)
    date_fin_preavis = models.DateField(blank=True, null=True)
    duree_preavis_mois = models.IntegerField(default=0, help_text="Durée du préavis en mois")
    preavis_dispense = models.BooleanField(default=False, help_text="Dispense de préavis")
    indemnite_preavis = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Indemnités de licenciement
    anciennete_annees = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    salaire_moyen_reference = models.DecimalField(max_digits=15, decimal_places=2, default=0, 
                                                   help_text="Salaire moyen des 12 derniers mois")
    indemnite_licenciement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    detail_calcul_indemnite = models.JSONField(default=dict, blank=True)
    
    # Autres indemnités
    indemnite_conges_payes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    indemnite_compensatrice = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    autres_indemnites = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_indemnites = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Documents
    lettre_licenciement = models.FileField(upload_to='fins_contrat/lettres/', blank=True, null=True)
    certificat_travail = models.FileField(upload_to='fins_contrat/certificats/', blank=True, null=True)
    solde_tout_compte = models.FileField(upload_to='fins_contrat/soldes/', blank=True, null=True)
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    observations = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fins_contrat'
        verbose_name = 'Fin de contrat'
        verbose_name_plural = 'Fins de contrat'
        ordering = ['-date_notification']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_motif_display()} ({self.date_notification})"
    
    def calculer_preavis(self):
        """
        Calcule la durée du préavis selon la catégorie (Code du travail Art. 172)
        - Cadres supérieurs: 3 mois
        - Agents de maîtrise: 2 mois
        - Employés/Ouvriers: 1 mois
        """
        if not self.employe.poste:
            return 1  # Par défaut 1 mois
        
        categorie = getattr(self.employe.poste, 'categorie', '').lower()
        
        if 'cadre' in categorie or 'directeur' in categorie or 'responsable' in categorie:
            return 3
        elif 'maitrise' in categorie or 'superviseur' in categorie or 'chef' in categorie:
            return 2
        else:
            return 1
    
    def calculer_indemnite_licenciement(self):
        """
        Calcule l'indemnité de licenciement selon la Convention Collective Guinée.
        
        Formule:
        - Ancienneté 1-5 ans: 33% × Salaire moyen × Nb années
        - Ancienneté 6-10 ans: 35% × Salaire moyen × Nb années
        - Ancienneté >10 ans: 40% × Salaire moyen × Nb années
        
        Returns:
            tuple: (montant_total, detail_calcul)
        """
        # Pas d'indemnité pour faute grave/lourde ou période d'essai
        if self.motif in ('licenciement_faute_grave', 'licenciement_faute_lourde', 'fin_periode_essai'):
            return Decimal('0'), {'raison': 'Non éligible (faute grave/lourde ou période d\'essai)'}
        
        anciennete = float(self.anciennete_annees)
        salaire = float(self.salaire_moyen_reference)
        
        if anciennete < 1 or salaire <= 0:
            return Decimal('0'), {'raison': 'Ancienneté < 1 an ou salaire non renseigné'}
        
        detail = {
            'anciennete_totale': anciennete,
            'salaire_moyen': salaire,
            'tranches': []
        }
        
        total = Decimal('0')
        annees_restantes = anciennete
        
        # Tranche 1: 1-5 ans à 33%
        if annees_restantes > 0:
            annees_tranche1 = min(annees_restantes, 5)
            montant_tranche1 = Decimal(str(annees_tranche1)) * Decimal('0.33') * Decimal(str(salaire))
            total += montant_tranche1
            detail['tranches'].append({
                'periode': '1-5 ans',
                'annees': annees_tranche1,
                'taux': '33%',
                'montant': float(montant_tranche1)
            })
            annees_restantes -= annees_tranche1
        
        # Tranche 2: 6-10 ans à 35%
        if annees_restantes > 0:
            annees_tranche2 = min(annees_restantes, 5)
            montant_tranche2 = Decimal(str(annees_tranche2)) * Decimal('0.35') * Decimal(str(salaire))
            total += montant_tranche2
            detail['tranches'].append({
                'periode': '6-10 ans',
                'annees': annees_tranche2,
                'taux': '35%',
                'montant': float(montant_tranche2)
            })
            annees_restantes -= annees_tranche2
        
        # Tranche 3: >10 ans à 40%
        if annees_restantes > 0:
            montant_tranche3 = Decimal(str(annees_restantes)) * Decimal('0.40') * Decimal(str(salaire))
            total += montant_tranche3
            detail['tranches'].append({
                'periode': '>10 ans',
                'annees': annees_restantes,
                'taux': '40%',
                'montant': float(montant_tranche3)
            })
        
        detail['total'] = float(total)
        return total.quantize(Decimal('1')), detail
    
    def save(self, *args, **kwargs):
        # Calculer automatiquement le préavis si non défini
        if not self.duree_preavis_mois:
            self.duree_preavis_mois = self.calculer_preavis()
        
        # Calculer les dates de préavis
        if self.date_notification and not self.date_debut_preavis:
            self.date_debut_preavis = self.date_notification
        
        if self.date_debut_preavis and self.duree_preavis_mois and not self.date_fin_preavis:
            from dateutil.relativedelta import relativedelta
            self.date_fin_preavis = self.date_debut_preavis + relativedelta(months=self.duree_preavis_mois)
        
        # Calculer l'indemnité de licenciement
        if self.salaire_moyen_reference > 0:
            self.indemnite_licenciement, self.detail_calcul_indemnite = self.calculer_indemnite_licenciement()
        
        # Calculer le total des indemnités
        self.total_indemnites = (
            self.indemnite_licenciement + 
            self.indemnite_preavis + 
            self.indemnite_conges_payes + 
            self.indemnite_compensatrice + 
            self.autres_indemnites
        )
        
        super().save(*args, **kwargs)


class CongeMaternite(models.Model):
    """Gestion du congé maternité (Code du travail Art. 153)"""
    STATUTS = (
        ('demande', 'Demandé'),
        ('approuve', 'Approuvé'),
        ('en_cours', 'En cours'),
        ('prolonge', 'Prolongé'),
        ('termine', 'Terminé'),
        ('refuse', 'Refusé'),
    )
    
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE, related_name='conges_maternite')
    date_accouchement_prevue = models.DateField()
    date_accouchement_reelle = models.DateField(blank=True, null=True)
    
    # Période légale: 6 semaines avant + 8 semaines après = 14 semaines
    date_debut_prenatal = models.DateField(help_text="6 semaines avant accouchement")
    date_fin_postnatal = models.DateField(help_text="8 semaines après accouchement")
    
    # Prolongation maladie (max 21 jours)
    prolongation_maladie = models.BooleanField(default=False)
    date_fin_prolongation = models.DateField(blank=True, null=True)
    certificat_medical_prolongation = models.FileField(upload_to='maternite/certificats/', blank=True, null=True)
    
    # Congé non payé optionnel (jusqu'à 9 mois)
    conge_non_paye = models.BooleanField(default=False)
    date_fin_conge_non_paye = models.DateField(blank=True, null=True)
    
    # Indemnités CNSS
    indemnite_journaliere_cnss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_indemnites_cnss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='demande')
    observations = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conges_maternite'
        verbose_name = 'Congé maternité'
        verbose_name_plural = 'Congés maternité'
        ordering = ['-date_accouchement_prevue']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - Maternité {self.date_accouchement_prevue}"
    
    def calculer_dates(self):
        """Calcule les dates de début et fin du congé maternité"""
        if self.date_accouchement_prevue:
            # 6 semaines avant = 42 jours
            self.date_debut_prenatal = self.date_accouchement_prevue - timedelta(days=42)
            # 8 semaines après = 56 jours
            date_ref = self.date_accouchement_reelle or self.date_accouchement_prevue
            self.date_fin_postnatal = date_ref + timedelta(days=56)
            
            # Prolongation maladie (max 21 jours)
            if self.prolongation_maladie and not self.date_fin_prolongation:
                self.date_fin_prolongation = self.date_fin_postnatal + timedelta(days=21)
    
    def calculer_duree_totale(self):
        """Retourne la durée totale du congé en jours"""
        date_fin = self.date_fin_prolongation or self.date_fin_postnatal
        if self.conge_non_paye and self.date_fin_conge_non_paye:
            date_fin = self.date_fin_conge_non_paye
        
        if self.date_debut_prenatal and date_fin:
            return (date_fin - self.date_debut_prenatal).days
        return 0
    
    def save(self, *args, **kwargs):
        self.calculer_dates()
        super().save(*args, **kwargs)


class AllocationFamiliale(models.Model):
    """Allocations familiales CNSS (9 000 GNF/enfant/mois)"""
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE, related_name='allocations_familiales')
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    annee = models.IntegerField()
    
    # Enfants éligibles
    nombre_enfants_eligibles = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Montant (9 000 GNF/enfant, max 10 enfants)
    montant_par_enfant = models.DecimalField(max_digits=10, decimal_places=2, default=9000)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Conditions d'éligibilité
    jours_travailles = models.IntegerField(default=0, help_text="Min 18 jours ou 120h/mois")
    heures_travaillees = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    eligible = models.BooleanField(default=False)
    
    observations = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'allocations_familiales'
        verbose_name = 'Allocation familiale'
        verbose_name_plural = 'Allocations familiales'
        unique_together = ['employe', 'mois', 'annee']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.mois:02d}/{self.annee} - {self.montant_total} GNF"
    
    def calculer_eligibilite(self):
        """Vérifie l'éligibilité (18 jours ou 120h travaillées/mois)"""
        self.eligible = self.jours_travailles >= 18 or self.heures_travaillees >= 120
        return self.eligible
    
    def calculer_montant(self):
        """Calcule le montant des allocations familiales"""
        if not self.calculer_eligibilite():
            self.montant_total = Decimal('0')
            return self.montant_total
        
        # Max 10 enfants
        nb_enfants = min(self.nombre_enfants_eligibles, 10)
        self.montant_total = Decimal(str(nb_enfants)) * self.montant_par_enfant
        return self.montant_total
    
    def save(self, *args, **kwargs):
        self.calculer_montant()
        super().save(*args, **kwargs)


class ConjointEmploye(models.Model):
    """Conjoint (époux/épouse) de l'employé"""
    SEXES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    employe = models.OneToOneField('employes.Employe', on_delete=models.CASCADE, related_name='conjoint')
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=200)
    date_naissance = models.DateField(blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=SEXES, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    employeur = models.CharField(max_length=200, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_mariage = models.DateField(blank=True, null=True)
    lieu_mariage = models.CharField(max_length=100, blank=True, null=True)
    acte_mariage = models.FileField(upload_to='conjoints/actes_mariage/', blank=True, null=True)
    
    class Meta:
        db_table = 'conjoints_employes'
        verbose_name = 'Conjoint employé'
        verbose_name_plural = 'Conjoints employés'
    
    def __str__(self):
        return f"{self.nom} {self.prenoms} (conjoint de {self.employe.nom_complet})"


class EnfantEmploye(models.Model):
    """Enfants des employés pour les allocations familiales"""
    SEXES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE, related_name='enfants')
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=200)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXES, blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, blank=True, null=True)
    scolarise = models.BooleanField(default=False, help_text="Si scolarisé, éligible jusqu'à 20 ans")
    etablissement_scolaire = models.CharField(max_length=200, blank=True, null=True)
    certificat_scolarite = models.FileField(upload_to='enfants/scolarite/', blank=True, null=True)
    acte_naissance = models.FileField(upload_to='enfants/actes/', blank=True, null=True)
    
    class Meta:
        db_table = 'enfants_employes'
        verbose_name = 'Enfant employé'
        verbose_name_plural = 'Enfants employés'
        ordering = ['employe', '-date_naissance']
    
    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.employe.nom_complet})"
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
    
    def est_eligible_allocation(self):
        """
        Vérifie si l'enfant est éligible aux allocations familiales.
        - Âge limite: 17 ans (ou 20 ans si scolarisé)
        """
        age_limite = 20 if self.scolarise else 17
        return self.age < age_limite


# Note: Le modèle AccidentTravail existe déjà dans employes/models.py
# Note: Le modèle JourFerie existe déjà dans temps_travail/models.py


class PensionRetraite(models.Model):
    """Gestion des pensions de retraite CNSS"""
    TYPES_PENSION = (
        ('retraite_normale', 'Retraite normale'),
        ('retraite_anticipee', 'Retraite anticipée'),
        ('invalidite', 'Invalidité'),
        ('survivant', 'Pension de survivant'),
    )
    
    employe = models.ForeignKey('employes.Employe', on_delete=models.CASCADE, related_name='pensions')
    type_pension = models.CharField(max_length=30, choices=TYPES_PENSION)
    date_effet = models.DateField()
    
    # Calcul de la pension
    salaire_moyen_reference = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                   help_text="Moyenne des 3-5 meilleures années")
    trimestres_cotises = models.IntegerField(default=0)
    taux_pension = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                       help_text="% du salaire de référence")
    montant_mensuel = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Documents
    notification_cnss = models.FileField(upload_to='retraite/notifications/', blank=True, null=True)
    
    actif = models.BooleanField(default=True)
    observations = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pensions_retraite'
        verbose_name = 'Pension de retraite'
        verbose_name_plural = 'Pensions de retraite'
        ordering = ['-date_effet']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_pension_display()} ({self.montant_mensuel} GNF/mois)"
