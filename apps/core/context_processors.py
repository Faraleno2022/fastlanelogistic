from django.conf import settings
from .models import Parametres
from .session_helpers import get_contrat_actif


def site_context(request):
    try:
        params = Parametres.load()
        societe_nom = params.societe_nom
        devise = params.devise
    except Exception:
        societe_nom = settings.SOCIETE_NOM
        devise = settings.SOCIETE_DEVISE

    # Contrat actif en session (si l'utilisateur en a choisi un)
    contrat_actif = get_contrat_actif(request) if request.user.is_authenticated else None

    # Liste des contrats actifs pour le sélecteur navbar (query légère)
    contrats_actifs_choix = []
    if request.user.is_authenticated:
        try:
            from apps.facturation.models import Contrat
            contrats_actifs_choix = list(Contrat.objects.filter(actif=True).order_by("code"))
        except Exception:
            pass

    # Coordonnées publiques (footer du site public)
    contact_adresse = contact_email = contact_telephone = ""
    try:
        from apps.public.models import PageAPropos
        page = PageAPropos.load()
        contact_adresse = page.adresse
        contact_email = page.email
        contact_telephone = page.telephone
    except Exception:
        pass

    return {
        "SOCIETE_NOM": societe_nom,
        "DEVISE": devise,
        "CONTRAT_ACTIF": contrat_actif,
        "CONTRATS_ACTIFS_CHOIX": contrats_actifs_choix,
        "CONTACT_ADRESSE": contact_adresse,
        "CONTACT_EMAIL": contact_email,
        "CONTACT_TELEPHONE": contact_telephone,
    }
