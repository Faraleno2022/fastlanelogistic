"""
Système de gestion de licences pour Gestionnaire RH Guinée
"""
import uuid
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings


# Clé secrète HMAC obfusquée (seul le développeur la connaît)
# NE JAMAIS PARTAGER CE FICHIER SOURCE
def _get_hmac_key():
    """Récupère la clé HMAC de manière obfusquée"""
    _p = [71, 82, 72, 45, 71, 117, 105, 110, 101, 101, 45, 50, 48, 50, 53,
          45, 83, 101, 99, 114, 101, 116, 75, 101, 121, 45, 70, 97, 114, 97,
          108, 101, 110, 111]
    return bytes(_p).decode('utf-8')


class Licence(models.Model):
    """Modèle pour gérer les licences du logiciel"""
    
    TYPE_CHOICES = [
        ('trial', 'Essai (30 jours)'),
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('perpetuel', 'Perpétuel'),
    ]
    
    PLAN_CHOICES = [
        ('starter', 'Starter - 10 employés max'),
        ('pro', 'Professionnel - 50 employés max'),
        ('enterprise', 'Entreprise - Illimité'),
    ]
    
    # Clé de licence unique
    cle_licence = models.CharField(max_length=50, unique=True, editable=False)
    
    # Informations client
    nom_entreprise = models.CharField(max_length=200)
    email_contact = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    
    # Type et plan
    type_licence = models.CharField(max_length=20, choices=TYPE_CHOICES, default='trial')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    
    # Limites selon le plan
    max_employes = models.IntegerField(default=10)
    max_utilisateurs = models.IntegerField(default=2)
    
    # Dates
    date_activation = models.DateTimeField(null=True, blank=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Statut
    est_active = models.BooleanField(default=False)
    est_bloquee = models.BooleanField(default=False)
    raison_blocage = models.TextField(blank=True)
    
    # Identifiant machine (pour lier à un PC)
    machine_id = models.CharField(max_length=100, blank=True)
    
    # Métadonnées
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Licence"
        verbose_name_plural = "Licences"
    
    def __str__(self):
        return f"{self.cle_licence} - {self.nom_entreprise}"
    
    def save(self, *args, **kwargs):
        if not self.cle_licence:
            self.cle_licence = self.generer_cle()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generer_cle():
        """Génère une clé de licence unique au format XXXX-XXXX-XXXX-XXXX"""
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Sans I, O, 0, 1 pour éviter confusion
        segments = []
        for _ in range(4):
            segment = ''.join(secrets.choice(chars) for _ in range(4))
            segments.append(segment)
        return '-'.join(segments)
    
    @property
    def est_valide(self):
        """Vérifie si la licence est valide"""
        if self.est_bloquee:
            return False
        if not self.est_active:
            return False
        if self.date_expiration and timezone.now() > self.date_expiration:
            return False
        return True
    
    @property
    def jours_restants(self):
        """Retourne le nombre de jours restants"""
        if not self.date_expiration:
            return None  # Licence perpétuelle
        delta = self.date_expiration - timezone.now()
        return max(0, delta.days)
    
    def activer(self, machine_id=None):
        """Active la licence"""
        self.est_active = True
        self.date_activation = timezone.now()
        
        if machine_id:
            self.machine_id = machine_id
        
        # Définir la date d'expiration selon le type
        if self.type_licence == 'trial':
            self.date_expiration = timezone.now() + timedelta(days=30)
        elif self.type_licence == 'mensuel':
            self.date_expiration = timezone.now() + timedelta(days=30)
        elif self.type_licence == 'annuel':
            self.date_expiration = timezone.now() + timedelta(days=365)
        # perpetuel = pas de date d'expiration
        
        self.save()
    
    def renouveler(self, duree_jours):
        """Renouvelle la licence"""
        if self.date_expiration and self.date_expiration > timezone.now():
            # Ajouter à partir de la date d'expiration actuelle
            self.date_expiration = self.date_expiration + timedelta(days=duree_jours)
        else:
            # Ajouter à partir de maintenant
            self.date_expiration = timezone.now() + timedelta(days=duree_jours)
        self.save()


class LicenceLocale(models.Model):
    """
    Stocke la licence activée localement sur cette installation
    Une seule entrée possible
    """
    cle_licence = models.CharField(max_length=50)
    nom_entreprise = models.CharField(max_length=200)
    plan = models.CharField(max_length=20)
    max_employes = models.IntegerField(default=10)
    max_utilisateurs = models.IntegerField(default=2)
    date_activation = models.DateTimeField()
    date_expiration = models.DateTimeField(null=True, blank=True)
    machine_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=64)  # Hash de vérification
    
    class Meta:
        verbose_name = "Licence locale"
        verbose_name_plural = "Licences locales"
    
    def __str__(self):
        return f"Licence: {self.cle_licence}"
    
    @property
    def est_valide(self):
        """Vérifie si la licence locale est valide"""
        # Vérifier la signature
        if not self.verifier_signature():
            return False
        
        # Vérifier l'expiration
        if self.date_expiration and timezone.now() > self.date_expiration:
            return False
        
        # Vérifier le machine_id
        if self.machine_id != get_machine_id():
            return False
        
        return True
    
    @property
    def jours_restants(self):
        """Retourne le nombre de jours restants"""
        if not self.date_expiration:
            return 9999  # Licence perpétuelle
        delta = self.date_expiration - timezone.now()
        return max(0, delta.days)
    
    def generer_signature(self):
        """Génère une signature de vérification"""
        secret = getattr(settings, 'SECRET_KEY', 'default-secret')
        data = f"{self.cle_licence}{self.machine_id}{self.date_activation}{secret}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verifier_signature(self):
        """Vérifie que la signature est valide"""
        return self.signature == self.generer_signature()
    
    def save(self, *args, **kwargs):
        # Générer la signature avant de sauvegarder
        self.signature = self.generer_signature()
        super().save(*args, **kwargs)


