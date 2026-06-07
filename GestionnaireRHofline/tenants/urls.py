from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('inscription/', views.inscription_entreprise, name='inscription'),
    path('inscription/success/<str:schema_name>/', views.inscription_success, name='inscription_success'),
]
