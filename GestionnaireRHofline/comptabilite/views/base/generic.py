"""
Vues génériques réutilisables pour la comptabilité.

Fournissent:
- CRUD de base avec permissions
- Pagination et recherche
- Intégration service layer
- Messages et feedback utilisateur
- Audit logging
"""

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import logging

from comptabilite.mixins.views import (
    ComptabiliteAccessMixin, EntrepriseFilterMixin, AuditMixin,
    PaginationMixin, SearchMixin, FilterMixin
)

logger = logging.getLogger(__name__)


class ComptaListView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    PaginationMixin,
    SearchMixin,
    FilterMixin,
    ListView
):
    """Vue générique pour les listes avec filtres."""
    
    template_name = 'comptabilite/base/list.html'
    context_object_name = 'objects'
    paginate_by = 50


class ComptaDetailView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    DetailView
):
    """Vue générique pour les détails."""
    
    template_name = 'comptabilite/base/detail.html'
    context_object_name = 'object'


class ComptaCreateView(
    ComptabiliteAccessMixin,
    AuditMixin,
    SuccessMessageMixin,
    CreateView
):
    """Vue générique pour la création."""
    
    template_name = 'comptabilite/base/form.html'
    success_message = _("%(model_name)s créé(e) avec succès")
    
    def get_success_message(self, cleaned_data):
        return self.success_message % {
            'model_name': self.model._meta.verbose_name
        }
    
    def form_valid(self, form):
        """Associe l'entreprise avant sauvegarde."""
        form.instance.entreprise = self.request.user.entreprise
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context


class ComptaUpdateView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    AuditMixin,
    SuccessMessageMixin,
    UpdateView
):
    """Vue générique pour l'édition."""
    
    template_name = 'comptabilite/base/form.html'
    success_message = _("%(model_name)s modifié(e) avec succès")
    
    def get_success_message(self, cleaned_data):
        return self.success_message % {
            'model_name': self.model._meta.verbose_name
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        return context


class ComptaDeleteView(
    ComptabiliteAccessMixin,
    EntrepriseFilterMixin,
    SuccessMessageMixin,
    DeleteView
):
    """Vue générique pour la suppression."""
    
    template_name = 'comptabilite/base/confirm_delete.html'
    success_message = _("%(model_name)s supprimé(e) avec succès")
    
    def get_success_message(self, cleaned_data):
        return self.success_message % {
            'model_name': self.model._meta.verbose_name
        }
    
    def delete(self, request, *args, **kwargs):
        """Ajoute message avant suppression."""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, self.get_success_message({}))
        return response


class ComptaDashboardView(ComptabiliteAccessMixin, View):
    """Vue pour le tableau de bord comptable."""
    
    template_name = 'comptabilite/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Rassemble les données du dashboard."""
        context = {
            'entreprise': self.request.user.entreprise,
        }
        return context
    
    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        context = self.get_context_data()
        return render(request, self.template_name, context)


class ComptaExportView(ComptabiliteAccessMixin, EntrepriseFilterMixin, View):
    """Vue générique pour l'export."""
    
    def get(self, request, *args, **kwargs):
        """Export en fonction du format."""
        format_export = request.GET.get('format', 'csv')
        
        if format_export == 'csv':
            return self.export_csv()
        elif format_export == 'excel':
            return self.export_excel()
        elif format_export == 'pdf':
            return self.export_pdf()
        else:
            return JsonResponse({'error': 'Format non supporté'}, status=400)
    
    def export_csv(self):
        """Export CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.writer(response)
        
        # À implémenter par subclass
        return response
    
    def export_excel(self):
        """Export Excel."""
        # À implémenter avec openpyxl si nécessaire
        from django.http import HttpResponse
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        return response
    
    def export_pdf(self):
        """Export PDF."""
        # À implémenter avec reportlab si nécessaire
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/pdf')
        return response


class ComptaAjaxView(ComptabiliteAccessMixin, View):
    """Vue de base pour les requêtes AJAX."""
    
    def get_json_response(self, data, status=200):
        """Retourne une réponse JSON."""
        return JsonResponse(data, status=status)
    
    def get_error_response(self, message, status=400):
        """Retourne une erreur JSON."""
        return self.get_json_response({'error': message}, status=status)
    
    def get_success_response(self, message='Succès', data=None):
        """Retourne un succès JSON."""
        response = {'success': True, 'message': message}
        if data:
            response['data'] = data
        return self.get_json_response(response)
