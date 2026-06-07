"""
Modèles pour la gestion des missions et déplacements.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Mission(models.Model):
    """Mission ou déplacement professionnel"""
    TYPES = (
        ('mission_interne', 'Mission interne'),
        ('mission_externe', 'Mission externe'),
        ('formation', 'Formation'),
        ('conference', 'Conférence/Séminaire'),
        ('prospection', 'Prospection commerciale'),
        ('audit', 'Audit'),
        ('installation', 'Installation/Maintenance'),
        ('autre', 'Autre'),
    )
    
    STATUTS = (
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    )
    
    MOYENS_TRANSPORT = (
        ('vehicule_service', 'Véhicule de service'),
        ('vehicule_personnel', 'Véhicule personnel'),
        ('avion', 'Avion'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('taxi', 'Taxi'),
        ('autre', 'Autre'),
    )
    
    # Référence
    reference = models.CharField(max_length=50, unique=True, blank=True)
    
    # Employé
    employe = models.ForeignKey(
        'employes.Employe',
        on_delete=models.CASCADE,
        related_name='missions'
    )
    
    # Informations mission
    type_mission = models.CharField(max_length=30, choices=TYPES)
    objet = models.CharField(max_length=300, help_text="Objet de la mission")
    description = models.TextField(blank=True)
    
    # Destination
    lieu_depart = models.CharField(max_length=200, default='Conakry')
    destination = models.CharField(max_length=200)
    pays = models.CharField(max_length=100, default='Guinée')
    
    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField()
    heure_depart = models.TimeField(blank=True, null=True)
    heure_retour = models.TimeField(blank=True, null=True)
    
    # Transport
    moyen_transport = models.CharField(max_length=30, choices=MOYENS_TRANSPORT, default='vehicule_service')
    details_transport = models.TextField(blank=True, help_text="Détails du transport")
    
    # Hébergement
    avec_hebergement = models.BooleanField(default=False)
    hotel = models.CharField(max_length=200, blank=True)
    adresse_hebergement = models.TextField(blank=True)
    
    # Budget
    budget_previsionnel = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    avance_accordee = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    depenses_reelles = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Indemnités
    indemnite_journaliere = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        help_text="Per diem journalier"
    )
    
    # Workflow
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifiee')
    validee_par = models.ForeignKey(
        'employes.Employe',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='missions_validees'
    )
    date_validation = models.DateTimeField(blank=True, null=True)
    
    # Rapport
    rapport_mission = models.TextField(blank=True, help_text="Compte-rendu de mission")
    objectifs_atteints = models.BooleanField(default=False)
    
    # Documents
    ordre_mission = models.FileField(
        upload_to='missions/ordres/%Y/%m/',
        blank=True, null=True,
        help_text="Ordre de mission signé"
    )
    
    # Traçabilité
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'missions'
        verbose_name = 'Mission'
        verbose_name_plural = 'Missions'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.reference} - {self.employe.nom} - {self.destination}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            from datetime import date
            prefix = f"MIS{date.today().strftime('%Y%m')}"
            last = Mission.objects.filter(reference__startswith=prefix).order_by('-reference').first()
            if last:
                num = int(last.reference[-4:]) + 1
            else:
                num = 1
            self.reference = f"{prefix}{num:04d}"
        super().save(*args, **kwargs)
    
    @property
    def duree_jours(self):
        """Calculer la durée en jours"""
        if self.date_debut and self.date_fin:
            return (self.date_fin - self.date_debut).days + 1
        return 0
    
    @property
    def total_indemnites(self):
        """Total des indemnités journalières"""
        return self.indemnite_journaliere * self.duree_jours
    
    @property
    def solde_avance(self):
        """Solde entre avance et dépenses"""
        return self.avance_accordee - self.depenses_reelles


class FraisMission(models.Model):
    """Frais associés à une mission"""
    TYPES_FRAIS = (
        ('transport', 'Transport'),
        ('hebergement', 'Hébergement'),
        ('restauration', 'Restauration'),
        ('communication', 'Communication'),
        ('representation', 'Représentation'),
        ('divers', 'Divers'),
    )
    
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='frais'
    )
    type_frais = models.CharField(max_length=30, choices=TYPES_FRAIS)
    date_depense = models.DateField()
    description = models.CharField(max_length=500)
    montant = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    justificatif = models.FileField(
        upload_to='missions/justificatifs/%Y/%m/',
        blank=True, null=True
    )
    
    class Meta:
        db_table = 'frais_missions'
        verbose_name = 'Frais de mission'
        verbose_name_plural = 'Frais de mission'
        ordering = ['date_depense']
    
    def __str__(self):
        return f"{self.get_type_frais_display()} - {self.montant} GNF"


class BaremeIndemnite(models.Model):
    """Barèmes d'indemnités journalières par zone"""
    ZONES = (
        ('conakry', 'Conakry'),
        ('interieur', 'Intérieur du pays'),
        ('afrique', 'Afrique'),
        ('international', 'International'),
    )
    
    zone = models.CharField(max_length=30, choices=ZONES)
    categorie_employe = models.CharField(
        max_length=50,
        choices=(
            ('direction', 'Direction'),
            ('cadre_superieur', 'Cadre supérieur'),
            ('cadre', 'Cadre'),
            ('agent_maitrise', 'Agent de maîtrise'),
            ('employe', 'Employé'),
        ),
        blank=True,
        help_text="Laisser vide pour tous"
    )
    indemnite_journaliere = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Per diem en GNF"
    )
    plafond_hebergement = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        help_text="Plafond hébergement/nuit en GNF"
    )
    plafond_restauration = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        help_text="Plafond restauration/jour en GNF"
    )
    date_debut = models.DateField()
    date_fin = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'baremes_indemnites'
        verbose_name = 'Barème indemnité'
        verbose_name_plural = 'Barèmes indemnités'
        ordering = ['zone', 'categorie_employe']
    
    def __str__(self):
        return f"{self.get_zone_display()} - {self.get_categorie_employe_display() or 'Tous'}: {self.indemnite_journaliere} GNF/jour"
