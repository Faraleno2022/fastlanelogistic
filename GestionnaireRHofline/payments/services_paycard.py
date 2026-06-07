"""
Service Paycard pour l'intégration des paiements en Guinée
API: https://mapaycard.com/epay/
Méthodes: Orange Money, MTN MoMo, Carte bancaire, Paycard
"""
import logging
import uuid
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class PaycardService:
    """Service pour gérer les paiements via Paycard (Guinée)"""

    BASE_URL = "https://mapaycard.com"

    # Mapping méthodes de paiement → paramètre Paycard
    JUMP_MAP = {
        'PAYCARD':      'paycard-jump-to-paycard',
        'CREDIT_CARD':  'paycard-jump-to-cc',
        'ORANGE_MONEY': 'paycard-jump-to-om',
        'MOMO':         'paycard-jump-to-momo',
    }

    def __init__(self):
        self.api_key = getattr(settings, 'PAYCARD_API_KEY', '')
        self.is_configured = bool(self.api_key)

    def creer_paiement(self, transaction, callback_url, payment_method=None):
        """
        Crée un paiement Paycard et retourne l'URL de redirection.

        Paramètres
        ----------
        transaction : Transaction
            Objet Transaction Django (doit avoir .reference, .montant, .plan, .entreprise)
        callback_url : str
            URL GET appelée par Paycard après le paiement
        payment_method : str | None
            'ORANGE_MONEY', 'MOMO', 'CREDIT_CARD', 'PAYCARD' ou None (page choix)

        Retourne
        --------
        dict avec 'success', 'url' (+ 'error' si échec)
        """
        if not self.is_configured:
            return self._simuler_paiement(transaction)

        try:
            payload = {
                'c': self.api_key,
                'paycard-amount': int(transaction.montant),
                'paycard-description': (
                    f"Abonnement {transaction.plan.nom} - "
                    f"{transaction.entreprise.nom_entreprise}"
                )[:200],
                'paycard-operation-reference': transaction.reference,
                'paycard-callback-url': callback_url,
                'paycard-auto-redirect': 'on',
                'paycard-redirect-with-get': 'on',
            }

            # Diriger vers la méthode de paiement choisie
            if payment_method and payment_method in self.JUMP_MAP:
                payload[self.JUMP_MAP[payment_method]] = 'on'

            response = requests.post(
                f"{self.BASE_URL}/epay/create",
                data=payload,
                timeout=30,
            )
            data = response.json()

            if data.get('code') == 0:
                payment_url = data.get('payment_url', '')
                token = data.get('token', '')

                transaction.token_paydunya = token or transaction.reference
                transaction.save(update_fields=['token_paydunya'])

                return {
                    'success': True,
                    'url': payment_url,
                    'token': token,
                }
            else:
                error_msg = data.get('error_message', 'Erreur Paycard inconnue')
                logger.error(f"Erreur Paycard: {data}")
                return {
                    'success': False,
                    'error': error_msg,
                }

        except requests.exceptions.RequestException as e:
            logger.exception(f"Erreur réseau Paycard: {e}")
            return {
                'success': False,
                'error': f"Erreur de connexion Paycard: {e}",
            }
        except Exception as e:
            logger.exception(f"Exception Paycard: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def verifier_paiement(self, reference):
        """
        Vérifie le statut d'un paiement via sa référence.

        GET https://mapaycard.com/epay/{api_key}/{reference}/status

        Retourne
        --------
        dict avec 'success', 'status' ('success'|'failed'|'pending'), + 'raw_data'
        """
        if not self.is_configured:
            return self._simuler_verification()

        try:
            response = requests.get(
                f"{self.BASE_URL}/epay/{self.api_key}/{reference}/status",
                timeout=30,
            )
            data = response.json()

            if data.get('code') == 0:
                status = data.get('status', 'pending')
                # Mapper les statuts Paycard → nos statuts internes
                status_map = {
                    'success':   'completed',
                    'failed':    'failed',
                    'pending':   'pending',
                    'cancelled': 'cancelled',
                }
                return {
                    'success': True,
                    'status': status_map.get(status, 'pending'),
                    'payment_method': data.get('payment_method', ''),
                    'amount': data.get('amount', 0),
                    'raw_data': data,
                }
            else:
                error_msg = data.get('error_message', 'Erreur vérification')
                return {
                    'success': False,
                    'status': 'unknown',
                    'error': error_msg,
                }

        except Exception as e:
            logger.exception(f"Exception vérification Paycard: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    # -- Mode simulation (dev/test sans clé API) ----------------------------

    def _simuler_paiement(self, transaction):
        """Simulation locale quand PAYCARD_API_KEY n'est pas configurée."""
        fake_token = f"paycard_test_{uuid.uuid4().hex[:16]}"
        transaction.token_paydunya = fake_token
        transaction.save(update_fields=['token_paydunya'])

        return {
            'success': True,
            'url': f"/payments/simulate/{fake_token}/",
            'token': fake_token,
            'simulation': True,
        }

    def _simuler_verification(self):
        """Simulation de vérification pour les tests."""
        return {
            'success': True,
            'status': 'completed',
            'simulation': True,
        }
