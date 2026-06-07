"""
Commande pour initialiser l'exercice complexe de paie
Entreprise MINÉRAUX GUINÉE SA - Employé Diallo Abdoulaye
Secteur minier avec convention collective spécifique
"""
from django.core.management.base import BaseCommand
from datetime import date
from decimal import Decimal

from core.models import Societe, Etablissement, Service, Poste
from employes.models import Employe
from paie.models import (
    ParametrePaie, Constante, RubriquePaie, Variable,
    PeriodePaie
)


class Command(BaseCommand):
    help = 'Initialise l\'exercice complexe MINÉRAUX GUINÉE SA'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('⛏️  Initialisation MINÉRAUX GUINÉE SA...'))
        
        # 1. Créer la société
        societe = self.creer_societe()
        
        # 2. Créer l'établissement
        etablissement = self.creer_etablissement(societe)
        
        # 3. Créer le service
        service = self.creer_service(etablissement)
        
        # 4. Créer le poste
        poste = self.creer_poste(service)
        
        # 5. Créer l'employé
        employe = self.creer_employe(etablissement, service, poste)
        
        # 6. Créer les rubriques de paie (secteur minier)
        self.creer_rubriques_paie()
        
        # 7. Créer la période novembre 2025
        periode = self.creer_periode_novembre_2025()
        
        # 8. Ajouter les constantes spécifiques
        self.ajouter_constantes_specifiques()
        
        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée!'))
        self.stdout.write(self.style.SUCCESS(f'   Société : {societe.raison_sociale}'))
        self.stdout.write(self.style.SUCCESS(f'   Employé : {employe.nom} {employe.prenoms}'))
        self.stdout.write(self.style.SUCCESS(f'   Période : {periode}'))

    def creer_societe(self):
        """Créer la société MINÉRAUX GUINÉE SA"""
        self.stdout.write('🏢 Création MINÉRAUX GUINÉE SA...')
        
        societe, created = Societe.objects.get_or_create(
            raison_sociale='MINÉRAUX GUINÉE SA',
            defaults={
                'forme_juridique': 'SA',
                'ville': 'Kindia',
                'pays': 'Guinée',
                'secteur_activite': 'Exploitation minière',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Société créée'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Société déjà existante'))
        
        return societe

    def creer_etablissement(self, societe):
        """Créer l'établissement"""
        self.stdout.write('🏭 Création établissement...')
        
        etablissement, created = Etablissement.objects.get_or_create(
            societe=societe,
            code_etablissement='MG-KINDIA',
            defaults={
                'nom_etablissement': 'Site minier de Kindia',
                'type_etablissement': 'Site d\'exploitation',
                'ville': 'Kindia',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Établissement créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Établissement déjà existant'))
        
        return etablissement

    def creer_service(self, etablissement):
        """Créer le service Exploitation"""
        self.stdout.write('⛏️  Création service Exploitation...')
        
        service, created = Service.objects.get_or_create(
            etablissement=etablissement,
            code_service='EXPLOIT',
            defaults={
                'nom_service': 'Exploitation minière',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Service créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Service déjà existant'))
        
        return service

    def creer_poste(self, service):
        """Créer le poste Responsable de chantier"""
        self.stdout.write('👷 Création du poste...')
        
        poste, created = Poste.objects.get_or_create(
            code_poste='RESP-CHANT-A',
            defaults={
                'intitule_poste': 'Responsable de chantier',
                'service': service,
                'categorie_professionnelle': 'Cadre',
                'classification': 'A',
                'actif': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Poste créé'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Poste déjà existant'))
        
        return poste

    def creer_employe(self, etablissement, service, poste):
        """Créer l'employé Diallo Abdoulaye"""
        self.stdout.write('👤 Création employé Diallo Abdoulaye...')
        
        employe, created = Employe.objects.get_or_create(
            matricule='MG-2021-847',
            defaults={
                'civilite': 'M.',
                'nom': 'Diallo',
                'prenoms': 'Abdoulaye',
                'sexe': 'M',
                'situation_matrimoniale': 'Marié(e)',
                'nombre_enfants': 3,
                'date_naissance': date(1985, 5, 10),
                'nationalite': 'Guinéenne',
                'num_cnss_individuel': '987654321',
                'etablissement': etablissement,
                'service': service,
                'poste': poste,
                'date_embauche': date(2020, 3, 15),
                'type_contrat': 'CDI',
                'statut_employe': 'Actif',
                'telephone_principal': '+224 621 00 00 00',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Employé créé'))
            self.stdout.write(self.style.SUCCESS(f'     Matricule : {employe.matricule}'))
            self.stdout.write(self.style.SUCCESS(f'     Ancienneté : 5 ans'))
            self.stdout.write(self.style.SUCCESS(f'     Situation : Marié, {employe.nombre_enfants} enfants'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Employé déjà existant'))
        
        return employe

    def creer_rubriques_paie(self):
        """Créer les rubriques de paie pour le secteur minier"""
        self.stdout.write('💰 Création rubriques de paie...')
        
        rubriques = [
            # ===== GAINS - SALAIRES ET INDEMNITÉS DE BASE =====
            {
                'code_rubrique': 'SAL_BASE_CAT_A',
                'libelle_rubrique': 'Salaire mensuel de base (Catégorie A)',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 10,
                'ordre_affichage': 10,
            },
            {
                'code_rubrique': 'IND_FONCTION',
                'libelle_rubrique': 'Indemnité de fonction',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 20,
                'ordre_affichage': 20,
            },
            {
                'code_rubrique': 'PRIME_ANCIENNETE',
                'libelle_rubrique': 'Prime d\'ancienneté',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 30,
                'ordre_affichage': 30,
                'formule_calcul': 'SAL_BASE * TAUX_ANCIENNETE',
            },
            {
                'code_rubrique': 'PRIME_RESP',
                'libelle_rubrique': 'Prime de responsabilité',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 40,
                'ordre_affichage': 40,
            },
            
            # ===== RÉMUNÉRATIONS VARIABLES =====
            {
                'code_rubrique': 'PRIME_PROD',
                'libelle_rubrique': 'Prime de production',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 50,
                'ordre_affichage': 50,
            },
            {
                'code_rubrique': 'BONUS_SECURITE',
                'libelle_rubrique': 'Bonus de sécurité',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 60,
                'ordre_affichage': 60,
            },
            {
                'code_rubrique': 'COMMISSION_CA',
                'libelle_rubrique': 'Commission sur chiffre d\'affaires',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 70,
                'ordre_affichage': 70,
            },
            
            # ===== INDEMNITÉS ET ALLOCATIONS =====
            {
                'code_rubrique': 'IND_DEPLACE',
                'libelle_rubrique': 'Indemnité de déplacement',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': False,  # Souvent exonéré
                'ordre_calcul': 80,
                'ordre_affichage': 80,
            },
            {
                'code_rubrique': 'IND_REPAS_JOUR',
                'libelle_rubrique': 'Indemnité de repas',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': False,  # Souvent exonéré
                'ordre_calcul': 90,
                'ordre_affichage': 90,
            },
            {
                'code_rubrique': 'ALLOC_LOGEMENT',
                'libelle_rubrique': 'Allocation logement',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 100,
                'ordre_affichage': 100,
            },
            {
                'code_rubrique': 'ALLOC_TRANSPORT',
                'libelle_rubrique': 'Allocation transport',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'ordre_calcul': 110,
                'ordre_affichage': 110,
            },
            
            # ===== HEURES SUPPLÉMENTAIRES =====
            {
                'code_rubrique': 'HS_25',
                'libelle_rubrique': 'Heures supplémentaires (+25%)',
                'type_rubrique': 'gain',
                'soumis_cnss': True,
                'soumis_rts': True,
                'taux_rubrique': Decimal('1.25'),
                'ordre_calcul': 120,
                'ordre_affichage': 120,
            },
            
            # ===== RETENUES OBLIGATOIRES =====
            {
                'code_rubrique': 'CNSS_SAL_MINIER',
                'libelle_rubrique': 'Cotisation CNSS (salarié)',
                'type_rubrique': 'retenue',
                'taux_rubrique': Decimal('5.50'),
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 200,
                'ordre_affichage': 200,
            },
            {
                'code_rubrique': 'MUTUELLE_ENT',
                'libelle_rubrique': 'Cotisation mutuelle d\'entreprise',
                'type_rubrique': 'retenue',
                'taux_rubrique': Decimal('3.00'),
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 210,
                'ordre_affichage': 210,
            },
            {
                'code_rubrique': 'RTS_MINIER',
                'libelle_rubrique': 'RTS (Retenue sur le revenu)',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 220,
                'ordre_affichage': 220,
            },
            
            # ===== AUTRES RETENUES =====
            {
                'code_rubrique': 'AVANCE_SAL',
                'libelle_rubrique': 'Avance sur salaire',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 300,
                'ordre_affichage': 300,
            },
            {
                'code_rubrique': 'RET_SYNDICAT',
                'libelle_rubrique': 'Retenue syndicale',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 310,
                'ordre_affichage': 310,
            },
            {
                'code_rubrique': 'PRET_LOGEMENT',
                'libelle_rubrique': 'Remboursement prêt logement',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 320,
                'ordre_affichage': 320,
            },
            {
                'code_rubrique': 'RET_DISCIPLINAIRE',
                'libelle_rubrique': 'Retenue disciplinaire',
                'type_rubrique': 'retenue',
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 330,
                'ordre_affichage': 330,
            },
            
            # ===== COTISATIONS PATRONALES =====
            {
                'code_rubrique': 'CNSS_PAT_MINIER',
                'libelle_rubrique': 'CNSS Employeur',
                'type_rubrique': 'cotisation',
                'taux_rubrique': Decimal('8.10'),
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 400,
                'ordre_affichage': 400,
            },
            {
                'code_rubrique': 'COTIS_MATERNITE',
                'libelle_rubrique': 'Cotisation Maternité',
                'type_rubrique': 'cotisation',
                'taux_rubrique': Decimal('1.50'),
                'soumis_cnss': False,
                'soumis_rts': False,
                'ordre_calcul': 410,
                'ordre_affichage': 410,
            },
        ]
        
        count_created = 0
        for rub_data in rubriques:
            rub, created = RubriquePaie.objects.get_or_create(
                code_rubrique=rub_data['code_rubrique'],
                defaults=rub_data
            )
            if created:
                count_created += 1
        
        if count_created > 0:
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count_created} rubriques créées'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Toutes les rubriques existent déjà'))

    def creer_periode_novembre_2025(self):
        """Créer la période novembre 2025"""
        self.stdout.write('📅 Création période Novembre 2025...')
        
        periode, created = PeriodePaie.objects.get_or_create(
            annee=2025,
            mois=11,
            defaults={
                'libelle': 'Novembre 2025',
                'date_debut': date(2025, 11, 1),
                'date_fin': date(2025, 11, 30),
                'statut_periode': 'ouverte',
                'nombre_jours_travailles': 22,
                'nombre_heures_mois': Decimal('173.33'),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Période créée'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Période déjà existante'))
        
        return periode

    def ajouter_constantes_specifiques(self):
        """Ajouter les constantes spécifiques au secteur minier"""
        self.stdout.write('🔧 Ajout constantes spécifiques...')
        
        constantes = [
            # Taux d'ancienneté
            {
                'code': 'TAUX_ANCIENNETE_5ANS',
                'libelle': 'Taux prime d\'ancienneté (5 ans)',
                'valeur': Decimal('5.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'general',
                'unite': '%',
                'description': '5% du salaire de base après 5 ans d\'ancienneté'
            },
            
            # Déductions familiales RTS
            {
                'code': 'DEDUC_CONJOINT',
                'libelle': 'Déduction RTS conjoint à charge',
                'valeur': Decimal('50000'),
                'type_valeur': 'montant',
                'categorie': 'rts',
                'unite': 'GNF',
                'description': 'Déduction fixe pour conjoint à charge'
            },
            {
                'code': 'DEDUC_ENFANT',
                'libelle': 'Déduction RTS par enfant',
                'valeur': Decimal('75000'),
                'type_valeur': 'montant',
                'categorie': 'rts',
                'unite': 'GNF',
                'description': 'Déduction par enfant à charge (max 3)'
            },
            {
                'code': 'MAX_ENFANTS_DEDUC',
                'libelle': 'Nombre maximum d\'enfants déductibles',
                'valeur': Decimal('3'),
                'type_valeur': 'nombre',
                'categorie': 'rts',
                'unite': 'enfants',
                'description': 'Maximum 3 enfants pour déductions fiscales'
            },
            
            # Taux mutuelle
            {
                'code': 'TAUX_MUTUELLE_ENT',
                'libelle': 'Taux cotisation mutuelle d\'entreprise',
                'valeur': Decimal('3.00'),
                'type_valeur': 'pourcentage',
                'categorie': 'general',
                'unite': '%',
                'description': 'Cotisation mutuelle obligatoire secteur minier'
            },
            
            # Taux CNSS minier
            {
                'code': 'TAUX_CNSS_PAT_MINIER',
                'libelle': 'Taux CNSS employeur (secteur minier)',
                'valeur': Decimal('8.10'),
                'type_valeur': 'pourcentage',
                'categorie': 'cnss',
                'unite': '%',
                'description': 'Taux CNSS patronal pour secteur minier'
            },
            {
                'code': 'TAUX_MATERNITE',
                'libelle': 'Taux cotisation maternité',
                'valeur': Decimal('1.50'),
                'type_valeur': 'pourcentage',
                'categorie': 'cnss',
                'unite': '%',
                'description': 'Cotisation maternité (charge patronale)'
            },
            
            # Heures de base
            {
                'code': 'HEURES_BASE_MOIS',
                'libelle': 'Nombre d\'heures de base par mois',
                'valeur': Decimal('173.00'),
                'type_valeur': 'nombre',
                'categorie': 'temps',
                'unite': 'heures',
                'description': 'Base de calcul pour taux horaire (40h/semaine)'
            },
        ]
        
        count_created = 0
        for const_data in constantes:
            const, created = Constante.objects.get_or_create(
                code=const_data['code'],
                defaults={
                    **const_data,
                    'date_debut_validite': date(2025, 1, 1),
                    'actif': True
                }
            )
            if created:
                count_created += 1
        
        if count_created > 0:
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count_created} constantes ajoutées'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Toutes les constantes existent déjà'))
