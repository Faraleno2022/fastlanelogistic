import os

from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename


# Types MIME autorisés par catégorie
MIME_AUTORISES = {
    'document': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
    'image': [
        'image/jpeg',
        'image/png',
    ],
    'document_image': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
    ],
}

TAILLE_MAX_OCTETS = 5 * 1024 * 1024  # 5 Mo

# Extensions autorisées par type MIME (double vérification)
EXTENSIONS_AUTORISEES = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
}

# Signatures binaires connues (magic bytes)
SIGNATURES_FICHIER = {
    b'%PDF': 'application/pdf',
    b'\xd0\xcf\x11\xe0': 'application/msword',  # OLE2 (doc, xls)
    b'PK': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # ZIP-based (docx, xlsx)
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x89PNG': 'image/png',
}


def _detecter_mime(entete):
    """Détecte le type MIME réel via les magic bytes du fichier."""
    for signature, mime in SIGNATURES_FICHIER.items():
        if entete.startswith(signature):
            return mime
    return 'application/octet-stream'


def valider_fichier(fichier, categorie='document'):
    """
    Valide un fichier uploadé :
    - Taille maximale (5 Mo)
    - Type MIME réel (lu depuis les magic bytes, pas l'extension)
    - Cohérence entre extension et contenu
    - Nom de fichier sécurisé (anti path-traversal)
    """
    if not fichier:
        return

    # 1. Vérification de la taille
    if fichier.size > TAILLE_MAX_OCTETS:
        raise ValidationError(
            f"Le fichier est trop volumineux ({fichier.size // (1024 * 1024)} Mo). "
            f"Maximum autorisé : 5 Mo."
        )

    # 2. Lecture du vrai type MIME depuis le contenu binaire
    fichier.seek(0)
    entete = fichier.read(2048)
    fichier.seek(0)

    try:
        import magic
        mime_reel = magic.from_buffer(entete, mime=True)
    except (ImportError, Exception):
        # Fallback : détection par magic bytes intégrée
        mime_reel = _detecter_mime(entete)

    # 3. Vérifier que le MIME est dans la liste blanche
    mimes_autorises = MIME_AUTORISES.get(categorie, MIME_AUTORISES['document'])
    if mime_reel not in mimes_autorises:
        types_acceptes = {
            'document': 'PDF, Word (.doc/.docx)',
            'image': 'JPEG, PNG',
            'document_image': 'PDF, Word, JPEG, PNG',
        }
        raise ValidationError(
            f"Type de fichier non autorisé ({mime_reel}). "
            f"Formats acceptés : {types_acceptes.get(categorie, 'PDF, Word')}."
        )

    # 4. Vérifier la cohérence extension ↔ contenu réel
    nom = fichier.name.lower()
    extensions_attendues = EXTENSIONS_AUTORISEES.get(mime_reel, [])
    if extensions_attendues and not any(nom.endswith(ext) for ext in extensions_attendues):
        raise ValidationError(
            "L'extension du fichier ne correspond pas à son contenu réel. "
            "Fichier suspect rejeté."
        )

    # 5. Sécuriser le nom du fichier (anti path traversal)
    nom_base = os.path.basename(fichier.name)
    nom_securise = get_valid_filename(nom_base)
    if nom_securise != nom_base:
        fichier.name = nom_securise


def valider_cv(fichier):
    """Valide un CV (PDF ou Word uniquement)."""
    return valider_fichier(fichier, categorie='document')


def valider_image_document(fichier):
    """Valide un document pouvant être PDF, Word ou image."""
    return valider_fichier(fichier, categorie='document_image')


def valider_image(fichier):
    """Valide une image (JPEG ou PNG uniquement)."""
    return valider_fichier(fichier, categorie='image')


def _valider_taille(fichier, taille_mo):
    if not fichier:
        return
    if fichier.size > int(taille_mo * 1024 * 1024):
        raise ValidationError(
            f"Fichier trop volumineux ({fichier.size // (1024 * 1024)} Mo). "
            f"Maximum autorisé : {taille_mo} Mo."
        )


def valider_taille_2mo(fichier):
    """Limite stricte à 2 Mo — défense en profondeur contre saturation stockage."""
    _valider_taille(fichier, 2)


def valider_taille_3mo(fichier):
    """Limite stricte à 3 Mo — défense en profondeur contre saturation stockage."""
    _valider_taille(fichier, 3)


def valider_taille_5mo(fichier):
    """Limite stricte à 5 Mo — défense en profondeur contre saturation stockage."""
    _valider_taille(fichier, 5)
