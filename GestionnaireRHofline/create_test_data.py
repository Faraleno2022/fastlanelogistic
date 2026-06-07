"""
Script pour créer des données de test pour le système multi-entreprise
Usage: python manage.py shell < create_test_data.py
"""

from django.utils.text import slugify
from core.models import Entreprise, Utilisateur, ProfilUtilisateur

print("=" * 60)
print("CRÉATION DES DONNÉES DE TEST")
print("=" * 60)

# Créer les profils s'ils n'existent pas
profils_data = [
    {'nom_profil': 'Consultation', 'niveau_acces': 1, 'description': 'Accès en lecture seule'},
    {'nom_profil': 'Opérateur', 'niveau_acces': 2, 'description': 'Opérations courantes'},
    {'nom_profil': 'Manager', 'niveau_acces': 3, 'description': 'Gestion d\'équipe'},
    {'nom_profil': 'RH', 'niveau_acces': 4, 'description': 'Ressources Humaines'},
    {'nom_profil': 'Administrateur Entreprise', 'niveau_acces': 5, 'description': 'Administration complète'},
]

print("\n1. Création des profils utilisateurs...")
for profil_data in profils_data:
    profil, created = ProfilUtilisateur.objects.get_or_create(
        nom_profil=profil_data['nom_profil'],
        defaults={
            'niveau_acces': profil_data['niveau_acces'],
            'description': profil_data['description'],
            'actif': True
        }
    )
    if created:
        print(f"   ✓ Profil créé: {profil.nom_profil}")
    else:
        print(f"   - Profil existant: {profil.nom_profil}")

# Créer des entreprises de test
entreprises_data = [
    {
        'nom_entreprise': 'Société Test SARL',
        'email': 'contact@test.gn',
        'telephone': '+224 622 00 00 01',
        'ville': 'Conakry',
        'plan_abonnement': 'gratuit',
        'max_utilisateurs': 5,
    },
    {
        'nom_entreprise': 'Entreprise Demo SA',
        'email': 'info@demo.gn',
        'telephone': '+224 622 00 00 02',
        'ville': 'Conakry',
        'plan_abonnement': 'premium',
        'max_utilisateurs': 20,
    },
]

print("\n2. Création des entreprises de test...")
profil_admin = ProfilUtilisateur.objects.get(nom_profil='Administrateur Entreprise')

for ent_data in entreprises_data:
    slug = slugify(ent_data['nom_entreprise'])
    
    entreprise, created = Entreprise.objects.get_or_create(
        slug=slug,
        defaults=ent_data
    )
    
    if created:
        print(f"   ✓ Entreprise créée: {entreprise.nom_entreprise}")
        
        # Créer l'administrateur
        admin_username = f"admin_{slug.replace('-', '_')}"
        admin, admin_created = Utilisateur.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': f"admin@{slug}.gn",
                'first_name': 'Admin',
                'last_name': entreprise.nom_entreprise,
                'entreprise': entreprise,
                'profil': profil_admin,
                'est_admin_entreprise': True,
                'actif': True,
            }
        )
        
        if admin_created:
            admin.set_password('admin123')
            admin.save()
            print(f"     → Admin créé: {admin_username} / admin123")
        
        # Créer quelques utilisateurs de test
        profil_rh = ProfilUtilisateur.objects.get(nom_profil='RH')
        profil_manager = ProfilUtilisateur.objects.get(nom_profil='Manager')
        
        users_data = [
            {
                'username': f'rh_{slug.replace("-", "_")}',
                'email': f'rh@{slug}.gn',
                'first_name': 'Responsable',
                'last_name': 'RH',
                'profil': profil_rh,
                'require_reauth': True,  # Activer la réauth pour RH
            },
            {
                'username': f'manager_{slug.replace("-", "_")}',
                'email': f'manager@{slug}.gn',
                'first_name': 'Chef',
                'last_name': 'Service',
                'profil': profil_manager,
                'require_reauth': False,
            },
        ]
        
        for user_data in users_data:
            user, user_created = Utilisateur.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'entreprise': entreprise,
                    'profil': user_data['profil'],
                    'require_reauth': user_data['require_reauth'],
                    'actif': True,
                }
            )
            
            if user_created:
                user.set_password('test123')
                user.save()
                reauth_status = "avec réauth" if user_data['require_reauth'] else "sans réauth"
                print(f"     → Utilisateur créé: {user_data['username']} / test123 ({reauth_status})")
    else:
        print(f"   - Entreprise existante: {entreprise.nom_entreprise}")

print("\n" + "=" * 60)
print("RÉSUMÉ DES COMPTES DE TEST")
print("=" * 60)
print("\nENTREPRISE 1: Société Test SARL")
print("  Admin: admin_societe_test_sarl / admin123")
print("  RH: rh_societe_test_sarl / test123 (AVEC réauthentification)")
print("  Manager: manager_societe_test_sarl / test123 (sans réauthentification)")
print("\nENTREPRISE 2: Entreprise Demo SA")
print("  Admin: admin_entreprise_demo_sa / admin123")
print("  RH: rh_entreprise_demo_sa / test123 (AVEC réauthentification)")
print("  Manager: manager_entreprise_demo_sa / test123 (sans réauthentification)")

print("\n" + "=" * 60)
print("INSTRUCTIONS DE TEST")
print("=" * 60)
print("""
1. TESTER LA CRÉATION D'ENTREPRISE:
   - Aller sur /register-entreprise/
   - Créer une nouvelle entreprise
   - Vérifier la connexion automatique

2. TESTER LA RÉAUTHENTIFICATION:
   - Se connecter avec: rh_societe_test_sarl / test123
   - Aller sur le module Paie
   - Vérifier la demande de réauthentification
   - Entrer le mot de passe: test123

3. TESTER LA GESTION DES UTILISATEURS:
   - Se connecter avec: admin_societe_test_sarl / admin123
   - Aller sur /manage-users/
   - Créer un nouvel utilisateur
   - Vérifier le quota d'utilisateurs

4. TESTER LE TABLEAU DE BORD ADMIN:
   - Se connecter en tant qu'admin
   - Aller sur /admin-dashboard/
   - Vérifier les statistiques

5. TESTER L'ISOLATION DES DONNÉES:
   - Se connecter avec un compte de l'entreprise 1
   - Vérifier qu'on ne voit que les données de l'entreprise 1
   - Se déconnecter et se connecter avec un compte de l'entreprise 2
   - Vérifier l'isolation

6. TESTER LE QUOTA:
   - Avec admin_societe_test_sarl (plan gratuit, 5 users max)
   - Créer des utilisateurs jusqu'à atteindre le quota
   - Vérifier le message d'erreur
""")

print("\n✅ Données de test créées avec succès!")
