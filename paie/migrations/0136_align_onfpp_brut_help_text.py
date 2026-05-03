from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0135_merge_20260430_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulletinpaie',
            name='contribution_onfpp',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='ONFPP 1,5% sur salaire brut',
                max_digits=15,
            ),
        ),
        migrations.AlterField(
            model_name='bulletinpaie',
            name='taxe_apprentissage',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='TA 2% sur base VF',
                max_digits=15,
            ),
        ),
        migrations.AlterField(
            model_name='bulletinpaie',
            name='versement_forfaitaire',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='VF 6% sur base VF',
                max_digits=15,
            ),
        ),
    ]
