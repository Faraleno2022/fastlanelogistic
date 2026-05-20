"""
URLs publiques pour le schéma public
"""
from django.urls import path
from . import views

app_name = 'core_public'

urlpatterns = [
    path('', views.login_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('connexion/', views.login_view, name='connexion'),
]
