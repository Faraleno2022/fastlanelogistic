"""
Module Trésorerie Avancée - Modèles critiques
Synchronisation bancaire, échéancier, situation, optimisation, liquidité, numéraire
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur, Devise
from .models import CompteBancaire, Tiers, Facture, PlanComptable, EcritureComptable


class SynchronisationBancaire(models.Model):
    """Synchronisation automatique des comptes avec les banques"""
    STATUTS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('erreur', 'En erreur'),
        ('en_cours', 'En cours'),
    ]
    FREQUENCES = [
        ('temps_reel', 'Temps réel'),
        ('horaire', 'Toutes les heures'),
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire'),
    ]
    PROTOCOLES = [
        ('api_rest', 'API REST'),
        ('sftp', 'SFTP'),
        ('ebics', 'EBICS'),
        ('swift', 'SWIFT'),
        ('manuel', 'Import manuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='synchronisations_bancaires')
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='synchronisations')
    
    # Configuration
    nom_connexion = models.CharField(max_length=100, verbose_name='Nom de la connexion')
    protocole = models.CharField(max_length=20, choices=PROTOCOLES, default='api_rest')
    frequence_sync = models.CharField(max_length=20, choices=FREQUENCES, default='quotidien')
    heure_sync = models.TimeField(null=True, blank=True, help_text='Heure de synchronisation (si quotidien)')
    
    # Paramètres de connexion (chiffrés en production)
    url_api = models.URLField(blank=True, null=True)
    identifiant_api = models.CharField(max_length=200, blank=True, null=True)
    cle_api_chiffree = models.TextField(blank=True, null=True, help_text='Clé API chiffrée')
    certificat = models.FileField(upload_to='certificats_bancaires/', blank=True, null=True)
    
    # État
    statut = models.CharField(max_length=20, choices=STATUTS, default='inactive')
    derniere_sync = models.DateTimeField(null=True, blank=True)
    prochaine_sync = models.DateTimeField(null=True, blank=True)
    derniere_erreur = models.TextField(blank=True, null=True)
    nb_operations_importees = models.IntegerField(default=0)
    
    # Réconciliation automatique
    reconciliation_auto = models.BooleanField(default=False, help_text='Réconciliation automatique des opérations')
    seuil_reconciliation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.01'), 
                                                help_text='Écart max pour réconciliation auto')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'tresorerie_synchronisation_bancaire'
        verbose_name = 'Synchronisation bancaire'
        verbose_name_plural = 'Synchronisations bancaires'
        unique_together = ['entreprise', 'compte_bancaire']
    
    def __str__(self):
        return f"{self.nom_connexion} - {self.compte_bancaire.libelle}"


class EcheancierTresorerie(models.Model):
    """Calendrier des flux de trésorerie prévisionnels"""
    TYPES_FLUX = [
        ('encaissement', 'Encaissement'),
        ('decaissement', 'Décaissement'),
    ]
    ORIGINES = [
        ('facture_client', 'Facture client'),
        ('facture_fournisseur', 'Facture fournisseur'),
        ('salaire', 'Salaires'),
        ('charges_sociales', 'Charges sociales'),
        ('impots', 'Impôts et taxes'),
        ('pret', 'Remboursement prêt'),
        ('loyer', 'Loyer'),
        ('abonnement', 'Abonnement'),
        ('investissement', 'Investissement'),
        ('autre', 'Autre'),
    ]
    STATUTS = [
        ('prevu', 'Prévu'),
        ('confirme', 'Confirmé'),
        ('realise', 'Réalisé'),
        ('annule', 'Annulé'),
        ('reporte', 'Reporté'),
    ]
    PRIORITES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='echeancier_tresorerie')
    
    # Identification
    reference = models.CharField(max_length=50, verbose_name='Référence')
    libelle = models.CharField(max_length=200)
    type_flux = models.CharField(max_length=20, choices=TYPES_FLUX)
    origine = models.CharField(max_length=30, choices=ORIGINES)
    
    # Montants
    montant_prevu = models.DecimalField(max_digits=15, decimal_places=2)
    montant_realise = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    devise = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dates
    date_echeance = models.DateField(verbose_name='Date échéance')
    date_realisation = models.DateField(null=True, blank=True)
    date_report = models.DateField(null=True, blank=True, help_text='Nouvelle date si reporté')
    
    # Tiers
    tiers = models.ForeignKey(Tiers, on_delete=models.SET_NULL, null=True, blank=True)
    facture = models.ForeignKey(Facture, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Compte
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Statut et priorité
    statut = models.CharField(max_length=20, choices=STATUTS, default='prevu')
    priorite = models.CharField(max_length=20, choices=PRIORITES, default='normale')
    
    # Récurrence
    est_recurrent = models.BooleanField(default=False)
    frequence_recurrence = models.CharField(max_length=20, blank=True, null=True, 
                                            choices=[('mensuel', 'Mensuel'), ('trimestriel', 'Trimestriel'), 
                                                     ('annuel', 'Annuel')])
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tresorerie_echeancier'
        verbose_name = 'Échéance trésorerie'
        verbose_name_plural = 'Échéancier trésorerie'
        ordering = ['date_echeance', 'priorite']
        indexes = [
            models.Index(fields=['entreprise', 'date_echeance']),
            models.Index(fields=['statut']),
            models.Index(fields=['type_flux', 'date_echeance']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.libelle} ({self.date_echeance})"


class SituationTresorerie(models.Model):
    """Situation de trésorerie quotidienne/hebdomadaire"""
    PERIODICITES = [
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel', 'Mensuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='situations_tresorerie')
    
    # Période
    date_situation = models.DateField(verbose_name='Date de la situation')
    periodicite = models.CharField(max_length=20, choices=PERIODICITES, default='quotidien')
    
    # Soldes par compte
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, null=True, blank=True,
                                        help_text='Null = situation consolidée tous comptes')
    
    # Soldes
    solde_debut = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Solde début période')
    total_encaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_decaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    solde_fin = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Solde fin période')
    
    # Prévisions court terme
    prevision_j1 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), 
                                       verbose_name='Prévision J+1')
    prevision_j3 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                       verbose_name='Prévision J+3')
    prevision_j5 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                       verbose_name='Prévision J+5')
    prevision_j7 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                       verbose_name='Prévision J+7')
    prevision_j30 = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                        verbose_name='Prévision J+30')
    
    # Indicateurs
    variation_jour = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    variation_pourcentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    
    # Alertes
    alerte_seuil_bas = models.BooleanField(default=False)
    alerte_seuil_critique = models.BooleanField(default=False)
    
    # Validation
    est_valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Notes
    commentaires = models.TextField(blank=True, null=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tresorerie_situation'
        verbose_name = 'Situation trésorerie'
        verbose_name_plural = 'Situations trésorerie'
        ordering = ['-date_situation']
        unique_together = ['entreprise', 'date_situation', 'compte_bancaire', 'periodicite']
        indexes = [
            models.Index(fields=['entreprise', 'date_situation']),
            models.Index(fields=['alerte_seuil_bas']),
            models.Index(fields=['alerte_seuil_critique']),
        ]
    
    def __str__(self):
        compte = self.compte_bancaire.libelle if self.compte_bancaire else 'Consolidé'
        return f"Situation {self.date_situation} - {compte}"
    
    def calculer_previsions(self):
        """Calcule les prévisions à court terme basées sur l'échéancier"""
        from datetime import timedelta
        from django.db.models import Sum, Q
        
        date_base = self.date_situation
        solde_actuel = self.solde_fin
        
        for jours, champ in [(1, 'prevision_j1'), (3, 'prevision_j3'), (5, 'prevision_j5'), 
                             (7, 'prevision_j7'), (30, 'prevision_j30')]:
            date_limite = date_base + timedelta(days=jours)
            
            # Encaissements prévus
            encaissements = EcheancierTresorerie.objects.filter(
                entreprise=self.entreprise,
                type_flux='encaissement',
                statut__in=['prevu', 'confirme'],
                date_echeance__gt=date_base,
                date_echeance__lte=date_limite
            ).aggregate(total=Sum('montant_prevu'))['total'] or Decimal('0.00')
            
            # Décaissements prévus
            decaissements = EcheancierTresorerie.objects.filter(
                entreprise=self.entreprise,
                type_flux='decaissement',
                statut__in=['prevu', 'confirme'],
                date_echeance__gt=date_base,
                date_echeance__lte=date_limite
            ).aggregate(total=Sum('montant_prevu'))['total'] or Decimal('0.00')
            
            prevision = solde_actuel + encaissements - decaissements
            setattr(self, champ, prevision)
        
        self.save()


