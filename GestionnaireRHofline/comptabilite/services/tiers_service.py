"""Service pour la gestion des tiers (clients/fournisseurs)."""

from django.db import transaction
from django.core.exceptions import ValidationError
import logging

from .base_service import BaseComptaService
from ..models import Tiers

logger = logging.getLogger(__name__)


class TiersService(BaseComptaService):
    """Service métier pour les tiers."""
    
    def valider_solde_credit(self, tiers):
        """
        Valide que le solde client ne dépasse pas la limite de crédit.
        
        Args:
            tiers: Instance de Tiers
        
        Raises:
            ValidationError si dépassement
        """
        if tiers.solde > tiers.plafond_credit > 0:
            raise ValidationError(
                f"Solde {tiers.raison_sociale} ({tiers.solde}) "
                f"dépasse le plafond ({tiers.plafond_credit})"
            )
