from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0105_update_ta_2_pourcent'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinpaie',
            name='base_rts',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Base imposable RTS', max_digits=15),
        ),
        migrations.AddField(
            model_name='bulletinpaie',
            name='taux_effectif_rts',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Taux effectif RTS en %', max_digits=5),
        ),
    ]
