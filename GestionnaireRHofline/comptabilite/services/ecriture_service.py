"""Service pour la gestion des écritures comptables."""

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

from .base_service import BaseComptaService
from ..models import EcritureComptable, LigneEcriture

logger = logging.getLogger(__name__)


class EcritureService(BaseComptaService):
    """Service métier pour les écritures comptables."""
    
    def valider_ecriture(self, ecriture):
        """
        Valide qu'une écriture est équilibrée.
        
        Args:
            ecriture: Instance de EcritureComptable
        
        Raises:
            ValidationError si déséquilibrée
        """
        if not ecriture.est_equilibree:
            raise ValidationError(
                f"Écriture {ecriture.numero_ecriture} non équilibrée: "
                f"Débit={ecriture.total_debit} vs Crédit={ecriture.total_credit}"
            )
    
    @transaction.atomic
    def valider_ecriture_comptable(self, ecriture):
        """
        Valide et enregistre une écriture comptable.
        
        Args:
            ecriture: Instance de EcritureComptable
        """
        # Valide l'équilibre
        self.valider_ecriture(ecriture)
        
        # Valide que l'exercice est ouvert
        self.valider_exercice(ecriture.exercice)
        
        # Marque comme validée
        ecriture.est_validee = True
        ecriture.validee_par = self.utilisateur
        from django.utils import timezone
        ecriture.date_validation = timezone.now()
        ecriture.save()
        
        self.enregistrer_audit(
            'validation', 'Écritures comptables', 'EcritureComptable',
            ecriture.id
        )
        
        logger.info(f"Écriture validée: {ecriture.numero_ecriture}")
