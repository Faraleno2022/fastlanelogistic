"""
Sitemaps XML pour le site public Fastlane Logistic.
Exposés via /sitemap.xml (voir fastlane/urls.py).

Le domaine utilisé dans les URLs est forcé via SEO_SITE_URL (settings) plutôt
que via django.contrib.sites : pas de risque d'avoir "example.com" si le Site
par défaut n'a jamais été édité.
"""
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .models import Evenement, AppelOffre


class _FastlaneBaseSitemap(Sitemap):
    """Force le domaine et le schéma depuis settings.SEO_SITE_URL."""

    def get_domain(self, site=None):
        parsed = urlparse(getattr(settings, "SEO_SITE_URL", "") or "")
        return parsed.netloc or "fastlanelogisticgn.com"

    @property
    def protocol(self):
        parsed = urlparse(getattr(settings, "SEO_SITE_URL", "") or "")
        return parsed.scheme or "https"


class StaticViewSitemap(_FastlaneBaseSitemap):
    """Pages statiques principales."""
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return [
            ("public:home", 1.0, "daily"),
            ("public:a_propos", 0.8, "monthly"),
            ("public:contact", 0.9, "monthly"),
            ("public:evenements", 0.7, "weekly"),
            ("public:appels_offres", 0.9, "daily"),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        return timezone.now()


class EvenementSitemap(_FastlaneBaseSitemap):
    """Événements publiés (publics)."""
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Evenement.objects.filter(statut="publie").order_by("-date_evenement")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class AppelOffreSitemap(_FastlaneBaseSitemap):
    """Appels d'offres ouverts ou clos (hors brouillons)."""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return AppelOffre.objects.exclude(statut="brouillon").order_by("-date_publication")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


sitemaps = {
    "static": StaticViewSitemap,
    "evenements": EvenementSitemap,
    "appels_offres": AppelOffreSitemap,
}
