"""
Tests pour les services de fiscalité (TVA)
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User

from comptabilite.models import (
    RegimeTVA, TauxTVA, DeclarationTVA, LigneDeclarationTVA,
    ExerciceComptable, PlanComptable
)
from comptabilite.services.fiscalite_service import FiscaliteService
from comptabilite.services.calcul_tva_service import CalculTVAService
from core.models import Entreprise


class FiscaliteServiceTestCase(TestCase):
    """Tests du service FiscaliteService"""
    
    @classmethod
    def setUpTestData(cls):
        """Données initiales pour les tests"""
        # Utilisateur
        cls.utilisateur = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Entreprise
        cls.entreprise = Entreprise.objects.create(
            nom='Test Enterprise',
            siret='00000000000000',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            pays='France'
        )
        
        # Exercice
        cls.exercice = ExerciceComptable.objects.create(
            entreprise=cls.entreprise,
            annee=2024,
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 12, 31)
        )
        
        # Régime TVA
        cls.regime_tva = RegimeTVA.objects.create(
            entreprise=cls.entreprise,
            code='FR_NORMAL',
            nom='Régime Normal',
            regime='NORMAL',
            date_debut=date(2024, 1, 1),
            utilisateur_creation=cls.utilisateur,
            utilisateur_modification=cls.utilisateur
        )
        
        # Taux TVA
        cls.taux_normal = TauxTVA.objects.create(
            regime_tva=cls.regime_tva,
            code='TVA_20',
            nom='TVA Normal 20%',
            taux=Decimal('20.00'),
            nature='VENTE',
            date_debut=date(2024, 1, 1),
            utilisateur_creation=cls.utilisateur
        )
        
        cls.taux_reduit = TauxTVA.objects.create(
            regime_tva=cls.regime_tva,
            code='TVA_5.5',
            nom='TVA Réduit 5.5%',
            taux=Decimal('5.50'),
            nature='SERVICE',
            date_debut=date(2024, 1, 1),
            utilisateur_creation=cls.utilisateur
        )
    
    def setUp(self):
        """Préparation pour chaque test"""
        self.service = FiscaliteService(self.utilisateur)
    
    def test_creer_declaration_tva_valide(self):
        """Test création d'une déclaration TVA valide"""
        periode_debut = date(2024, 1, 1)
        periode_fin = date(2024, 1, 31)
        
        declaration, errors = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=periode_debut,
            periode_fin=periode_fin,
            exercice=self.exercice
        )
        
        self.assertIsNotNone(declaration)
        self.assertEqual(declaration.statut, 'BROUILLON')
        self.assertEqual(declaration.entreprise, self.entreprise)
        self.assertEqual(declaration.regime_tva, self.regime_tva)
        self.assertFalse(errors)
    
    def test_creer_declaration_doublon(self):
        """Test création d'une déclaration TVA en doublon"""
        periode_debut = date(2024, 1, 1)
        periode_fin = date(2024, 1, 31)
        
        # Première création
        self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=periode_debut,
            periode_fin=periode_fin
        )
        
        # Deuxième création (devrait échouer)
        declaration2, errors = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=periode_debut,
            periode_fin=periode_fin
        )
        
        self.assertIsNone(declaration2)
        self.assertTrue(errors)
    
    def test_ajouter_ligne_declaration(self):
        """Test ajout de lignes à une déclaration"""
        # Créer déclaration
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 1, 1),
            periode_fin=date(2024, 1, 31)
        )
        
        # Ajouter ligne
        ligne, errors = self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Vente de marchandises',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        
        self.assertIsNotNone(ligne)
        self.assertEqual(ligne.montant_ht, Decimal('1000.00'))
        self.assertEqual(ligne.montant_tva, Decimal('200.00'))  # 20% de 1000
        self.assertEqual(ligne.numero_ligne, 1)
        self.assertFalse(errors)
    
    def test_ajouter_multiple_lignes(self):
        """Test ajout de plusieurs lignes"""
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 2, 1),
            periode_fin=date(2024, 2, 29)
        )
        
        # Première ligne
        ligne1, _ = self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Ventes',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        
        # Deuxième ligne
        ligne2, _ = self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Services',
            taux_tva=self.taux_reduit,
            montant_ht=Decimal('500.00')
        )
        
        self.assertEqual(ligne1.numero_ligne, 1)
        self.assertEqual(ligne2.numero_ligne, 2)
        self.assertEqual(declaration.lignes.count(), 2)
    
    def test_calculer_montants_declaration(self):
        """Test calcul des montants de déclaration"""
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 3, 1),
            periode_fin=date(2024, 3, 31)
        )
        
        # Ajouter lignes
        self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Ventes',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        
        self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Services',
            taux_tva=self.taux_reduit,
            montant_ht=Decimal('500.00')
        )
        
        # Calculer
        montants = self.service.calculer_montants_declaration(declaration)
        
        self.assertEqual(montants['montant_ht'], Decimal('1500.00'))
        self.assertEqual(montants['montant_tva_collecte'], Decimal('227.50'))  # 200 + 27.5
        self.assertEqual(montants['montant_tva_due'], Decimal('227.50'))
    
    def test_valider_declaration(self):
        """Test validation d'une déclaration"""
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 4, 1),
            periode_fin=date(2024, 4, 30)
        )
        
        # Ajouter ligne
        self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Ventes',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        
        # Valider
        success, errors = self.service.valider_declaration(declaration)
        
        self.assertTrue(success)
        self.assertFalse(errors)
        
        # Vérifier statut
        declaration.refresh_from_db()
        self.assertEqual(declaration.statut, 'VALIDEE')
        self.assertEqual(declaration.montant_ht, Decimal('1000.00'))
        self.assertEqual(declaration.montant_tva_due, Decimal('200.00'))
    
    def test_deposer_declaration(self):
        """Test dépôt d'une déclaration"""
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 5, 1),
            periode_fin=date(2024, 5, 31)
        )
        
        # Ajouter et valider
        self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Ventes',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        self.service.valider_declaration(declaration)
        
        # Déposer
        success, errors = self.service.deposer_declaration(
            declaration=declaration,
            numero_depot='DEP2024051234'
        )
        
        self.assertTrue(success)
        
        declaration.refresh_from_db()
        self.assertEqual(declaration.statut, 'DEPOSEE')
        self.assertEqual(declaration.numero_depot, 'DEP2024051234')
        self.assertIsNotNone(declaration.date_depot)
    
    def test_lister_declarations_periode(self):
        """Test listage des déclarations par période"""
        # Créer plusieurs déclarations
        self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 1, 1),
            periode_fin=date(2024, 1, 31)
        )
        
        self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 2, 1),
            periode_fin=date(2024, 2, 29)
        )
        
        # Lister
        declarations = self.service.lister_declarations_periode(
            entreprise=self.entreprise,
            date_debut=date(2024, 1, 1),
            date_fin=date(2024, 12, 31)
        )
        
        self.assertEqual(declarations.count(), 2)
    
    def test_montant_a_payer(self):
        """Test calcul montant TVA à payer"""
        declaration, _ = self.service.creer_declaration_tva(
            entreprise=self.entreprise,
            regime_tva=self.regime_tva,
            periode_debut=date(2024, 6, 1),
            periode_fin=date(2024, 6, 30)
        )
        
        # Ajouter lignes
        self.service.ajouter_ligne_declaration(
            declaration=declaration,
            description='Ventes',
            taux_tva=self.taux_normal,
            montant_ht=Decimal('1000.00')
        )
        
        self.service.valider_declaration(declaration)
        
        montant = self.service.obtenir_montant_a_payer(declaration)
        self.assertEqual(montant, Decimal('200.00'))


