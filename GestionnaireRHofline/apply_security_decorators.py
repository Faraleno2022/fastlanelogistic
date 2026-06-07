"""
Script pour appliquer automatiquement les décorateurs de sécurité aux vues sensibles
"""

# Liste des fonctions de paie qui nécessitent @reauth_required
PAIE_SENSITIVE_FUNCTIONS = [
    'liste_periodes',
    'creer_periode',
    'detail_periode',
    'calculer_periode',
    'valider_periode',
    'cloturer_periode',
    'liste_bulletins',
    'detail_bulletin',
    'imprimer_bulletin',
    'livre_paie',
    'declarations_sociales',
    'liste_elements_salaire',
    'elements_salaire_employe',
    'ajouter_element_salaire',
    'modifier_element_salaire',
    'supprimer_element_salaire',
    'liste_rubriques',
    'creer_rubrique',
    'detail_rubrique',
]

# Liste des fonctions d'employés qui nécessitent @reauth_required
EMPLOYES_SENSITIVE_FUNCTIONS = [
    'detail_employe',
    'modifier_employe',
    'supprimer_employe',
    'documents_employe',
    'ajouter_document',
    'contrats_employe',
    'historique_employe',
]

# Instructions pour appliquer manuellement
MANUAL_INSTRUCTIONS = """
INSTRUCTIONS POUR APPLIQUER LES DÉCORATEURS DE SÉCURITÉ
========================================================

MODULE PAIE (paie/views.py)
---------------------------
Ajouter ces décorateurs aux fonctions suivantes:

@login_required
@entreprise_active_required
@reauth_required
def nom_fonction(request):
    ...

Fonctions concernées:
"""

for func in PAIE_SENSITIVE_FUNCTIONS:
    MANUAL_INSTRUCTIONS += f"  - {func}\n"

MANUAL_INSTRUCTIONS += """
MODULE EMPLOYÉS (employes/views.py)
-----------------------------------
Ajouter ces décorateurs aux fonctions suivantes:

@login_required
@entreprise_active_required
@reauth_required
def nom_fonction(request):
    ...

Fonctions concernées:
"""

for func in EMPLOYES_SENSITIVE_FUNCTIONS:
    MANUAL_INSTRUCTIONS += f"  - {func}\n"

MANUAL_INSTRUCTIONS += """
EXEMPLE DE MODIFICATION
-----------------------
AVANT:
    @login_required
    def detail_bulletin(request, pk):
        ...

APRÈS:
    @login_required
    @entreprise_active_required
    @reauth_required
    def detail_bulletin(request, pk):
        ...

N'OUBLIEZ PAS D'AJOUTER L'IMPORT EN HAUT DU FICHIER:
    from core.decorators import reauth_required, entreprise_active_required
"""

if __name__ == '__main__':
    print(MANUAL_INSTRUCTIONS)
    
    # Sauvegarder dans un fichier
    with open('SECURITY_DECORATORS_GUIDE.txt', 'w', encoding='utf-8') as f:
        f.write(MANUAL_INSTRUCTIONS)
    
    print("\n✅ Guide sauvegardé dans SECURITY_DECORATORS_GUIDE.txt")
