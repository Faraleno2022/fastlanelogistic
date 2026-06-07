"""
Mixins réutilisables pour les vues comptables.

Fournissent des fonctionnalités communes:
- Permissions par entreprise
- Contrôle d'accès
- Pagination
- Filtrage
- Audit
"""

from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class EntrepriseRequiredMixin(LoginRequiredMixin):
    """Garantit que l'utilisateur appartient à une entreprise."""
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier d'abord si l'utilisateur est authentifié (utilise LoginRequiredMixin)
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        # Les superusers et staff peuvent accéder sans entreprise
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # Vérifier si l'utilisateur a une entreprise
        if not hasattr(request.user, 'entreprise') or not request.user.entreprise:
            raise PermissionDenied("Vous n'appartenez à aucune entreprise")
        return super().dispatch(request, *args, **kwargs)


class ComptabiliteAccessMixin(EntrepriseRequiredMixin, UserPassesTestMixin):
    """
    Mixin pour vérifier l'accès au module de comptabilité.
    
    L'utilisateur doit:
    - Être connecté
    - Appartenir à une entreprise
    - Avoir la permission 'comptabilite' (ou être admin/staff)
    """
    
    def test_func(self):
        """Vérifie si l'utilisateur a accès à la comptabilité."""
        user = self.request.user
        
        # Admin = accès complet
        if user.is_superuser or user.is_staff:
            return True
        
        # Admin entreprise = accès complet
        if hasattr(user, 'est_admin_entreprise') and user.est_admin_entreprise:
            return True
        
        # Utilisateur avec entreprise = accès (pour le moment)
        if hasattr(user, 'entreprise') and user.entreprise:
            return True
        
        # Vérifie la permission
        return user.has_perm('comptabilite.view_comptabilite')
    
    def handle_no_permission(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission refusée'}, status=403)
        raise PermissionDenied("Accès refusé au module de comptabilité")


class EntrepriseFilterMixin:
    """Filtre automatiquement les objets par entreprise."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les superusers/staff sans entreprise voient tout
        user = self.request.user
        if (user.is_superuser or user.is_staff) and not getattr(user, 'entreprise', None):
            return queryset
        
        # Vérifier si l'utilisateur a une entreprise
        entreprise = getattr(user, 'entreprise', None)
        if not entreprise:
            return queryset.none()
        
        # Vérifier si le modèle a un champ direct 'entreprise'
        model_fields = [field.name for field in self.model._meta.get_fields()]
        
        if 'entreprise' in model_fields:
            # Filtrage direct
            return queryset.filter(entreprise=entreprise)
        elif 'compte_bancaire' in model_fields:
            # Filtrage via relation compte_bancaire (pour RapprochementBancaire, etc.)
            return queryset.filter(compte_bancaire__entreprise=entreprise)
        elif 'exercice' in model_fields:
            # Filtrage via relation exercice
            return queryset.filter(exercice__entreprise=entreprise)
        elif 'journal' in model_fields:
            # Filtrage via relation journal
            return queryset.filter(journal__entreprise=entreprise)
        elif 'tiers' in model_fields:
            # Filtrage via relation tiers
            return queryset.filter(tiers__entreprise=entreprise)
        elif 'plan_comptable' in model_fields:
            # Filtrage via relation plan_comptable
            return queryset.filter(plan_comptable__entreprise=entreprise)
        
        # Si aucune relation d'entreprise trouvée, retourner le queryset sans filtre
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entreprise'] = getattr(self.request.user, 'entreprise', None)
        return context


class AuditMixin:
    """Enregistre les actions en piste d'audit."""
    
    def get_audit_data(self):
        """Retourne les données pour l'audit."""
        return {}
    
    def form_valid(self, form):
        """Enregistre l'action en audit avant sauvegarde."""
        response = super().form_valid(form)
        
        from ..models import PisteAudit
        try:
            PisteAudit.objects.create(
                entreprise=self.request.user.entreprise,
                utilisateur=self.request.user,
                action=self.get_audit_action(),
                module=self.get_audit_module(),
                type_objet=self.model.__name__,
                id_objet=str(self.object.id),
                donnees_nouvelles=str(self.get_audit_data())
            )
        except Exception as e:
            logger.error(f"Erreur audit: {e}")
        
        return response
    
    def get_audit_action(self):
        """Retourne le type d'action ('create' ou 'update')."""
        return 'update' if self.object.pk else 'create'
    
    def get_audit_module(self):
        """Retourne le module pour l'audit."""
        return self.model._meta.verbose_name_plural


class PaginationMixin:
    """Ajoute la pagination standardisée."""
    
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_by'] = self.paginate_by
        return context


class SearchMixin:
    """Ajoute la recherche sur les listes."""
    
    search_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        search = self.request.GET.get('search', '').strip()
        if search and self.search_fields:
            from django.db.models import Q
            q = Q()
            for field in self.search_fields:
                q |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(q)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class FilterMixin:
    """Ajoute les filtres standardisés."""
    
    filter_fields = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        for field in self.filter_fields:
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in self.filter_fields:
            context[f'{field}_value'] = self.request.GET.get(field, '')
        return context


class ExportMixin:
    """Ajoute l'export des données."""
    
    def get_export_filename(self):
        """Retourne le nom du fichier d'export."""
        return f"export_{self.model._meta.model_name}"
    
    def export_csv(self, queryset):
        """Exporte en CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename()}.csv"'
        
        writer = csv.writer(response)
        # À implémenter par subclass
        return response
    
    def export_excel(self, queryset):
        """Exporte en Excel."""
        # À implémenter avec openpyxl si nécessaire
        pass
