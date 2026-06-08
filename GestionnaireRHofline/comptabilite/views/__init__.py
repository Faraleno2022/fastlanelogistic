"""
Views pour le module comptabilité.
Ce fichier importe et expose toutes les vues des sous-modules.
"""

# Importer les vues de rapprochements
from .rapprochements.views import (
    CompteBancaireListView,
    CompteBancaireDetailView,
    CompteBancaireCreateView,
    CompteBancaireUpdateView,
    CompteBancaireDeleteView,
    RapprochementListView,
    RapprochementDetailView,
    RapprochementCreateView,
    RapprochementUpdateView,
    RapprochementDeleteView,
    OperationImportView,
    LettrageView,
    LettrageAnnulationView,
    RapprochementFinalisationView,
)

# Importer les vues de fiscalité
try:
    from .fiscalite.tva_views import (
        RegimeTVAListView,
        RegimeTVACreateView,
        RegimeTVAUpdateView,
        RegimeTVADeleteView,
        TauxTVAListView,
        TauxTVACreateView,
        TauxTVAUpdateView,
        TauxTVADeleteView,
        DeclarationTVAListView,
        DeclarationTVACreateView,
        DeclarationTVAUpdateView,
        DeclarationTVADeleteView,
        LigneDeclarationTVAView,
        LigneDeclarationTVACreateView,
        LigneDeclarationTVAUpdateView,
        LigneDeclarationTVADeleteView,
    )
except ImportError:
    # Si les vues de fiscalité ne sont pas encore implémentées
    pass

# Importer les vues d'audit
try:
    from .audit.views import (
        AuditListView,
        AuditDetailView,
        AuditCreateView,
        AuditUpdateView,
        AuditDeleteView,
    )
except ImportError:
    # Si les vues d'audit ne sont pas encore implémentées
    pass

# Importer les vues de base
try:
    from .base.views import (
        DashboardView,
        PlanComptableListView,
        PlanComptableCreateView,
        PlanComptableUpdateView,
        PlanComptableDeleteView,
        JournalListView,
        JournalCreateView,
        JournalUpdateView,
        JournalDeleteView,
        EcritureListView,
        EcritureCreateView,
        EcritureUpdateView,
        EcritureDeleteView,
    )
except ImportError:
    # Si les vues de base ne sont pas encore implémentées
    pass

__all__ = [
    # Rapprochements
    'CompteBancaireListView',
    'CompteBancaireDetailView',
    'CompteBancaireCreateView',
    'CompteBancaireUpdateView',
    'CompteBancaireDeleteView',
    'RapprochementListView',
    'RapprochementDetailView',
    'RapprochementCreateView',
    'RapprochementUpdateView',
    'RapprochementDeleteView',
    'OperationImportView',
    'LettrageView',
    'LettrageAnnulationView',
    'RapprochementFinalisationView',
]
