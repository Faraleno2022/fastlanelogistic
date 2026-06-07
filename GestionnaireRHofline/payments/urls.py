from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('plans/', views.plans_liste, name='plans'),
    path('checkout/<slug:plan_slug>/', views.checkout, name='checkout'),
    path('simulate/<str:token>/', views.simulate_payment, name='simulate'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.webhook, name='webhook'),
    path('paycard/callback/', views.paycard_callback, name='paycard_callback'),
    path('historique/', views.historique_transactions, name='historique'),
    path('mon-abonnement/', views.mon_abonnement, name='mon_abonnement'),
]