class OptimisationTresorerie(models.Model):
    """Stratégies d'optimisation de la trésorerie"""
    TYPES_STRATEGIE = [
        ('placement', 'Placement excédents'),
        ('financement', 'Financement court terme'),
        ('equilibrage', 'Équilibrage comptes'),
        ('negociation', 'Négociation conditions'),
        ('reduction_delai', 'Réduction délais paiement'),
        ('acceleration', 'Accélération encaissements'),
    ]
    STATUTS = [
        ('proposition', 'Proposition'),
        ('en_cours', 'En cours d\'analyse'),
        ('approuvee', 'Approuvée'),
        ('mise_en_oeuvre', 'Mise en œuvre'),
        ('terminee', 'Terminée'),
        ('rejetee', 'Rejetée'),
    ]
    PRIORITES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='optimisations_tresorerie')
    
    # Identification
    reference = models.CharField(max_length=50, unique=True)
    titre = models.CharField(max_length=200)
    type_strategie = models.CharField(max_length=30, choices=TYPES_STRATEGIE)
    description = models.TextField()
    
    # Analyse
    situation_actuelle = models.TextField(help_text='Description de la situation actuelle')
    objectif = models.TextField(help_text='Objectif visé')
    actions_proposees = models.TextField(help_text='Actions à mettre en œuvre')
    
    # Impact financier
    gain_estime = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                      help_text='Gain financier estimé')
    cout_mise_en_oeuvre = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    delai_retour_investissement = models.IntegerField(null=True, blank=True, help_text='En jours')
    
    # Risques
    risques_identifies = models.TextField(blank=True, null=True)
    niveau_risque = models.CharField(max_length=20, choices=[
        ('faible', 'Faible'), ('moyen', 'Moyen'), ('eleve', 'Élevé')
    ], default='moyen')
    
    # Statut et priorité
    statut = models.CharField(max_length=20, choices=STATUTS, default='proposition')
    priorite = models.CharField(max_length=20, choices=PRIORITES, default='normale')
    
    # Dates
    date_debut_prevue = models.DateField(null=True, blank=True)
    date_fin_prevue = models.DateField(null=True, blank=True)
    date_mise_en_oeuvre = models.DateField(null=True, blank=True)
    
    # Validation
    approuve_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='optimisations_approuvees')
    date_approbation = models.DateTimeField(null=True, blank=True)
    
    # Résultats
    gain_realise = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    commentaires_resultats = models.TextField(blank=True, null=True)
    
    # Audit
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='optimisations_creees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tresorerie_optimisation'
        verbose_name = 'Optimisation trésorerie'
        verbose_name_plural = 'Optimisations trésorerie'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class LiquiditeSouhaitee(models.Model):
    """Seuils de liquidité par compte ou global"""
    TYPES_SEUIL = [
        ('minimum', 'Seuil minimum'),
        ('securite', 'Seuil de sécurité'),
        ('optimal', 'Niveau optimal'),
        ('maximum', 'Seuil maximum'),
        ('critique', 'Seuil critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='seuils_liquidite')
    
    # Compte (null = seuil global)
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, null=True, blank=True,
                                        help_text='Null = seuil global entreprise')
    
    # Seuils
    type_seuil = models.CharField(max_length=20, choices=TYPES_SEUIL)
    montant_seuil = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Alertes
    alerte_active = models.BooleanField(default=True)
    destinataires_alerte = models.TextField(blank=True, null=True, help_text='Emails séparés par virgule')
    delai_alerte_jours = models.IntegerField(default=0, help_text='Anticiper l\'alerte de X jours')
    
    # Période de validité
    date_debut_validite = models.DateField(null=True, blank=True)
    date_fin_validite = models.DateField(null=True, blank=True)
    
    # Notes
    justification = models.TextField(blank=True, null=True, help_text='Justification du seuil')
    
    # Statut
    actif = models.BooleanField(default=True)
    
    # Audit
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tresorerie_liquidite_souhaitee'
        verbose_name = 'Seuil de liquidité'
        verbose_name_plural = 'Seuils de liquidité'
        unique_together = ['entreprise', 'compte_bancaire', 'type_seuil']
    
    def __str__(self):
        compte = self.compte_bancaire.libelle if self.compte_bancaire else 'Global'
        return f"{self.get_type_seuil_display()} - {compte}: {self.montant_seuil}"


class GestionNumeraire(models.Model):
    """Gestion des espèces et numéraire"""
    TYPES_MOUVEMENT = [
        ('approvisionnement', 'Approvisionnement caisse'),
        ('versement', 'Versement en banque'),
        ('encaissement', 'Encaissement espèces'),
        ('decaissement', 'Décaissement espèces'),
        ('transfert', 'Transfert entre caisses'),
        ('ecart', 'Écart de caisse'),
    ]
    STATUTS = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='mouvements_numeraire')
    
    # Identification
    reference = models.CharField(max_length=50)
    date_mouvement = models.DateField()
    type_mouvement = models.CharField(max_length=20, choices=TYPES_MOUVEMENT)
    
    # Montants
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    devise = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Détail des coupures (JSON)
    detail_coupures = models.JSONField(null=True, blank=True, 
                                       help_text='{"100000": 5, "50000": 10, ...}')
    
    # Comptes
    caisse_source = models.ForeignKey(CompteBancaire, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='sorties_numeraire')
    caisse_destination = models.ForeignKey(CompteBancaire, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='entrees_numeraire')
    
    # Justification
    motif = models.CharField(max_length=200)
    piece_justificative = models.FileField(upload_to='numeraire/', blank=True, null=True)
    
    # Validation
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='mouvements_numeraire_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Écriture comptable
    ecriture = models.ForeignKey(EcritureComptable, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Audit
    effectue_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='mouvements_numeraire_effectues')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tresorerie_gestion_numeraire'
        verbose_name = 'Mouvement numéraire'
        verbose_name_plural = 'Mouvements numéraire'
        ordering = ['-date_mouvement', '-date_creation']
        indexes = [
            models.Index(fields=['entreprise', 'date_mouvement']),
            models.Index(fields=['type_mouvement']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.get_type_mouvement_display()} - {self.montant}"


class AlerteTresorerie(models.Model):
    """Alertes automatiques de trésorerie"""
    TYPES_ALERTE = [
        ('seuil_bas', 'Seuil bas atteint'),
        ('seuil_critique', 'Seuil critique atteint'),
        ('echeance_proche', 'Échéance proche'),
        ('echeance_depassee', 'Échéance dépassée'),
        ('ecart_prevision', 'Écart prévision/réalisé'),
        ('sync_erreur', 'Erreur synchronisation'),
        ('reconciliation', 'Problème réconciliation'),
    ]
    NIVEAUX = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('danger', 'Danger'),
        ('critical', 'Critique'),
    ]
    STATUTS = [
        ('active', 'Active'),
        ('acquittee', 'Acquittée'),
        ('resolue', 'Résolue'),
        ('ignoree', 'Ignorée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='alertes_tresorerie')
    
    # Type et niveau
    type_alerte = models.CharField(max_length=30, choices=TYPES_ALERTE)
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='warning')
    
    # Contenu
    titre = models.CharField(max_length=200)
    message = models.TextField()
    
    # Contexte
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.SET_NULL, null=True, blank=True)
    montant_concerne = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    seuil_reference = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    ecart = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='active')
    
    # Traitement
    acquittee_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='alertes_tresorerie_acquittees')
    date_acquittement = models.DateTimeField(null=True, blank=True)
    commentaire_traitement = models.TextField(blank=True, null=True)
    
    # Notification
    notification_envoyee = models.BooleanField(default=False)
    date_notification = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tresorerie_alerte'
        verbose_name = 'Alerte trésorerie'
        verbose_name_plural = 'Alertes trésorerie'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['entreprise', 'statut']),
            models.Index(fields=['niveau', 'statut']),
            models.Index(fields=['type_alerte']),
        ]
    
    def __str__(self):
        return f"[{self.get_niveau_display()}] {self.titre}"


