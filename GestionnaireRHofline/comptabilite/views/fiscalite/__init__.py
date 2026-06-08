"""
Vues pour la gestion de la fiscalité (TVA, déclarations).

Fournissent:
- Gestion des régimes TVA
- Gestion des déclarations TVA
- Validation et dépôt des déclarations
- Historique et rapports
"""

from .tva_views import (
    RegimeTVAListView,
    RegimeTVADetailView,
    RegimeTVACreateView,
    RegimeTVAUpdateView,
    DeclarationTVAListView,
    DeclarationTVADetailView,
    DeclarationTVACreateView,
    DeclarationTVAUpdateView,
    DeclarationTVAValidateView,
    DeclarationTVADepotView,
    LigneDeclarationTVACreateView,
    LigneDeclarationTVAUpdateView,
    LigneDeclarationTVADeleteView,
    TauxTVAListView,
    TauxTVACreateView,
    TauxTVAUpdateView,
)

__all__ = [
    'RegimeTVAListView',
    'RegimeTVADetailView',
    'RegimeTVACreateView',
    'RegimeTVAUpdateView',
    'DeclarationTVAListView',
    'DeclarationTVADetailView',
    'DeclarationTVACreateView',
    'DeclarationTVAUpdateView',
    'DeclarationTVAValidateView',
    'DeclarationTVADepotView',
    'LigneDeclarationTVACreateView',
    'LigneDeclarationTVAUpdateView',
    'LigneDeclarationTVADeleteView',
    'TauxTVAListView',
    'TauxTVACreateView',
    'TauxTVAUpdateView',
]
