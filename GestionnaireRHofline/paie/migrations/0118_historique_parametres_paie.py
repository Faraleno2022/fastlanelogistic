from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('paie', '0117_parametres_calcul_paie'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoriqueParametresPaie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_modification', models.DateTimeField(auto_now_add=True)),
                ('champ_modifie', models.CharField(max_length=100)),
                ('ancienne_valeur', models.TextField(blank=True)),
                ('nouvelle_valeur', models.TextField(blank=True)),
                ('raison', models.CharField(blank=True, max_length=200)),
                ('modifie_par', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='core.utilisateur',
                )),
                ('parametres', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='historique',
                    to='paie.parametrescalculpaie',
                )),
            ],
            options={
                'verbose_name': 'Historique paramètres paie',
                'verbose_name_plural': 'Historiques paramètres paie',
                'db_table': 'historique_parametres_paie',
                'ordering': ['-date_modification'],
            },
        ),
    ]
