"""
Script to create a superuser for the GestionnaireRH application
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
django.setup()

from core.models import Utilisateur, ProfilUtilisateur

# Create admin profile if it doesn't exist
profil, created = ProfilUtilisateur.objects.get_or_create(
    nom_profil='Administrateur',
    defaults={
        'description': 'Profil administrateur avec tous les droits',
        'niveau_acces': 5,
        'actif': True
    }
)

if created:
    print("✓ Profil Administrateur créé")
else:
    print("✓ Profil Administrateur existe déjà")

# Create superuser
username = 'LENO'
email = 'leno@example.com'
password = '1994'

if Utilisateur.objects.filter(username=username).exists():
    print(f"✗ L'utilisateur '{username}' existe déjà")
    user = Utilisateur.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"✓ Mot de passe mis à jour pour '{username}'")
else:
    user = Utilisateur.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        profil=profil
    )
    print(f"✓ Superutilisateur '{username}' créé avec succès")

print(f"\nVous pouvez maintenant vous connecter avec:")
print(f"  Nom d'utilisateur: {username}")
print(f"  Mot de passe: {password}")
