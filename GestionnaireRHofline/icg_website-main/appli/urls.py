from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from appli.views import (
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    about,
    CustomLogin,
    logOut
)

from django.conf.urls.static import static
from appli import contact_views

urlpatterns = [
    # Pages publiques
    path('', about, name='show_entreprise'),
    path('about', about, name='about'),
    path('contact', contact_views.ContactCreateView.as_view(), name='contact'),
    
    # Événements - partie publique
    path('show_event', EventListView.as_view(), name='event_list'),
    path('event_detail/<int:pk>', EventDetailView.as_view(), name='event_detail'),
    
    # Événements - partie admin protégée Pour les admins
    path('create_event', EventCreateView.as_view(), name='event_create'),    
    path('<int:pk>/update_event',EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete_event', EventDeleteView.as_view(),name='event_delete'),
    
    # Contacts - partie admin protégée pour les admins
    path('contact_list', contact_views.ContactListView.as_view(), name='contact_list'),
    path('show_contact/<int:pk>', contact_views.ContactDetailView.as_view(), name='contact_detail'),
    path('delete_contact/<int:pk>', contact_views.ContactDeleteView.as_view(), name='contact_delete'),
    
    # Connexion et déconnexion
    path('connexion', CustomLogin.as_view(), name='login'),
    path('deconnexion', logOut, name='logout'),
]


