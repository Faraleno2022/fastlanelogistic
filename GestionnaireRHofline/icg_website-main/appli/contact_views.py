from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from django.views.decorators.csrf import requires_csrf_token
from appli.models import Events

from appli.models import Contacts
from appli.views import AdminRequiredMixin



class ContactCreateView(CreateView):
    """Permet à tout le monde de créer un contact"""
    model = Contacts
    fields = ['contact_name', 'contact_email', 'contact_phone_number', 'contact_subject', 'contact_message']
    template_name = 'contacts/contact.html'
    success_url = reverse_lazy('show_entreprise')
    
    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, "Votre message a été envoyé avec succès !")
        return super().form_valid(form)

class ContactListView(AdminRequiredMixin, ListView):
    """Liste des contacts - réservée aux admins"""
    model = Contacts
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    ordering = ['-received_at']  # Du plus récent au plus ancien

class ContactDetailView(AdminRequiredMixin, DetailView):
    """Détail d'un contact - réservé aux admins"""
    model = Contacts
    template_name = 'contacts/contact_detail.html'
    context_object_name = 'contact'
    
class ContactDeleteView(AdminRequiredMixin, DeleteView):
    """Suppression d'un contact - réservé aux admins"""
    model = Contacts
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contact_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Contact supprimé avec succès !")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_detail_url'] = reverse('contact_detail', kwargs={'pk': self.object.pk})
        return context