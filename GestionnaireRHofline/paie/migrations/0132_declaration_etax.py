# Generated manually for eTax declaration tracking.

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paie', '0131_merge_0130_add_arrondi_net_0130_simulationfiscale'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeclarationEtax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee', models.IntegerField()),
                ('mois', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('reference', models.CharField(max_length=60, unique=True)),
                ('effectif_declare', models.IntegerField(default=0)),
                ('total_brut', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_net', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_base_rts', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_rts', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_vf', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_ta', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_onfpp', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_fiscal', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_cnss_employe', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_cnss_employeur', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_cnss', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('total_general', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('generee', 'Générée'), ('declaree', 'Déclarée sur eTax'), ('payee', 'Payée'), ('rejetee', 'Rejetée')], default='brouillon', max_length=20)),
                ('reference_etax', models.CharField(blank=True, max_length=100, null=True)),
                ('date_generation', models.DateTimeField(blank=True, null=True)),
                ('date_declaration', models.DateField(blank=True, null=True)),
                ('date_paiement', models.DateField(blank=True, null=True)),
                ('fichier_pdf', models.FileField(blank=True, null=True, upload_to='declarations/etax/pdf/')),
                ('fichier_excel', models.FileField(blank=True, null=True, upload_to='declarations/etax/excel/')),
                ('fichier_recu', models.FileField(blank=True, null=True, upload_to='declarations/etax/recus/')),
                ('observations', models.TextField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='declarations_etax', to='core.entreprise')),
                ('genere_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='declarations_etax_generees', to=settings.AUTH_USER_MODEL)),
                ('periode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='declarations_etax', to='paie.periodepaie')),
            ],
            options={
                'verbose_name': 'Déclaration eTax',
                'verbose_name_plural': 'Déclarations eTax',
                'db_table': 'declarations_etax',
                'ordering': ['-annee', '-mois'],
                'unique_together': {('entreprise', 'annee', 'mois')},
            },
        ),
    ]
