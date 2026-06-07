from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0115_ajout_categorie_mode_calcul_rubriques'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinpaie',
            name='heures_feries_nuit',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Heures jours fériés (nuit) à +100%', max_digits=6),
        ),
        migrations.AddField(
            model_name='bulletinpaie',
            name='prime_feries_nuit',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Prime jours fériés (nuit)', max_digits=15),
        ),
    ]
