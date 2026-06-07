from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('paie', '0121_type_bareme_tranche_rts'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimulationFiscale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_simulation', models.DateTimeField(default=django.utils.timezone.now)),
                ('salaire_brut', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_indemnites', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('label', models.CharField(blank=True, max_length=200)),
                ('baremes_compares', models.JSONField(default=list, help_text='Labels lisibles des barèmes comparés')),
                ('parametres_json', models.JSONField(default=dict, help_text='Snapshot barèmes + constantes utilisés')),
                ('resultats_json', models.JSONField(default=list, help_text='Résultats comparatifs par barème')),
                ('notes', models.TextField(blank=True)),
                ('entreprise', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='simulations_fiscales',
                    to='core.entreprise',
                )),
                ('utilisateur', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='simulations_fiscales',
                    to='core.utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Simulation fiscale',
                'verbose_name_plural': 'Simulations fiscales',
                'db_table': 'simulations_fiscales',
                'ordering': ['-date_simulation'],
            },
        ),
        migrations.AddIndex(
            model_name='simulationfiscale',
            index=models.Index(fields=['entreprise', 'date_simulation'], name='idx_sim_entrep_date'),
        ),
    ]