class FluxTresorerieJournalier(models.Model):
    """Flux de trésorerie par jour - détail des mouvements"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='flux_journaliers')
    
    # Date
    date_flux = models.DateField()
    
    # Compte
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE)
    
    # Soldes
    solde_ouverture = models.DecimalField(max_digits=15, decimal_places=2)
    solde_cloture = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Mouvements par catégorie
    encaissements_clients = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    decaissements_fournisseurs = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    salaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    charges_sociales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    impots_taxes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    frais_bancaires = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_encaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    autres_decaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Totaux
    total_encaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_decaissements = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    variation_nette = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Nombre d'opérations
    nb_operations = models.IntegerField(default=0)
    
    # Validation
    est_cloture = models.BooleanField(default=False)
    cloture_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tresorerie_flux_journalier'
        verbose_name = 'Flux journalier'
        verbose_name_plural = 'Flux journaliers'
        unique_together = ['entreprise', 'date_flux', 'compte_bancaire']
        ordering = ['-date_flux']
        indexes = [
            models.Index(fields=['entreprise', 'date_flux']),
            models.Index(fields=['compte_bancaire', 'date_flux']),
        ]
    
    def __str__(self):
        return f"Flux {self.date_flux} - {self.compte_bancaire.libelle}"
    
    def calculer_totaux(self):
        """Recalcule les totaux à partir des catégories"""
        self.total_encaissements = (
            self.encaissements_clients + 
            self.autres_encaissements
        )
        self.total_decaissements = (
            self.decaissements_fournisseurs +
            self.salaires +
            self.charges_sociales +
            self.impots_taxes +
            self.frais_bancaires +
            self.autres_decaissements
        )
        self.variation_nette = self.total_encaissements - self.total_decaissements
        self.solde_cloture = self.solde_ouverture + self.variation_nette
        self.save()
