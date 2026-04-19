from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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

    # Site public — racine en dernier
    path("", include("apps.public.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
