from django.db import migrations


def creer_plans_defaut(apps, schema_editor):
    """Créer les plans d'abonnement par défaut"""
    PlanAbonnement = apps.get_model('payments', 'PlanAbonnement')
    
    plans = [
        {
            'nom': 'Gratuit',
            'slug': 'gratuit',
            'description': 'Idéal pour découvrir la plateforme',
            'prix_mensuel': 0,
            'prix_annuel': 0,
            'max_utilisateurs': 1,
            'max_employes': 2,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': False,
            'module_formation': False,
            'support_prioritaire': False,
            'actif': True,
            'ordre': 1,
        },
        {
            'nom': 'Basique',
            'slug': 'basique',
            'description': 'Pour les petites entreprises',
            'prix_mensuel': 150000,
            'prix_annuel': 1500000,
            'max_utilisateurs': 5,
            'max_employes': 50,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': False,
            'module_formation': False,
            'support_prioritaire': False,
            'actif': True,
            'ordre': 2,
        },
        {
            'nom': 'Premium',
            'slug': 'premium',
            'description': 'Pour les entreprises en croissance',
            'prix_mensuel': 350000,
            'prix_annuel': 3500000,
            'max_utilisateurs': 15,
            'max_employes': 200,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': True,
            'module_formation': True,
            'support_prioritaire': True,
            'actif': True,
            'ordre': 3,
        },
        {
            'nom': 'Entreprise',
            'slug': 'entreprise',
            'description': 'Solution complète pour grandes entreprises',
            'prix_mensuel': 750000,
            'prix_annuel': 7500000,
            'max_utilisateurs': 50,
            'max_employes': 1000,
            'module_paie': True,
            'module_conges': True,
            'module_recrutement': True,
            'module_formation': True,
            'support_prioritaire': True,
            'actif': True,
            'ordre': 4,
        },
    ]
    
    for plan_data in plans:
        PlanAbonnement.objects.get_or_create(
            slug=plan_data['slug'],
            defaults=plan_data
        )


def supprimer_plans_defaut(apps, schema_editor):
    """Supprimer les plans par défaut"""
    PlanAbonnement = apps.get_model('payments', 'PlanAbonnement')
    PlanAbonnement.objects.filter(slug__in=['gratuit', 'basique', 'premium', 'entreprise']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(creer_plans_defaut, supprimer_plans_defaut),
    ]