def get_machine_id():
    """
    Génère un identifiant unique pour cette machine
    Basé sur MAC address + hostname + infos matérielles
    """
    import platform
    import socket
    
    try:
        hostname = socket.gethostname()
        mac = uuid.getnode()  # Adresse MAC unique
        processor = platform.processor()
        system = platform.system()
        machine = platform.machine()
        
        # Combiner MAC + hostname + hardware
        data = f"{mac}{hostname}{processor}{system}{machine}"
        return hashlib.sha256(data.encode()).hexdigest()[:24]
    except:
        # Fallback sur MAC seule
        return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:24]


def valider_cle_hmac(cle_licence):
    """
    Vérifie qu'une clé de licence a été générée par le développeur
    via signature HMAC. Retourne True si la clé est authentique.
    
    Format clé: PPDD-XXXX-XXXX-HHHH
      PP = plan (ST/PR/EN)
      DD = durée (TR/ME/AN/PE)
      XXXX-XXXX = identifiant aléatoire
      HHHH = signature HMAC tronquée
    """
    try:
        parts = cle_licence.strip().upper().split('-')
        if len(parts) != 4:
            return False
        
        # Les 3 premiers segments = données, le 4ème = signature
        payload = f"{parts[0]}-{parts[1]}-{parts[2]}"
        signature_recue = parts[3]
        
        # Calculer la signature attendue
        key = _get_hmac_key().encode('utf-8')
        signature_calculee = hmac.new(key, payload.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
        
        # Convertir en caractères du jeu de licence (A-Z sans I,O + 2-9)
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        sig_finale = ''
        for c in signature_calculee:
            idx = int(c, 16) % len(chars)
            sig_finale += chars[idx]
        
        return hmac.compare_digest(signature_recue, sig_finale)
    except:
        return False


def get_licence_active():
    """Récupère la licence active ou None"""
    try:
        licence = LicenceLocale.objects.first()
        if licence and licence.est_valide:
            return licence
        return None
    except:
        return None
