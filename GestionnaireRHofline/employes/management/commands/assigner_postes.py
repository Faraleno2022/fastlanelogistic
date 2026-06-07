from django.core.management.base import BaseCommand
from employes.models import Employe
from core.models import Poste, Service


class Command(BaseCommand):
    help = 'Créer des postes et les assigner aux employés sans poste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Réassigner même les employés qui ont déjà un poste',
        )
        parser.add_argument(
            '--poste-defaut',
            type=str,
            default='Employé',
            help='Intitulé du poste par défaut (défaut: Employé)',
        )

    def handle(self, *args, **options):
        force = options['force']
        poste_defaut = options['poste_defaut']
        
        # Créer les postes de base s'ils n'existent pas
        postes_base = [
            ('DG', 'Directeur Général', 'cadre'),
            ('DRH', 'Directeur des Ressources Humaines', 'cadre'),
            ('DAF', 'Directeur Administratif et Financier', 'cadre'),
            ('COMPT', 'Comptable', 'maitrise'),
            ('ASSIST', 'Assistant(e)', 'employe'),
            ('TECH', 'Technicien', 'ouvrier'),
            ('SECR', 'Secrétaire', 'employe'),
            ('CHAUF', 'Chauffeur', 'ouvrier'),
            ('AGENT', 'Agent', 'ouvrier'),
            ('EMP', 'Employé', 'employe'),
        ]
        
        self.stdout.write(self.style.MIGRATE_HEADING('Création des postes de base...'))
        
        for code, intitule, categorie in postes_base:
            poste, created = Poste.objects.get_or_create(
                code_poste=code,
                defaults={
                    'intitule_poste': intitule,
                    'categorie_professionnelle': categorie,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Poste créé: {intitule}'))
            else:
                self.stdout.write(f'  - Poste existant: {intitule}')
        
        # Récupérer ou créer le poste par défaut
        poste_default, _ = Poste.objects.get_or_create(
            intitule_poste=poste_defaut,
            defaults={'code_poste': poste_defaut[:10].upper().replace(' ', '_')}
        )
        
        # Assigner les postes aux employés
        self.stdout.write(self.style.MIGRATE_HEADING('\nAssignation des postes aux employés...'))
        
        if force:
            employes = Employe.objects.all()
        else:
            employes = Employe.objects.filter(poste__isnull=True)
        
        count = 0
        for employe in employes:
            # Essayer de deviner le poste basé sur le nom ou attribuer le défaut
            poste_assigne = self._deviner_poste(employe) or poste_default
            
            employe.poste = poste_assigne
            employe.save(update_fields=['poste'])
            count += 1
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ {employe.matricule} - {employe.nom} {employe.prenoms} → {poste_assigne.intitule_poste}')
            )
        
        if count == 0:
            self.stdout.write(self.style.WARNING('\n  Aucun employé à mettre à jour (tous ont déjà un poste)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {count} employé(s) mis à jour'))
        
        # Afficher un résumé
        self.stdout.write(self.style.MIGRATE_HEADING('\nRésumé:'))
        for poste in Poste.objects.all():
            nb = Employe.objects.filter(poste=poste).count()
            if nb > 0:
                self.stdout.write(f'  {poste.intitule_poste}: {nb} employé(s)')

    def _deviner_poste(self, employe):
        """Essayer de deviner le poste basé sur les informations disponibles"""
        # Si l'employé a un service, on peut essayer de deviner
        nom_complet = f"{employe.nom} {employe.prenoms}".lower()
        
        # Règles simples de déduction
        if 'directeur' in nom_complet or 'dg' in nom_complet:
            return Poste.objects.filter(code_poste='DG').first()
        
        if 'comptable' in nom_complet:
            return Poste.objects.filter(code_poste='COMPT').first()
        
        if 'assistant' in nom_complet or 'secrétaire' in nom_complet:
            return Poste.objects.filter(code_poste='ASSIST').first()
        
        if 'technicien' in nom_complet:
            return Poste.objects.filter(code_poste='TECH').first()
        
        if 'chauffeur' in nom_complet:
            return Poste.objects.filter(code_poste='CHAUF').first()
        
        # Par défaut, retourner None pour utiliser le poste par défaut
        return None
