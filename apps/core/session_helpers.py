"""
Helpers pour la gestion du "contrat actif" en session.

Le contrat actif est un contexte persistant (par utilisateur, via session)
qui permet de pré-remplir automatiquement le champ `contrat` dans les
formulaires d'opérations (carburant, pannes, dépenses, voyages, bons).

Workflow :
  1. L'utilisateur choisit un contrat via le sélecteur de la navbar
     → POST vers `core:set_contrat_actif` avec `code=CTR-2026-CBG`
     → stockage dans `request.session["contrat_actif_id"]`
  2. Tous les formulaires de création lisent cette valeur comme `initial`
  3. L'utilisateur peut changer à tout moment (autre contrat) ou effacer
     (POST vers `core:clear_contrat_actif`)

La valeur par défaut est None (pas de contrat forcé → comportement classique).
"""
SESSION_KEY = "contrat_actif_id"


def get_contrat_actif(request):
    """Retourne l'instance Contrat active en session, ou None."""
    if not hasattr(request, "session"):
        return None
    cid = request.session.get(SESSION_KEY)
    if not cid:
        return None
    # Import local pour éviter les imports circulaires au chargement
    from apps.facturation.models import Contrat
    try:
        return Contrat.objects.get(pk=cid, actif=True)
    except Contrat.DoesNotExist:
        # Contrat supprimé ou désactivé → nettoyer la session
        request.session.pop(SESSION_KEY, None)
        return None


def set_contrat_actif(request, contrat):
    """Définit le contrat actif en session (ou None pour effacer)."""
    if contrat is None:
        request.session.pop(SESSION_KEY, None)
    else:
        request.session[SESSION_KEY] = contrat.pk
    request.session.modified = True


def clear_contrat_actif(request):
    """Efface le contrat actif."""
    set_contrat_actif(request, None)
