from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ComptabiliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comptabilite'
    verbose_name = 'Comptabilité'
    
    def ready(self):
        """Exécuté au démarrage de l'app."""
        # Importe les signaux
        try:
            import comptabilite.signals
        except:
            pass
        
        # Crée les permissions par défaut
        post_migrate.connect(self.create_default_permissions, sender=self)
    
    @staticmethod
    def create_default_permissions(sender, **kwargs):
        """Crée les permissions par défaut."""
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from comptabilite.models import ExerciceComptable
        
        try:
            content_type = ContentType.objects.get_for_model(ExerciceComptable)
            
            # Permissions personnalisées
            permissions_to_create = [
                ('view_comptabilite', 'Peut voir la comptabilité'),
                ('change_comptabilite', 'Peut modifier la comptabilité'),
                ('approve_comptabilite', 'Peut approuver les écritures'),
            ]
            
            for codename, name in permissions_to_create:
                Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name}
                )
        except Exception:
            pass
