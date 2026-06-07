from django.db import migrations
from decimal import Decimal


def fix_taux_ta(apps, schema_editor):
    """Corriger le taux TA à 2% (au lieu de 1.5%) dans Constante et ConfigPaieEntreprise."""
    Constante = apps.get_model('paie', 'Constante')
    Constante.objects.filter(code='TAUX_TA').update(valeur=Decimal('2.00'))

    try:
        ConfigPaieEntreprise = apps.get_model('paie', 'ConfigPaieEntreprise')
        ConfigPaieEntreprise.objects.filter(taux_taxe_apprentissage=Decimal('1.50')).update(
            taux_taxe_apprentissage=Decimal('2.00')
        )
    except Exception:
        pass


def revert_taux_ta(apps, schema_editor):
    Constante = apps.get_model('paie', 'Constante')
    Constante.objects.filter(code='TAUX_TA').update(valeur=Decimal('1.50'))

    try:
        ConfigPaieEntreprise = apps.get_model('paie', 'ConfigPaieEntreprise')
        ConfigPaieEntreprise.objects.filter(taux_taxe_apprentissage=Decimal('2.00')).update(
            taux_taxe_apprentissage=Decimal('1.50')
        )
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0112_add_taux_ta_bulletin'),
    ]

    operations = [
        migrations.RunPython(fix_taux_ta, revert_taux_ta),
    ]
