"""
Service de gestion des devises et conversions
"""
from decimal import Decimal
from datetime import date
from django.db.models import Q
from core.models import Devise, TauxChange


class DeviseService:
    """Service pour la gestion multi-devises"""
    
    @staticmethod
    def get_devise_base():
        """Retourne la devise de base (GNF)"""
        return Devise.objects.filter(est_devise_base=True, actif=True).first()
    
    @staticmethod
    def get_taux_change(devise_source, devise_cible, date_taux=None):
        """
        Récupère le taux de change entre deux devises
        Si pas de taux à la date exacte, prend le plus récent
        """
        if date_taux is None:
            date_taux = date.today()
        
        # Chercher le taux exact ou le plus récent
        taux = TauxChange.objects.filter(
            devise_source=devise_source,
            devise_cible=devise_cible,
            date_taux__lte=date_taux
        ).order_by('-date_taux').first()
        
        if taux:
            return taux.taux
        
        # Essayer le taux inverse
        taux_inverse = TauxChange.objects.filter(
            devise_source=devise_cible,
            devise_cible=devise_source,
            date_taux__lte=date_taux
        ).order_by('-date_taux').first()
        
        if taux_inverse and taux_inverse.taux != 0:
            return Decimal('1') / taux_inverse.taux
        
        return None
    
    @staticmethod
    def convertir(montant, devise_source, devise_cible, date_taux=None):
        """
        Convertit un montant d'une devise à une autre
        """
        if devise_source == devise_cible:
            return montant
        
        taux = DeviseService.get_taux_change(devise_source, devise_cible, date_taux)
        
        if taux is None:
            raise ValueError(f"Aucun taux de change trouvé pour {devise_source.code} -> {devise_cible.code}")
        
        return Decimal(str(montant)) * taux
    
    @staticmethod
    def convertir_vers_gnf(montant, devise_source, date_taux=None):
        """Convertit un montant vers GNF"""
        devise_gnf = DeviseService.get_devise_base()
        if not devise_gnf:
            raise ValueError("Devise de base (GNF) non configurée")
        
        return DeviseService.convertir(montant, devise_source, devise_gnf, date_taux)
    
    @staticmethod
    def formater_montant(montant, devise):
        """Formate un montant avec le symbole de la devise"""
        if devise.code == 'GNF':
            return f"{montant:,.0f} {devise.symbole}"
        else:
            return f"{montant:,.2f} {devise.symbole}"
