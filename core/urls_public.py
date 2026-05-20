"""
URLs publiques pour le schéma public
"""
from django.urls import path
from . import views

app_name = 'core_public'

urlpatterns = [
    path('', views.landing_page, name='landing'),
]
