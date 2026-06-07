from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import uuid

from core.models import Entreprise
from employes.models import Employe


class TypeContrat(models.Model):
    """Types de contrats"""
    CATEGORIES = (
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('stage', 'Stage'),
        ('apprentissage', 'Apprentissage'),
        ('prestation', 'Prestation'),
        ('consultant', 'Consultant'),
    )
    
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='types_contrats')
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    duree_periode_essai_jours = models.IntegerField(default=90, help_text="Durée période d'essai en jours")
    renouvelable = models.BooleanField(default=False)
    duree_max_mois = models.IntegerField(null=True, blank=True, help_text="Durée maximale en mois (pour CDD)")
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'types_contrats'
        verbose_name = 'Type de contrat'
        verbose_name_plural = 'Types de contrats'
        unique_together = ['entreprise', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_categorie_display()})"


class Contrat(models.Model):
    """Contrats employés"""
    STATUTS = (
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('expire', 'Expiré'),
        ('resilie', 'Résilié'),
        ('termine', 'Terminé'),
    )
    
    MOTIFS_FIN = (
        ('demission', 'Démission'),
        ('licenciement', 'Licenciement'),
        ('fin_cdd', 'Fin de CDD'),
        ('retraite', 'Retraite'),
        ('deces', 'Décès'),
        ('abandon_poste', 'Abandon de poste'),
        ('fin_stage', 'Fin de stage'),
        ('rupture_conventionnelle', 'Rupture conventionnelle'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='contrats_gestion')
    type_contrat = models.ForeignKey(TypeContrat, on_delete=models.PROTECT)
    numero_contrat = models.CharField(max_length=50, unique=True)
    
    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    date_fin_periode_essai = models.DateField(null=True, blank=True)
    date_signature = models.DateField(null=True, blank=True)
    
    # Conditions
    salaire_base = models.DecimalField(max_digits=15, decimal_places=2)
    heures_semaine = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal('40.0'))
    lieu_travail = models.CharField(max_length=200, blank=True, null=True)
    
    # Statut et fin
    statut = models.CharField(max_length=20, choices=STATUTS, default='actif')
    date_fin_effective = models.DateField(null=True, blank=True)
    motif_fin = models.CharField(max_length=30, choices=MOTIFS_FIN, null=True, blank=True)
    commentaire_fin = models.TextField(blank=True, null=True)
    
    # Documents
    fichier_contrat = models.FileField(upload_to='contrats/documents/', null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='contrats_crees')
    
    class Meta:
        db_table = 'contrats'
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['employe', 'statut'], name='idx_contrat_emp_statut'),
            models.Index(fields=['date_fin'], name='idx_contrat_date_fin'),
            models.Index(fields=['date_debut'], name='idx_contrat_date_debut'),
            models.Index(fields=['statut'], name='idx_contrat_statut'),
        ]
    
    def __str__(self):
        return f"{self.numero_contrat} - {self.employe.nom} {self.employe.prenoms}"
    
    @property
    def est_en_periode_essai(self):
        """Vérifie si le contrat est encore en période d'essai"""
        if not self.date_fin_periode_essai:
            return False
        return date.today() <= self.date_fin_periode_essai
    
    @property
    def jours_avant_expiration(self):
        """Nombre de jours avant expiration du contrat"""
        if not self.date_fin:
            return None
        return (self.date_fin - date.today()).days
    
    @property
    def expire_bientot(self):
        """Vérifie si le contrat expire dans les 30 jours"""
        jours = self.jours_avant_expiration
        return jours is not None and 0 <= jours <= 30


class AvantageContrat(models.Model):
    """Avantages liés aux contrats"""
    TYPES_AVANTAGES = (
        ('transport', 'Transport'),
        ('logement', 'Logement'),
        ('telephone', 'Téléphone'),
        ('vehicule', 'Véhicule de fonction'),
        ('formation', 'Formation'),
        ('assurance', 'Assurance'),
        ('prime', 'Prime'),
        ('autre', 'Autre'),
    )
    
    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE, related_name='avantages')
    type_avantage = models.CharField(max_length=20, choices=TYPES_AVANTAGES)
    description = models.CharField(max_length=200)
    valeur_mensuelle = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actif = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'avantages_contrats'
        verbose_name = 'Avantage contrat'
        verbose_name_plural = 'Avantages contrats'
        indexes = [
            models.Index(fields=['contrat', 'type_avantage'], name='idx_avantage_contrat_type'),
        ]
    
    def __str__(self):
        return f"{self.contrat.numero_contrat} - {self.get_type_avantage_display()}"


class AlerteContrat(models.Model):
    """Alertes pour les contrats"""
    TYPES_ALERTES = (
        ('expiration', 'Expiration contrat'),
        ('fin_essai', 'Fin période d\'essai'),
        ('renouvellement', 'Renouvellement nécessaire'),
        ('document_manquant', 'Document manquant'),
    )
    
    STATUTS_ALERTES = (
        ('active', 'Active'),
        ('traitee', 'Traitée'),
        ('ignoree', 'Ignorée'),
    )
    
    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE, related_name='alertes')
    type_alerte = models.CharField(max_length=30, choices=TYPES_ALERTES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    date_alerte = models.DateField()
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUTS_ALERTES, default='active')
    traitee_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alertes_contrats'
        verbose_name = 'Alerte contrat'
        verbose_name_plural = 'Alertes contrats'
        ordering = ['date_echeance']
        indexes = [
            models.Index(fields=['contrat', 'statut'], name='idx_alerte_contrat_statut'),
            models.Index(fields=['date_echeance'], name='idx_alerte_echeance'),
        ]
    
    def __str__(self):
        return f"{self.contrat.numero_contrat} - {self.titre}"


class DisponibiliteEmploye(models.Model):
    """Disponibilités des employés"""
    TYPES_DISPONIBILITE = (
        ('conge', 'Congé'),
        ('maladie', 'Maladie'),
        ('formation', 'Formation'),
        ('mission', 'Mission'),
        ('disponible', 'Disponible'),
        ('indisponible', 'Indisponible'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='disponibilites')
    type_disponibilite = models.CharField(max_length=20, choices=TYPES_DISPONIBILITE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    commentaire = models.TextField(blank=True, null=True)
    approuve = models.BooleanField(default=False)
    approuve_par = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='disponibilites_approuvees')
    
    class Meta:
        db_table = 'disponibilites_employes'
        verbose_name = 'Disponibilité employé'
        verbose_name_plural = 'Disponibilités employés'
        ordering = ['date_debut']
    
    def __str__(self):
        return f"{self.employe.nom} - {self.get_type_disponibilite_display()} ({self.date_debut} - {self.date_fin})"
