"""
Module Contrôle Interne & Conformité
Procédures, tests, matrice risques, ségrégation tâches, workflows approbation
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import Entreprise, Utilisateur


class MatriceRisques(models.Model):
    """Matrice risques/contrôles"""
    CATEGORIES_RISQUE = [
        ('operationnel', 'Risque opérationnel'),
        ('financier', 'Risque financier'),
        ('conformite', 'Risque de conformité'),
        ('fraude', 'Risque de fraude'),
        ('it', 'Risque IT/Cybersécurité'),
        ('reputation', 'Risque de réputation'),
    ]
    NIVEAUX_IMPACT = [
        (1, 'Négligeable'),
        (2, 'Mineur'),
        (3, 'Modéré'),
        (4, 'Majeur'),
        (5, 'Critique'),
    ]
    NIVEAUX_PROBABILITE = [
        (1, 'Très rare'),
        (2, 'Rare'),
        (3, 'Possible'),
        (4, 'Probable'),
        (5, 'Très probable'),
    ]
    STATUTS = [
        ('identifie', 'Identifié'),
        ('evalue', 'Évalué'),
        ('traite', 'Traité'),
        ('accepte', 'Accepté'),
        ('cloture', 'Clôturé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='risques_controle')
    
    # Identification
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=20, choices=CATEGORIES_RISQUE)
    
    # Évaluation risque inhérent
    impact_inherent = models.IntegerField(choices=NIVEAUX_IMPACT)
    probabilite_inherente = models.IntegerField(choices=NIVEAUX_PROBABILITE)
    score_inherent = models.IntegerField(default=0)
    
    # Évaluation risque résiduel (après contrôles)
    impact_residuel = models.IntegerField(choices=NIVEAUX_IMPACT, null=True, blank=True)
    probabilite_residuelle = models.IntegerField(choices=NIVEAUX_PROBABILITE, null=True, blank=True)
    score_residuel = models.IntegerField(default=0)
    
    # Processus concerné
    processus = models.CharField(max_length=100)
    sous_processus = models.CharField(max_length=100, blank=True, null=True)
    
    # Propriétaire du risque
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='risques_proprietaire')
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUTS, default='identifie')
    
    # Plan de traitement
    strategie_traitement = models.TextField(blank=True, null=True)
    date_revue = models.DateField(null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='risques_crees')
    
    class Meta:
        db_table = 'controle_matrice_risques'
        verbose_name = 'Risque'
        verbose_name_plural = 'Matrice des risques'
        ordering = ['-score_inherent']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"
    
    def calculer_scores(self):
        self.score_inherent = self.impact_inherent * self.probabilite_inherente
        if self.impact_residuel and self.probabilite_residuelle:
            self.score_residuel = self.impact_residuel * self.probabilite_residuelle
        self.save()


class ProcedureControle(models.Model):
    """Procédures de contrôle formalisées"""
    TYPES_CONTROLE = [
        ('preventif', 'Contrôle préventif'),
        ('detectif', 'Contrôle détectif'),
        ('correctif', 'Contrôle correctif'),
    ]
    FREQUENCES = [
        ('continu', 'Continu'),
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('annuel', 'Annuel'),
        ('ponctuel', 'Ponctuel'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('active', 'Active'),
        ('suspendue', 'Suspendue'),
        ('obsolete', 'Obsolète'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='procedures_controle')
    
    # Identification
    code = models.CharField(max_length=20)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    objectif = models.TextField()
    
    # Classification
    type_controle = models.CharField(max_length=15, choices=TYPES_CONTROLE)
    frequence = models.CharField(max_length=15, choices=FREQUENCES)
    
    # Processus
    processus = models.CharField(max_length=100)
    
    # Risques couverts
    risques = models.ManyToManyField(MatriceRisques, related_name='procedures', blank=True)
    
    # Responsable
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='procedures_responsable')
    
    # Documentation
    etapes_controle = models.TextField(verbose_name='Étapes du contrôle')
    documents_requis = models.TextField(blank=True, null=True)
    criteres_succes = models.TextField(blank=True, null=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='brouillon')
    date_mise_en_vigueur = models.DateField(null=True, blank=True)
    date_derniere_revue = models.DateField(null=True, blank=True)
    prochaine_revue = models.DateField(null=True, blank=True)
    
    # Version
    version = models.CharField(max_length=10, default='1.0')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='procedures_creees')
    
    class Meta:
        db_table = 'controle_procedure'
        verbose_name = 'Procédure de contrôle'
        verbose_name_plural = 'Procédures de contrôle'
        unique_together = ['entreprise', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.titre}"


class TestControle(models.Model):
    """Tests de contrôle automatisés ou manuels"""
    TYPES_TEST = [
        ('automatique', 'Automatique'),
        ('manuel', 'Manuel'),
        ('semi_auto', 'Semi-automatique'),
    ]
    RESULTATS = [
        ('reussi', 'Réussi'),
        ('echoue', 'Échoué'),
        ('partiel', 'Partiellement réussi'),
        ('non_applicable', 'Non applicable'),
        ('en_cours', 'En cours'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    procedure = models.ForeignKey(ProcedureControle, on_delete=models.CASCADE,
                                  related_name='tests')
    
    # Identification
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    
    # Type
    type_test = models.CharField(max_length=15, choices=TYPES_TEST)
    
    # Exécution
    date_execution = models.DateTimeField()
    execute_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='tests_executes')
    
    # Résultat
    resultat = models.CharField(max_length=15, choices=RESULTATS, default='en_cours')
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                null=True, blank=True, help_text='Score en %')
    
    # Détails
    observations = models.TextField(blank=True, null=True)
    anomalies_detectees = models.TextField(blank=True, null=True)
    recommandations = models.TextField(blank=True, null=True)
    
    # Preuves
    pieces_jointes = models.FileField(upload_to='controle/tests/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'controle_test'
        verbose_name = 'Test de contrôle'
        verbose_name_plural = 'Tests de contrôle'
        ordering = ['-date_execution']
    
    def __str__(self):
        return f"{self.reference} - {self.get_resultat_display()}"


class NonConformite(models.Model):
    """Suivi des non-conformités et corrections"""
    NIVEAUX_GRAVITE = [
        ('mineur', 'Mineur'),
        ('majeur', 'Majeur'),
        ('critique', 'Critique'),
    ]
    STATUTS = [
        ('ouverte', 'Ouverte'),
        ('en_analyse', 'En analyse'),
        ('plan_action', 'Plan d\'action défini'),
        ('en_correction', 'En correction'),
        ('verifiee', 'Vérifiée'),
        ('cloturee', 'Clôturée'),
    ]
    ORIGINES = [
        ('audit_interne', 'Audit interne'),
        ('audit_externe', 'Audit externe'),
        ('test_controle', 'Test de contrôle'),
        ('incident', 'Incident'),
        ('reclamation', 'Réclamation'),
        ('auto_evaluation', 'Auto-évaluation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='non_conformites')
    
    # Identification
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    niveau_gravite = models.CharField(max_length=10, choices=NIVEAUX_GRAVITE)
    origine = models.CharField(max_length=20, choices=ORIGINES)
    
    # Lien avec test/procédure
    test = models.ForeignKey(TestControle, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='non_conformites')
    procedure = models.ForeignKey(ProcedureControle, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='non_conformites')
    risque = models.ForeignKey(MatriceRisques, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='non_conformites')
    
    # Analyse
    cause_racine = models.TextField(blank=True, null=True)
    impact = models.TextField(blank=True, null=True)
    
    # Plan d'action
    actions_correctives = models.TextField(blank=True, null=True)
    actions_preventives = models.TextField(blank=True, null=True)
    responsable_correction = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                               related_name='corrections_responsable')
    date_echeance = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='ouverte')
    date_detection = models.DateField()
    date_resolution = models.DateField(null=True, blank=True)
    
    # Vérification
    verifie_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='verifications_nc')
    date_verification = models.DateField(null=True, blank=True)
    efficacite_verifiee = models.BooleanField(default=False)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='nc_creees')
    
    class Meta:
        db_table = 'controle_non_conformite'
        verbose_name = 'Non-conformité'
        verbose_name_plural = 'Non-conformités'
        ordering = ['-date_detection']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class DelegationPouvoirs(models.Model):
    """Matrice de délégation des pouvoirs"""
    TYPES_POUVOIR = [
        ('signature', 'Signature'),
        ('engagement', 'Engagement financier'),
        ('validation', 'Validation'),
        ('approbation', 'Approbation'),
        ('autorisation', 'Autorisation'),
    ]
    STATUTS = [
        ('active', 'Active'),
        ('suspendue', 'Suspendue'),
        ('expiree', 'Expirée'),
        ('revoquee', 'Révoquée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='delegations_pouvoirs')
    
    # Délégant et délégataire
    delegant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                 related_name='delegations_donnees')
    delegataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                    related_name='delegations_recues')
    
    # Pouvoir délégué
    type_pouvoir = models.CharField(max_length=15, choices=TYPES_POUVOIR)
    domaine = models.CharField(max_length=100, verbose_name='Domaine d\'application')
    description = models.TextField()
    
    # Limites
    montant_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                      verbose_name='Montant maximum')
    conditions = models.TextField(blank=True, null=True)
    
    # Période
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='active')
    
    # Document
    document_delegation = models.FileField(upload_to='controle/delegations/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='delegations_creees')
    
    class Meta:
        db_table = 'controle_delegation_pouvoirs'
        verbose_name = 'Délégation de pouvoirs'
        verbose_name_plural = 'Délégations de pouvoirs'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.delegant} → {self.delegataire}: {self.get_type_pouvoir_display()}"


class ApprovalMatrix(models.Model):
    """Matrices d'approbation multi-niveaux"""
    TYPES_DOCUMENT = [
        ('facture', 'Facture'),
        ('bon_commande', 'Bon de commande'),
        ('demande_achat', 'Demande d\'achat'),
        ('note_frais', 'Note de frais'),
        ('contrat', 'Contrat'),
        ('paiement', 'Paiement'),
        ('ecriture', 'Écriture comptable'),
        ('budget', 'Budget'),
        ('autre', 'Autre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='matrices_approbation')
    
    # Identification
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    type_document = models.CharField(max_length=20, choices=TYPES_DOCUMENT)
    
    # Seuils
    montant_min = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    montant_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Niveaux d'approbation requis
    niveau_1_requis = models.BooleanField(default=True)
    niveau_2_requis = models.BooleanField(default=False)
    niveau_3_requis = models.BooleanField(default=False)
    niveau_4_requis = models.BooleanField(default=False)
    
    # Rôles approbateurs par niveau
    role_niveau_1 = models.CharField(max_length=100, blank=True, null=True)
    role_niveau_2 = models.CharField(max_length=100, blank=True, null=True)
    role_niveau_3 = models.CharField(max_length=100, blank=True, null=True)
    role_niveau_4 = models.CharField(max_length=100, blank=True, null=True)
    
    # Délais
    delai_niveau_1 = models.IntegerField(default=2, help_text='Délai en jours')
    delai_niveau_2 = models.IntegerField(default=3)
    delai_niveau_3 = models.IntegerField(default=5)
    delai_niveau_4 = models.IntegerField(default=7)
    
    # Statut
    est_active = models.BooleanField(default=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'controle_approval_matrix'
        verbose_name = 'Matrice d\'approbation'
        verbose_name_plural = 'Matrices d\'approbation'
        ordering = ['type_document', 'montant_min']
    
    def __str__(self):
        return f"{self.code} - {self.libelle}"


class WorkflowApprobation(models.Model):
    """Instance de workflow d'approbation"""
    STATUTS = [
        ('en_attente', 'En attente'),
        ('niveau_1', 'Niveau 1'),
        ('niveau_2', 'Niveau 2'),
        ('niveau_3', 'Niveau 3'),
        ('niveau_4', 'Niveau 4'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('annule', 'Annulé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matrice = models.ForeignKey(ApprovalMatrix, on_delete=models.CASCADE,
                                related_name='workflows')
    
    # Document concerné (référence générique)
    type_document = models.CharField(max_length=50)
    document_id = models.UUIDField()
    reference_document = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Demandeur
    demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                  related_name='workflows_demandes')
    date_demande = models.DateTimeField(auto_now_add=True)
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='en_attente')
    niveau_actuel = models.IntegerField(default=1)
    
    # Dates
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    # Commentaires
    commentaire_demande = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'controle_workflow_approbation'
        verbose_name = 'Workflow d\'approbation'
        verbose_name_plural = 'Workflows d\'approbation'
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"WF-{self.reference_document} - {self.get_statut_display()}"


class EtapeApprobation(models.Model):
    """Étapes d'un workflow d'approbation"""
    DECISIONS = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('demande_info', 'Demande d\'information'),
        ('delegue', 'Délégué'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowApprobation, on_delete=models.CASCADE,
                                 related_name='etapes')
    
    # Niveau
    niveau = models.IntegerField()
    
    # Approbateur
    approbateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                    related_name='etapes_approbation')
    
    # Décision
    decision = models.CharField(max_length=15, choices=DECISIONS, default='en_attente')
    commentaire = models.TextField(blank=True, null=True)
    
    # Dates
    date_assignation = models.DateTimeField(auto_now_add=True)
    date_decision = models.DateTimeField(null=True, blank=True)
    date_limite = models.DateTimeField(null=True, blank=True)
    
    # Délégation
    delegue_a = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='etapes_deleguees')
    
    class Meta:
        db_table = 'controle_etape_approbation'
        verbose_name = 'Étape d\'approbation'
        verbose_name_plural = 'Étapes d\'approbation'
        ordering = ['workflow', 'niveau']
    
    def __str__(self):
        return f"Niveau {self.niveau} - {self.approbateur}"


class SegregationTaches(models.Model):
    """Vérification de la ségrégation des tâches"""
    TYPES_CONFLIT = [
        ('incompatible', 'Fonctions incompatibles'),
        ('concentration', 'Concentration de pouvoirs'),
        ('auto_controle', 'Auto-contrôle'),
    ]
    STATUTS = [
        ('detecte', 'Détecté'),
        ('analyse', 'En analyse'),
        ('justifie', 'Justifié'),
        ('corrige', 'Corrigé'),
        ('accepte', 'Risque accepté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='conflits_segregation')
    
    # Utilisateur concerné
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                    related_name='conflits_segregation')
    
    # Conflit
    type_conflit = models.CharField(max_length=15, choices=TYPES_CONFLIT)
    fonction_1 = models.CharField(max_length=100)
    fonction_2 = models.CharField(max_length=100)
    description = models.TextField()
    
    # Évaluation
    niveau_risque = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='detecte')
    
    # Justification/Correction
    justification = models.TextField(blank=True, null=True)
    mesures_compensatoires = models.TextField(blank=True, null=True)
    
    # Audit
    date_detection = models.DateTimeField(auto_now_add=True)
    detecte_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='conflits_detectes')
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'controle_segregation_taches'
        verbose_name = 'Conflit de ségrégation'
        verbose_name_plural = 'Conflits de ségrégation'
        ordering = ['-niveau_risque', '-date_detection']
    
    def __str__(self):
        return f"{self.utilisateur} - {self.get_type_conflit_display()}"


