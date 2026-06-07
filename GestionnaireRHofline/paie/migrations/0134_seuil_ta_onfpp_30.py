from decimal import Decimal
from datetime import date

from django.db import migrations


def appliquer_seuil_legal(apps, schema_editor):
    Constante = apps.get_model('paie', 'Constante')
    Constante.objects.update_or_create(
        code='SEUIL_TA_ONFPP',
        defaults={
            'libelle': 'Seuil TA / ONFPP',
            'valeur': Decimal('30.00'),
            'type_valeur': 'nombre',
            'categorie': 'general',
            'unite': 'salaries',
            'description': 'TA si effectif < 30 salaries ; contribution ONFPP si effectif >= 30 salaries',
            'date_debut_validite': date(2026, 1, 1),
            'actif': True,
        },
    )


def revenir_seuil_precedent(apps, schema_editor):
    Constante = apps.get_model('paie', 'Constante')
    Constante.objects.filter(code='SEUIL_TA_ONFPP').update(
        valeur=Decimal('25.00'),
        description='TA si effectif < 25 salaries ; contribution ONFPP si effectif >= 25 salaries',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0133_modele_standard_guineerh'),
    ]

    operations = [
        migrations.RunPython(appliquer_seuil_legal, revenir_seuil_precedent),
    ]
