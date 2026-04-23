from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.public.sitemaps import sitemaps as public_sitemaps
from apps.public.views import robots_txt

admin.site.site_header = "Fastlane Logistic — Administration"
admin.site.site_title = "Fastlane Logistic Admin"
admin.site.index_title = "Gestion de flotte & logistique minière"

urlpatterns = [
    path("admin/", admin.site.urls),

    # Connexion unique (alias public de accounts:login)
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="connexion",
    ),

    # Backoffice (authentifié)
    path("accounts/", include("apps.accounts.urls")),
    path("core/", include("apps.core.urls")),
    path("flotte/", include("apps.flotte.urls")),
    path("rh/", include("apps.rh.urls")),
    path("operations/", include("apps.operations.urls")),
    path("facturation/", include("apps.facturation.urls")),
    path("dashboard/", include("apps.dashboard.urls")),

    # SEO — sitemap & robots.txt
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": public_sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", robots_txt, name="robots_txt"),

    # Site public — racine en dernier
    path("", include("apps.public.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