class CalculTVAServiceTestCase(TestCase):
    """Tests du service CalculTVAService"""
    
    def setUp(self):
        """Préparation pour chaque test"""
        self.utilisateur = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.service = CalculTVAService(self.utilisateur)
    
    def test_calculer_tva(self):
        """Test calcul TVA simple"""
        montant_tva = self.service.calculer_tva(
            montant_ht=Decimal('1000.00'),
            taux=Decimal('20.00')
        )
        
        self.assertEqual(montant_tva, Decimal('200.00'))
    
    def test_calculer_tva_reduite(self):
        """Test calcul TVA réduite"""
        montant_tva = self.service.calculer_tva(
            montant_ht=Decimal('1000.00'),
            taux=Decimal('5.50')
        )
        
        self.assertEqual(montant_tva, Decimal('55.00'))
    
    def test_calculer_ttc(self):
        """Test calcul TTC"""
        montant_ttc = self.service.calculer_ttc(
            montant_ht=Decimal('1000.00'),
            taux=Decimal('20.00')
        )
        
        self.assertEqual(montant_ttc, Decimal('1200.00'))
    
    def test_calculer_ht(self):
        """Test calcul HT à partir TTC"""
        montant_ht = self.service.calculer_ht(
            montant_ttc=Decimal('1200.00'),
            taux=Decimal('20.00')
        )
        
        self.assertEqual(montant_ht, Decimal('1000.00'))
    
    def test_calculer_ht_precision(self):
        """Test calcul HT avec précision"""
        montant_ht = self.service.calculer_ht(
            montant_ttc=Decimal('119.60'),
            taux=Decimal('20.00')
        )
        
        self.assertEqual(montant_ht, Decimal('99.67'))
    
    def test_appliquer_taux(self):
        """Test application d'un taux"""
        entreprise = Entreprise.objects.create(
            nom='Test',
            siret='00000000000001'
        )
        
        regime = RegimeTVA.objects.create(
            entreprise=entreprise,
            code='TEST',
            nom='Test',
            regime='NORMAL',
            date_debut=date.today(),
            utilisateur_creation=self.utilisateur,
            utilisateur_modification=self.utilisateur
        )
        
        taux_tva = TauxTVA.objects.create(
            regime_tva=regime,
            code='TEST_20',
            nom='Test 20%',
            taux=Decimal('20.00'),
            nature='VENTE',
            date_debut=date.today(),
            utilisateur_creation=self.utilisateur
        )
        
        resultat = self.service.appliquer_taux(
            montant_ht=Decimal('1000.00'),
            taux_tva=taux_tva
        )
        
        self.assertEqual(resultat['montant_ht'], Decimal('1000.00'))
        self.assertEqual(resultat['montant_tva'], Decimal('200.00'))
        self.assertEqual(resultat['montant_ttc'], Decimal('1200.00'))
        self.assertEqual(resultat['taux'], Decimal('20.00'))
    
    def test_obtenir_taux_effectif(self):
        """Test calcul taux effectif"""
        taux = self.service.obtenir_taux_effectif(
            montant_ht=Decimal('1000.00'),
            montant_tva=Decimal('200.00')
        )
        
        self.assertEqual(taux, Decimal('20.00'))
    
    def test_validation_montant_negatif(self):
        """Test validation montant négatif"""
        montant_tva = self.service.calculer_tva(
            montant_ht=Decimal('-100.00'),
            taux=Decimal('20.00')
        )
        
        # Devrait retourner 0 en cas d'erreur
        self.assertEqual(montant_tva, Decimal('0.00'))
    
    def test_validation_taux_invalide(self):
        """Test validation taux invalide"""
        montant_tva = self.service.calculer_tva(
            montant_ht=Decimal('1000.00'),
            taux=Decimal('150.00')  # Taux > 100%
        )
        
        self.assertEqual(montant_tva, Decimal('0.00'))
