from datetime import date # Importe date directement
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from django.views.decorators.csrf import requires_csrf_token
from appli.models import Events
from appli.forms import EventForm # <-- NOUVEAU : Importe ton formulaire
from django.contrib.auth.views import LoginView, LogoutView


# Mixin personnalisé pour vérifier les droits admin
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser and self.request.user.is_authenticated
    
    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé aux administrateurs")
        return redirect('show_entreprise') 

# Vue Liste (publique)
class EventListView(ListView):
    model = Events
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    ordering = ['-event_date']
    paginate_by = 10

# Vue Création (réservée aux utilisateurs connectés)
class EventCreateView(AdminRequiredMixin, CreateView):
    model = Events
    template_name = 'events/event_form.html'
    form_class = EventForm
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        messages.success(self.request, "Événement créé avec succès!")
        return super().form_valid(form) # Appelle la méthode form_valid de la classe parente

    def get_login_url(self):
        messages.warning(self.request, "Vous devez être connecté pour créer un événement")
        return super().get_login_url()

# Vue Détail (publique)
class EventDetailView(DetailView):
    model = Events
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

# Vue Modification (réservée aux admins)
class EventUpdateView(AdminRequiredMixin, UpdateView):
    model = Events
    template_name = 'events/event_form.html'
    form_class = EventForm 
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        messages.success(self.request, "Événement mis à jour avec succès!")
        return super().form_valid(form)

# Vue Suppression (réservée aux admins)
class EventDeleteView(AdminRequiredMixin, DeleteView):
    model = Events
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')  # Redirection après suppression
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_detail_url'] = reverse('event_detail', kwargs={'pk': self.object.pk})
        return context

# Gestion des erreurs CSRF
@requires_csrf_token
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, '403_csrf.html', context, status=403)


def about(request):
    return render(request, 'about.html')


class CustomLogin(LoginView):
    template_name = 'register/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('contact_list')

    def get_success_url(self):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return self.success_url
        else:
            return reverse_lazy('login')
    
def logOut(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')