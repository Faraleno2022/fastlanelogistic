"""
Service de calcul TVA
"""
from decimal import Decimal
from django.contrib.auth.models import User

from comptabilite.models import RegimeTVA, TauxTVA
from .base_service import BaseComptaService


class CalculTVAService(BaseComptaService):
    """
    Service de calcul TVA
    - Calcul montant TTC à partir HT
    - Calcul montant HT à partir TTC
    - Calcul TVA
    - Application taux spécifiques
    """
    
    def __init__(self, utilisateur: User):
        super().__init__(utilisateur)
        self.service_name = 'CalculTVAService'
    
    def calculer_tva(self, montant_ht: Decimal, taux: Decimal) -> Decimal:
        """
        Calcule le montant TVA
        
        Args:
            montant_ht: Montant HT
            taux: Taux TVA en pourcentage (ex: 20.00 pour 20%)
        
        Returns:
            Montant TVA
        """
        try:
            montant_ht = Decimal(str(montant_ht))
            taux = Decimal(str(taux))
            
            conditions = {
                'montant_ht_positif': montant_ht >= 0,
                'taux_valide': 0 <= taux <= 100
            }
            
            self.valider(conditions)
            
            if self.erreurs:
                return Decimal('0.00')
            
            montant_tva = montant_ht * (taux / 100)
            return montant_tva.quantize(Decimal('0.01'))
            
        except Exception as e:
            self.avertissement(f"Erreur calcul TVA: {str(e)}")
            return Decimal('0.00')
    
    def calculer_ttc(self, montant_ht: Decimal, taux: Decimal) -> Decimal:
        """
        Calcule le montant TTC à partir du HT
        
        Args:
            montant_ht: Montant HT
            taux: Taux TVA en pourcentage
        
        Returns:
            Montant TTC
        """
        try:
            montant_ht = Decimal(str(montant_ht))
            montant_tva = self.calculer_tva(montant_ht, taux)
            montant_ttc = montant_ht + montant_tva
            return montant_ttc.quantize(Decimal('0.01'))
            
        except Exception as e:
            self.avertissement(f"Erreur calcul TTC: {str(e)}")
            return Decimal('0.00')
    
    def calculer_ht(self, montant_ttc: Decimal, taux: Decimal) -> Decimal:
        """
        Calcule le montant HT à partir du TTC
        
        Args:
            montant_ttc: Montant TTC
            taux: Taux TVA en pourcentage
        
        Returns:
            Montant HT
        """
        try:
            montant_ttc = Decimal(str(montant_ttc))
            taux = Decimal(str(taux))
            
            conditions = {
                'montant_ttc_positif': montant_ttc >= 0,
                'taux_valide': 0 <= taux < 100
            }
            
            self.valider(conditions)
            
            if self.erreurs:
                return Decimal('0.00')
            
            # HT = TTC / (1 + taux/100)
            montant_ht = montant_ttc / (1 + (taux / 100))
            return montant_ht.quantize(Decimal('0.01'))
            
        except Exception as e:
            self.avertissement(f"Erreur calcul HT: {str(e)}")
            return Decimal('0.00')
    
    def appliquer_taux(self, montant_ht: Decimal, taux_tva: TauxTVA) -> dict:
        """
        Applique un taux TVA complet
        
        Args:
            montant_ht: Montant HT
            taux_tva: Objet TauxTVA
        
        Returns:
            dict avec montant_ht, montant_tva, montant_ttc
        """
        try:
            montant_ht = Decimal(str(montant_ht))
            
            conditions = {
                'montant_positif': montant_ht >= 0,
                'taux_exists': bool(taux_tva),
                'taux_actif': taux_tva.actif if taux_tva else False
            }
            
            self.valider(conditions)
            
            if self.erreurs:
                return {
                    'montant_ht': Decimal('0.00'),
                    'montant_tva': Decimal('0.00'),
                    'montant_ttc': Decimal('0.00'),
                    'taux': Decimal('0.00')
                }
            
            montant_tva = self.calculer_tva(montant_ht, taux_tva.taux)
            montant_ttc = montant_ht + montant_tva
            
            return {
                'montant_ht': montant_ht,
                'montant_tva': montant_tva,
                'montant_ttc': montant_ttc,
                'taux': taux_tva.taux,
                'taux_nom': taux_tva.nom
            }
            
        except Exception as e:
            self.avertissement(f"Erreur application taux: {str(e)}")
            return {}
    
    def calculer_tva_depuis_regime(self, montant_ht: Decimal, regime_tva: RegimeTVA,
                                   type_taux: str = 'NORMAL') -> dict:
        """
        Calcule TVA en utilisant les taux du régime
        
        Args:
            montant_ht: Montant HT
            regime_tva: Le régime TVA
            type_taux: Type de taux (NORMAL, REDUIT, SUPER_REDUIT)
        
        Returns:
            dict avec les montants calculés
        """
        try:
            taux = regime_tva.get_taux_applicable(type_taux)
            return self.appliquer_taux(montant_ht, taux)
            
        except Exception as e:
            self.avertissement(f"Erreur calcul depuis régime: {str(e)}")
            return {}
    
    def obtenir_taux_effectif(self, montant_ht: Decimal, montant_tva: Decimal) -> Decimal:
        """
        Calcule le taux effectif TVA
        
        Args:
            montant_ht: Montant HT
            montant_tva: Montant TVA
        
        Returns:
            Taux en pourcentage
        """
        try:
            montant_ht = Decimal(str(montant_ht))
            montant_tva = Decimal(str(montant_tva))
            
            if montant_ht == 0:
                return Decimal('0.00')
            
            taux = (montant_tva / montant_ht) * 100
            return taux.quantize(Decimal('0.01'))
            
        except Exception as e:
            self.avertissement(f"Erreur taux effectif: {str(e)}")
            return Decimal('0.00')
