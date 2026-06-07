from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('paie', '0116_ajout_heures_feries_nuit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParametresCalculPaie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode_exoneration_indemnites', models.CharField(
                    choices=[
                        ('plafond_pct', 'Plafond % du brut (CGI strict)'),
                        ('integrale', 'Exonération intégrale'),
                        ('formule', 'Formule personnalisée'),
                    ],
                    default='plafond_pct',
                    max_length=20,
                )),
                ('plafond_exoneration_pct', models.DecimalField(
                    decimal_places=2,
                    default=25,
                    help_text='Plafond % du brut (défaut CGI: 25%)',
                    max_digits=5,
                )),
                ('formule_exoneration', models.TextField(
                    blank=True,
                    help_text='Ex: brut * 0.25 ou indemnites if indemnites <= brut * 0.3 else brut * 0.3',
                )),
                ('mode_base_vf', models.CharField(
                    choices=[
                        ('brut', 'Brut direct (simplifié)'),
                        ('brut_moins_deduction', 'Brut − déduction fixe (si brut≥2.5M: −150000)'),
                        ('formule', 'Formule personnalisée'),
                    ],
                    default='brut',
                    max_length=30,
                )),
                ('formule_base_vf', models.TextField(
                    blank=True,
                    help_text='Ex: brut - 150000 if brut >= 2500000 else brut * 0.94',
                )),
                ('utiliser_formule_base_rts', models.BooleanField(default=False)),
                ('formule_base_rts', models.TextField(
                    blank=True,
                    help_text='Ex: brut - cnss - (indemnites if indemnites <= brut*0.25 else brut*0.25)',
                )),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parametres_calcul_paie',
                    to='core.entreprise',
                )),
            ],
            options={
                'verbose_name': 'Paramètres calcul paie',
                'verbose_name_plural': 'Paramètres calcul paie',
                'db_table': 'parametres_calcul_paie',
            },
        ),
    ]
