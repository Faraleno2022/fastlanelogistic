from django.urls import path
from . import views
from . import views_public
from . import views_integration

app_name = 'recrutement'

urlpatterns = [
    # Accueil
    path('', views.recrutement_home, name='home'),
    
    # Vues publiques (sans authentification)
    path('offre/<uuid:offre_uuid>/', views_public.offre_detail_public, name='offre_public'),
    path('offre/<uuid:offre_uuid>/postuler/', views_public.postuler, name='postuler'),
    path('candidature/confirmation/<str:numero>/', views_public.candidature_confirmee, name='candidature_confirmee'),
    
    # Offres d'emploi
    path('offres/', views.liste_offres, name='offres'),
    path('offres/creer/', views.creer_offre, name='creer_offre'),
    path('offres/<uuid:offre_uuid>/', views.detail_offre, name='detail_offre'),
    path('offres/<uuid:offre_uuid>/modifier/', views.modifier_offre, name='modifier_offre'),
    path('offres/<uuid:offre_uuid>/supprimer/', views.supprimer_offre, name='supprimer_offre'),
    
    # Candidatures
    path('candidatures/', views.liste_candidatures, name='candidatures'),
    path('candidatures/creer/', views.creer_candidature, name='creer_candidature'),
    path('candidatures/<int:pk>/', views.detail_candidature, name='detail_candidature'),
    path('candidatures/<int:pk>/evaluer/', views.evaluer_candidature, name='evaluer_candidature'),
    path('candidatures/<int:pk>/supprimer-document/', views.supprimer_document_candidature, name='supprimer_document_candidature'),
    path('candidatures/<int:pk>/telecharger/<str:type_doc>/', views.telecharger_document_candidature, name='telecharger_document'),
    
    # Entretiens
    path('entretiens/', views.liste_entretiens, name='entretiens'),
    path('entretiens/creer/<int:candidature_id>/', views.creer_entretien, name='creer_entretien'),
    path('entretiens/<int:pk>/', views.detail_entretien, name='detail_entretien'),
    path('entretiens/<int:pk>/evaluer/', views.evaluer_entretien, name='evaluer_entretien'),
    
    # Décisions d'embauche
    path('decisions/', views_integration.liste_decisions, name='decisions'),
    path('decisions/creer/<int:candidature_id>/', views_integration.creer_decision, name='creer_decision'),
    path('decisions/<int:pk>/', views_integration.detail_decision, name='detail_decision'),
    path('decisions/<int:pk>/accepter/', views_integration.accepter_offre, name='accepter_offre'),
    path('decisions/<int:pk>/refuser/', views_integration.refuser_offre, name='refuser_offre'),
    
    # Intégration candidat
    path('integration/', views_integration.liste_integrations, name='integrations'),
    path('integration/demarrer/<int:pk>/', views_integration.demarrer_integration, name='demarrer_integration'),
    path('integration/<int:pk>/', views_integration.detail_integration, name='detail_integration'),
    path('integration/etape/<int:pk>/valider/', views_integration.valider_etape, name='valider_etape'),
    path('integration/<int:pk>/creer-employe/', views_integration.creer_employe_depuis_candidat, name='creer_employe'),
    
    # Alertes recrutement
    path('alertes/', views_integration.liste_alertes_recrutement, name='alertes'),
    path('alertes/<int:pk>/traiter/', views_integration.traiter_alerte_recrutement, name='traiter_alerte'),
]
