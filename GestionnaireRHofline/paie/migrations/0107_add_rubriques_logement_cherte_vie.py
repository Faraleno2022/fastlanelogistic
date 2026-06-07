"""
Ajouter les rubriques Prime de Logement et Prime de cherté de vie
"""
from django.db import migrations


def ajouter_rubriques(apps, schema_editor):
    RubriquePaie = apps.get_model('paie', 'RubriquePaie')
    
    rubriques = [
        {
            'code_rubrique': 'PL',
            'libelle_rubrique': 'Prime de Logement',
            'type_rubrique': 'gain',
            'formule_calcul': '',
            'taux_rubrique': None,
            'montant_fixe': None,
            'soumis_cnss': True,
            'soumis_irg': False,
            'ordre_calcul': 20,
            'ordre_affichage': 20,
            'affichage_bulletin': True,
            'actif': True,
        },
        {
            'code_rubrique': 'PCV',
            'libelle_rubrique': 'Prime de cherté de vie',
            'type_rubrique': 'gain',
            'formule_calcul': '',
            'taux_rubrique': None,
            'montant_fixe': None,
            'soumis_cnss': True,
            'soumis_irg': True,
            'ordre_calcul': 21,
            'ordre_affichage': 21,
            'affichage_bulletin': True,
            'actif': True,
        },
    ]
    
    for rub in rubriques:
        RubriquePaie.objects.get_or_create(
            code_rubrique=rub['code_rubrique'],
            defaults=rub,
        )


def supprimer_rubriques(apps, schema_editor):
    RubriquePaie = apps.get_model('paie', 'RubriquePaie')
    RubriquePaie.objects.filter(code_rubrique__in=['PL', 'PCV']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0106_add_base_rts_taux_effectif_rts'),
    ]

    operations = [
        migrations.RunPython(ajouter_rubriques, supprimer_rubriques),
    ]
