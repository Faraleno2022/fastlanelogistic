from django.urls import path
from . import views

app_name = 'contrats'

urlpatterns = [
    # Dashboard contrats
    path('', views.contrats_dashboard, name='dashboard'),
    
    # Types de contrats
    path('types/', views.liste_types_contrats, name='types'),
    path('types/creer/', views.creer_type_contrat, name='creer_type'),
    path('types/<int:pk>/modifier/', views.modifier_type_contrat, name='modifier_type'),
    
    # Contrats
    path('liste/', views.liste_contrats, name='liste'),
    path('creer/', views.creer_contrat, name='creer'),
    path('<uuid:pk>/', views.detail_contrat, name='detail'),
    path('<uuid:pk>/modifier/', views.modifier_contrat, name='modifier'),
    path('<uuid:pk>/terminer/', views.terminer_contrat, name='terminer'),
    path('<uuid:pk>/renouveler/', views.renouveler_contrat, name='renouveler'),
    path('<uuid:pk>/imprimer/', views.imprimer_contrat, name='imprimer'),
    path('<uuid:pk>/solde-tout-compte/', views.solde_tout_compte, name='solde_tout_compte'),
    
    # Alertes
    path('alertes/', views.liste_alertes, name='alertes'),
    path('alertes/<int:pk>/traiter/', views.traiter_alerte, name='traiter_alerte'),
    path('alertes/generer/', views.generer_alertes, name='generer_alertes'),
    
    # Disponibilités
    path('disponibilites/', views.liste_disponibilites, name='disponibilites'),
    path('disponibilites/creer/', views.creer_disponibilite, name='creer_disponibilite'),
    path('disponibilites/<int:pk>/approuver/', views.approuver_disponibilite, name='approuver_disponibilite'),
    
    # Rapports
    path('rapports/', views.rapports_contrats, name='rapports'),
    path('rapports/expirations/', views.rapport_expirations, name='rapport_expirations'),
]
