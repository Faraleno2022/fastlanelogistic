"""
Décorateurs et utilitaires de permissions pour la comptabilité.

Fournissent:
- Décorateurs pour vérifier les permissions
- Vérification de l'exercice fiscal
- Contrôle d'accès par rôle
"""

from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)


def comptabilite_required(view_func):
    """Vérifie que l'utilisateur a accès au module comptabilité."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Admin = accès complet
        if request.user.is_superuser or request.user.est_admin_entreprise:
            return view_func(request, *args, **kwargs)
        
        # Vérifie la permission
        if not request.user.has_perm('comptabilite.view_comptabilite'):
            raise PermissionDenied(_("Accès refusé au module de comptabilité"))
        
        return view_func(request, *args, **kwargs)
    
    return login_required(wrapper)


def exercice_actif_required(view_func):
    """Vérifie que l'exercice fiscal est actif."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            from .models import ExerciceComptable
            
            exercice = ExerciceComptable.objects.filter(
                entreprise=request.user.entreprise,
                statut='OUVERT'
            ).first()
            
            if not exercice:
                raise PermissionDenied(
                    _("Aucun exercice comptable ouvert")
                )
            
            # Ajoute l'exercice au request
            request.exercice = exercice
            
        except Exception as e:
            logger.error(f"Erreur vérification exercice: {e}")
            raise PermissionDenied(_("Erreur lors de la vérification de l'exercice"))
        
        return view_func(request, *args, **kwargs)
    
    return comptabilite_required(wrapper)


def admin_comptabilite_required(view_func):
    """Vérifie que l'utilisateur est admin de la comptabilité."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # SuperUser = accès complet
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Admin entreprise = accès complet
        if request.user.est_admin_entreprise:
            return view_func(request, *args, **kwargs)
        
        # Permission explicite
        if not request.user.has_perm('comptabilite.change_comptabilite'):
            raise PermissionDenied(
                _("Vous devez être administrateur pour accéder à cette fonctionnalité")
            )
        
        return view_func(request, *args, **kwargs)
    
    return comptabilite_required(wrapper)


def ajax_required(view_func):
    """Vérifie que la requête est AJAX."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.is_ajax() or 
                request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
            return JsonResponse(
                {'error': _('Requête AJAX requise')},
                status=400
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def lock_modification_required(view_func):
    """Vérifie que l'objet n'est pas verrouillé."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # À implémenter basé sur le modèle
        return view_func(request, *args, **kwargs)
    
    return wrapper


class ComptabilitePermission:
    """Classe pour vérifier les permissions de comptabilité."""
    
    @staticmethod
    def can_view(user, entreprise):
        """Peut voir la comptabilité."""
        if user.is_superuser:
            return True
        return user.has_perm('comptabilite.view_comptabilite')
    
    @staticmethod
    def can_edit(user, entreprise):
        """Peut éditer la comptabilité."""
        if user.is_superuser:
            return True
        if user.est_admin_entreprise and user.entreprise == entreprise:
            return True
        return user.has_perm('comptabilite.change_comptabilite')
    
    @staticmethod
    def can_delete(user, entreprise):
        """Peut supprimer de la comptabilité."""
        if user.is_superuser:
            return True
        if user.est_admin_entreprise and user.entreprise == entreprise:
            return True
        return user.has_perm('comptabilite.delete_comptabilite')
    
    @staticmethod
    def can_approve(user, entreprise):
        """Peut approuver des écritures."""
        if user.is_superuser:
            return True
        if user.est_admin_entreprise and user.entreprise == entreprise:
            return True
        return user.has_perm('comptabilite.approve_comptabilite')
    
    @staticmethod
    def can_export(user, entreprise):
        """Peut exporter les données."""
        if user.is_superuser:
            return True
        if user.est_admin_entreprise and user.entreprise == entreprise:
            return True
        return user.has_perm('comptabilite.export_comptabilite')


class RoleBasedAccess:
    """Contrôle d'accès basé sur les rôles."""
    
    ROLES = {
        'ADMIN': ['view', 'create', 'edit', 'delete', 'approve', 'export'],
        'COMPTABLE': ['view', 'create', 'edit', 'approve'],
        'ASSISTANT': ['view', 'create', 'edit'],
        'VIEWER': ['view'],
    }
    
    @staticmethod
    def has_permission(user_role, action):
        """Vérifie si le rôle peut effectuer l'action."""
        permissions = RoleBasedAccess.ROLES.get(user_role, [])
        return action in permissions
    
    @staticmethod
    def get_allowed_actions(user_role):
        """Retourne les actions autorisées pour un rôle."""
        return RoleBasedAccess.ROLES.get(user_role, [])
