from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('<slug:slug>/', views.liste, name='liste'),
    path('<slug:slug>/nouveau/', views.creer, name='creer'),
    path('<slug:slug>/<int:pk>/modifier/', views.modifier, name='modifier'),
    path('<slug:slug>/<int:pk>/supprimer/', views.supprimer, name='supprimer'),
]
