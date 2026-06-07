"""
Tests de vérification de l'isolation multi-tenant pour les évaluations et sanctions
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Entreprise, ProfilUtilisateur
from employes.models import Employe, EvaluationEmploye, SanctionDisciplinaire
from datetime import date
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class MultiTenantIsolationTest(TestCase):
    """Tests d'isolation multi-tenant pour évaluations et sanctions"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        # Créer deux entreprises distinctes
        self.entreprise1 = Entreprise.objects.create(
            nom_entreprise="Entreprise 1",
            slug="entreprise-1",
            email="contact@entreprise1.com"
        )
        
        self.entreprise2 = Entreprise.objects.create(
            nom_entreprise="Entreprise 2", 
            slug="entreprise-2",
            email="contact@entreprise2.com"
        )
        
        # Créer un profil RH
        self.profil_rh = ProfilUtilisateur.objects.create(
            nom_profil="RH",
            niveau_acces=4
        )
        
        # Créer des utilisateurs pour chaque entreprise
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
            entreprise=self.entreprise1,
            profil=self.profil_rh
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com', 
            password='testpass123',
            entreprise=self.entreprise2,
            profil=self.profil_rh
        )
        
        # Créer des employés pour chaque entreprise
        self.employe1 = Employe.objects.create(
            entreprise=self.entreprise1,
            matricule="EMP001",
            nom="Dupont",
            prenoms="Jean",
            sexe="M",
            date_naissance=date(1990, 1, 1),
            date_embauche=date(2020, 1, 1),
            type_contrat="CDI"
        )
        
        self.employe2 = Employe.objects.create(
            entreprise=self.entreprise2,
            matricule="EMP002",
            nom="Martin",
            prenoms="Marie",
            sexe="F",
            date_naissance=date(1985, 5, 15),
            date_embauche=date(2019, 6, 1),
            type_contrat="CDI"
        )
        
        # Créer des évaluations
        self.evaluation1 = EvaluationEmploye.objects.create(
            employe=self.employe1,
            annee_evaluation=2024,
            periode="annuelle",
            date_evaluation=date(2024, 1, 15),
            evaluateur=self.employe1,
            note_globale=85
        )
        
        self.evaluation2 = EvaluationEmploye.objects.create(
            employe=self.employe2,
            annee_evaluation=2024,
            periode="annuelle", 
            date_evaluation=date(2024, 1, 20),
            evaluateur=self.employe2,
            note_globale=90
        )
        
        # Créer des sanctions
        self.sanction1 = SanctionDisciplinaire.objects.create(
            employe=self.employe1,
            type_sanction="avertissement_ecrit",
            motif="Retards répétés",
            date_faits=date(2024, 1, 10),
            statut="notifiee"
        )
        
        self.sanction2 = SanctionDisciplinaire.objects.create(
            employe=self.employe2,
            type_sanction="blame",
            motif="Non respect des consignes",
            date_faits=date(2024, 1, 12),
            statut="executee"
        )
        
        self.client = Client()
    
    def test_evaluation_list_isolation(self):
        """Test que les utilisateurs ne voient que les évaluations de leur entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Accès aux évaluations de l'employé 1 (même entreprise)
        url = reverse('employes:evaluation_list', args=[self.employe1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.employe1.nom)
        self.assertContains(response, str(self.evaluation1.note_globale))
        
        # Tentative d'accès aux évaluations de l'employé 2 (autre entreprise)
        url = reverse('employes:evaluation_list', args=[self.employe2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_evaluation_detail_isolation(self):
        """Test que les utilisateurs ne peuvent voir que les détails des évaluations de leur entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Accès à l'évaluation 1 (même entreprise)
        url = reverse('employes:evaluation_detail', args=[self.evaluation1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative d'accès à l'évaluation 2 (autre entreprise)
        url = reverse('employes:evaluation_detail', args=[self.evaluation2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_evaluation_create_isolation(self):
        """Test que les utilisateurs ne peuvent créer des évaluations que pour leur entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Création d'évaluation pour employé 1 (même entreprise) - devrait fonctionner
        url = reverse('employes:evaluation_create', args=[self.employe1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative de création pour employé 2 (autre entreprise) - devrait échouer
        url = reverse('employes:evaluation_create', args=[self.employe2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_evaluation_update_isolation(self):
        """Test que les utilisateurs ne peuvent modifier que les évaluations de leur entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Modification évaluation 1 (même entreprise)
        url = reverse('employes:evaluation_detail', args=[self.evaluation1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative modification évaluation 2 (autre entreprise)
        url = reverse('employes:evaluation_detail', args=[self.evaluation2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_evaluation_delete_isolation(self):
        """Test que les utilisateurs ne peuvent supprimer que les évaluations de leur entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Suppression évaluation 1 (même entreprise)
        url = reverse('employes:evaluation_delete', args=[self.evaluation1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative suppression évaluation 2 (autre entreprise)
        url = reverse('employes:evaluation_delete', args=[self.evaluation2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_sanction_list_isolation(self):
        """Test que les utilisateurs ne voient que les sanctions de leur entreprise"""
        # Connexion avec user2
        self.client.force_login(self.user2)
        
        # Accès aux sanctions de l'employé 2 (même entreprise)
        url = reverse('employes:sanction_list', args=[self.employe2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.employe2.nom)
        # Vérifier que la date des faits est affichée (le motif n'est pas dans la liste)
        self.assertContains(response, '12/01/2024')
        
        # Tentative d'accès aux sanctions de l'employé 1 (autre entreprise)
        url = reverse('employes:sanction_list', args=[self.employe1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_sanction_detail_isolation(self):
        """Test que les utilisateurs ne peuvent voir que les détails des sanctions de leur entreprise"""
        # Connexion avec user2
        self.client.force_login(self.user2)
        
        # Accès à la sanction 2 (même entreprise)
        url = reverse('employes:sanction_detail', args=[self.sanction2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative d'accès à la sanction 1 (autre entreprise)
        url = reverse('employes:sanction_detail', args=[self.sanction1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_sanction_create_isolation(self):
        """Test que les utilisateurs ne peuvent créer des sanctions que pour leur entreprise"""
        # Connexion avec user2
        self.client.force_login(self.user2)
        
        # Création de sanction pour employé 2 (même entreprise)
        url = reverse('employes:sanction_create', args=[self.employe2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative de création pour employé 1 (autre entreprise)
        url = reverse('employes:sanction_create', args=[self.employe1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_sanction_update_isolation(self):
        """Test que les utilisateurs ne peuvent modifier que les sanctions de leur entreprise"""
        # Connexion avec user2
        self.client.force_login(self.user2)
        
        # Modification sanction 2 (même entreprise)
        url = reverse('employes:sanction_detail', args=[self.sanction2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative modification sanction 1 (autre entreprise)
        url = reverse('employes:sanction_detail', args=[self.sanction1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_sanction_delete_isolation(self):
        """Test que les utilisateurs ne peuvent supprimer que les sanctions de leur entreprise"""
        # Connexion avec user2
        self.client.force_login(self.user2)
        
        # Suppression sanction 2 (même entreprise)
        url = reverse('employes:sanction_delete', args=[self.sanction2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Tentative suppression sanction 1 (autre entreprise)
        url = reverse('employes:sanction_delete', args=[self.sanction1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_cross_reference_protection(self):
        """Test que les évaluateurs ne peuvent être que de la même entreprise"""
        # Connexion avec user1
        self.client.force_login(self.user1)
        
        # Tentative de création d'évaluation avec évaluateur d'une autre entreprise
        url = reverse('employes:evaluation_create', args=[self.employe1.id])
        data = {
            'annee_evaluation': 2024,
            'periode': 'annuelle',
            'date_evaluation': '2024-02-01',
            'evaluateur': self.employe2.id,  # Employé d'une autre entreprise
            'note_globale': 75
        }
        response = self.client.post(url, data)
        
        # Vérifier que l'évaluateur invalide n'est pas dans les choix du formulaire
        form = response.context.get('form')
        if form:
            evaluateur_choices = [choice[0] for choice in form.fields['evaluateur'].choices]
            self.assertNotIn(self.employe2.id, evaluateur_choices)
