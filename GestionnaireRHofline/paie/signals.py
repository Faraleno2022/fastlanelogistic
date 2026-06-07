"""
Signaux pour le module de paie
Initialisation automatique des éléments de salaire pour les nouveaux employés
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from decimal import Decimal

from employes.models import Employe
from .models import ElementSalaire, RubriquePaie


@receiver(post_save, sender=Employe)
def creer_element_salaire_base(sender, instance, created, **kwargs):
    """
    Crée automatiquement un élément de salaire de base pour chaque nouvel employé.
    Utilise le salaire_base de l'employé s'il est défini, sinon un montant par défaut.
    """
    if created:
        # Chercher la rubrique de salaire de base
        rubrique_base = RubriquePaie.objects.filter(
            code_rubrique__icontains='SAL_BASE',
            type_rubrique='gain',
            actif=True
        ).first()
        
        # Si pas trouvée, chercher par libellé
        if not rubrique_base:
            rubrique_base = RubriquePaie.objects.filter(
                libelle_rubrique__icontains='Salaire de base',
                type_rubrique='gain',
                actif=True
            ).first()
        
        # Si toujours pas trouvée, créer la rubrique
        if not rubrique_base:
            rubrique_base, _ = RubriquePaie.objects.get_or_create(
                code_rubrique='SAL_BASE',
                defaults={
                    'libelle_rubrique': 'Salaire de base',
                    'type_rubrique': 'gain',
                    'soumis_cnss': True,
                    'soumis_irg': True,
                    'ordre_calcul': 10,
                    'ordre_affichage': 10,
                    'actif': True
                }
            )
        
        # Déterminer le montant du salaire de base
        # Utiliser le salaire_base de l'employé s'il existe, sinon le SMIG guinéen
        montant_base = Decimal('550000')  # SMIG par défaut
        
        if hasattr(instance, 'salaire_base') and instance.salaire_base:
            montant_base = instance.salaire_base
        
        # Créer l'élément de salaire de base
        ElementSalaire.objects.get_or_create(
            employe=instance,
            rubrique=rubrique_base,
            defaults={
                'montant': montant_base,
                'date_debut': instance.date_embauche or date.today(),
                'actif': True,
                'recurrent': True
            }
        )
