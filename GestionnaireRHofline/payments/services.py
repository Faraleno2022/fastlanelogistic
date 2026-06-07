"""
Service CinetPay pour l'intégration des paiements
Documentation: https://cinetpay.com/developer/api
"""
import logging
import requests
import uuid
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class CinetPayService:
    """Service pour gérer les paiements via CinetPay"""
    
    # URLs API CinetPay
    API_BASE_URL = "https://api-checkout.cinetpay.com/v2"
    
    def __init__(self):
        self.api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        self.site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        self.secret_key = getattr(settings, 'CINETPAY_SECRET_KEY', '')
        self.mode = getattr(settings, 'CINETPAY_MODE', 'test')  # 'test' ou 'live'
        
        self.is_configured = bool(self.api_key and self.site_id)
    
    def creer_paiement(self, transaction, return_url, cancel_url, notify_url):
        """
        Crée un paiement CinetPay et retourne l'URL de paiement
        Documentation: https://cinetpay.com/developer/api#intPayment
        """
        if not self.is_configured:
            # Mode simulation pour les tests
            return self._simuler_paiement(transaction)
        
        try:
            # Générer un ID de transaction unique
            transaction_id = f"GRH-{transaction.reference}"
            
            # Données du paiement
            payload = {
                "apikey": self.api_key,
                "site_id": self.site_id,
                "transaction_id": transaction_id,
                "amount": int(transaction.montant),
                "currency": "GNF",
                "description": f"Abonnement {transaction.plan.nom} - {transaction.entreprise.nom_entreprise}",
                "return_url": return_url,
                "notify_url": notify_url,
                "cancel_url": cancel_url,
                "channels": "ALL",  # Orange Money, MTN, Visa, Mastercard
                "metadata": str(transaction.id),
                "customer_name": transaction.entreprise.nom_entreprise[:50],
                "customer_surname": transaction.cree_par.get_full_name()[:50] if transaction.cree_par else "Client",
                "customer_email": transaction.cree_par.email if transaction.cree_par else "",
                "customer_phone_number": "",
                "customer_address": "Guinée",
                "customer_city": "Conakry",
                "customer_country": "GN",
                "customer_state": "Conakry",
                "customer_zip_code": "00000",
            }
            
            # Appel API CinetPay
            response = requests.post(
                f"{self.API_BASE_URL}/payment",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            data = response.json()
            
            if data.get("code") == "201":
                # Succès - sauvegarder le token
                payment_token = data.get("data", {}).get("payment_token", "")
                payment_url = data.get("data", {}).get("payment_url", "")
                
                transaction.token_paydunya = payment_token  # Réutiliser le champ existant
                transaction.save(update_fields=['token_paydunya'])
                
                return {
                    'success': True,
                    'url': payment_url,
                    'token': payment_token,
                }
            else:
                error_msg = data.get("message", "Erreur lors de la création du paiement")
                logger.error(f"Erreur CinetPay: {data}")
                return {
                    'success': False,
                    'error': error_msg,
                }
                
        except requests.exceptions.RequestException as e:
            logger.exception(f"Erreur réseau CinetPay: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur de connexion: {str(e)}",
            }
        except Exception as e:
            logger.exception(f"Exception CinetPay: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def verifier_paiement(self, transaction_id, token=None):
        """
        Vérifie le statut d'un paiement via son ID
        Documentation: https://cinetpay.com/developer/api#checkPayment
        """
        if not self.is_configured:
            return self._simuler_verification(token)
        
        try:
            payload = {
                "apikey": self.api_key,
                "site_id": self.site_id,
                "transaction_id": transaction_id,
            }
            
            response = requests.post(
                f"{self.API_BASE_URL}/payment/check",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            data = response.json()
            
            if data.get("code") == "00":
                payment_data = data.get("data", {})
                status = payment_data.get("status", "")
                
                # Mapper les statuts CinetPay
                status_map = {
                    "ACCEPTED": "completed",
                    "REFUSED": "failed",
                    "PENDING": "pending",
                }
                
                return {
                    'success': True,
                    'status': status_map.get(status, "pending"),
                    'payment_method': payment_data.get("payment_method", ""),
                    'amount': payment_data.get("amount", 0),
                    'currency': payment_data.get("currency", "GNF"),
                    'raw_data': payment_data,
                }
            else:
                return {
                    'success': False,
                    'status': 'unknown',
                    'error': data.get("message", "Erreur de vérification"),
                }
                
        except Exception as e:
            logger.exception(f"Exception vérification CinetPay: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _simuler_paiement(self, transaction):
        """Mode simulation pour les tests sans CinetPay"""
        fake_token = f"test_{uuid.uuid4().hex[:16]}"
        transaction.token_paydunya = fake_token
        transaction.save(update_fields=['token_paydunya'])
        
        return {
            'success': True,
            'url': f"/payments/simulate/{fake_token}/",
            'token': fake_token,
            'simulation': True,
        }
    
    def _simuler_verification(self, token):
        """Simulation de vérification pour les tests"""
        return {
            'success': True,
            'status': 'completed',
            'simulation': True,
        }


# Alias pour compatibilité
PaymentService = CinetPayService


def activer_abonnement(transaction):
    """
    Active ou renouvelle l'abonnement après un paiement réussi
    """
    from .models import Abonnement
    
    entreprise = transaction.entreprise
    plan = transaction.plan
    duree_mois = transaction.duree_mois
    
    # Calculer les dates
    today = timezone.now().date()
    
    try:
        abonnement = Abonnement.objects.get(entreprise=entreprise)
        
        # Renouvellement - partir de la date de fin actuelle si encore valide
        if abonnement.date_fin and abonnement.date_fin > today:
            date_debut = abonnement.date_fin
        else:
            date_debut = today
            
        date_fin = date_debut + relativedelta(months=duree_mois)
        
        abonnement.plan = plan
        abonnement.date_fin = date_fin
        abonnement.statut = 'actif'
        abonnement.derniere_transaction = transaction
        abonnement.save()
        
    except Abonnement.DoesNotExist:
        # Nouvel abonnement
        date_debut = today
        date_fin = today + relativedelta(months=duree_mois)
        
        abonnement = Abonnement.objects.create(
            entreprise=entreprise,
            plan=plan,
            date_debut=date_debut,
            date_fin=date_fin,
            statut='actif',
            derniere_transaction=transaction
        )
    
    # Mettre à jour l'entreprise — synchroniser TOUTES les limites et modules du plan
    entreprise.plan_abonnement = plan.slug
    entreprise.date_expiration = date_fin
    entreprise.actif = True
    entreprise.sync_from_plan(plan)
    entreprise.save(update_fields=[
        'plan_abonnement', 'date_expiration', 'actif',
        'max_utilisateurs', 'max_employes',
        'module_paie', 'module_conges', 'module_recrutement', 'module_formation',
        'module_comptabilite', 'module_portail',
        'acces_declarations_fiscales', 'acces_export_comptable',
    ])
    
    # Mettre à jour la transaction
    transaction.statut = 'completed'
    transaction.date_paiement = timezone.now()
    transaction.date_expiration_abonnement = date_fin
    transaction.save()
    
    return abonnement
