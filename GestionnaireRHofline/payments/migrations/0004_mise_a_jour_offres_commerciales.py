from django.db import migrations


def mettre_a_jour_offres(apps, schema_editor):
    """Mettre a jour les plans d'abonnement avec les 3 offres commerciales GuineeRH"""
    PlanAbonnement = apps.get_model('payments', 'PlanAbonnement')

    # Desactiver tous les anciens plans
    PlanAbonnement.objects.all().update(actif=False)

    plans = [
        {
            'nom': 'Starter',
            'slug': 'starter',
            'description': (
                "Solution de paie simple et efficace pour les petites entreprises. "
                "Bulletins de paie automatiques, gestion CNSS/RTS conforme, "
                "et export PDF professionnel."
            ),
            'sous_titre': 'Petites entreprises (1-30 employes)',
            'prix_mensuel': 200000,
            'prix_annuel': 2000000,
            'prix_installation': 1500000,
            'max_utilisateurs': 2,
            'max_employes': 30,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': False,
            'module_formation': False,
            'module_comptabilite': False,
            'module_portail': False,
            'support_prioritaire': False,
            'support_telephonique': False,
            'formation_incluse': False,
            'personnalisation': False,
            'multi_entreprise': False,
            'declarations_fiscales': False,
            'export_comptable': False,
            'badge': '',
            'couleur': '#198754',
            'icone': 'bi-rocket-takeoff',
            'actif': True,
            'ordre': 1,
        },
        {
            'nom': 'Pro',
            'slug': 'pro',
            'description': (
                "Solution complete pour les PME. Paie avancee avec declarations "
                "fiscales automatiques, gestion des conges, recrutement, "
                "export comptable et support technique dedié."
            ),
            'sous_titre': 'PME & entreprises en croissance (30-150 employes)',
            'prix_mensuel': 400000,
            'prix_annuel': 4000000,
            'prix_installation': 3000000,
            'max_utilisateurs': 10,
            'max_employes': 150,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': True,
            'module_formation': False,
            'module_comptabilite': False,
            'module_portail': False,
            'support_prioritaire': True,
            'support_telephonique': True,
            'formation_incluse': True,
            'personnalisation': False,
            'multi_entreprise': False,
            'declarations_fiscales': True,
            'export_comptable': True,
            'badge': 'Populaire',
            'couleur': '#EF7707',
            'icone': 'bi-briefcase-fill',
            'actif': True,
            'ordre': 2,
        },
        {
            'nom': 'Premium',
            'slug': 'premium',
            'description': (
                "Solution haut de gamme pour grandes entreprises. Multi-utilisateurs, "
                "portail employe, formation, comptabilite integree, personnalisation "
                "complete et assistance VIP avec formation sur site."
            ),
            'sous_titre': 'Grandes entreprises & groupes (150+ employes)',
            'prix_mensuel': 750000,
            'prix_annuel': 7500000,
            'prix_installation': 5000000,
            'max_utilisateurs': 50,
            'max_employes': 9999,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': True,
            'module_formation': True,
            'module_comptabilite': True,
            'module_portail': True,
            'support_prioritaire': True,
            'support_telephonique': True,
            'formation_incluse': True,
            'personnalisation': True,
            'multi_entreprise': True,
            'declarations_fiscales': True,
            'export_comptable': True,
            'badge': 'Recommande',
            'couleur': '#6f42c1',
            'icone': 'bi-gem',
            'actif': True,
            'ordre': 3,
        },
    ]

    for plan_data in plans:
        PlanAbonnement.objects.update_or_create(
            slug=plan_data['slug'],
            defaults=plan_data
        )


def revenir_anciens_plans(apps, schema_editor):
    """Revenir aux anciens plans"""
    PlanAbonnement = apps.get_model('payments', 'PlanAbonnement')
    PlanAbonnement.objects.filter(slug__in=['starter', 'pro']).delete()
    PlanAbonnement.objects.filter(slug__in=['gratuit', 'basique', 'premium', 'entreprise']).update(actif=True)


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_offres_commerciales_starter_pro_premium'),
    ]

    operations = [
        migrations.RunPython(mettre_a_jour_offres, revenir_anciens_plans),
    ]