class RapportControleInterne(models.Model):
    """Rapports de contrôle interne périodiques"""
    TYPES_RAPPORT = [
        ('mensuel', 'Rapport mensuel'),
        ('trimestriel', 'Rapport trimestriel'),
        ('annuel', 'Rapport annuel'),
        ('special', 'Rapport spécial'),
    ]
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('en_revue', 'En revue'),
        ('valide', 'Validé'),
        ('diffuse', 'Diffusé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='rapports_controle')
    
    # Identification
    reference = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    type_rapport = models.CharField(max_length=15, choices=TYPES_RAPPORT)
    
    # Période
    date_debut_periode = models.DateField()
    date_fin_periode = models.DateField()
    
    # Contenu
    resume_executif = models.TextField()
    constats_principaux = models.TextField()
    recommandations = models.TextField()
    plan_action = models.TextField(blank=True, null=True)
    
    # Statistiques
    nb_tests_realises = models.IntegerField(default=0)
    nb_tests_reussis = models.IntegerField(default=0)
    nb_non_conformites = models.IntegerField(default=0)
    taux_conformite = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    statut = models.CharField(max_length=15, choices=STATUTS, default='brouillon')
    
    # Validation
    redige_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='rapports_rediges')
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='rapports_valides')
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Fichier
    fichier_rapport = models.FileField(upload_to='controle/rapports/', null=True, blank=True)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'controle_rapport'
        verbose_name = 'Rapport de contrôle interne'
        verbose_name_plural = 'Rapports de contrôle interne'
        ordering = ['-date_fin_periode']
    
    def __str__(self):
        return f"{self.reference} - {self.titre}"


class TraceModification(models.Model):
    """Traçabilité complète des modifications"""
    TYPES_ACTION = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('validation', 'Validation'),
        ('approbation', 'Approbation'),
        ('rejet', 'Rejet'),
        ('consultation', 'Consultation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE,
                                   related_name='traces_modifications')
    
    # Action
    type_action = models.CharField(max_length=15, choices=TYPES_ACTION)
    
    # Objet modifié
    type_objet = models.CharField(max_length=100)
    objet_id = models.UUIDField()
    reference_objet = models.CharField(max_length=200)
    
    # Détails
    description = models.TextField()
    champs_modifies = models.JSONField(null=True, blank=True)
    valeurs_avant = models.JSONField(null=True, blank=True)
    valeurs_apres = models.JSONField(null=True, blank=True)
    
    # Utilisateur
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contexte
    date_action = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'controle_trace_modification'
        verbose_name = 'Trace de modification'
        verbose_name_plural = 'Traces de modifications'
        ordering = ['-date_action']
        indexes = [
            models.Index(fields=['type_objet', 'objet_id']),
            models.Index(fields=['utilisateur', 'date_action']),
        ]
    
    def __str__(self):
        return f"{self.get_type_action_display()} - {self.reference_objet}"
