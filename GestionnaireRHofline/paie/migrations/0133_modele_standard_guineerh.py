from django.db import migrations, models


def appliquer_modele_standard_aux_configs_legacy(apps, schema_editor):
    ParametresCalculPaie = apps.get_model('paie', 'ParametresCalculPaie')
    ParametresCalculPaie.objects.filter(
        mode_base_vf='brut',
        formule_base_vf='',
    ).update(mode_base_vf='brut_moins_deduction')


def revenir_base_brut(apps, schema_editor):
    ParametresCalculPaie = apps.get_model('paie', 'ParametresCalculPaie')
    ParametresCalculPaie.objects.filter(
        mode_base_vf='brut_moins_deduction',
        formule_base_vf='',
    ).update(mode_base_vf='brut')


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0132_declaration_etax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametrescalculpaie',
            name='mode_base_vf',
            field=models.CharField(
                choices=[
                    ('brut', 'Brut direct (simplifié)'),
                    ('brut_moins_deduction', 'Modèle standard GuinéeRH : brut − déduction CGI plafonnée'),
                    ('formule', 'Formule personnalisée'),
                ],
                default='brut_moins_deduction',
                max_length=30,
            ),
        ),
        migrations.RunPython(appliquer_modele_standard_aux_configs_legacy, revenir_base_brut),
    ]
