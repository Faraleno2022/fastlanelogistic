"""
Migration: Add 4 Audit models (Phase 2 Week 2).

Ajoute:
- RapportAudit: Rapports d'audit comptable
- AlerteNonConformite: Alertes de non-conformité
- ReglesConformite: Règles de conformité
- HistoriqueModification: Historique détaillé des modifications
"""

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comptabilite', '0003_fiscalite_models'),
        ('core', '0005_societe_entreprise'),
        ('core', '0001_initial'),
    ]

    operations = [
        # RapportAudit
        migrations.CreateModel(
            name='RapportAudit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('titre', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('date_publication', models.DateField(blank=True, null=True)),
                ('objectifs', models.TextField(help_text="Objectifs de l'audit")),
                ('perimetre', models.TextField(help_text="Périmètre de l'audit")),
                ('resultats', models.TextField(blank=True)),
                ('conclusion', models.TextField(blank=True)),
                ('recommandations', models.TextField(blank=True)),
                ('statut', models.CharField(
                    choices=[('PLANIFIE', 'Planifié'), ('EN_COURS', 'En cours'), ('TERMINE', 'Terminé'), ('PUBLIE', 'Publié')],
                    default='PLANIFIE',
                    max_length=20
                )),
                ('niveau_risque_global', models.CharField(
                    choices=[('FAIBLE', 'Faible'), ('MOYEN', 'Moyen'), ('ELEVE', 'Élevé'), ('CRITIQUE', 'Critique')],
                    default='MOYEN',
                    max_length=20
                )),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('auditeur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rapports_audites', to='core.utilisateur')),
                ('cree_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rapports_audit_crees', to='core.utilisateur')),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rapports_audit', to='core.entreprise')),
                ('responsable_correction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corrections_audit', to='core.utilisateur')),
            ],
            options={
                'verbose_name': "Rapport d'audit",
                'verbose_name_plural': "Rapports d'audit",
                'db_table': 'comptabilite_rapport_audit',
                'ordering': ['-date_debut'],
            },
        ),
        
        # AlerteNonConformite
        migrations.CreateModel(
            name='AlerteNonConformite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_alerte', models.CharField(max_length=50)),
                ('titre', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('severite', models.CharField(
                    choices=[('MINEURE', 'Mineure'), ('MAJEURE', 'Majeure'), ('CRITIQUE', 'Critique')],
                    max_length=20
                )),
                ('domaine', models.CharField(help_text='Domaine affecté: TVA, Comptabilité, etc.', max_length=100)),
                ('plan_action', models.TextField(blank=True)),
                ('date_correction_prevue', models.DateField(blank=True, null=True)),
                ('date_correction_reelle', models.DateField(blank=True, null=True)),
                ('statut', models.CharField(
                    choices=[('DETECTEE', 'Détectée'), ('EN_CORRECTION', 'En correction'), ('CORRIGEE', 'Corrigée'), ('VERIFIEE', 'Vérifiée'), ('ACCEPTEE', 'Acceptée')],
                    default='DETECTEE',
                    max_length=20
                )),
                ('observations', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertes_non_conformite', to='core.entreprise')),
                ('rapport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertes', to='comptabilite.rapportaudit')),
                ('responsable_correction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.utilisateur')),
            ],
            options={
                'verbose_name': 'Alerte de non-conformité',
                'verbose_name_plural': 'Alertes de non-conformité',
                'db_table': 'comptabilite_alerte_non_conformite',
                'ordering': ['-date_creation'],
            },
        ),
        
        # ReglesConformite
        migrations.CreateModel(
            name='ReglesConformite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('critere_conformite', models.TextField(help_text='Critère exact à vérifier')),
                ('consequence_non_conformite', models.TextField()),
                ('documentation_requise', models.TextField(blank=True)),
                ('periodicite', models.CharField(
                    choices=[('MENSUELLE', 'Mensuelle'), ('TRIMESTRIELLE', 'Trimestrielle'), ('SEMESTRIELLE', 'Semestrielle'), ('ANNUELLE', 'Annuelle'), ('A_LA_DEMANDE', 'À la demande')],
                    max_length=20
                )),
                ('module_concerne', models.CharField(help_text='TVA, Paie, Temps, etc.', max_length=100)),
                ('criticite', models.CharField(
                    choices=[('FAIBLE', 'Faible'), ('MOYEN', 'Moyen'), ('ELEVE', 'Élevé'), ('CRITIQUE', 'Critique')],
                    max_length=20
                )),
                ('actif', models.BooleanField(default=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('cree_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regles_conformite_creees', to='core.utilisateur')),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regles_conformite', to='core.entreprise')),
            ],
            options={
                'verbose_name': 'Règle de conformité',
                'verbose_name_plural': 'Règles de conformité',
                'db_table': 'comptabilite_regles_conformite',
                'ordering': ['module_concerne', 'code'],
            },
        ),
        
        # HistoriqueModification
        migrations.CreateModel(
            name='HistoriqueModification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type_objet', models.CharField(
                    choices=[
                        ('DECLARATION_TVA', 'Déclaration TVA'),
                        ('LIGNE_TVA', 'Ligne déclaration TVA'),
                        ('ECRITURE', 'Écriture comptable'),
                        ('FACTURE', 'Facture'),
                        ('REGLEMENT', 'Règlement'),
                        ('RAPPORT_AUDIT', "Rapport d'audit"),
                        ('ALERTE', 'Alerte non-conformité'),
                        ('AUTRE', 'Autre'),
                    ],
                    max_length=50
                )),
                ('id_objet', models.CharField(help_text='UUID ou ID de l\'objet modifié', max_length=100)),
                ('nom_objet', models.CharField(help_text='Nom/libellé de l\'objet', max_length=255)),
                ('action', models.CharField(
                    choices=[('CREATE', 'Création'), ('UPDATE', 'Modification'), ('DELETE', 'Suppression'), ('APPROVE', 'Approbation'), ('REJECT', 'Rejet'), ('REOPEN', 'Réouverture')],
                    max_length=20
                )),
                ('champ_modifie', models.CharField(blank=True, help_text='Champ spécifique modifié', max_length=100)),
                ('valeur_ancienne', models.TextField(blank=True)),
                ('valeur_nouvelle', models.TextField(blank=True)),
                ('description_modification', models.TextField(blank=True)),
                ('motif', models.CharField(blank=True, max_length=255)),
                ('reference', models.CharField(blank=True, help_text='Référence: N° ticket, N° demande, etc.', max_length=100)),
                ('date_modification', models.DateTimeField(auto_now_add=True)),
                ('ip_adresse', models.GenericIPAddressField(blank=True, null=True)),
                ('session_id', models.CharField(blank=True, max_length=255)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historiques_modification', to='core.entreprise')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='modifications_historique', to='core.utilisateur')),
            ],
            options={
                'verbose_name': 'Historique de modification',
                'verbose_name_plural': 'Historiques de modification',
                'db_table': 'comptabilite_historique_modification',
                'ordering': ['-date_modification'],
            },
        ),
        
        # Indexes
        migrations.AddIndex(
            model_name='rapportaudit',
            index=models.Index(fields=['entreprise', 'statut'], name='comptabilite_r_entrap_idx1'),
        ),
        migrations.AddIndex(
            model_name='rapportaudit',
            index=models.Index(fields=['date_debut'], name='comptabilite_r_date_d_idx'),
        ),
        migrations.AddIndex(
            model_name='rapportaudit',
            index=models.Index(fields=['code'], name='comptabilite_r_code_idx'),
        ),
        
        migrations.AddIndex(
            model_name='alertenonconformite',
            index=models.Index(fields=['entreprise', 'severite'], name='comptabilite_a_entrap_sever_idx'),
        ),
        migrations.AddIndex(
            model_name='alertenonconformite',
            index=models.Index(fields=['statut'], name='comptabilite_a_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='alertenonconformite',
            index=models.Index(fields=['date_correction_prevue'], name='comptabilite_a_date_c_idx'),
        ),
        
        migrations.AddIndex(
            model_name='reglesconformite',
            index=models.Index(fields=['entreprise', 'module_concerne'], name='comptabilite_r_entrap_mod_idx'),
        ),
        migrations.AddIndex(
            model_name='reglesconformite',
            index=models.Index(fields=['actif'], name='comptabilite_r_actif_idx'),
        ),
        
        migrations.AddIndex(
            model_name='historiquemodification',
            index=models.Index(fields=['entreprise', 'type_objet'], name='comptabilite_h_entrap_type_idx'),
        ),
        migrations.AddIndex(
            model_name='historiquemodification',
            index=models.Index(fields=['utilisateur', 'date_modification'], name='comptabilite_h_util_date_idx'),
        ),
        migrations.AddIndex(
            model_name='historiquemodification',
            index=models.Index(fields=['id_objet'], name='comptabilite_h_id_obj_idx'),
        ),
        migrations.AddIndex(
            model_name='historiquemodification',
            index=models.Index(fields=['date_modification'], name='comptabilite_h_date_m_idx'),
        ),
        
        # Unique constraints
        migrations.AlterUniqueTogether(
            name='alertenonconformite',
            unique_together={('rapport', 'numero_alerte')},
        ),
        migrations.AlterUniqueTogether(
            name='reglesconformite',
            unique_together={('entreprise', 'code')},
        ),
    ]
