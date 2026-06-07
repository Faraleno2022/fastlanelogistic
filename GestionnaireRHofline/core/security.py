"""
Utilitaires de sécurité pour l'application
"""
import bleach
import hashlib
import secrets
from django.core.exceptions import ValidationError
from django.utils.html import escape
from cryptography.fernet import Fernet
from django.conf import settings
import re


class DataSanitizer:
    """
    Classe pour nettoyer et valider les données utilisateur
    """
    
    # Tags HTML autorisés
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def sanitize_html(text):
        """
        Nettoie le HTML en ne gardant que les tags autorisés
        """
        if not text:
            return text
        return bleach.clean(
            text,
            tags=DataSanitizer.ALLOWED_TAGS,
            attributes=DataSanitizer.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def sanitize_input(text):
        """
        Échappe tous les caractères HTML dangereux
        """
        if not text:
            return text
        return escape(str(text))
    
    @staticmethod
    def validate_no_script(text):
        """
        Valide qu'il n'y a pas de script dans le texte
        """
        if not text:
            return True
        
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'onclick=',
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower):
                raise ValidationError("Contenu non autorisé détecté")
        
        return True
    
    @staticmethod
    def sanitize_filename(filename):
        """
        Nettoie un nom de fichier pour éviter les attaques de traversée de répertoire
        """
        if not filename:
            return filename
        
        # Supprimer les caractères dangereux
        filename = re.sub(r'[^\w\s\.-]', '', filename)
        # Supprimer les .. pour éviter la traversée de répertoire
        filename = filename.replace('..', '')
        # Limiter la longueur
        filename = filename[:255]
        
        return filename
    
    @staticmethod
    def validate_email(email):
        """
        Valide le format d'un email
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Format d'email invalide")
        return True
    
    @staticmethod
    def validate_phone(phone):
        """
        Valide le format d'un numéro de téléphone guinéen
        """
        # Format: +224 XXX XX XX XX ou 6XX XX XX XX
        pattern = r'^(\+224|00224)?[6-7]\d{8}$'
        clean_phone = re.sub(r'[\s\-\.]', '', phone)
        if not re.match(pattern, clean_phone):
            raise ValidationError("Format de téléphone invalide")
        return True


class DataEncryption:
    """
    Classe pour chiffrer et déchiffrer les données sensibles
    """
    
    @staticmethod
    def get_encryption_key():
        """
        Récupère ou génère une clé de chiffrement
        """
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # Générer une nouvelle clé si elle n'existe pas
            key = Fernet.generate_key()
        elif isinstance(key, str):
            key = key.encode()
        return key
    
    @staticmethod
    def encrypt_data(data):
        """
        Chiffre des données sensibles
        """
        if not data:
            return data
        
        try:
            key = DataEncryption.get_encryption_key()
            f = Fernet(key)
            
            if isinstance(data, str):
                data = data.encode()
            
            encrypted = f.encrypt(data)
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Erreur lors du chiffrement: {str(e)}")
    
    @staticmethod
    def decrypt_data(encrypted_data):
        """
        Déchiffre des données
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            key = DataEncryption.get_encryption_key()
            f = Fernet(key)
            
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            
            decrypted = f.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Erreur lors du déchiffrement: {str(e)}")
    
    @staticmethod
    def hash_sensitive_data(data):
        """
        Hash des données sensibles (non réversible)
        """
        if not data:
            return data
        
        if isinstance(data, str):
            data = data.encode()
        
        return hashlib.sha256(data).hexdigest()


class TokenGenerator:
    """
    Générateur de tokens sécurisés
    """
    
    @staticmethod
    def generate_token(length=32):
        """
        Génère un token aléatoire sécurisé
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_numeric_code(length=6):
        """
        Génère un code numérique aléatoire
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


class PasswordValidator:
    """
    Validateur de mot de passe personnalisé
    """
    
    @staticmethod
    def validate_password_strength(password):
        """
        Valide la force d'un mot de passe
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        
        if not re.search(r'[a-z]', password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")
        
        if not re.search(r'\d', password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        if errors:
            raise ValidationError(errors)
        
        return True


class FileValidator:
    """
    Validateur de fichiers uploadés
    """
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {
        'images': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'documents': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'],
        'all': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt']
    }
    
    # Taille maximale en bytes (5MB par défaut)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    @staticmethod
    def validate_file_extension(filename, file_type='all'):
        """
        Valide l'extension d'un fichier
        """
        allowed = FileValidator.ALLOWED_EXTENSIONS.get(file_type, [])
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if extension not in allowed:
            raise ValidationError(
                f"Extension de fichier non autorisée. Extensions autorisées: {', '.join(allowed)}"
            )
        
        return True
    
    @staticmethod
    def validate_file_size(file_size, max_size=None):
        """
        Valide la taille d'un fichier
        """
        max_size = max_size or FileValidator.MAX_FILE_SIZE
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise ValidationError(
                f"Fichier trop volumineux. Taille maximale: {max_mb}MB"
            )
        
        return True
    
    @staticmethod
    def validate_uploaded_file(uploaded_file, file_type='all', max_size=None):
        """
        Valide un fichier uploadé (extension et taille)
        """
        FileValidator.validate_file_extension(uploaded_file.name, file_type)
        FileValidator.validate_file_size(uploaded_file.size, max_size)
        
        return True


class IPValidator:
    """
    Validateur d'adresses IP
    """
    
    @staticmethod
    def is_valid_ipv4(ip):
        """
        Valide une adresse IPv4
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def is_private_ip(ip):
        """
        Vérifie si une IP est privée
        """
        if not IPValidator.is_valid_ipv4(ip):
            return False
        
        parts = [int(x) for x in ip.split('.')]
        
        # 10.0.0.0/8
        if parts[0] == 10:
            return True
        
        # 172.16.0.0/12
        if parts[0] == 172 and 16 <= parts[1] <= 31:
            return True
        
        # 192.168.0.0/16
        if parts[0] == 192 and parts[1] == 168:
            return True
        
        return False
