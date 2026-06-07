"""
Service d'archivage des bulletins de paie
Conservation légale : 10 ans minimum
"""
import hashlib
import io
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import BulletinPaie, ArchiveBulletin


class ArchivageService:
    """Service de gestion des archives de bulletins"""
    
    @staticmethod
    def calculer_hash(contenu_pdf):
        """Calcule le hash SHA256 du fichier PDF"""
        return hashlib.sha256(contenu_pdf).hexdigest()
    
    @staticmethod
    def archiver_bulletin(bulletin, contenu_pdf):
        """
        Archive un bulletin de paie avec son PDF
        
        Args:
            bulletin: Instance BulletinPaie
            contenu_pdf: Bytes du fichier PDF
            
        Returns:
            ArchiveBulletin créé ou existant
        """
        # Vérifier si déjà archivé
        if hasattr(bulletin, 'archive'):
            return bulletin.archive
        
        # Calculer le hash pour l'intégrité
        hash_fichier = ArchivageService.calculer_hash(contenu_pdf)
        
        # Créer le nom du fichier
        nom_fichier = f"bulletin_{bulletin.employe.matricule}_{bulletin.annee_paie}{bulletin.mois_paie:02d}.pdf"
        
        # Créer l'archive
        archive = ArchiveBulletin.objects.create(
            bulletin=bulletin,
            taille_fichier=len(contenu_pdf),
            hash_fichier=hash_fichier,
            employe_matricule=bulletin.employe.matricule,
            employe_nom=f"{bulletin.employe.nom} {bulletin.employe.prenoms}",
            periode_annee=bulletin.annee_paie,
            periode_mois=bulletin.mois_paie,
            montant_net=bulletin.net_a_payer,
        )
        
        # Sauvegarder le fichier PDF
        archive.fichier_pdf.save(nom_fichier, ContentFile(contenu_pdf))
        
        return archive
    
    @staticmethod
    def verifier_integrite(archive):
        """
        Vérifie l'intégrité d'une archive en comparant les hash
        
        Returns:
            bool: True si intégrité OK
        """
        if not archive.fichier_pdf:
            return False
        
        with archive.fichier_pdf.open('rb') as f:
            contenu = f.read()
        
        hash_actuel = ArchivageService.calculer_hash(contenu)
        return hash_actuel == archive.hash_fichier
    
    @staticmethod
    def archiver_periode(periode):
        """
        Archive tous les bulletins validés d'une période
        
        Returns:
            dict: Statistiques d'archivage
        """
        from .utils import generer_bulletin_pdf
        
        bulletins = BulletinPaie.objects.filter(
            periode=periode,
            statut_bulletin__in=['valide', 'paye']
        ).exclude(archive__isnull=False)
        
        stats = {'archivés': 0, 'erreurs': 0, 'deja_archives': 0}
        
        for bulletin in bulletins:
            try:
                # Générer le PDF
                contenu_pdf = generer_bulletin_pdf(bulletin)
                
                # Archiver
                ArchivageService.archiver_bulletin(bulletin, contenu_pdf)
                stats['archivés'] += 1
                
            except Exception as e:
                stats['erreurs'] += 1
                print(f"Erreur archivage bulletin {bulletin.numero_bulletin}: {e}")
        
        return stats
    
    @staticmethod
    def telecharger_archive(archive):
        """
        Télécharge une archive et met à jour les statistiques
        
        Returns:
            bytes: Contenu du PDF
        """
        if not archive.fichier_pdf:
            return None
        
        # Mettre à jour les stats
        archive.nombre_telechargements += 1
        archive.dernier_telechargement = timezone.now()
        archive.save(update_fields=['nombre_telechargements', 'dernier_telechargement'])
        
        with archive.fichier_pdf.open('rb') as f:
            return f.read()
    
    @staticmethod
    def stats_archives(entreprise):
        """Statistiques des archives pour une entreprise"""
        from django.db.models import Sum, Count
        
        archives = ArchiveBulletin.objects.filter(
            bulletin__employe__entreprise=entreprise
        )
        
        return archives.aggregate(
            total_archives=Count('id'),
            total_taille=Sum('taille_fichier'),
            total_telechargements=Sum('nombre_telechargements'),
        )
