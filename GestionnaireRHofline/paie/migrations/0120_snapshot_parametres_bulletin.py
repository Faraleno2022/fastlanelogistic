from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0119_alter_bulletinpaie_heures_feries_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinpaie',
            name='snapshot_parametres',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text='Paramètres figés au calcul : constantes, barème RTS, config entreprise'
            ),
        ),
    ]
