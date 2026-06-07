from django.urls import path
from . import views

app_name = 'conges'

urlpatterns = [
    path('', views.liste_conges, name='liste'),
    path('soldes/', views.soldes_conges, name='soldes'),
    path('demander/', views.demander_conge, name='demander'),
    path('<int:pk>/approuver/', views.approuver_conge, name='approuver'),
]
