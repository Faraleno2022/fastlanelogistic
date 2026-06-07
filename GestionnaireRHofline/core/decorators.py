"""
Décorateurs personnalisés pour la sécurité
"""
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def role_required(*roles):
    """
    Décorateur pour vérifier le rôle de l'utilisateur
    Usage: @role_required('admin', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Accès refusé pour {request.user.username} - "
                f"Rôle requis: {roles}, Rôle actuel: {getattr(request.user, 'role', 'N/A')}"
            )
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('dashboard:index')
        
        return wrapped_view
    return decorator


def permission_required(permission_name):
    """
    Décorateur pour vérifier une permission spécifique
    Usage: @permission_required('employes.add_employe')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Permission refusée pour {request.user.username} - "
                f"Permission requise: {permission_name}"
            )
            messages.error(request, "Vous n'avez pas la permission nécessaire.")
            return redirect('dashboard:index')
        
        return wrapped_view
    return decorator


def rate_limit(max_requests=10, time_window=60):
    """
    Décorateur pour limiter le nombre de requêtes
    Usage: @rate_limit(max_requests=5, time_window=60)
    
    Args:
        max_requests: Nombre maximum de requêtes
        time_window: Fenêtre de temps en secondes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Créer une clé unique basée sur l'IP et la vue
            ip = get_client_ip(request)
            cache_key = f"rate_limit_{view_func.__name__}_{ip}"
            
            # Récupérer le compteur actuel
            current_count = cache.get(cache_key, 0)
            
            if current_count >= max_requests:
                logger.warning(
                    f"Rate limit dépassé pour {ip} sur {view_func.__name__} - "
                    f"{current_count} requêtes en {time_window}s"
                )
                return HttpResponseForbidden(
                    "Trop de requêtes. Veuillez réessayer plus tard."
                )
            
            # Incrémenter le compteur
            cache.set(cache_key, current_count + 1, time_window)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def ajax_required(view_func):
    """
    Décorateur pour s'assurer qu'une vue n'est accessible que via AJAX
    Usage: @ajax_required
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.warning(
                f"Tentative d'accès non-AJAX à {view_func.__name__} "
                f"depuis {get_client_ip(request)}"
            )
            return HttpResponseForbidden("Cette requête doit être effectuée via AJAX")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def secure_view(view_func):
    """
    Décorateur combiné pour sécuriser une vue
    - Requiert l'authentification
    - Vérifie que l'utilisateur est actif
    - Log l'accès
    
    Usage: @secure_view
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        # Vérifier que l'utilisateur est actif
        if not request.user.actif:
            logger.warning(
                f"Tentative d'accès par utilisateur inactif: {request.user.username}"
            )
            messages.error(request, "Votre compte est désactivé.")
            return redirect('core:login')
        
        # Logger l'accès
        logger.info(
            f"Accès sécurisé: {request.user.username} -> {view_func.__name__} "
            f"depuis {get_client_ip(request)}"
        )
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def ip_whitelist_required(view_func):
    """
    Décorateur pour restreindre l'accès à certaines IPs
    Usage: @ip_whitelist_required
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        from django.conf import settings
        
        if not getattr(settings, 'IP_WHITELIST_ENABLED', False):
            return view_func(request, *args, **kwargs)
        
        whitelist = getattr(settings, 'IP_WHITELIST', [])
        client_ip = get_client_ip(request)
        
        if client_ip not in whitelist:
            logger.warning(
                f"Accès refusé pour IP non autorisée: {client_ip} "
                f"sur {view_func.__name__}"
            )
            return HttpResponseForbidden("Accès non autorisé depuis cette adresse IP")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def log_access(action_name=None):
    """
    Décorateur pour logger l'accès à une vue
    Usage: @log_access("Consultation liste employés")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            action = action_name or view_func.__name__
            
            # Logger l'accès
            if request.user.is_authenticated:
                from core.views import log_activity
                log_activity(
                    request,
                    action=action,
                    module=view_func.__module__
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def validate_referer(view_func):
    """
    Décorateur pour valider le referer HTTP
    Protection contre les requêtes externes non autorisées
    
    Usage: @validate_referer
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        from django.conf import settings
        
        referer = request.META.get('HTTP_REFERER', '')
        allowed_hosts = settings.ALLOWED_HOSTS
        
        # Vérifier si le referer est valide
        if referer and not any(host in referer for host in allowed_hosts):
            logger.warning(
                f"Referer invalide détecté: {referer} "
                f"pour {view_func.__name__} depuis {get_client_ip(request)}"
            )
            return HttpResponseForbidden("Referer invalide")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_input(view_func):
    """
    Décorateur pour nettoyer automatiquement les entrées POST
    Usage: @sanitize_input
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.method == 'POST':
            from core.security import DataSanitizer
            
            # Créer une copie mutable du POST
            post_data = request.POST.copy()
            
            # Nettoyer chaque champ
            for key, value in post_data.items():
                if isinstance(value, str):
                    post_data[key] = DataSanitizer.sanitize_input(value)
            
            # Remplacer le POST par les données nettoyées
            request.POST = post_data
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def reauth_required(view_func):
    """
    Décorateur pour exiger une réauthentification avant d'accéder à une vue
    Usage: @reauth_required
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        
        # Vérifier si l'utilisateur nécessite une réauthentification
        if hasattr(request.user, 'require_reauth') and request.user.require_reauth:
            # Vérifier si la dernière réauthentification est récente (moins de 5 minutes)
            if request.user.last_reauth:
                time_since_reauth = timezone.now() - request.user.last_reauth
                if time_since_reauth < timedelta(minutes=5):
                    return view_func(request, *args, **kwargs)
            
            # Stocker l'URL de destination
            request.session['reauth_next'] = request.get_full_path()
            messages.warning(request, "Veuillez vous réauthentifier pour accéder à cette section.")
            return redirect('core:reauth')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def entreprise_active_required(view_func):
    """
    Décorateur pour vérifier que l'entreprise de l'utilisateur est active
    Usage: @entreprise_active_required
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'entreprise') or not request.user.entreprise:
            messages.error(request, "Vous n'êtes associé à aucune entreprise.")
            return redirect('core:login')

        if not request.user.entreprise.actif:
            messages.error(request, "Votre entreprise est désactivée. Contactez le support.")
            return redirect('core:login')

        return view_func(request, *args, **kwargs)

    return wrapped_view


def module_required(module_name):
    """
    Décorateur pour vérifier qu'un module est inclus dans le plan de l'entreprise.
    Usage: @module_required('recrutement')

    Modules possibles : paie, conges, recrutement, formation, comptabilite, portail
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            entreprise = getattr(request.user, 'entreprise', None)
            if not entreprise:
                messages.error(request, "Vous n'êtes associé à aucune entreprise.")
                return redirect('core:login')

            if not entreprise.has_module(module_name):
                plan = entreprise.plan_abonnement or 'gratuit'
                messages.warning(
                    request,
                    f"Le module « {module_name.title()} » n'est pas inclus dans votre "
                    f"plan {plan.title()}. Passez au plan supérieur pour y accéder."
                )
                return redirect('payments:plans')

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
