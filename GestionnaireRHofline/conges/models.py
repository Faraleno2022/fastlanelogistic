"""
Module Congés - App Django distincte
Les modèles restent dans temps_travail pour éviter la migration de données,
mais cette app fournit une interface dédiée et des vues spécifiques.
"""
from temps_travail.models import Conge, SoldeConge
