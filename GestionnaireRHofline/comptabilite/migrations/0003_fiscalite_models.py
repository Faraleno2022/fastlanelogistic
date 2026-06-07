# Generated migration for Fiscalité/TVA models
# Phase 2 - Week 1 Implementation

import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comptabilite', '0002_analysecomparative_analyseimpayes_apiintegration_and_more'),
        ('core', '0010_entreprise_type_module'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegimeTVA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(help_text='Code unique: FR_NORMAL, FR_SIMPLIFIE', max_length=20, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('regime', models.CharField(choices=[('NORMAL', 'Normal'), ('SIMPLIFIE', 'Simplifié'), ('MICRO', 'Micro-entreprise'), ('EXEMPT', 'Exempté'), ('SERVICES', 'Services spécialisés')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('seuil_chiffre_affaires', models.DecimalField(blank=True, decimal_places=2, help_text='Seuil CA pour changement de régime', max_digits=15, null=True)),
                ('taux_normal', models.DecimalField(decimal_places=2, default=Decimal('20.00'), max_digits=5)),
                ('taux_reduit', models.DecimalField(decimal_places=2, default=Decimal('5.50'), max_digits=5)),
                ('taux_super_reduit', models.DecimalField(decimal_places=2, default=Decimal('2.10'), max_digits=5)),
                ('periodicite', models.CharField(choices=[('MENSUELLE', 'Mensuelle'), ('TRIMESTRIELLE', 'Trimestrielle'), ('ANNUELLE', 'Annuelle')], default='MENSUELLE', max_length=20)),
                ('actif', models.BooleanField(default=True)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regimes_tva', to='core.entreprise')),
                ('utilisateur_creation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regimes_tva_created', to=settings.AUTH_USER_MODEL)),
                ('utilisateur_modification', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regimes_tva_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Régime TVA',
                'verbose_name_plural': 'Régimes TVA',
                'db_table': 'comptabilite_regime_tva',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='TauxTVA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(help_text='TVA_NORMAL, TVA_5.5', max_length=20)),
                ('nom', models.CharField(max_length=100)),
                ('taux', models.DecimalField(decimal_places=2, help_text='Exemple: 20.00, 5.50', max_digits=5)),
                ('nature', models.CharField(choices=[('VENTE', 'Vente'), ('SERVICE', 'Service'), ('TRAVAUX', 'Travaux'), ('LIVRAISON', 'Livraison'), ('IMPORTATION', 'Importation')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('applicable_au_ventes', models.BooleanField(default=True)),
                ('applicable_aux_achats', models.BooleanField(default=True)),
                ('actif', models.BooleanField(default=True)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('regime_tva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taux', to='comptabilite.regimetva')),
                ('utilisateur_creation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='taux_tva_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Taux TVA',
                'verbose_name_plural': 'Taux TVA',
                'db_table': 'comptabilite_taux_tva',
                'ordering': ['-taux'],
                'unique_together': {('regime_tva', 'code')},
            },
        ),
        migrations.CreateModel(
            name='DeclarationTVA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('periode_debut', models.DateField()),
                ('periode_fin', models.DateField()),
                ('montant_ht', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('montant_tva_collecte', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('montant_tva_deductible', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('montant_tva_due', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15)),
                ('statut', models.CharField(choices=[('BROUILLON', 'Brouillon'), ('EN_COURS', 'En cours'), ('VALIDEE', 'Validée'), ('DEPOSEE', 'Déposée'), ('ACCEPTEE', 'Acceptée'), ('REJETEE', 'Rejetée')], default='BROUILLON', max_length=20)),
                ('date_depot', models.DateField(blank=True, null=True)),
                ('numero_depot', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='declarations_tva', to='core.entreprise')),
                ('exercice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations_tva', to='comptabilite.exercicecomptable')),
                ('regime_tva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations', to='comptabilite.regimetva')),
                ('utilisateur_creation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations_tva_created', to=settings.AUTH_USER_MODEL)),
                ('utilisateur_modification', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations_tva_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Déclaration TVA',
                'verbose_name_plural': 'Déclarations TVA',
                'db_table': 'comptabilite_declaration_tva',
                'ordering': ['-periode_debut'],
                'unique_together': {('entreprise', 'periode_debut', 'periode_fin')},
            },
        ),
        migrations.CreateModel(
            name='LigneDeclarationTVA',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_ligne', models.PositiveIntegerField(help_text='Numéro de ligne dans déclaration')),
                ('description', models.CharField(max_length=200)),
                ('montant_ht', models.DecimalField(decimal_places=2, max_digits=15)),
                ('montant_tva', models.DecimalField(decimal_places=2, max_digits=15)),
                ('type_ligne', models.CharField(choices=[('OPERATIONS', 'Opérations'), ('AJUSTEMENT', 'Ajustement'), ('CORRECTION', 'Correction'), ('OPTION', 'Option')], default='OPERATIONS', max_length=20)),
                ('compte_comptable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='comptabilite.plancomptable')),
                ('declaration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='comptabilite.declarationtva')),
                ('ecriture_comptable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lignes_tva', to='comptabilite.ecriturecomptable')),
                ('taux', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='comptabilite.tauxtva')),
            ],
            options={
                'verbose_name': 'Ligne déclaration TVA',
                'verbose_name_plural': 'Lignes déclaration TVA',
                'db_table': 'comptabilite_ligne_declaration_tva',
                'ordering': ['declaration', 'numero_ligne'],
                'unique_together': {('declaration', 'numero_ligne')},
            },
        ),
        migrations.AddIndex(
            model_name='regimetva',
            index=models.Index(fields=['entreprise', 'actif'], name='comptabilite_regime_tva_entreprise_actif_idx'),
        ),
        migrations.AddIndex(
            model_name='regimetva',
            index=models.Index(fields=['code'], name='comptabilite_regime_tva_code_idx'),
        ),
        migrations.AddIndex(
            model_name='declarationtva',
            index=models.Index(fields=['entreprise', 'statut'], name='comptabilite_declaration_tva_entreprise_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='declarationtva',
            index=models.Index(fields=['periode_debut'], name='comptabilite_declaration_tva_periode_debut_idx'),
        ),
    ]
