"""
Contexte SEO partagé entre toutes les pages publiques.

Expose au template :
 - SEO : dict avec site_url, site_name, default_title/description/keywords,
         locale, twitter_handle, fb_app_id, default_og_image_url
 - ORG  : identité organisation (pour JSON-LD Organization / LocalBusiness)
 - CANONICAL_URL : URL absolue de la page courante (sans query-string)
 - ABSOLUTE_URI  : URL absolue complète (avec query-string)
"""
from django.conf import settings
from django.templatetags.static import static


def seo_context(request):
    site_url = getattr(settings, "SEO_SITE_URL", "").rstrip("/")

    # URL absolue recalculée depuis la requête (fallback sur SEO_SITE_URL)
    try:
        absolute_uri = request.build_absolute_uri()
        canonical = request.build_absolute_uri(request.path)
    except Exception:
        absolute_uri = site_url + (request.path if hasattr(request, "path") else "/")
        canonical = absolute_uri

    # Sur PythonAnywhere derrière proxy, on force le schéma https sur la canonique
    # si le host correspond au domaine configuré.
    try:
        from urllib.parse import urlparse
        parsed = urlparse(canonical)
        if site_url and parsed.netloc in site_url:
            canonical = canonical.replace("http://", "https://", 1)
            absolute_uri = absolute_uri.replace("http://", "https://", 1)
    except Exception:
        pass

    default_og_rel = getattr(settings, "SEO_DEFAULT_OG_IMAGE", "images/home2.png")
    try:
        og_path = static(default_og_rel)
    except Exception:
        og_path = "/static/" + default_og_rel
    # Préfixe host si chemin relatif
    if og_path.startswith("/"):
        default_og_image_url = f"{site_url}{og_path}"
    else:
        default_og_image_url = og_path

    seo = {
        "site_url": site_url,
        "site_name": getattr(settings, "SEO_SITE_NAME", "Fastlane Logistic"),
        "default_title": getattr(settings, "SEO_DEFAULT_TITLE", ""),
        "default_description": getattr(settings, "SEO_DEFAULT_DESCRIPTION", ""),
        "default_keywords": getattr(settings, "SEO_DEFAULT_KEYWORDS", ""),
        "locale": getattr(settings, "SEO_LOCALE", "fr_FR"),
        "twitter_handle": getattr(settings, "SEO_TWITTER_HANDLE", ""),
        "fb_app_id": getattr(settings, "SEO_FB_APP_ID", ""),
        "default_og_image_url": default_og_image_url,
    }

    return {
        "SEO": seo,
        "ORG": getattr(settings, "SEO_ORGANIZATION", {}),
        "CANONICAL_URL": canonical,
        "ABSOLUTE_URI": absolute_uri,
    }
