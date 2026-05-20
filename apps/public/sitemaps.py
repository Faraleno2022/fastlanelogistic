"""
Sitemap XML pour l'acces production Fastlane Logistic.

La partie publique est desactivee: le sitemap expose uniquement la page de
connexion afin d'eviter l'indexation des anciennes pages vitrines.
"""
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class _FastlaneBaseSitemap(Sitemap):
    """Force le domaine et le schema depuis settings.SEO_SITE_URL."""

    def get_domain(self, site=None):
        parsed = urlparse(getattr(settings, "SEO_SITE_URL", "") or "")
        return parsed.netloc or "fastlanelogisticgn.com"

    @property
    def protocol(self):
        parsed = urlparse(getattr(settings, "SEO_SITE_URL", "") or "")
        return parsed.scheme or "https"


class StaticViewSitemap(_FastlaneBaseSitemap):
    """Page de connexion principale."""

    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return [("connexion", 1.0, "monthly")]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        return timezone.now()


sitemaps = {
    "static": StaticViewSitemap,
}
