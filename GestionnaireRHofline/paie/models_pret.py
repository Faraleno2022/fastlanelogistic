"""
Modèles pour la gestion des prêts employés.
- Prêt avec échéancier de remboursement
- Retenues automatiques sur salaire
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from employes.models import Employe
from core.models import Entreprise


class Pret(models.Model):
    """Prêt accordé à un employé"""
    TYPES_PRET = (
        ('avance_salaire', 'Avance sur salaire'),
        ('pret_personnel', 'Prêt personnel'),
        ('pret_logement', 'Prêt logement'),
        ('pret_vehicule', 'Prêt véhicule'),
        ('pret_social', 'Prêt social'),
        ('autre', 'Autre'),
    )
    
    STATUTS = (
        ('en_attente', 'En attente d\'approbation'),
        ('approuve', 'Approuvé'),
        ('en_cours', 'En cours de remboursement'),
        ('solde', 'Soldé'),
        ('annule', 'Annulé'),
    )
    
    # Identification
    numero_pret = models.CharField(max_length=20, unique=True, help_text="Numéro unique du prêt")
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='prets')
    type_pret = models.CharField(max_length=30, choices=TYPES_PRET, default='avance_salaire')
    
    # Montants
    montant_pret = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], help_text="Montant total du prêt")
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Taux d'intérêt annuel en %")
    montant_interets = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Total des intérêts")
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Montant total à rembourser")
    
    # Remboursement
    nombre_echeances = models.IntegerField(validators=[MinValueValidator(1)], help_text="Nombre de mensualités")
    montant_echeance = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Montant de chaque échéance")
    date_debut_remboursement = models.DateField(help_text="Date de la première échéance")
    
    # Suivi
    montant_rembourse = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Montant déjà remboursé")
    solde_restant = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Solde restant à rembourser")
    echeances_payees = models.IntegerField(default=0, help_text="Nombre d'échéances payées")
    
    # Dates et statut
    date_demande = models.DateField(auto_now_add=True)
    date_approbation = models.DateField(null=True, blank=True)
    date_cloture = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    
    # Approbation
    approbateur = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='prets_approuves')
    motif = models.TextField(blank=True, help_text="Motif de la demande de prêt")
    commentaire_approbation = models.TextField(blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prets'
        verbose_name = 'Prêt'
        verbose_name_plural = 'Prêts'
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"{self.numero_pret} - {self.employe.nom} ({self.montant_pret:,.0f} GNF)"
    
    def save(self, *args, **kwargs):
        # Générer le numéro de prêt si nouveau
        if not self.numero_pret:
            annee = date.today().year
            dernier = Pret.objects.filter(numero_pret__startswith=f'PRT-{annee}').count()
            self.numero_pret = f'PRT-{annee}-{dernier + 1:04d}'
        
        # Calculer les montants
        self.calculer_montants()
        
        super().save(*args, **kwargs)
    
    def calculer_montants(self):
        """Calcule les montants du prêt"""
        # Intérêts simples
        if self.taux_interet > 0:
            duree_annees = self.nombre_echeances / Decimal('12')
            self.montant_interets = (self.montant_pret * self.taux_interet / Decimal('100') * duree_annees).quantize(Decimal('1'))
        else:
            self.montant_interets = Decimal('0')
        
        self.montant_total = self.montant_pret + self.montant_interets
        self.montant_echeance = (self.montant_total / self.nombre_echeances).quantize(Decimal('1'))
        self.solde_restant = self.montant_total - self.montant_rembourse
    
    def generer_echeancier(self):
        """Génère l'échéancier de remboursement"""
        # Supprimer les anciennes échéances non payées
        self.echeances.filter(statut='en_attente').delete()
        
        date_echeance = self.date_debut_remboursement
        solde = self.montant_total
        
        for i in range(1, self.nombre_echeances + 1):
            # Vérifier si l'échéance existe déjà
            echeance_existante = self.echeances.filter(numero_echeance=i).first()
            if echeance_existante and echeance_existante.statut == 'paye':
                date_echeance = date_echeance + relativedelta(months=1)
                continue
            
            montant = self.montant_echeance
            # Ajuster la dernière échéance pour le solde exact
            if i == self.nombre_echeances:
                montant = solde
            
            EcheancePret.objects.update_or_create(
                pret=self,
                numero_echeance=i,
                defaults={
                    'date_echeance': date_echeance,
                    'montant_echeance': montant,
                    'solde_avant': solde,
                    'solde_apres': solde - montant,
                }
            )
            
            solde -= montant
            date_echeance = date_echeance + relativedelta(months=1)
    
    def enregistrer_remboursement(self, montant, bulletin=None):
        """Enregistre un remboursement"""
        # Trouver la prochaine échéance à payer
        echeance = self.echeances.filter(statut='en_attente').order_by('numero_echeance').first()
        
        if echeance:
            echeance.montant_paye = montant
            echeance.date_paiement = date.today()
            echeance.bulletin = bulletin
            echeance.statut = 'paye'
            echeance.save()
            
            # Mettre à jour le prêt
            self.montant_rembourse += montant
            self.solde_restant = self.montant_total - self.montant_rembourse
            self.echeances_payees += 1
            
            # Vérifier si le prêt est soldé
            if self.solde_restant <= 0:
                self.statut = 'solde'
                self.date_cloture = date.today()
            
            self.save()
            return True
        
        return False


class EcheancePret(models.Model):
    """Échéance de remboursement d'un prêt"""
    STATUTS = (
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('en_retard', 'En retard'),
    )
    
    pret = models.ForeignKey(Pret, on_delete=models.CASCADE, related_name='echeances')
    numero_echeance = models.IntegerField()
    date_echeance = models.DateField()
    montant_echeance = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Soldes
    solde_avant = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    solde_apres = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Paiement
    montant_paye = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_paiement = models.DateField(null=True, blank=True)
    bulletin = models.ForeignKey('paie.BulletinPaie', on_delete=models.SET_NULL, null=True, blank=True, related_name='remboursements_prets')
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    
    class Meta:
        db_table = 'echeances_prets'
        verbose_name = 'Échéance de prêt'
        verbose_name_plural = 'Échéances de prêts'
        unique_together = ['pret', 'numero_echeance']
        ordering = ['pret', 'numero_echeance']
    
    def __str__(self):
        return f"{self.pret.numero_pret} - Éch. {self.numero_echeance}/{self.pret.nombre_echeances}"
    
    def est_en_retard(self):
        """Vérifie si l'échéance est en retard"""
        if self.statut == 'en_attente' and self.date_echeance < date.today():
            self.statut = 'en_retard'
            self.save()
            return True
        return self.statut == 'en_retard'
