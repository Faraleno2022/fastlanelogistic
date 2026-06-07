"""
Middleware pour servir les fichiers statiques en mode PyInstaller.
"""
import os
import sys
import mimetypes
from pathlib import Path
from django.http import FileResponse


class PyInstallerStaticMiddleware:
    """
    Middleware qui sert les fichiers statiques quand l'application
    est exécutée depuis un exécutable PyInstaller.
    Cherche dans plusieurs emplacements et passe au middleware suivant si non trouvé.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Déterminer le chemin de base
        if getattr(sys, 'frozen', False):
            self.exe_dir = Path(os.path.dirname(sys.executable))
            self.internal_dir = Path(sys._MEIPASS)
        else:
            self.exe_dir = Path(__file__).resolve().parent.parent
            self.internal_dir = self.exe_dir
        
        # Chercher static dans plusieurs emplacements possibles
        self.static_dirs = []
        for candidate in [
            self.internal_dir / 'static',
            self.exe_dir / '_internal' / 'static',
            self.exe_dir / 'static',
            self.internal_dir / 'staticfiles',
            self.exe_dir / '_internal' / 'staticfiles',
            self.exe_dir / 'staticfiles',
        ]:
            if candidate.exists():
                self.static_dirs.append(candidate)
        
        self.media_dir = self.exe_dir / 'media'
    
    def __call__(self, request):
        path = request.path
        
        # Servir les fichiers statiques
        if path.startswith('/static/'):
            relative = path[8:]  # Enlever '/static/'
            for static_dir in self.static_dirs:
                file_path = static_dir / relative
                if file_path.exists() and file_path.is_file():
                    return self._serve_file(file_path)
            # Pas trouvé -> laisser passer au middleware suivant
            return self.get_response(request)
        
        # Servir les fichiers media
        if path.startswith('/media/'):
            file_path = self.media_dir / path[7:]  # Enlever '/media/'
            if file_path.exists() and file_path.is_file():
                return self._serve_file(file_path)
            return self.get_response(request)
        
        return self.get_response(request)
    
    def _serve_file(self, file_path):
        """Sert un fichier si il existe."""
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = 'application/octet-stream'
        
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        return response
