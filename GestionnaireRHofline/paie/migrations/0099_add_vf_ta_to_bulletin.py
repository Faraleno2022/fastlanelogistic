from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0015_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinpaie',
            name='versement_forfaitaire',
            field=models.DecimalField(decimal_places=2, default=0, help_text='VF 6% sur brut total', max_digits=15),
        ),
        migrations.AddField(
            model_name='bulletinpaie',
            name='taxe_apprentissage',
            field=models.DecimalField(decimal_places=2, default=0, help_text='TA 1,5% sur brut total', max_digits=15),
        ),
    ]
