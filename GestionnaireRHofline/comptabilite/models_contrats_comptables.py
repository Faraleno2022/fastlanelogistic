"""
Module Gestion Comptable des Contrats
Contrats fournisseurs/clients, conditions paiement/livraison, pénalités, suivi
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur
from .models import Tiers, Facture


class ContratFournisseur(models.Model):
    """Contrats avec les fournisseurs"""
    TYPES_CONTRAT = [
        ('achat', 'Contrat d\'achat'),
        ('service', 'Contrat de service'),
        ('maintenance', 'Contrat de maintenance'),
        ('location', 'Contrat de location'),
        ('prestation', 'Contrat de prestation'),
        ('cadre', 'Contrat cadre'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('en_negociation', 'En négociation'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('expire', 'Expiré'),
        ('resilie', 'Résilié'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='contrats_fournisseurs')
    fournisseur = models.ForeignKey(Tiers, on_delete=models.CASCADE,
                                    related_name='contrats_fournisseur',
                                    limit_choices_to={'type_tiers': 'fournisseur'})
    
    # Identification
    numero_contrat = models.CharField(max_length=50)
    reference_externe = models.CharField(max_length=50, blank=True, null=True,
                                         help_text='Référence chez le fournisseur')
    type_contrat = models.CharField(max_length=20, choices=TYPES_CONTRAT)
    objet = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    
    # Montants
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_annuel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    devise = models.CharField(max_length=3, default='GNF')
    
    # Période
    date_signature = models.DateField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    duree_mois = models.IntegerField(default=12)
    
    # Renouvellement
    renouvellement_auto = models.BooleanField(default=False)
    preavis_resiliation_jours = models.IntegerField(default=30)
    date_prochain_renouvellement = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    
    # Documents
    document_contrat = models.FileField(upload_to='contrats/fournisseurs/', null=True, blank=True)
    
    # Responsable interne
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='contrats_fournisseurs_responsable')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='contrats_fournisseurs_crees')
    
    class Meta:
        db_table = 'contrats_fournisseur'
        verbose_name = 'Contrat fournisseur'
        verbose_name_plural = 'Contrats fournisseurs'
        unique_together = ['entreprise', 'numero_contrat']
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.numero_contrat} - {self.fournisseur.nom}"
    
    @property
    def est_actif(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.statut == 'actif' and self.date_debut <= today <= self.date_fin
    
    @property
    def jours_avant_expiration(self):
        from django.utils import timezone
        if self.date_fin:
            return (self.date_fin - timezone.now().date()).days
        return None


class ContratClient(models.Model):
    """Contrats avec les clients"""
    TYPES_CONTRAT = [
        ('vente', 'Contrat de vente'),
        ('service', 'Contrat de service'),
        ('abonnement', 'Abonnement'),
        ('maintenance', 'Contrat de maintenance'),
        ('projet', 'Contrat projet'),
        ('cadre', 'Contrat cadre'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('en_negociation', 'En négociation'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('expire', 'Expiré'),
        ('resilie', 'Résilié'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='contrats_clients')
    client = models.ForeignKey(Tiers, on_delete=models.CASCADE,
                               related_name='contrats_client',
                               limit_choices_to={'type_tiers': 'client'})
    
    # Identification
    numero_contrat = models.CharField(max_length=50)
    reference_client = models.CharField(max_length=50, blank=True, null=True)
    type_contrat = models.CharField(max_length=20, choices=TYPES_CONTRAT)
    objet = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    
    # Montants
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_annuel = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    devise = models.CharField(max_length=3, default='GNF')
    
    # Période
    date_signature = models.DateField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    duree_mois = models.IntegerField(default=12)
    
    # Renouvellement
    renouvellement_auto = models.BooleanField(default=False)
    preavis_resiliation_jours = models.IntegerField(default=30)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    
    # Documents
    document_contrat = models.FileField(upload_to='contrats/clients/', null=True, blank=True)
    
    # Responsable commercial
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='contrats_clients_responsable')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='contrats_clients_crees')
    
    class Meta:
        db_table = 'contrats_client'
        verbose_name = 'Contrat client'
        verbose_name_plural = 'Contrats clients'
        unique_together = ['entreprise', 'numero_contrat']
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.numero_contrat} - {self.client.nom}"


class ConditionsPaiement(models.Model):
    """Conditions de paiement spécifiques par contrat"""
    MODES_PAIEMENT = [
        ('comptant', 'Comptant'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('traite', 'Traite'),
        ('lettre_change', 'Lettre de change'),
        ('prelevement', 'Prélèvement'),
        ('especes', 'Espèces'),
    ]
    ECHEANCES = [
        ('reception', 'À réception'),
        ('30_jours', '30 jours'),
        ('45_jours', '45 jours'),
        ('60_jours', '60 jours'),
        ('90_jours', '90 jours'),
        ('fin_mois', 'Fin de mois'),
        ('fin_mois_30', 'Fin de mois + 30 jours'),
        ('personnalise', 'Personnalisé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat (un seul à la fois)
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='conditions_paiement')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='conditions_paiement')
    
    # Conditions
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT)
    echeance = models.CharField(max_length=20, choices=ECHEANCES)
    delai_paiement_jours = models.IntegerField(default=30)
    
    # Escompte
    escompte_paiement_anticipe = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'),
                                                     help_text='Pourcentage d\'escompte')
    delai_escompte_jours = models.IntegerField(default=10)
    
    # Acompte
    acompte_requis = models.BooleanField(default=False)
    pourcentage_acompte = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Paiement échelonné
    paiement_echelonne = models.BooleanField(default=False)
    nombre_echeances = models.IntegerField(default=1)
    
    # Notes
    conditions_speciales = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'contrats_conditions_paiement'
        verbose_name = 'Condition de paiement'
        verbose_name_plural = 'Conditions de paiement'
    
    def __str__(self):
        contrat = self.contrat_fournisseur or self.contrat_client
        return f"Paiement {self.get_echeance_display()} - {contrat}"


class ConditionsLivraison(models.Model):
    """Conditions de livraison"""
    INCOTERMS = [
        ('EXW', 'EXW - Ex Works'),
        ('FCA', 'FCA - Free Carrier'),
        ('CPT', 'CPT - Carriage Paid To'),
        ('CIP', 'CIP - Carriage Insurance Paid'),
        ('DAP', 'DAP - Delivered At Place'),
        ('DPU', 'DPU - Delivered at Place Unloaded'),
        ('DDP', 'DDP - Delivered Duty Paid'),
        ('FAS', 'FAS - Free Alongside Ship'),
        ('FOB', 'FOB - Free On Board'),
        ('CFR', 'CFR - Cost and Freight'),
        ('CIF', 'CIF - Cost Insurance Freight'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='conditions_livraison')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='conditions_livraison')
    
    # Incoterm
    incoterm = models.CharField(max_length=3, choices=INCOTERMS, blank=True, null=True)
    lieu_livraison = models.CharField(max_length=200)
    
    # Délais
    delai_livraison_jours = models.IntegerField(default=0)
    delai_livraison_description = models.CharField(max_length=200, blank=True, null=True)
    
    # Transport
    mode_transport = models.CharField(max_length=50, blank=True, null=True)
    frais_transport_inclus = models.BooleanField(default=False)
    
    # Assurance
    assurance_incluse = models.BooleanField(default=False)
    
    # Conditions spéciales
    conditions_speciales = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'contrats_conditions_livraison'
        verbose_name = 'Condition de livraison'
        verbose_name_plural = 'Conditions de livraison'
    
    def __str__(self):
        return f"{self.get_incoterm_display()} - {self.lieu_livraison}"


class PointGaranti(models.Model):
    """Points garantis contractuels"""
    TYPES_GARANTIE = [
        ('qualite', 'Garantie qualité'),
        ('delai', 'Garantie délai'),
        ('performance', 'Garantie performance'),
        ('sav', 'Service après-vente'),
        ('remplacement', 'Garantie remplacement'),
        ('remboursement', 'Garantie remboursement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='garanties')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='garanties')
    
    # Garantie
    type_garantie = models.CharField(max_length=20, choices=TYPES_GARANTIE)
    description = models.TextField()
    
    # Durée
    duree_garantie_mois = models.IntegerField(default=12)
    date_debut_garantie = models.DateField(null=True, blank=True)
    date_fin_garantie = models.DateField(null=True, blank=True)
    
    # Conditions
    conditions_application = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)
    
    # Valeur
    montant_garanti = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'contrats_point_garanti'
        verbose_name = 'Point garanti'
        verbose_name_plural = 'Points garantis'
    
    def __str__(self):
        return f"{self.get_type_garantie_display()}"


class PenaliteRetard(models.Model):
    """Pénalités de retard contractuelles"""
    TYPES_PENALITE = [
        ('retard_paiement', 'Retard de paiement'),
        ('retard_livraison', 'Retard de livraison'),
        ('non_conformite', 'Non-conformité'),
        ('rupture', 'Rupture de contrat'),
    ]
    MODES_CALCUL = [
        ('pourcentage_jour', 'Pourcentage par jour'),
        ('pourcentage_semaine', 'Pourcentage par semaine'),
        ('montant_fixe_jour', 'Montant fixe par jour'),
        ('montant_forfaitaire', 'Montant forfaitaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='penalites')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='penalites')
    
    # Type
    type_penalite = models.CharField(max_length=20, choices=TYPES_PENALITE)
    description = models.TextField()
    
    # Calcul
    mode_calcul = models.CharField(max_length=20, choices=MODES_CALCUL)
    taux = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.00'),
                               help_text='Taux en pourcentage')
    montant_fixe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Plafond
    plafond_penalite = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                           help_text='Montant maximum de pénalité')
    plafond_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                              help_text='Pourcentage max du montant contrat')
    
    # Franchise
    jours_franchise = models.IntegerField(default=0, help_text='Jours sans pénalité')
    
    class Meta:
        db_table = 'contrats_penalite_retard'
        verbose_name = 'Pénalité de retard'
        verbose_name_plural = 'Pénalités de retard'
    
    def __str__(self):
        return f"{self.get_type_penalite_display()} - {self.taux}%"


class ReclamationContractuelle(models.Model):
    """Réclamations liées aux contrats"""
    TYPES_RECLAMATION = [
        ('qualite', 'Problème qualité'),
        ('delai', 'Retard livraison'),
        ('facturation', 'Erreur facturation'),
        ('conformite', 'Non-conformité'),
        ('garantie', 'Litige garantie'),
        ('autre', 'Autre'),
    ]
    STATUTS = [
        ('ouverte', 'Ouverte'),
        ('en_cours', 'En cours de traitement'),
        ('en_attente', 'En attente réponse'),
        ('resolue', 'Résolue'),
        ('rejetee', 'Rejetée'),
        ('litige', 'En litige'),
    ]
    PRIORITES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='reclamations_contractuelles')
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='reclamations')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='reclamations')
    
    # Identification
    numero_reclamation = models.CharField(max_length=50)
    type_reclamation = models.CharField(max_length=20, choices=TYPES_RECLAMATION)
    priorite = models.CharField(max_length=10, choices=PRIORITES, default='normale')
    
    # Description
    objet = models.CharField(max_length=300)
    description = models.TextField()
    
    # Montant en jeu
    montant_reclame = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_accorde = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Dates
    date_reclamation = models.DateField()
    date_limite_reponse = models.DateField(null=True, blank=True)
    date_resolution = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='ouverte')
    
    # Résolution
    resolution = models.TextField(blank=True, null=True)
    
    # Responsable
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reclamations_responsable')
    
    # Documents
    pieces_jointes = models.FileField(upload_to='contrats/reclamations/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'contrats_reclamation'
        verbose_name = 'Réclamation contractuelle'
        verbose_name_plural = 'Réclamations contractuelles'
        ordering = ['-date_reclamation']
    
    def __str__(self):
        return f"{self.numero_reclamation} - {self.objet}"


class SuiviContrat(models.Model):
    """Suivi de conformité des contrats"""
    TYPES_EVENEMENT = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('renouvellement', 'Renouvellement'),
        ('suspension', 'Suspension'),
        ('reprise', 'Reprise'),
        ('resiliation', 'Résiliation'),
        ('alerte', 'Alerte'),
        ('echeance', 'Échéance'),
        ('facturation', 'Facturation'),
        ('paiement', 'Paiement'),
        ('livraison', 'Livraison'),
        ('reclamation', 'Réclamation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='suivi')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='suivi')
    
    # Événement
    type_evenement = models.CharField(max_length=20, choices=TYPES_EVENEMENT)
    date_evenement = models.DateTimeField()
    description = models.TextField()
    
    # Montant associé
    montant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Lien facture
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='suivi_contrat')
    
    # Conformité
    conforme = models.BooleanField(default=True)
    ecart_constate = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'contrats_suivi'
        verbose_name = 'Suivi contrat'
        verbose_name_plural = 'Suivis contrats'
        ordering = ['-date_evenement']
    
    def __str__(self):
        return f"{self.get_type_evenement_display()} - {self.date_evenement}"


class AlerteContrat(models.Model):
    """Alertes automatiques sur les contrats"""
    TYPES_ALERTE = [
        ('expiration', 'Expiration proche'),
        ('renouvellement', 'Renouvellement à prévoir'),
        ('echeance_paiement', 'Échéance paiement'),
        ('depassement_budget', 'Dépassement budget'),
        ('retard_livraison', 'Retard livraison'),
        ('non_conformite', 'Non-conformité'),
    ]
    NIVEAUX = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('critical', 'Critique'),
    ]
    STATUTS = [
        ('active', 'Active'),
        ('acquittee', 'Acquittée'),
        ('ignoree', 'Ignorée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='alertes_contrats')
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='alertes')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='alertes')
    
    # Alerte
    type_alerte = models.CharField(max_length=20, choices=TYPES_ALERTE)
    niveau = models.CharField(max_length=10, choices=NIVEAUX, default='warning')
    message = models.TextField()
    
    # Date
    date_alerte = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='active')
    acquittee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_acquittement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'contrats_alerte'
        verbose_name = 'Alerte contrat'
        verbose_name_plural = 'Alertes contrats'
        ordering = ['-date_alerte']
    
    def __str__(self):
        return f"{self.get_type_alerte_display()} - {self.get_niveau_display()}"


class HistoriqueContrat(models.Model):
    """Historique des modifications de contrats"""
    TYPES_MODIFICATION = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('avenant', 'Avenant'),
        ('renouvellement', 'Renouvellement'),
        ('resiliation', 'Résiliation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien contrat
    contrat_fournisseur = models.ForeignKey(ContratFournisseur, on_delete=models.CASCADE,
                                            null=True, blank=True, related_name='historique')
    contrat_client = models.ForeignKey(ContratClient, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='historique')
    
    # Modification
    type_modification = models.CharField(max_length=20, choices=TYPES_MODIFICATION)
    description = models.TextField()
    
    # Valeurs
    champs_modifies = models.JSONField(null=True, blank=True)
    valeurs_avant = models.JSONField(null=True, blank=True)
    valeurs_apres = models.JSONField(null=True, blank=True)
    
    # Audit
    date_modification = models.DateTimeField(auto_now_add=True)
    modifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'contrats_historique'
        verbose_name = 'Historique contrat'
        verbose_name_plural = 'Historiques contrats'
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.get_type_modification_display()} - {self.date_modification}"
