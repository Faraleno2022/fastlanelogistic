#!/usr/bin/env python
"""
Script pour générer les clés de sécurité nécessaires
"""
import secrets
from django.core.management.utils import get_random_secret_key
from cryptography.fernet import Fernet


def generate_django_secret_key():
    """Génère une SECRET_KEY Django"""
    return get_random_secret_key()


def generate_encryption_key():
    """Génère une clé de chiffrement Fernet"""
    return Fernet.generate_key().decode()


def generate_random_password(length=16):
    """Génère un mot de passe aléatoire sécurisé"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def main():
    print("=" * 80)
    print("GÉNÉRATEUR DE CLÉS DE SÉCURITÉ - Gestionnaire RH Guinée")
    print("=" * 80)
    print()
    
    print("1. SECRET_KEY Django:")
    print("-" * 80)
    secret_key = generate_django_secret_key()
    print(f"SECRET_KEY={secret_key}")
    print()
    
    print("2. Clé de Chiffrement (ENCRYPTION_KEY):")
    print("-" * 80)
    encryption_key = generate_encryption_key()
    print(f"ENCRYPTION_KEY={encryption_key}")
    print()
    
    print("3. Mot de passe aléatoire sécurisé (16 caractères):")
    print("-" * 80)
    password = generate_random_password(16)
    print(f"PASSWORD={password}")
    print()
    
    print("4. Mot de passe aléatoire sécurisé (32 caractères):")
    print("-" * 80)
    password_long = generate_random_password(32)
    print(f"PASSWORD={password_long}")
    print()
    
    print("=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print("1. Copiez ces valeurs dans votre fichier .env")
    print("2. Ne partagez JAMAIS ces clés")
    print("3. Utilisez des clés différentes pour chaque environnement")
    print("4. Sauvegardez ces clés dans un gestionnaire de mots de passe")
    print("=" * 80)
    print()
    
    # Créer un fichier .env si demandé
    create_env = input("Voulez-vous créer/mettre à jour le fichier .env ? (o/n): ")
    
    if create_env.lower() == 'o':
        try:
            # Lire le fichier .env.example
            with open('.env.example', 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            # Remplacer les valeurs
            env_content = env_content.replace(
                'SECRET_KEY=your-secret-key-here-change-in-production',
                f'SECRET_KEY={secret_key}'
            )
            env_content = env_content.replace(
                'ENCRYPTION_KEY=',
                f'ENCRYPTION_KEY={encryption_key}'
            )
            
            # Écrire dans .env
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print("✅ Fichier .env créé avec succès!")
            print("⚠️  N'oubliez pas de configurer les autres variables (DB, Email, etc.)")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier .env: {e}")
    
    print()
    print("Terminé!")


if __name__ == '__main__':
    main()
