"""
Service pour l'interface CNSS et la génération des déclarations
"""
import csv
import io
import json
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum
from core.models import ConfigurationCNSS, TransmissionCNSS, Entreprise


class CNSSService:
    """Service pour la gestion des déclarations CNSS"""
    
    def __init__(self, entreprise):
        self.entreprise = entreprise
        self.config = self._get_config()
    
    def _get_config(self):
        """Récupère la configuration CNSS de l'entreprise"""
        try:
            return ConfigurationCNSS.objects.get(entreprise=self.entreprise)
        except ConfigurationCNSS.DoesNotExist:
            return None
    
    def generer_declaration(self, mois, annee):
        """
        Génère une déclaration CNSS pour une période donnée
        
        Args:
            mois: Mois de la période (1-12)
            annee: Année de la période
        
        Returns:
            TransmissionCNSS: L'objet de transmission créé
        """
        from paie.models import BulletinPaie
        
        # Récupérer les bulletins de la période
        bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            periode__mois=mois,
            periode__annee=annee,
            statut_bulletin='valide'
        ).select_related('employe', 'periode')
        
        # Calculer les totaux
        totaux = bulletins.aggregate(
            masse_salariale=Sum('salaire_brut'),
            cotisation_employe=Sum('cnss_employe'),
            cotisation_employeur=Sum('cnss_employeur')
        )
        
        # Créer ou mettre à jour la transmission
        reference = f"CNSS-{self.entreprise.id}-{annee}{mois:02d}"
        
        transmission, created = TransmissionCNSS.objects.update_or_create(
            entreprise=self.entreprise,
            periode_mois=mois,
            periode_annee=annee,
            defaults={
                'reference': reference,
                'nombre_salaries': bulletins.count(),
                'masse_salariale_brute': totaux['masse_salariale'] or Decimal('0'),
                'base_cnss_totale': totaux['masse_salariale'] or Decimal('0'),
                'cotisation_employe': totaux['cotisation_employe'] or Decimal('0'),
                'cotisation_employeur': totaux['cotisation_employeur'] or Decimal('0'),
                'total_cotisations': (totaux['cotisation_employe'] or Decimal('0')) + 
                                     (totaux['cotisation_employeur'] or Decimal('0')),
                'statut': 'brouillon',
                'date_generation': timezone.now()
            }
        )
        
        return transmission
    
    def generer_fichier_csv(self, transmission):
        """
        Génère le fichier CSV pour la déclaration CNSS
        
        Format standard CNSS Guinée:
        - Numéro employeur
        - Période (MM/AAAA)
        - Matricule employé
        - Nom
        - Prénoms
        - Date naissance
        - Numéro CNSS employé
        - Salaire brut
        - Base CNSS
        - Cotisation employé
        - Cotisation employeur
        """
        from paie.models import BulletinPaie
        
        bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            periode__mois=transmission.periode_mois,
            periode__annee=transmission.periode_annee,
            statut_bulletin='valide'
        ).select_related('employe')
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-tête
        writer.writerow([
            'NUM_EMPLOYEUR',
            'PERIODE',
            'MATRICULE',
            'NOM',
            'PRENOMS',
            'DATE_NAISSANCE',
            'NUM_CNSS',
            'SALAIRE_BRUT',
            'BASE_CNSS',
            'COTIS_EMPLOYE',
            'COTIS_EMPLOYEUR'
        ])
        
        # Données
        num_employeur = self.config.numero_employeur if self.config else ''
        periode = f"{transmission.periode_mois:02d}/{transmission.periode_annee}"
        
        for bulletin in bulletins:
            emp = bulletin.employe
            writer.writerow([
                num_employeur,
                periode,
                emp.matricule,
                emp.nom,
                emp.prenoms,
                emp.date_naissance.strftime('%d/%m/%Y') if emp.date_naissance else '',
                emp.numero_cnss or '',
                f"{bulletin.salaire_brut:.2f}",
                f"{bulletin.cnss_base:.2f}",
                f"{bulletin.cnss_employe:.2f}",
                f"{bulletin.cnss_employeur:.2f}"
            ])
        
        return output.getvalue()
    
    def generer_fichier_xml(self, transmission):
        """Génère le fichier XML pour la déclaration CNSS"""
        from paie.models import BulletinPaie
        import xml.etree.ElementTree as ET
        
        bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            periode__mois=transmission.periode_mois,
            periode__annee=transmission.periode_annee,
            statut_bulletin='valide'
        ).select_related('employe')
        
        # Créer la structure XML
        root = ET.Element('DeclarationCNSS')
        root.set('version', '1.0')
        
        # En-tête
        header = ET.SubElement(root, 'Entete')
        ET.SubElement(header, 'NumeroEmployeur').text = self.config.numero_employeur if self.config else ''
        ET.SubElement(header, 'Periode').text = f"{transmission.periode_annee}-{transmission.periode_mois:02d}"
        ET.SubElement(header, 'DateGeneration').text = datetime.now().isoformat()
        ET.SubElement(header, 'NombreEmployes').text = str(transmission.nombre_salaries)
        
        # Totaux
        totaux = ET.SubElement(root, 'Totaux')
        ET.SubElement(totaux, 'MasseSalariale').text = f"{transmission.masse_salariale_brute:.2f}"
        ET.SubElement(totaux, 'BaseCNSS').text = f"{transmission.base_cnss_totale:.2f}"
        ET.SubElement(totaux, 'CotisationEmploye').text = f"{transmission.cotisation_employe:.2f}"
        ET.SubElement(totaux, 'CotisationEmployeur').text = f"{transmission.cotisation_employeur:.2f}"
        ET.SubElement(totaux, 'TotalCotisations').text = f"{transmission.total_cotisations:.2f}"
        
        # Détail des employés
        employes = ET.SubElement(root, 'Employes')
        for bulletin in bulletins:
            emp = bulletin.employe
            employe_elem = ET.SubElement(employes, 'Employe')
            ET.SubElement(employe_elem, 'Matricule').text = emp.matricule
            ET.SubElement(employe_elem, 'Nom').text = emp.nom
            ET.SubElement(employe_elem, 'Prenoms').text = emp.prenoms
            ET.SubElement(employe_elem, 'DateNaissance').text = emp.date_naissance.strftime('%Y-%m-%d') if emp.date_naissance else ''
            ET.SubElement(employe_elem, 'NumeroCNSS').text = emp.numero_cnss or ''
            ET.SubElement(employe_elem, 'SalaireBrut').text = f"{bulletin.salaire_brut:.2f}"
            ET.SubElement(employe_elem, 'BaseCNSS').text = f"{bulletin.cnss_base:.2f}"
            ET.SubElement(employe_elem, 'CotisationEmploye').text = f"{bulletin.cnss_employe:.2f}"
            ET.SubElement(employe_elem, 'CotisationEmployeur').text = f"{bulletin.cnss_employeur:.2f}"
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def generer_fichier_json(self, transmission):
        """Génère le fichier JSON pour la déclaration CNSS"""
        from paie.models import BulletinPaie
        
        bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            periode__mois=transmission.periode_mois,
            periode__annee=transmission.periode_annee,
            statut_bulletin='valide'
        ).select_related('employe')
        
        data = {
            'declaration': {
                'numero_employeur': self.config.numero_employeur if self.config else '',
                'periode': {
                    'mois': transmission.periode_mois,
                    'annee': transmission.periode_annee
                },
                'date_generation': datetime.now().isoformat(),
                'totaux': {
                    'nombre_employes': transmission.nombre_salaries,
                    'masse_salariale': float(transmission.masse_salariale_brute),
                    'base_cnss': float(transmission.base_cnss_totale),
                    'cotisation_employe': float(transmission.cotisation_employe),
                    'cotisation_employeur': float(transmission.cotisation_employeur),
                    'total_cotisations': float(transmission.total_cotisations)
                },
                'employes': []
            }
        }
        
        for bulletin in bulletins:
            emp = bulletin.employe
            data['declaration']['employes'].append({
                'matricule': emp.matricule,
                'nom': emp.nom,
                'prenoms': emp.prenoms,
                'date_naissance': emp.date_naissance.strftime('%Y-%m-%d') if emp.date_naissance else None,
                'numero_cnss': emp.numero_cnss,
                'salaire_brut': float(bulletin.salaire_brut),
                'base_cnss': float(bulletin.salaire_brut),
                'cotisation_employe': float(bulletin.cnss_employe),
                'cotisation_employeur': float(bulletin.cnss_employeur)
            })
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def generer_fichier(self, transmission):
        """
        Génère le fichier de déclaration selon le format configuré
        """
        if not self.config:
            format_fichier = 'csv'
        else:
            format_fichier = self.config.format_fichier
        
        if format_fichier == 'csv':
            contenu = self.generer_fichier_csv(transmission)
            extension = 'csv'
        elif format_fichier == 'xml':
            contenu = self.generer_fichier_xml(transmission)
            extension = 'xml'
        else:
            contenu = self.generer_fichier_json(transmission)
            extension = 'json'
        
        return contenu, extension
    
    def valider_declaration(self, transmission):
        """
        Valide les données de la déclaration avant transmission
        
        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        
        # Vérifier la configuration
        if not self.config:
            errors.append("Configuration CNSS non définie pour cette entreprise")
        elif not self.config.numero_employeur:
            errors.append("Numéro employeur CNSS non renseigné")
        
        # Vérifier les données
        if transmission.nombre_salaries == 0:
            errors.append("Aucun salarié dans la déclaration")
        
        if transmission.base_cnss_totale <= 0:
            errors.append("Base CNSS totale invalide")
        
        # Vérifier les numéros CNSS des employés
        from paie.models import BulletinPaie
        bulletins = BulletinPaie.objects.filter(
            employe__entreprise=self.entreprise,
            periode__mois=transmission.periode_mois,
            periode__annee=transmission.periode_annee,
            statut_bulletin='valide'
        ).select_related('employe')
        
        employes_sans_cnss = [b.employe.nom_complet for b in bulletins if not b.employe.numero_cnss]
        if employes_sans_cnss:
            errors.append(f"Employés sans numéro CNSS: {', '.join(employes_sans_cnss[:5])}")
            if len(employes_sans_cnss) > 5:
                errors.append(f"... et {len(employes_sans_cnss) - 5} autres")
        
        return len(errors) == 0, errors
    
    def marquer_transmis(self, transmission):
        """Marque la déclaration comme transmise"""
        transmission.statut = 'transmis'
        transmission.date_transmission = timezone.now()
        transmission.save()
        return transmission
