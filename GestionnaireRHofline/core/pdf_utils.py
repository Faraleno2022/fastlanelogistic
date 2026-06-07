"""
Utilitaires pour la génération de PDF avec logo en filigrane
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os


def add_watermark_logo(pdf_canvas, logo_path, opacity=0.1):
    """
    Ajoute un logo en filigrane au centre d'une page PDF
    
    Args:
        pdf_canvas: Canvas ReportLab
        logo_path: Chemin vers le fichier logo
        opacity: Opacité du filigrane (0.0 à 1.0)
    """
    if not logo_path or not os.path.exists(logo_path):
        return
    
    try:
        # Ouvrir l'image
        img = Image.open(logo_path)
        
        # Convertir en RGBA si nécessaire
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Ajuster l'opacité
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        img.putalpha(alpha)
        
        # Sauvegarder dans un buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Dimensions de la page A4
        page_width, page_height = A4
        
        # Calculer les dimensions du logo (max 50% de la page)
        max_width = page_width * 0.5
        max_height = page_height * 0.5
        
        # Calculer le ratio pour maintenir les proportions
        img_width, img_height = img.size
        ratio = min(max_width / img_width, max_height / img_height)
        
        logo_width = img_width * ratio
        logo_height = img_height * ratio
        
        # Centrer le logo
        x = (page_width - logo_width) / 2
        y = (page_height - logo_height) / 2
        
        # Dessiner le logo
        pdf_canvas.drawImage(
            ImageReader(img_buffer),
            x, y,
            width=logo_width,
            height=logo_height,
            mask='auto'
        )
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du filigrane: {e}")


def add_header_logo(pdf_canvas, logo_path, entreprise_nom, x=1*cm, y=None, max_height=2*cm):
    """
    Ajoute un logo en en-tête d'une page PDF
    
    Args:
        pdf_canvas: Canvas ReportLab
        logo_path: Chemin vers le fichier logo
        entreprise_nom: Nom de l'entreprise
        x: Position X du logo
        y: Position Y du logo (None = en haut de page)
        max_height: Hauteur maximale du logo
    """
    if not logo_path or not os.path.exists(logo_path):
        # Si pas de logo, afficher juste le nom
        if y is None:
            y = A4[1] - 2*cm
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x, y, entreprise_nom)
        return
    
    try:
        # Ouvrir l'image
        img = Image.open(logo_path)
        img_width, img_height = img.size
        
        # Calculer les dimensions en maintenant le ratio
        ratio = max_height / img_height
        logo_width = img_width * ratio
        logo_height = max_height
        
        # Position Y par défaut en haut de page
        if y is None:
            y = A4[1] - logo_height - 1*cm
        
        # Dessiner le logo
        pdf_canvas.drawImage(
            logo_path,
            x, y,
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True
        )
        
        # Ajouter le nom de l'entreprise à côté du logo
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x + logo_width + 0.5*cm, y + logo_height/2, entreprise_nom)
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du logo en en-tête: {e}")
        # Fallback: afficher juste le nom
        if y is None:
            y = A4[1] - 2*cm
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x, y, entreprise_nom)


def create_pdf_with_logo(filename, entreprise, add_watermark=True):
    """
    Crée un canvas PDF avec le logo de l'entreprise
    
    Args:
        filename: Nom du fichier PDF ou buffer
        entreprise: Instance du modèle Entreprise
        add_watermark: Ajouter le logo en filigrane
    
    Returns:
        Canvas ReportLab configuré
    """
    from reportlab.pdfgen import canvas as pdf_canvas
    
    c = pdf_canvas.Canvas(filename, pagesize=A4)
    
    # Ajouter le logo en en-tête
    if entreprise and entreprise.logo:
        logo_path = entreprise.logo.path
        add_header_logo(c, logo_path, entreprise.nom_entreprise)
        
        # Ajouter le filigrane si demandé
        if add_watermark:
            add_watermark_logo(c, logo_path)
    else:
        # Pas de logo, juste le nom
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1*cm, A4[1] - 2*cm, entreprise.nom_entreprise if entreprise else "")
    
    return c


# Fonction helper pour obtenir le logo de l'entreprise de l'utilisateur
def get_user_entreprise_logo(user):
    """
    Récupère le chemin du logo de l'entreprise de l'utilisateur
    
    Args:
        user: Instance de l'utilisateur
    
    Returns:
        Chemin du logo ou None
    """
    if hasattr(user, 'entreprise') and user.entreprise and user.entreprise.logo:
        return user.entreprise.logo.path
    return None
