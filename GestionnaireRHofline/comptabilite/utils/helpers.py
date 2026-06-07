"""
Utilitaires et helpers pour la comptabilité.

Fournissent:
- Formatage des montants
- Conversion de devises
- Calculs comptables
- Génération de numéros
"""

from decimal import Decimal, ROUND_HALF_UP
from django.utils.translation import gettext as _
from datetime import datetime, date
import hashlib
import uuid


class MontantFormatter:
    """Formate les montants décimaux."""
    
    @staticmethod
    def format_montant(montant, devise='EUR', decimales=2):
        """Formate un montant avec séparateurs."""
        if montant is None:
            return ''
        
        montant = Decimal(str(montant))
        format_str = f"{{:,.{decimales}f}}"
        value_str = format_str.format(montant)
        
        # Remplace les séparateurs selon la locale
        value_str = value_str.replace(',', '█')  # Placeholder
        value_str = value_str.replace('.', ',')   # Decimal separator
        value_str = value_str.replace('█', ' ')   # Thousands separator
        
        return f"{value_str} {devise}"
    
    @staticmethod
    def parse_montant(texte):
        """Parse un montant au format texte."""
        if not texte:
            return None
        
        # Nettoie
        texte = str(texte).strip()
        texte = texte.replace(' ', '')
        texte = texte.replace(',', '.')
        
        try:
            return Decimal(texte)
        except:
            raise ValueError(f"Format de montant invalide: {texte}")


class ComptesUtils:
    """Utilitaires pour les comptes."""
    
    @staticmethod
    def generer_numero_compte():
        """Génère un numéro de compte unique."""
        return str(uuid.uuid4()).replace('-', '')[:11]
    
    @staticmethod
    def valider_iban(iban):
        """Valide un numéro IBAN."""
        if not iban:
            return False
        
        iban = iban.replace(' ', '').upper()
        
        # Longueur
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Structure
        if not iban[2:4].isdigit():
            return False
        
        # Checksum (algorithme IBAN)
        rearranged = iban[4:] + iban[:4]
        numeric = ''
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)
        
        return int(numeric) % 97 == 1
    
    @staticmethod
    def valider_bic(bic):
        """Valide un code BIC."""
        if not bic:
            return False
        
        bic = bic.upper()
        
        # Longueur: 8 ou 11 caractères
        if len(bic) not in [8, 11]:
            return False
        
        # Format: 4 lettres, 2 lettres, 2 lettres, 3 caractères optionnels
        return all(c.isalnum() for c in bic)


class EcritureUtils:
    """Utilitaires pour les écritures comptables."""
    
    @staticmethod
    def generer_numero_ecriture(exercice):
        """Génère un numéro d'écriture unique."""
        from ..models import EcritureComptable
        
        compteur = EcritureComptable.objects.filter(
            exercice=exercice
        ).count() + 1
        
        return f"{exercice.code}-{compteur:05d}"
    
    @staticmethod
    def valider_equilibre(montant_debit, montant_credit, tolerance=Decimal('0.01')):
        """Valide l'équilibre débit/crédit."""
        if montant_debit is None:
            montant_debit = Decimal('0.00')
        if montant_credit is None:
            montant_credit = Decimal('0.00')
        
        diff = abs(Decimal(montant_debit) - Decimal(montant_credit))
        return diff <= tolerance
    
    @staticmethod
    def calculer_solde(montants_debit, montants_credit):
        """Calcule le solde (débit - crédit)."""
        debit = sum(Decimal(m) for m in montants_debit if m)
        credit = sum(Decimal(m) for m in montants_credit if m)
        return debit - credit


class RapprochementUtils:
    """Utilitaires pour les rapprochements."""
    
    @staticmethod
    def generer_numero_rapprochement(compte, date_rapprochement):
        """Génère un numéro de rapprochement."""
        date_str = date_rapprochement.strftime('%Y%m')
        return f"RAPP-{compte.id}-{date_str}"
    
    @staticmethod
    def calculer_tolerance_ecart(montant, pourcentage=0.5):
        """Calcule la tolérance d'écart autorisée."""
        return (Decimal(montant) * Decimal(pourcentage)) / Decimal(100)
    
    @staticmethod
    def detecter_doublons(operations):
        """Détecte les opérations en doublon."""
        doublons = []
        seen = set()
        
        for op in operations:
            # Signature = date + montant + libellé
            signature = (
                op.date.isoformat(),
                str(op.montant),
                op.libelle_operation[:20]
            )
            
            if signature in seen:
                doublons.append(op)
            else:
                seen.add(signature)
        
        return doublons


class DeviseUtils:
    """Utilitaires pour les devises."""
    
    # Taux de change fixes (à remplacer par une API)
    TAUX_CHANGE = {
        'EUR': Decimal('1.00'),
        'USD': Decimal('1.10'),
        'GBP': Decimal('0.86'),
        'CHF': Decimal('0.95'),
        'XOF': Decimal('655.957'),  # Franc CFA
    }
    
    @staticmethod
    def convertir(montant, devise_source, devise_cible):
        """Convertit un montant d'une devise à une autre."""
        if devise_source == devise_cible:
            return montant
        
        source_rate = DeviseUtils.TAUX_CHANGE.get(devise_source)
        cible_rate = DeviseUtils.TAUX_CHANGE.get(devise_cible)
        
        if not source_rate or not cible_rate:
            raise ValueError(f"Devise non supportée")
        
        montant = Decimal(montant)
        # Convertit en EUR, puis en devise cible
        montant_eur = montant / source_rate
        montant_cible = montant_eur * cible_rate
        
        return montant_cible.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ExerciceUtils:
    """Utilitaires pour les exercices comptables."""
    
    @staticmethod
    def generer_code_exercice(date_debut, date_fin):
        """Génère un code d'exercice."""
        debut = date_debut.year if isinstance(date_debut, date) else int(date_debut)
        fin = date_fin.year if isinstance(date_fin, date) else int(date_fin)
        return f"{debut}-{fin}"
    
    @staticmethod
    def est_date_valide_exercice(test_date, exercice):
        """Vérifie si une date appartient à l'exercice."""
        if isinstance(test_date, datetime):
            test_date = test_date.date()
        return exercice.date_debut <= test_date <= exercice.date_fin
    
    @staticmethod
    def jours_restants_exercice(exercice):
        """Calcule les jours restants avant fermeture."""
        today = date.today()
        if today > exercice.date_fin:
            return 0
        return (exercice.date_fin - today).days


class AuditUtils:
    """Utilitaires pour l'audit."""
    
    @staticmethod
    def generer_hash_donnees(donnees):
        """Génère un hash des données pour l'intégrité."""
        donnees_str = str(donnees).encode('utf-8')
        return hashlib.sha256(donnees_str).hexdigest()
    
    @staticmethod
    def comparer_donnees(avant, apres):
        """Compare deux versions de données."""
        changements = {}
        
        if isinstance(avant, dict) and isinstance(apres, dict):
            all_keys = set(avant.keys()) | set(apres.keys())
            for key in all_keys:
                val_avant = avant.get(key)
                val_apres = apres.get(key)
                if val_avant != val_apres:
                    changements[key] = {
                        'avant': val_avant,
                        'apres': val_apres
                    }
        
        return changements


class PageSize:
    """Tailles de pagination standards."""
    
    SMALL = 10
    NORMAL = 50
    LARGE = 100
    
    CHOICES = [
        (SMALL, f"{SMALL} par page"),
        (NORMAL, f"{NORMAL} par page"),
        (LARGE, f"{LARGE} par page"),
    ]
