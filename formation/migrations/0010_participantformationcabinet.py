from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_licence_licencelocale'),
        ('formation', '0009_inscriptionformation_idx_inscription_sess_stat_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantFormationCabinet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_participant', models.CharField(max_length=200)),
                ('titre_formation', models.CharField(max_length=255)),
                ('date_formation', models.DateField()),
                ('numero_identite_attestation', models.CharField(max_length=100)),
                ('date_enregistrement', models.DateTimeField(auto_now_add=True)),
                ('observations', models.TextField(blank=True, null=True)),
                ('entreprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants_formations_cabinet', to='core.entreprise')),
            ],
            options={
                'verbose_name': 'Participant formation cabinet',
                'verbose_name_plural': 'Participants formations cabinet',
                'db_table': 'participants_formations_cabinet',
                'ordering': ['-date_formation', 'nom_participant'],
                'unique_together': {('entreprise', 'numero_identite_attestation')},
            },
        ),
        migrations.AddIndex(
            model_name='participantformationcabinet',
            index=models.Index(fields=['entreprise', 'date_formation'], name='idx_part_form_cab_date'),
        ),
        migrations.AddIndex(
            model_name='participantformationcabinet',
            index=models.Index(fields=['entreprise', 'numero_identite_attestation'], name='idx_part_form_cab_att'),
        ),
    ]
