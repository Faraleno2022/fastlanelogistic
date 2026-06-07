from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from core.models import Etablissement, Service, Poste, Entreprise, Devise
from django.utils import timezone


class Employe(models.Model):
    """Modèle principal des employés"""
    CIVILITES = (
        ('M.', 'Monsieur'),
        ('Mme', 'Madame'),
        ('Mlle', 'Mademoiselle'),
    )
    
    SEXES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    SITUATIONS_MATRIMONIALES = (
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf(ve)'),
    )
    
    TYPES_PIECES = (
        ('CNI', 'Carte Nationale d\'Identité'),
        ('passeport', 'Passeport'),
    )
    
    TYPES_CONTRATS = (
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('CDImp', 'Contrat à Durée Imprécise'),
        ('CTI', 'Contrat de Travail Intermittent'),
        ('stage', 'Stage'),
        ('apprentissage', 'Contrat d\'Apprentissage'),
        ('temporaire', 'Temporaire'),
    )
    
    STATUTS = (
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('demissionnaire', 'Démissionnaire'),
        ('licencie', 'Licencié'),
        ('retraite', 'Retraité'),
    )
    
    MODES_PAIEMENT = (
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
    )
    
    # Entreprise (multi-tenant)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='employes_entreprise', null=True, blank=True)
    
    # Identification
    matricule = models.CharField(max_length=20, unique=True)
    
    # État civil
    civilite = models.CharField(max_length=10, choices=CIVILITES, blank=True, null=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=200)
    nom_jeune_fille = models.CharField(max_length=100, blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=SEXES, blank=True, null=True)
    situation_matrimoniale = models.CharField(max_length=20, choices=SITUATIONS_MATRIMONIALES, blank=True, null=True)
    nombre_enfants = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    photo = models.ImageField(upload_to='employes/photos/', blank=True, null=True)
    
    # Naissance
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, blank=True, null=True)
    commune_naissance = models.CharField(max_length=100, blank=True, null=True)
    prefecture_naissance = models.CharField(max_length=100, blank=True, null=True)
    departement = models.CharField(max_length=100, blank=True, null=True)
    nationalite = models.CharField(max_length=50, default='Guinéenne')
    
    # Pièce d'identité
    type_piece_identite = models.CharField(max_length=20, choices=TYPES_PIECES, blank=True, null=True)
    numero_piece_identite = models.CharField(max_length=50, blank=True, null=True)
    date_delivrance_piece = models.DateField(blank=True, null=True)
    date_expiration_piece = models.DateField(blank=True, null=True)
    num_cnss_individuel = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='N° CNSS')
    
    # Contact
    adresse_actuelle = models.TextField(blank=True, null=True)
    commune_residence = models.CharField(max_length=100, blank=True, null=True)
    prefecture_residence = models.CharField(max_length=100, blank=True, null=True)
    telephone_principal = models.CharField(max_length=20, blank=True, null=True)
    telephone_secondaire = models.CharField(max_length=20, blank=True, null=True)
    email_personnel = models.EmailField(blank=True, null=True)
    email_professionnel = models.EmailField(blank=True, null=True)
    
    # Contact d'urgence
    contact_urgence_nom = models.CharField(max_length=100, blank=True, null=True)
    contact_urgence_lien = models.CharField(max_length=50, blank=True, null=True)
    contact_urgence_telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Informations professionnelles
    etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, related_name='employes')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='employes')
    poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True, related_name='employes')
    date_embauche = models.DateField(blank=True, null=True)
    date_anciennete = models.DateField(blank=True, null=True)
    type_contrat = models.CharField(max_length=20, choices=TYPES_CONTRATS, blank=True, null=True)
    date_debut_contrat = models.DateField(blank=True, null=True)
    date_fin_contrat = models.DateField(blank=True, null=True)
    num_contrat = models.CharField(max_length=50, blank=True, null=True)
    statut_employe = models.CharField(max_length=20, choices=STATUTS, default='actif')
    date_depart = models.DateField(blank=True, null=True)
    motif_depart = models.CharField(max_length=50, blank=True, null=True)
    superieur_hierarchique = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordonnes')
    
    # Filiation
    nom_pere = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nom du père')
    nom_mere = models.CharField(max_length=200, blank=True, null=True, verbose_name='Nom de la mère')
    nombre_femmes = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Nombre de femmes')

    # Conducteur / Transport
    id_conducteur = models.CharField(max_length=50, blank=True, null=True, verbose_name='ID Conducteur')
    tracteur = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tracteur assigné')
    citerne = models.CharField(max_length=100, blank=True, null=True, verbose_name='Citerne assignée')
    numero_permis = models.CharField(max_length=50, blank=True, null=True, verbose_name='N° de permis')
    date_obtention_permis = models.DateField(blank=True, null=True, verbose_name='Date obtention permis')
    date_validite_permis = models.DateField(blank=True, null=True, verbose_name='Date validité permis')
    groupe_sanguin = models.CharField(max_length=10, blank=True, null=True, verbose_name='Groupe sanguin',
                                      choices=[('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                                               ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')])
    base_chauffeur = models.CharField(max_length=100, blank=True, null=True, verbose_name='Chauffeur basé à')
    vehicule_assigne = models.CharField(max_length=200, blank=True, null=True, verbose_name='Camion/Voiture assigné(e)',
                                        help_text='Véhicule assigné à l\'employé (immatriculation ou description)')

    # Formation transport / sécurité
    date_formation_apth = models.DateField(blank=True, null=True, verbose_name='Date formation APTH')
    anciennete_transport_hcl = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)],
                                                    verbose_name='Ancienneté transport HCL (ans)')
    date_dernier_recyclage = models.DateField(blank=True, null=True, verbose_name='Date dernier recyclage')
    formation_extincteur = models.BooleanField(default=False, verbose_name='Formation extincteur')

    # Visite médicale (suivi rapide)
    date_derniere_visite_medicale = models.DateField(blank=True, null=True, verbose_name='Dernière visite médicale')
    service_medical_accredite = models.CharField(max_length=200, blank=True, null=True, verbose_name='Service médical accrédité')
    date_prochaine_visite_medicale = models.DateField(blank=True, null=True, verbose_name='Prochaine visite médicale')

    # Informations bancaires
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT, default='virement')
    nom_banque = models.CharField(max_length=100, blank=True, null=True)
    agence_banque = models.CharField(max_length=100, blank=True, null=True)
    numero_compte = models.CharField(max_length=50, blank=True, null=True)
    rib = models.CharField(max_length=50, blank=True, null=True, verbose_name='RIB')
    operateur_mobile_money = models.CharField(max_length=50, blank=True, null=True)
    numero_mobile_money = models.CharField(max_length=20, blank=True, null=True)
    
    # Devise de paie (pour expatriés et employés multi-devises)
    devise_paie = models.ForeignKey(Devise, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='employes_devise',
                                   help_text='Devise de paiement du salaire (par défaut GNF)')
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    utilisateur_creation = models.ForeignKey('core.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='employes_crees')
    utilisateur_modification = models.ForeignKey('core.Utilisateur', on_delete=models.SET_NULL, null=True, related_name='employes_modifies')
    
    class Meta:
        db_table = 'employes'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['matricule']
        indexes = [
            models.Index(fields=['entreprise', 'statut_employe'], name='idx_emp_entreprise_statut'),
            models.Index(fields=['entreprise', 'nom'], name='idx_emp_entreprise_nom'),
            models.Index(fields=['statut_employe'], name='idx_emp_statut'),
            models.Index(fields=['service'], name='idx_emp_service'),
            models.Index(fields=['type_contrat'], name='idx_emp_type_contrat'),
            models.Index(fields=['date_embauche'], name='idx_emp_date_embauche'),
            models.Index(fields=['matricule'], name='idx_emp_matricule'),
        ]
    
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenoms}"
    
    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenoms}"
    
    @property
    def age(self):
        if self.date_naissance:
            today = timezone.now().date()
            return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return None
    
    @property
    def anciennete_annees(self):
        if self.date_embauche:
            today = timezone.now().date()
            return today.year - self.date_embauche.year
        return None
    
    @property
    def jours_restants_permis(self):
        """Nombre de jours restants avant expiration du permis"""
        if self.date_validite_permis:
            delta = self.date_validite_permis - timezone.now().date()
            return max(delta.days, 0)
        return None

    @property
    def statut_permis(self):
        """Statut du permis: Valide / Expiré / Proche expiration"""
        jours = self.jours_restants_permis
        if jours is None:
            return 'Non renseigné'
        if jours <= 0:
            return 'Expiré'
        if jours <= 30:
            return 'Proche expiration'
        return 'Valide'

    @property
    def jours_restants_recyclage(self):
        """Jours restants avant prochain recyclage (cycle 12 mois)"""
        if self.date_dernier_recyclage:
            from dateutil.relativedelta import relativedelta
            prochaine = self.date_dernier_recyclage + relativedelta(years=1)
            delta = prochaine - timezone.now().date()
            return max(delta.days, 0)
        return None

    @property
    def date_prochain_recyclage(self):
        """Date du prochain recyclage"""
        if self.date_dernier_recyclage:
            from dateutil.relativedelta import relativedelta
            return self.date_dernier_recyclage + relativedelta(years=1)
        return None

    @property
    def jours_restants_visite_medicale(self):
        """Jours restants avant prochaine visite médicale"""
        if self.date_prochaine_visite_medicale:
            delta = self.date_prochaine_visite_medicale - timezone.now().date()
            return max(delta.days, 0)
        return None

    @property
    def est_stagiaire_ou_apprenti(self):
        """Vérifie si l'employé est stagiaire ou apprenti"""
        return self.type_contrat in ('stage', 'apprentissage')
    
    def est_eligible_exoneration_rts(self, date_calcul=None):
        """
        Vérifie si l'employé est éligible à l'exonération RTS pour stagiaires/apprentis.
        
        Conditions (législation guinéenne):
        - Type de contrat: Stage ou Apprentissage
        - Durée: Maximum 12 mois depuis le début du contrat
        - Indemnité: ≤ 1 200 000 GNF/mois (vérifié dans le calcul de paie)
        
        Args:
            date_calcul: Date de référence pour le calcul (par défaut: aujourd'hui)
            
        Returns:
            tuple: (eligible: bool, raison: str)
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if date_calcul is None:
            date_calcul = timezone.now().date()
        
        # Vérifier le type de contrat
        if not self.est_stagiaire_ou_apprenti:
            return False, "Type de contrat non éligible (CDI/CDD/Temporaire)"
        
        # Vérifier la date de début du contrat
        date_debut = self.date_debut_contrat or self.date_embauche
        if not date_debut:
            return False, "Date de début de contrat non renseignée"
        
        # Calculer la durée depuis le début du contrat
        duree = relativedelta(date_calcul, date_debut)
        mois_ecoules = duree.years * 12 + duree.months
        
        if mois_ecoules > 12:
            return False, f"Durée dépassée ({mois_ecoules} mois > 12 mois max)"
        
        type_contrat_label = dict(self.TYPES_CONTRATS).get(self.type_contrat, self.type_contrat)
        return True, f"{type_contrat_label} - {mois_ecoules} mois (≤ 12 mois)"


class ContratEmploye(models.Model):
    """Contrats des employés"""
    STATUTS = (
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('rompu', 'Rompu'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='contrats')
    num_contrat = models.CharField(max_length=50, unique=True)
    type_contrat = models.CharField(max_length=20, choices=Employe.TYPES_CONTRATS)
    date_debut = models.DateField()
    date_fin = models.DateField(blank=True, null=True)
    duree_mois = models.IntegerField(blank=True, null=True)
    motif_contrat = models.TextField(blank=True, null=True)
    periode_essai_mois = models.IntegerField(blank=True, null=True)
    date_fin_essai = models.DateField(blank=True, null=True)
    statut_contrat = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    renouvellements = models.IntegerField(default=0)
    fichier_contrat = models.FileField(upload_to='contrats/', blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    date_signature = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'contrats_employes'
        verbose_name = 'Contrat employé'
        verbose_name_plural = 'Contrats employés'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.num_contrat} - {self.employe.nom_complet}"


class FormationEmploye(models.Model):
    """Formations des employés"""
    TYPES_FORMATION = (
        ('initiale', 'Formation initiale'),
        ('continue', 'Formation continue'),
        ('certification', 'Certification'),
    )
    
    RESULTATS = (
        ('acquis', 'Acquis'),
        ('non_acquis', 'Non acquis'),
        ('en_cours', 'En cours'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='formations')
    inscription_formation = models.OneToOneField('formation.InscriptionFormation', on_delete=models.SET_NULL, null=True, blank=True, related_name='formation_employe', help_text="Lien vers l'inscription dans le module formation")
    type_formation = models.CharField(max_length=50, choices=TYPES_FORMATION)
    intitule_formation = models.CharField(max_length=200)
    organisme_formation = models.CharField(max_length=200, blank=True, null=True)
    diplome_obtenu = models.CharField(max_length=100, blank=True, null=True)
    niveau = models.CharField(max_length=50, blank=True, null=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    duree_heures = models.IntegerField(blank=True, null=True)
    cout_formation = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    lieu_formation = models.CharField(max_length=100, blank=True, null=True)
    resultat = models.CharField(max_length=50, choices=RESULTATS, blank=True, null=True)
    fichier_attestation = models.FileField(upload_to='formations/', blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'formations_employes'
        verbose_name = 'Formation employé'
        verbose_name_plural = 'Formations employés'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.intitule_formation}"


class CarriereEmploye(models.Model):
    """Mouvements de carrière"""
    TYPES_MOUVEMENT = (
        ('promotion', 'Promotion'),
        ('mutation', 'Mutation'),
        ('reclassement', 'Reclassement'),
        ('detachement', 'Détachement'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='carrieres')
    type_mouvement = models.CharField(max_length=50, choices=TYPES_MOUVEMENT)
    date_mouvement = models.DateField()
    ancien_poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True, related_name='anciens_employes')
    nouveau_poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True, related_name='nouveaux_employes')
    ancien_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='anciens_employes')
    nouveau_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='nouveaux_employes')
    ancien_etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, related_name='anciens_employes')
    nouveau_etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, related_name='nouveaux_employes')
    ancienne_categorie = models.CharField(max_length=50, blank=True, null=True)
    nouvelle_categorie = models.CharField(max_length=50, blank=True, null=True)
    ancienne_classification = models.CharField(max_length=10, blank=True, null=True)
    nouvelle_classification = models.CharField(max_length=10, blank=True, null=True)
    ancien_salaire = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    nouveau_salaire = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    motif = models.TextField(blank=True, null=True)
    decision_reference = models.CharField(max_length=100, blank=True, null=True)
    date_decision = models.DateField(blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'carrieres_employes'
        verbose_name = 'Carrière employé'
        verbose_name_plural = 'Carrières employés'
        ordering = ['-date_mouvement']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_mouvement_display()} - {self.date_mouvement}"


class EvaluationEmploye(models.Model):
    """Évaluations des employés"""
    PERIODES = (
        ('annuelle', 'Annuelle'),
        ('semestrielle', 'Semestrielle'),
    )
    
    APPRECIATIONS = (
        ('excellent', 'Excellent'),
        ('bien', 'Bien'),
        ('satisfaisant', 'Satisfaisant'),
        ('insuffisant', 'Insuffisant'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='evaluations')
    annee_evaluation = models.IntegerField()
    periode = models.CharField(max_length=20, choices=PERIODES)
    date_evaluation = models.DateField()
    evaluateur = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, related_name='evaluations_effectuees')
    objectifs_atteints = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    competences_techniques = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    competences_comportementales = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    note_globale = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    appreciation = models.CharField(max_length=20, choices=APPRECIATIONS, blank=True, null=True)
    points_forts = models.TextField(blank=True, null=True)
    points_amelioration = models.TextField(blank=True, null=True)
    plan_developpement = models.TextField(blank=True, null=True)
    recommandations = models.TextField(blank=True, null=True)
    date_prochain_entretien = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'evaluations_employes'
        verbose_name = 'Évaluation employé'
        verbose_name_plural = 'Évaluations employés'
        ordering = ['-date_evaluation']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.annee_evaluation} - {self.get_periode_display()}"


class DocumentEmploye(models.Model):
    """Documents des employés"""
    TYPES_DOCUMENT = (
        ('cv', 'CV'),
        ('diplome', 'Diplôme'),
        ('attestation', 'Attestation'),
        ('certificat', 'Certificat'),
        ('piece_identite', 'Pièce d\'identité'),
        ('acte_naissance', 'Acte de naissance'),
        ('acte_mariage', 'Acte de mariage'),
        ('livret_famille', 'Livret de famille'),
        ('certificat_medical', 'Certificat médical'),
        ('contrat', 'Contrat de travail'),
        ('avenant', 'Avenant au contrat'),
        ('attestation_travail', 'Attestation de travail'),
        ('lettre_recommandation', 'Lettre de recommandation'),
        ('certificat_emploi', 'Certificat d\'emploi antérieur'),
        ('fiche_paie', 'Fiche de paie'),
        ('photo', 'Photo d\'identité'),
        ('autre', 'Autre document'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=50, choices=TYPES_DOCUMENT)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    fichier = models.FileField(upload_to='documents_employes/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_document = models.DateField(blank=True, null=True, help_text="Date du document")
    date_expiration = models.DateField(blank=True, null=True, help_text="Date d'expiration si applicable")
    taille_fichier = models.IntegerField(blank=True, null=True, help_text="Taille en octets")
    ajoute_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    confidentiel = models.BooleanField(default=False)
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'documents_employes'
        verbose_name = 'Document employé'
        verbose_name_plural = 'Documents employés'
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_document_display()} - {self.titre}"
    
    def get_extension(self):
        """Retourne l'extension du fichier"""
        import os
        return os.path.splitext(self.fichier.name)[1].lower()
    
    def get_icon(self):
        """Retourne l'icône Bootstrap selon le type de fichier"""
        ext = self.get_extension()
        icons = {
            '.pdf': 'bi-file-pdf text-danger',
            '.doc': 'bi-file-word text-primary',
            '.docx': 'bi-file-word text-primary',
            '.xls': 'bi-file-excel text-success',
            '.xlsx': 'bi-file-excel text-success',
            '.jpg': 'bi-file-image text-info',
            '.jpeg': 'bi-file-image text-info',
            '.png': 'bi-file-image text-info',
            '.zip': 'bi-file-zip text-warning',
            '.rar': 'bi-file-zip text-warning',
        }
        return icons.get(ext, 'bi-file-earmark text-secondary')
    
    def get_taille_lisible(self):
        """Retourne la taille du fichier en format lisible"""
        if not self.taille_fichier:
            return "N/A"
        
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if self.taille_fichier < 1024.0:
                return f"{self.taille_fichier:.1f} {unit}"
            self.taille_fichier /= 1024.0
        return f"{self.taille_fichier:.1f} To"
    
    def save(self, *args, **kwargs):
        """Calculer la taille du fichier avant la sauvegarde"""
        if self.fichier and not self.taille_fichier:
            self.taille_fichier = self.fichier.size
        super().save(*args, **kwargs)


