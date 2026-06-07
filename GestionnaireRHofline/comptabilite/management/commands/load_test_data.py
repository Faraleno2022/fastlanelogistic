"""
Commande Django pour charger des données de test pour le module comptabilité.
Usage: python manage.py load_test_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

from core.models import Entreprise, Utilisateur
from django.contrib.auth import get_user_model

User = get_user_model()
from comptabilite.models import (
    PlanComptable, Journal, ExerciceComptable, EcritureComptable,
    LigneEcriture, Tiers, Facture, LigneFacture, Reglement, TauxTVA,
    PieceComptable, Immobilisation, Stock, RegimeTVA
)


class Command(BaseCommand):
    help = 'Charge des données de test pour le module comptabilité'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entreprise',
            type=str,
            help='Code de l\'entreprise (optionnel, utilise la première si non spécifié)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime les données existantes avant de charger'
        )

    def handle(self, *args, **options):
        self.stdout.write('Chargement des données de test comptabilité...')
        
        # Récupérer ou créer l'entreprise
        entreprise = self.get_or_create_entreprise(options.get('entreprise'))
        if not entreprise:
            self.stdout.write(self.style.ERROR('Aucune entreprise trouvée.'))
            return
        
        self.stdout.write(f'Entreprise: {entreprise.nom_entreprise}')
        
        if options.get('clear'):
            self.clear_data(entreprise)
        
        with transaction.atomic():
            # 1. Plan comptable SYSCOHADA
            self.create_plan_comptable(entreprise)
            
            # 2. Journaux
            self.create_journaux(entreprise)
            
            # 3. Exercice comptable
            exercice = self.create_exercice(entreprise)
            
            # 4. Régime TVA et Taux
            self.create_regime_tva(entreprise)
            
            # 5. Tiers (clients et fournisseurs)
            self.create_tiers(entreprise)
            
            # 6. Factures
            self.create_factures(entreprise)
            
            # 7. Écritures comptables
            self.create_ecritures(entreprise, exercice)
            
            # 8. Immobilisations
            self.create_immobilisations(entreprise)
            
            # 9. Stocks
            self.create_stocks(entreprise)
        
        self.stdout.write(self.style.SUCCESS('Données de test chargées avec succès!'))

    def get_or_create_entreprise(self, code=None):
        if code:
            return Entreprise.objects.filter(slug=code).first()
        
        entreprise = Entreprise.objects.first()
        if not entreprise:
            entreprise = Entreprise.objects.create(
                nom_entreprise='Entreprise Test SARL',
                slug='entreprise-test-sarl',
                nif='123456789',
                adresse='Conakry, Guinée',
                telephone='+224 620 00 00 00',
                email='contact@entreprise-test.gn',
                type_module='both'
            )
        return entreprise

    def clear_data(self, entreprise):
        self.stdout.write('Suppression des données existantes...')
        LigneEcriture.objects.filter(ecriture__entreprise=entreprise).delete()
        EcritureComptable.objects.filter(entreprise=entreprise).delete()
        LigneFacture.objects.filter(facture__entreprise=entreprise).delete()
        Reglement.objects.filter(entreprise=entreprise).delete()
        Facture.objects.filter(entreprise=entreprise).delete()
        Tiers.objects.filter(entreprise=entreprise).delete()
        PieceComptable.objects.filter(entreprise=entreprise).delete()
        Journal.objects.filter(entreprise=entreprise).delete()
        ExerciceComptable.objects.filter(entreprise=entreprise).delete()
        PlanComptable.objects.filter(entreprise=entreprise).delete()
        Stock.objects.filter(entreprise=entreprise).delete()
        Immobilisation.objects.filter(entreprise=entreprise).delete()

    def create_plan_comptable(self, entreprise):
        """Crée le plan comptable SYSCOHADA simplifié"""
        if PlanComptable.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Plan comptable existant, ignoré.')
            return
        
        self.stdout.write('  Création du plan comptable SYSCOHADA...')
        
        comptes = [
            # Classe 1 - Comptes de ressources durables
            ('10', 'Capital', '1'),
            ('101', 'Capital social', '1'),
            ('106', 'Réserves', '1'),
            ('12', 'Report à nouveau', '1'),
            ('13', 'Résultat net de l\'exercice', '1'),
            ('16', 'Emprunts et dettes assimilées', '1'),
            ('162', 'Emprunts auprès des établissements de crédit', '1'),
            
            # Classe 2 - Comptes d'actif immobilisé
            ('20', 'Charges immobilisées', '2'),
            ('21', 'Immobilisations incorporelles', '2'),
            ('22', 'Terrains', '2'),
            ('23', 'Bâtiments', '2'),
            ('24', 'Matériel', '2'),
            ('241', 'Matériel industriel', '2'),
            ('244', 'Matériel de transport', '2'),
            ('245', 'Matériel de bureau', '2'),
            ('28', 'Amortissements', '2'),
            ('281', 'Amortissements des immobilisations incorporelles', '2'),
            ('283', 'Amortissements des bâtiments', '2'),
            ('284', 'Amortissements du matériel', '2'),
            
            # Classe 3 - Comptes de stocks
            ('31', 'Marchandises', '3'),
            ('32', 'Matières premières', '3'),
            ('33', 'Autres approvisionnements', '3'),
            ('36', 'Produits finis', '3'),
            ('37', 'Produits en cours', '3'),
            ('39', 'Dépréciations des stocks', '3'),
            
            # Classe 4 - Comptes de tiers
            ('40', 'Fournisseurs et comptes rattachés', '4'),
            ('401', 'Fournisseurs', '4'),
            ('408', 'Fournisseurs - Factures non parvenues', '4'),
            ('41', 'Clients et comptes rattachés', '4'),
            ('411', 'Clients', '4'),
            ('416', 'Clients douteux', '4'),
            ('42', 'Personnel', '4'),
            ('421', 'Personnel - Rémunérations dues', '4'),
            ('422', 'Personnel - Avances et acomptes', '4'),
            ('43', 'Organismes sociaux', '4'),
            ('431', 'Sécurité sociale (CNSS)', '4'),
            ('44', 'État et collectivités publiques', '4'),
            ('441', 'État - Impôts sur les bénéfices', '4'),
            ('443', 'État - TVA facturée', '4'),
            ('445', 'État - TVA récupérable', '4'),
            ('447', 'État - Impôts retenus à la source', '4'),
            ('449', 'État - Créances et dettes diverses', '4'),
            ('46', 'Débiteurs et créditeurs divers', '4'),
            ('47', 'Comptes transitoires', '4'),
            
            # Classe 5 - Comptes de trésorerie
            ('51', 'Banques', '5'),
            ('512', 'Banques locales', '5'),
            ('52', 'Établissements financiers', '5'),
            ('53', 'Caisse', '5'),
            ('531', 'Caisse siège', '5'),
            ('54', 'Régies d\'avances', '5'),
            ('57', 'Caisse', '5'),
            ('58', 'Virements internes', '5'),
            
            # Classe 6 - Comptes de charges
            ('60', 'Achats', '6'),
            ('601', 'Achats de marchandises', '6'),
            ('602', 'Achats de matières premières', '6'),
            ('604', 'Achats stockés de matières', '6'),
            ('605', 'Autres achats', '6'),
            ('61', 'Transports', '6'),
            ('62', 'Services extérieurs A', '6'),
            ('621', 'Sous-traitance générale', '6'),
            ('622', 'Locations', '6'),
            ('623', 'Entretien et réparations', '6'),
            ('624', 'Primes d\'assurance', '6'),
            ('625', 'Études et recherches', '6'),
            ('63', 'Services extérieurs B', '6'),
            ('631', 'Frais bancaires', '6'),
            ('632', 'Rémunérations d\'intermédiaires', '6'),
            ('633', 'Frais de formation du personnel', '6'),
            ('64', 'Impôts et taxes', '6'),
            ('641', 'Impôts et taxes directs', '6'),
            ('645', 'Autres impôts et taxes', '6'),
            ('65', 'Autres charges', '6'),
            ('66', 'Charges de personnel', '6'),
            ('661', 'Rémunérations du personnel', '6'),
            ('662', 'Rémunérations du personnel extérieur', '6'),
            ('664', 'Charges sociales', '6'),
            ('67', 'Frais financiers', '6'),
            ('671', 'Intérêts des emprunts', '6'),
            ('68', 'Dotations aux amortissements', '6'),
            ('681', 'Dotations aux amortissements d\'exploitation', '6'),
            ('69', 'Dotations aux provisions', '6'),
            
            # Classe 7 - Comptes de produits
            ('70', 'Ventes', '7'),
            ('701', 'Ventes de marchandises', '7'),
            ('702', 'Ventes de produits finis', '7'),
            ('704', 'Travaux facturés', '7'),
            ('705', 'Études facturées', '7'),
            ('706', 'Prestations de services', '7'),
            ('71', 'Subventions d\'exploitation', '7'),
            ('72', 'Production immobilisée', '7'),
            ('73', 'Variations de stocks', '7'),
            ('75', 'Autres produits', '7'),
            ('77', 'Revenus financiers', '7'),
            ('771', 'Intérêts de prêts', '7'),
            ('78', 'Transferts de charges', '7'),
            ('79', 'Reprises de provisions', '7'),
            
            # Classe 8 - Comptes des autres charges et produits
            ('81', 'Valeurs comptables des cessions', '8'),
            ('82', 'Produits des cessions', '8'),
            ('83', 'Charges hors activités ordinaires', '8'),
            ('84', 'Produits hors activités ordinaires', '8'),
            ('85', 'Dotations HAO', '8'),
            ('86', 'Reprises HAO', '8'),
            ('87', 'Participation des travailleurs', '8'),
            ('89', 'Impôts sur le résultat', '8'),
        ]
        
        for numero, intitule, classe in comptes:
            PlanComptable.objects.create(
                entreprise=entreprise,
                numero_compte=numero,
                intitule=intitule,
                classe=classe,
                est_actif=True
            )
        
        self.stdout.write(f'    {len(comptes)} comptes créés.')

    def create_journaux(self, entreprise):
        """Crée les journaux comptables"""
        if Journal.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Journaux existants, ignorés.')
            return
        
        self.stdout.write('  Création des journaux...')
        
        journaux = [
            ('AC', 'Journal des Achats', 'achat'),
            ('VT', 'Journal des Ventes', 'vente'),
            ('BQ', 'Journal de Banque', 'banque'),
            ('CA', 'Journal de Caisse', 'caisse'),
            ('OD', 'Journal des Opérations Diverses', 'od'),
            ('AN', 'Journal des À-Nouveaux', 'an'),
            ('SA', 'Journal des Salaires', 'od'),
        ]
        
        for code, libelle, type_journal in journaux:
            Journal.objects.create(
                entreprise=entreprise,
                code=code,
                libelle=libelle,
                type_journal=type_journal,
                est_actif=True
            )
        
        self.stdout.write(f'    {len(journaux)} journaux créés.')

    def create_exercice(self, entreprise):
        """Crée l'exercice comptable courant"""
        exercice = ExerciceComptable.objects.filter(
            entreprise=entreprise, est_courant=True
        ).first()
        
        if exercice:
            self.stdout.write('  Exercice existant, ignoré.')
            return exercice
        
        self.stdout.write('  Création de l\'exercice comptable...')
        
        today = date.today()
        exercice = ExerciceComptable.objects.create(
            entreprise=entreprise,
            libelle=f'Exercice {today.year}',
            date_debut=date(today.year, 1, 1),
            date_fin=date(today.year, 12, 31),
            statut='ouvert',
            est_courant=True
        )
        
        self.stdout.write(f'    Exercice {exercice.libelle} créé.')
        return exercice

    def get_admin_user(self):
        """Récupère ou crée un utilisateur admin pour les données de test"""
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()
        return user

    def create_regime_tva(self, entreprise):
        """Crée le régime TVA et les taux"""
        if RegimeTVA.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Régime TVA existant, ignoré.')
            return
        
        self.stdout.write('  Création du régime TVA...')
        
        user = self.get_admin_user()
        if not user:
            self.stdout.write(self.style.WARNING('    Aucun utilisateur trouvé, régime TVA ignoré.'))
            return
        
        regime = RegimeTVA.objects.create(
            entreprise=entreprise,
            code='REEL_NORMAL',
            nom='Régime Réel Normal',
            description='Régime de TVA réel normal - Guinée',
            taux_normal=Decimal('18.00'),
            taux_reduit=Decimal('10.00'),
            taux_super_reduit=Decimal('0.00'),
            periodicite='MENSUELLE',
            actif=True,
            date_debut=date.today(),
            utilisateur_creation=user,
            utilisateur_modification=user
        )
        
        # Créer les taux TVA
        taux_data = [
            ('TVA_18', 'TVA 18%', Decimal('18.00'), 'VENTE'),
            ('TVA_10', 'TVA 10%', Decimal('10.00'), 'VENTE'),
            ('TVA_0', 'Exonéré', Decimal('0.00'), 'VENTE'),
            ('TVA_IMPORT', 'TVA Import 18%', Decimal('18.00'), 'IMPORTATION'),
        ]
        
        for code, nom, taux, nature in taux_data:
            TauxTVA.objects.create(
                regime_tva=regime,
                code=code,
                nom=nom,
                taux=taux,
                nature=nature,
                actif=True,
                date_debut=date.today(),
                utilisateur_creation=user,
                utilisateur_modification=user
            )
        
        self.stdout.write(f'    Régime TVA et {len(taux_data)} taux créés.')

    def create_tiers(self, entreprise):
        """Crée des tiers (clients et fournisseurs)"""
        if Tiers.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Tiers existants, ignorés.')
            return
        
        self.stdout.write('  Création des tiers...')
        
        clients = [
            ('CLI001', 'SONEG SA', 'client', '123456789A'),
            ('CLI002', 'EDG - Électricité de Guinée', 'client', '234567890B'),
            ('CLI003', 'Orange Guinée', 'client', '345678901C'),
            ('CLI004', 'MTN Guinée', 'client', '456789012D'),
            ('CLI005', 'Société Minière de Boké', 'client', '567890123E'),
        ]
        
        fournisseurs = [
            ('FOU001', 'SOBRAGUI', 'fournisseur', '111222333A'),
            ('FOU002', 'TOPAZ SA', 'fournisseur', '222333444B'),
            ('FOU003', 'Ciment de Guinée', 'fournisseur', '333444555C'),
            ('FOU004', 'SOGUIPAH', 'fournisseur', '444555666D'),
            ('FOU005', 'Imprimerie Nationale', 'fournisseur', '555666777E'),
        ]
        
        compte_client = PlanComptable.objects.filter(
            entreprise=entreprise, numero_compte='411'
        ).first()
        compte_fournisseur = PlanComptable.objects.filter(
            entreprise=entreprise, numero_compte='401'
        ).first()
        
        for code, raison_sociale, type_tiers, nif in clients + fournisseurs:
            compte = compte_client if type_tiers == 'client' else compte_fournisseur
            Tiers.objects.create(
                entreprise=entreprise,
                code=code,
                raison_sociale=raison_sociale,
                type_tiers=type_tiers,
                nif=nif,
                adresse='Conakry, Guinée',
                telephone=f'+224 62{random.randint(0, 9)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}',
                email=f'contact@{raison_sociale.lower().replace(" ", "")[:10]}.gn',
                compte_comptable=compte,
                plafond_credit=Decimal(random.randint(10, 100) * 1000000),
                est_actif=True
            )
        
        self.stdout.write(f'    {len(clients)} clients et {len(fournisseurs)} fournisseurs créés.')

    def create_factures(self, entreprise):
        """Crée des factures de test"""
        if Facture.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Factures existantes, ignorées.')
            return
        
        self.stdout.write('  Création des factures...')
        
        clients = Tiers.objects.filter(entreprise=entreprise, type_tiers='client')
        fournisseurs = Tiers.objects.filter(entreprise=entreprise, type_tiers='fournisseur')
        
        today = date.today()
        factures_creees = 0
        
        # Factures de vente
        for i, client in enumerate(clients[:3]):
            montant_ht = Decimal(random.randint(5, 50) * 1000000)
            montant_tva = montant_ht * Decimal('0.18')
            montant_ttc = montant_ht + montant_tva
            
            facture = Facture.objects.create(
                entreprise=entreprise,
                numero=f'FV-{today.year}-{str(i+1).zfill(4)}',
                type_facture='vente',
                tiers=client,
                date_facture=today - timedelta(days=random.randint(1, 30)),
                date_echeance=today + timedelta(days=30),
                montant_ht=montant_ht,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc,
                statut='validee'
            )
            
            LigneFacture.objects.create(
                facture=facture,
                designation='Prestation de services',
                quantite=Decimal('1'),
                prix_unitaire=montant_ht,
                taux_tva=Decimal('18.00'),
                montant_ht=montant_ht,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc
            )
            factures_creees += 1
        
        # Factures d'achat
        for i, fournisseur in enumerate(fournisseurs[:3]):
            montant_ht = Decimal(random.randint(2, 20) * 1000000)
            montant_tva = montant_ht * Decimal('0.18')
            montant_ttc = montant_ht + montant_tva
            
            facture = Facture.objects.create(
                entreprise=entreprise,
                numero=f'FA-{today.year}-{str(i+1).zfill(4)}',
                type_facture='achat',
                tiers=fournisseur,
                date_facture=today - timedelta(days=random.randint(1, 30)),
                date_echeance=today + timedelta(days=45),
                montant_ht=montant_ht,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc,
                statut='validee'
            )
            
            LigneFacture.objects.create(
                facture=facture,
                designation='Fournitures diverses',
                quantite=Decimal('1'),
                prix_unitaire=montant_ht,
                taux_tva=Decimal('18.00'),
                montant_ht=montant_ht,
                montant_tva=montant_tva,
                montant_ttc=montant_ttc
            )
            factures_creees += 1
        
        self.stdout.write(f'    {factures_creees} factures créées.')

    def create_ecritures(self, entreprise, exercice):
        """Crée des écritures comptables de test"""
        if EcritureComptable.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Écritures existantes, ignorées.')
            return
        
        self.stdout.write('  Création des écritures comptables...')
        
        journal_od = Journal.objects.filter(entreprise=entreprise, code='OD').first()
        journal_bq = Journal.objects.filter(entreprise=entreprise, code='BQ').first()
        
        if not journal_od or not journal_bq:
            self.stdout.write(self.style.WARNING('    Journaux non trouvés, écritures ignorées.'))
            return
        
        today = date.today()
        ecritures_creees = 0
        
        # Écriture d'ouverture - Capital
        compte_capital = PlanComptable.objects.filter(entreprise=entreprise, numero_compte='101').first()
        compte_banque = PlanComptable.objects.filter(entreprise=entreprise, numero_compte='512').first()
        
        if compte_capital and compte_banque:
            ecriture = EcritureComptable.objects.create(
                entreprise=entreprise,
                exercice=exercice,
                journal=journal_od,
                numero_ecriture=f'OD-{today.year}-0001',
                date_ecriture=date(today.year, 1, 1),
                libelle='Constitution du capital social',
                est_validee=True,
                date_validation=timezone.now()
            )
            
            LigneEcriture.objects.create(
                ecriture=ecriture,
                compte=compte_banque,
                libelle='Apport en numéraire',
                montant_debit=Decimal('100000000'),
                montant_credit=Decimal('0')
            )
            LigneEcriture.objects.create(
                ecriture=ecriture,
                compte=compte_capital,
                libelle='Capital social',
                montant_debit=Decimal('0'),
                montant_credit=Decimal('100000000')
            )
            ecritures_creees += 1
        
        # Écritures de charges
        compte_charges = PlanComptable.objects.filter(entreprise=entreprise, numero_compte='622').first()
        if compte_charges and compte_banque:
            for i in range(3):
                montant = Decimal(random.randint(1, 5) * 1000000)
                ecriture = EcritureComptable.objects.create(
                    entreprise=entreprise,
                    exercice=exercice,
                    journal=journal_bq,
                    numero_ecriture=f'BQ-{today.year}-{str(i+1).zfill(4)}',
                    date_ecriture=today - timedelta(days=random.randint(1, 60)),
                    libelle=f'Paiement loyer mois {i+1}',
                    est_validee=True,
                    date_validation=timezone.now()
                )
                
                LigneEcriture.objects.create(
                    ecriture=ecriture,
                    compte=compte_charges,
                    libelle='Loyer mensuel',
                    montant_debit=montant,
                    montant_credit=Decimal('0')
                )
                LigneEcriture.objects.create(
                    ecriture=ecriture,
                    compte=compte_banque,
                    libelle='Paiement par virement',
                    montant_debit=Decimal('0'),
                    montant_credit=montant
                )
                ecritures_creees += 1
        
        self.stdout.write(f'    {ecritures_creees} écritures créées.')

    def create_immobilisations(self, entreprise):
        """Crée des immobilisations de test"""
        if Immobilisation.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Immobilisations existantes, ignorées.')
            return
        
        self.stdout.write('  Création des immobilisations...')
        
        immobilisations = [
            ('IMM-001', 'Véhicule Toyota Hilux', 'vehicule', Decimal('150000000'), 5),
            ('IMM-002', 'Ordinateurs bureaux (lot 10)', 'informatique', Decimal('50000000'), 3),
            ('IMM-003', 'Mobilier de bureau', 'mobilier', Decimal('25000000'), 10),
            ('IMM-004', 'Climatiseurs (lot 5)', 'materiel', Decimal('15000000'), 5),
            ('IMM-005', 'Serveur informatique', 'informatique', Decimal('30000000'), 5),
        ]
        
        today = date.today()
        
        for numero, designation, categorie, valeur, duree in immobilisations:
            Immobilisation.objects.create(
                entreprise=entreprise,
                numero=numero,
                designation=designation,
                categorie=categorie,
                date_acquisition=today - timedelta(days=random.randint(30, 365)),
                valeur_acquisition=valeur,
                duree_vie_ans=duree,
                mode_amortissement='lineaire',
                est_actif=True
            )
        
        self.stdout.write(f'    {len(immobilisations)} immobilisations créées.')

    def create_stocks(self, entreprise):
        """Crée des articles de stock de test"""
        if Stock.objects.filter(entreprise=entreprise).exists():
            self.stdout.write('  Stocks existants, ignorés.')
            return
        
        self.stdout.write('  Création des stocks...')
        
        articles = [
            ('ART-001', 'Papier A4 (ramette)', 'Ramette', 500, Decimal('25000')),
            ('ART-002', 'Stylos BIC (boîte)', 'Boîte', 200, Decimal('15000')),
            ('ART-003', 'Cartouches imprimante', 'Unité', 50, Decimal('150000')),
            ('ART-004', 'Classeurs', 'Unité', 100, Decimal('8000')),
            ('ART-005', 'Agrafeuses', 'Unité', 30, Decimal('12000')),
        ]
        
        for code, designation, unite, qte, prix in articles:
            Stock.objects.create(
                entreprise=entreprise,
                code=code,
                designation=designation,
                unite=unite,
                quantite_stock=Decimal(str(qte)),
                prix_unitaire_moyen=prix,
                valeur_stock=Decimal(str(qte)) * prix,
                stock_minimum=Decimal('10'),
                stock_maximum=Decimal('1000'),
                est_actif=True
            )
        
        self.stdout.write(f'    {len(articles)} articles de stock créés.')
