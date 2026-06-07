from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0129_regle_indemnite_conformite'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationpaieentreprise',
            name='arrondi_net',
            field=models.IntegerField(
                choices=[
                    (0, "Aucun (à l'unité GNF)"),
                    (100, 'Centaine de GNF'),
                    (500, 'Demi-millier (500 GNF)'),
                    (1000, 'Millier de GNF'),
                ],
                default=0,
                help_text="Arrondi appliqué uniquement sur le net final. "
                          "Les bases fiscales (CNSS, RTS) restent à l'unité.",
                verbose_name='Arrondi du net à payer',
            ),
        ),
    ]
