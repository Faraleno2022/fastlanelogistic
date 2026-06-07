"""
URLs pour le schéma public (inscription, landing page, etc.)
Ces URLs sont accessibles sans être dans un tenant spécifique
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin du système (super admin)
    path('admin/', admin.site.urls),
    
    # Inscription de nouvelles entreprises
    path('inscription/', include('tenants.urls')),
    
    # Landing page publique
    path('', include('core.urls_public')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