# ============= CONTRATS & RELATIONS DE TRAVAIL =============

class AvenantContrat(models.Model):
    """Avenants aux contrats de travail"""
    MOTIFS = (
        ('promotion', 'Promotion'),
        ('mutation', 'Mutation'),
        ('augmentation', 'Augmentation de salaire'),
        ('changement_poste', 'Changement de poste'),
        ('changement_horaire', 'Changement d\'horaire'),
        ('renouvellement', 'Renouvellement CDD'),
        ('autre', 'Autre'),
    )
    
    contrat = models.ForeignKey(ContratEmploye, on_delete=models.CASCADE, related_name='avenants')
    numero_avenant = models.CharField(max_length=50, unique=True)
    date_avenant = models.DateField()
    date_effet = models.DateField()
    motif = models.CharField(max_length=30, choices=MOTIFS)
    description = models.TextField()
    
    # Anciennes valeurs
    ancien_poste = models.ForeignKey('core.Poste', on_delete=models.SET_NULL, null=True, blank=True, related_name='avenants_ancien')
    ancien_service = models.ForeignKey('core.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='avenants_ancien')
    ancien_salaire = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Nouvelles valeurs
    nouveau_poste = models.ForeignKey('core.Poste', on_delete=models.SET_NULL, null=True, blank=True, related_name='avenants_nouveau')
    nouveau_service = models.ForeignKey('core.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='avenants_nouveau')
    nouveau_salaire = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    fichier_avenant = models.FileField(upload_to='avenants/', blank=True, null=True)
    date_signature = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'avenants_contrats'
        verbose_name = 'Avenant au contrat'
        verbose_name_plural = 'Avenants aux contrats'
        ordering = ['-date_avenant']
    
    def __str__(self):
        return f"{self.numero_avenant} - {self.contrat.employe.nom_complet}"


class RuptureContrat(models.Model):
    """Rupture de contrat de travail"""
    TYPES_RUPTURE = (
        ('demission', 'Démission'),
        ('licenciement_faute', 'Licenciement pour faute'),
        ('licenciement_economique', 'Licenciement économique'),
        ('licenciement_inaptitude', 'Licenciement pour inaptitude'),
        ('rupture_conventionnelle', 'Rupture conventionnelle'),
        ('fin_cdd', 'Fin de CDD'),
        ('fin_essai', 'Fin de période d\'essai'),
        ('retraite', 'Départ à la retraite'),
        ('deces', 'Décès'),
        ('autre', 'Autre'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='ruptures')
    contrat = models.ForeignKey(ContratEmploye, on_delete=models.CASCADE, related_name='rupture')
    type_rupture = models.CharField(max_length=30, choices=TYPES_RUPTURE)
    motif_detaille = models.TextField()
    
    # Dates
    date_notification = models.DateField()
    date_effet = models.DateField(help_text="Date effective de fin de contrat")
    duree_preavis_jours = models.IntegerField(default=0)
    date_fin_preavis = models.DateField(null=True, blank=True)
    preavis_effectue = models.BooleanField(default=True)
    
    # Indemnités
    indemnite_licenciement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    indemnite_preavis = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    indemnite_conges_payes = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    autres_indemnites = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_indemnites = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Documents
    lettre_notification = models.FileField(upload_to='ruptures/', blank=True, null=True)
    certificat_travail = models.FileField(upload_to='ruptures/certificats/', blank=True, null=True)
    solde_tout_compte = models.FileField(upload_to='ruptures/stc/', blank=True, null=True)
    attestation_pole_emploi = models.FileField(upload_to='ruptures/', blank=True, null=True)
    
    date_generation_certificat = models.DateField(null=True, blank=True)
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'ruptures_contrats'
        verbose_name = 'Rupture de contrat'
        verbose_name_plural = 'Ruptures de contrats'
        ordering = ['-date_effet']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_rupture_display()}"
    
    def save(self, *args, **kwargs):
        self.total_indemnites = (
            self.indemnite_licenciement + 
            self.indemnite_preavis + 
            self.indemnite_conges_payes + 
            self.autres_indemnites
        )
        super().save(*args, **kwargs)


# ============= DISCIPLINE & SANCTIONS =============

class SanctionDisciplinaire(models.Model):
    """Sanctions disciplinaires"""
    TYPES_SANCTION = (
        ('avertissement_verbal', 'Avertissement verbal'),
        ('avertissement_ecrit', 'Avertissement écrit'),
        ('blame', 'Blâme'),
        ('mise_a_pied', 'Mise à pied disciplinaire'),
        ('retrogradation', 'Rétrogradation'),
        ('mutation_disciplinaire', 'Mutation disciplinaire'),
        ('licenciement', 'Licenciement'),
    )
    STATUTS = (
        ('en_cours', 'En cours'),
        ('notifiee', 'Notifiée'),
        ('contestee', 'Contestée'),
        ('annulee', 'Annulée'),
        ('executee', 'Exécutée'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='sanctions')
    type_sanction = models.CharField(max_length=30, choices=TYPES_SANCTION)
    motif = models.TextField(help_text="Description détaillée des faits reprochés")
    
    # Procédure
    date_faits = models.DateField()
    date_convocation = models.DateField(null=True, blank=True)
    date_entretien = models.DateField(null=True, blank=True)
    proces_verbal_entretien = models.FileField(upload_to='sanctions/pv/', blank=True, null=True)
    date_notification = models.DateField(null=True, blank=True)
    lettre_notification = models.FileField(upload_to='sanctions/', blank=True, null=True)
    
    # Application
    date_debut_application = models.DateField(null=True, blank=True)
    date_fin_application = models.DateField(null=True, blank=True)
    duree_jours = models.IntegerField(null=True, blank=True, help_text="Durée en jours pour mise à pied")
    
    # Recours
    recours_depose = models.BooleanField(default=False)
    date_recours = models.DateField(null=True, blank=True)
    decision_recours = models.TextField(blank=True, null=True)
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'sanctions_disciplinaires'
        verbose_name = 'Sanction disciplinaire'
        verbose_name_plural = 'Sanctions disciplinaires'
        ordering = ['-date_notification']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_sanction_display()}"


# ============= SANTÉ & SÉCURITÉ =============

class VisiteMedicale(models.Model):
    """Visites médicales"""
    TYPES_VISITE = (
        ('embauche', 'Visite d\'embauche'),
        ('periodique', 'Visite périodique'),
        ('reprise', 'Visite de reprise'),
        ('pre_reprise', 'Visite de pré-reprise'),
        ('demande', 'Visite à la demande'),
    )
    APTITUDES = (
        ('apte', 'Apte'),
        ('apte_reserves', 'Apte avec réserves'),
        ('inapte_temporaire', 'Inapte temporaire'),
        ('inapte_definitif', 'Inapte définitif'),
        ('en_attente', 'En attente de résultat'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='visites_medicales')
    type_visite = models.CharField(max_length=20, choices=TYPES_VISITE)
    date_visite = models.DateField()
    medecin = models.CharField(max_length=100, blank=True, null=True)
    centre_medical = models.CharField(max_length=200, blank=True, null=True)
    
    aptitude = models.CharField(max_length=20, choices=APTITUDES, default='en_attente')
    reserves = models.TextField(blank=True, null=True, help_text="Détail des réserves si applicable")
    recommandations = models.TextField(blank=True, null=True)
    
    date_prochaine_visite = models.DateField(null=True, blank=True)
    fichier_certificat = models.FileField(upload_to='visites_medicales/', blank=True, null=True)
    
    class Meta:
        db_table = 'visites_medicales'
        verbose_name = 'Visite médicale'
        verbose_name_plural = 'Visites médicales'
        ordering = ['-date_visite']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_visite_display()} ({self.date_visite})"


class AccidentTravail(models.Model):
    """Accidents du travail"""
    GRAVITES = (
        ('benin', 'Bénin'),
        ('leger', 'Léger'),
        ('grave', 'Grave'),
        ('tres_grave', 'Très grave'),
        ('mortel', 'Mortel'),
    )
    STATUTS = (
        ('declare', 'Déclaré'),
        ('en_instruction', 'En instruction CNSS'),
        ('reconnu', 'Reconnu'),
        ('refuse', 'Refusé'),
        ('cloture', 'Clôturé'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='accidents_travail')
    date_accident = models.DateField()
    heure_accident = models.TimeField(null=True, blank=True)
    lieu_accident = models.CharField(max_length=200)
    circonstances = models.TextField(help_text="Description détaillée des circonstances")
    
    # Lésions
    nature_lesions = models.TextField()
    siege_lesions = models.CharField(max_length=200, help_text="Partie du corps touchée")
    gravite = models.CharField(max_length=20, choices=GRAVITES)
    
    # Témoins
    temoins = models.TextField(blank=True, null=True, help_text="Noms et coordonnées des témoins")
    
    # Déclaration CNSS
    date_declaration_cnss = models.DateField(null=True, blank=True)
    numero_declaration_cnss = models.CharField(max_length=50, blank=True, null=True)
    declaration_cnss = models.FileField(upload_to='accidents/cnss/', blank=True, null=True)
    
    # Arrêt de travail
    arret_travail = models.ForeignKey('temps_travail.ArretTravail', on_delete=models.SET_NULL, null=True, blank=True, related_name='accident_origine')
    jours_arret = models.IntegerField(default=0)
    
    # Incapacité
    taux_ipp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Taux d'Incapacité Permanente Partielle")
    
    statut = models.CharField(max_length=20, choices=STATUTS, default='declare')
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'accidents_travail'
        verbose_name = 'Accident du travail'
        verbose_name_plural = 'Accidents du travail'
        ordering = ['-date_accident']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.date_accident} ({self.get_gravite_display()})"


class EquipementProtection(models.Model):
    """Équipements de protection individuelle (EPI)"""
    TYPES_EPI = (
        ('casque', 'Casque de sécurité'),
        ('lunettes', 'Lunettes de protection'),
        ('gants', 'Gants'),
        ('chaussures', 'Chaussures de sécurité'),
        ('gilet', 'Gilet de sécurité'),
        ('masque', 'Masque de protection'),
        ('bouchons_oreilles', 'Bouchons d\'oreilles'),
        ('harnais', 'Harnais de sécurité'),
        ('combinaison', 'Combinaison de travail'),
        ('autre', 'Autre'),
    )
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='equipements_protection')
    type_epi = models.CharField(max_length=30, choices=TYPES_EPI)
    designation = models.CharField(max_length=100)
    marque = models.CharField(max_length=50, blank=True, null=True)
    taille = models.CharField(max_length=20, blank=True, null=True)
    
    date_remise = models.DateField()
    date_peremption = models.DateField(null=True, blank=True)
    signature_employe = models.BooleanField(default=False)
    fiche_remise = models.FileField(upload_to='epi/', blank=True, null=True)
    
    observations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'equipements_protection'
        verbose_name = 'Équipement de protection'
        verbose_name_plural = 'Équipements de protection'
        ordering = ['-date_remise']
    
    def __str__(self):
        return f"{self.employe.nom_complet} - {self.get_type_epi_display()}"


# Import des modèles d'évaluation
from .models_evaluation import CampagneEvaluation, Evaluation, ObjectifEvaluation, CompetenceEvaluation

# Import des modèles de mission
from .models_mission import Mission, FraisMission, BaremeIndemnite

# Import des modèles de réclamation
from .models_reclamation import CategorieReclamation, Reclamation, CommentaireReclamation

# Import des modèles RH légaux guinéens
from .models_rh_legal import (
    FinContrat, CongeMaternite, AllocationFamiliale, EnfantEmploye,
    ConjointEmploye, PensionRetraite
)
