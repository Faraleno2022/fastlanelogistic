"""
URLs pour les tenants (entreprises)
Ces URLs sont accessibles uniquement dans le contexte d'un tenant
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin de l'entreprise
    path('admin/', admin.site.urls),
    
    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
    # Applications
    path('', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('employes/', include('employes.urls')),
    path('paie/', include('paie.urls')),
    path('temps-travail/', include('temps_travail.urls')),
    path('recrutement/', include('recrutement.urls')),
    path('formation/', include('formation.urls')),
    path('payments/', include('payments.urls')),
    path('portail/', include('portail.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
