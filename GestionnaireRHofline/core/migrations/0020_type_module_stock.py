from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_type_module_secretariat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entreprise',
            name='type_module',
            field=models.CharField(
                max_length=20,
                default='rh',
                verbose_name='Type de compte',
                choices=[
                    ('rh', 'Ressources Humaines'),
                    ('compta', 'Comptabilité'),
                    ('secretariat', 'Secrétariat'),
                    ('stock', 'Gestion de stock'),
                    ('both', 'RH + Comptabilité'),
                ],
            ),
        ),
    ]
