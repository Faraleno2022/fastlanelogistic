from django.db import migrations
from decimal import Decimal
from django.utils import timezone


def set_taux_ta_default(apps, schema_editor):
    """Définir TAUX_TA à 1,5% par défaut"""
    Constante = apps.get_model('paie', 'Constante')
    
    # Créer ou mettre à jour la constante TAUX_TA
    obj, created = Constante.objects.update_or_create(
        code='TAUX_TA',
        defaults={
            'libelle': 'Taxe d\'Apprentissage (%)',
            'valeur': Decimal('1.50'),
            'type_valeur': 'pourcentage',
            'description': 'Taux de la Taxe d\'Apprentissage - 1,5% du brut (légal Guinée)',
            'actif': True,
            'date_debut_validite': timezone.now().date(),
        }
    )
    
    # Mettre à jour aussi TAUX_VF si nécessaire
    Constante.objects.update_or_create(
        code='TAUX_VF',
        defaults={
            'libelle': 'Versement Forfaitaire (%)',
            'valeur': Decimal('6.00'),
            'type_valeur': 'pourcentage',
            'description': 'Taux du Versement Forfaitaire - 6% du brut (légal Guinée)',
            'actif': True,
            'date_debut_validite': timezone.now().date(),
        }
    )


def reverse_taux_ta(apps, schema_editor):
    pass  # Pas de rollback nécessaire


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0099_add_vf_ta_to_bulletin'),
    ]

    operations = [
        migrations.RunPython(set_taux_ta_default, reverse_taux_ta),
    ]
