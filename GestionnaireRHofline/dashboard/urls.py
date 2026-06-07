from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('rapports/', views.rapports, name='rapports'),
    path('statistiques-paie/', views.statistiques_paie, name='statistiques_paie'),
    path('manuel/', views.telecharger_manuel, name='telecharger_manuel'),
]
