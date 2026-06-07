from django.db import models
from django.conf import settings
from core.models import Entreprise
import uuid


class PlanAbonnement(models.Model):
    """Plans d'abonnement disponibles"""
    nom = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    sous_titre = models.CharField(max_length=100, blank=True, help_text="Ex: Idéal pour les petites entreprises")

    # Tarification
    prix_mensuel = models.DecimalField(max_digits=12, decimal_places=0, help_text="Prix en GNF")
    prix_annuel = models.DecimalField(max_digits=12, decimal_places=0, help_text="Prix en GNF (avec réduction)")
    prix_installation = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text="Frais d'installation one-shot en GNF")

    # Limites
    max_utilisateurs = models.IntegerField(default=5)
    max_employes = models.IntegerField(default=50)

    # Fonctionnalités
    module_paie = models.BooleanField(default=True)
    module_conges = models.BooleanField(default=True)
    module_recrutement = models.BooleanField(default=False)
    module_formation = models.BooleanField(default=False)
    module_comptabilite = models.BooleanField(default=False)
    module_portail = models.BooleanField(default=False)
    support_prioritaire = models.BooleanField(default=False)
    support_telephonique = models.BooleanField(default=False)
    formation_incluse = models.BooleanField(default=False)
    personnalisation = models.BooleanField(default=False)
    multi_entreprise = models.BooleanField(default=False)
    declarations_fiscales = models.BooleanField(default=False)
    export_comptable = models.BooleanField(default=False)

    # Badges / mise en avant
    badge = models.CharField(max_length=30, blank=True, help_text="Ex: Populaire, Recommandé")
    couleur = models.CharField(max_length=7, default='#0d6efd', help_text="Couleur principale hex")
    icone = models.CharField(max_length=50, default='bi-box', help_text="Classe Bootstrap Icons")

    actif = models.BooleanField(default=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'plans_abonnement'
        ordering = ['ordre', 'prix_mensuel']
        verbose_name = 'Plan d\'abonnement'
        verbose_name_plural = 'Plans d\'abonnement'
    
    def __str__(self):
        return f"{self.nom} - {self.prix_mensuel:,.0f} GNF/mois"


class Transaction(models.Model):
    """Historique des transactions de paiement"""
    STATUTS = (
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    )
    
    METHODES = (
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Mobile Money'),
        ('visa', 'Carte Visa'),
        ('mastercard', 'Carte Mastercard'),
        ('paydunya', 'PayDunya'),
        ('paycard', 'Paycard'),
    )

    PASSERELLES = (
        ('cinetpay', 'CinetPay'),
        ('paycard', 'Paycard'),
    )
    
    TYPES = (
        ('abonnement', 'Abonnement'),
        ('renouvellement', 'Renouvellement'),
        ('upgrade', 'Mise à niveau'),
        ('installation', 'Installation & Configuration'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='transactions')
    plan = models.ForeignKey(PlanAbonnement, on_delete=models.SET_NULL, null=True)
    
    # Informations transaction
    reference = models.CharField(max_length=100, unique=True)
    token_paydunya = models.CharField(max_length=255, blank=True, null=True)
    
    type_transaction = models.CharField(max_length=20, choices=TYPES, default='abonnement')
    methode_paiement = models.CharField(max_length=20, choices=METHODES, blank=True, null=True)
    passerelle = models.CharField(max_length=20, choices=PASSERELLES, default='paycard', blank=True)
    
    # Montants
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    devise = models.CharField(max_length=3, default='GNF')
    duree_mois = models.IntegerField(default=1, help_text="Durée de l'abonnement en mois")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='pending')
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    date_expiration_abonnement = models.DateField(null=True, blank=True)
    
    # Réponse PayDunya
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    
    # Utilisateur
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='transactions_creees'
    )
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-date_creation']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.reference} - {self.montant:,.0f} GNF - {self.get_statut_display()}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            # Générer une référence unique
            import datetime
            prefix = 'GRH'
            date_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.reference = f"{prefix}-{date_str}-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)


class Abonnement(models.Model):
    """Abonnement actif d'une entreprise"""
    STATUTS = (
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('suspendu', 'Suspendu'),
        ('annule', 'Annulé'),
    )
    
    entreprise = models.OneToOneField(Entreprise, on_delete=models.CASCADE, related_name='abonnement')
    plan = models.ForeignKey(PlanAbonnement, on_delete=models.PROTECT)
    
    date_debut = models.DateField()
    date_fin = models.DateField()
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='actif')
    
    # Dernière transaction
    derniere_transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='abonnement_actif'
    )
    
    auto_renouvellement = models.BooleanField(default=False)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'abonnements'
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
    
    def __str__(self):
        return f"{self.entreprise.nom_entreprise} - {self.plan.nom} ({self.get_statut_display()})"
    
    @property
    def est_actif(self):
        from django.utils import timezone
        return self.statut == 'actif' and self.date_fin >= timezone.now().date()
    
    @property
    def jours_restants(self):
        from django.utils import timezone
        if self.date_fin:
            delta = self.date_fin - timezone.now().date()
            return max(0, delta.days)
        return 0
