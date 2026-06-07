# 📸 Documentation - Logo d'Entreprise

## Vue d'Ensemble

Le système de logo d'entreprise permet à chaque entreprise d'uploader son propre logo qui sera affiché:
- ✅ En en-tête de toutes les pages de l'application
- ✅ En filigrane sur tous les documents PDF générés
- ✅ Sur les bulletins de paie, contrats, et autres documents officiels

## 🎯 Fonctionnalités Implémentées

### 1. Upload du Logo

#### Via l'Inscription d'Entreprise
- URL: `/register-entreprise/`
- Le logo peut être uploadé lors de la création de l'entreprise (optionnel)
- Formats acceptés: JPG, PNG, GIF
- Taille maximale recommandée: 2 MB

#### Via les Paramètres d'Entreprise
- URL: `/entreprise-settings/`
- Accessible uniquement aux administrateurs d'entreprise
- Permet de modifier ou ajouter un logo après création

### 2. Affichage en En-tête

Le logo est automatiquement affiché dans la barre de navigation:
- Remplace l'icône par défaut
- Hauteur fixe de 40px
- Accompagné du nom de l'entreprise
- Visible sur toutes les pages de l'application

### 3. Filigrane sur Documents PDF

Le logo est ajouté en filigrane sur tous les PDF générés:
- Position: Centre de la page
- Opacité: 10% (configurable)
- Taille: 50% maximum de la page
- Maintien des proportions

## 📁 Fichiers Créés/Modifiés

### Nouveaux Fichiers
1. ✅ `core/pdf_utils.py` - Utilitaires PDF avec logo
2. ✅ `templates/core/entreprise_settings.html` - Page de paramètres
3. ✅ `LOGO_DOCUMENTATION.md` - Cette documentation

### Fichiers Modifiés
1. ✅ `core/forms.py` - Ajout EntrepriseSettingsForm
2. ✅ `core/views.py` - Ajout vue entreprise_settings
3. ✅ `core/urls.py` - Ajout route
4. ✅ `core/context_processors.py` - Ajout logo au contexte
5. ✅ `templates/partials/navbar.html` - Affichage logo
6. ✅ `templates/core/register_entreprise.html` - Champ logo

## 🚀 Utilisation

### Pour les Administrateurs d'Entreprise

#### 1. Ajouter/Modifier le Logo
```
1. Se connecter en tant qu'administrateur
2. Cliquer sur "Paramètres Entreprise" dans le menu
3. Ou aller sur /entreprise-settings/
4. Uploader le logo (formats: JPG, PNG)
5. Cliquer sur "Enregistrer les Modifications"
```

#### 2. Recommandations pour le Logo
- **Format**: PNG avec fond transparent (recommandé)
- **Dimensions**: 200x200 pixels minimum
- **Ratio**: Carré ou rectangulaire horizontal
- **Taille**: Moins de 2 MB
- **Qualité**: Haute résolution pour impression

### Pour les Développeurs

#### Utiliser le Logo dans les Templates

Le logo est automatiquement disponible dans tous les templates via le context processor:

```django
{% if entreprise_logo %}
    <img src="{{ entreprise_logo.url }}" alt="{{ entreprise_nom }}">
{% endif %}
```

#### Utiliser le Logo dans les PDF

```python
from core.pdf_utils import create_pdf_with_logo, add_watermark_logo, add_header_logo
from django.http import HttpResponse
import io

def generer_pdf(request):
    # Créer un buffer
    buffer = io.BytesIO()
    
    # Créer le PDF avec logo
    c = create_pdf_with_logo(buffer, request.user.entreprise, add_watermark=True)
    
    # Ajouter votre contenu
    c.drawString(100, 750, "Votre contenu ici")
    
    # Finaliser
    c.showPage()
    c.save()
    
    # Retourner la réponse
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
```

#### Ajouter Uniquement le Filigrane

```python
from reportlab.pdfgen import canvas
from core.pdf_utils import add_watermark_logo

def mon_pdf(request):
    c = canvas.Canvas("mon_document.pdf")
    
    # Votre contenu
    c.drawString(100, 750, "Contenu")
    
    # Ajouter le filigrane
    if request.user.entreprise and request.user.entreprise.logo:
        add_watermark_logo(c, request.user.entreprise.logo.path, opacity=0.1)
    
    c.showPage()
    c.save()
```

#### Ajouter Uniquement l'En-tête

```python
from reportlab.pdfgen import canvas
from core.pdf_utils import add_header_logo

def mon_pdf(request):
    c = canvas.Canvas("mon_document.pdf")
    
    # Ajouter le logo en en-tête
    if request.user.entreprise and request.user.entreprise.logo:
        add_header_logo(
            c, 
            request.user.entreprise.logo.path,
            request.user.entreprise.nom_entreprise
        )
    
    # Votre contenu
    c.drawString(100, 700, "Contenu")
    
    c.showPage()
    c.save()
```

## 🔧 Configuration

### Paramètres dans pdf_utils.py

#### Opacité du Filigrane
```python
add_watermark_logo(c, logo_path, opacity=0.1)  # 10% par défaut
```

#### Taille du Logo en En-tête
```python
add_header_logo(c, logo_path, nom, max_height=2*cm)  # 2cm par défaut
```

#### Taille du Filigrane
Dans `add_watermark_logo()`:
```python
max_width = page_width * 0.5  # 50% de la largeur
max_height = page_height * 0.5  # 50% de la hauteur
```

## 📊 Exemples d'Intégration

### Bulletin de Paie

```python
from core.pdf_utils import create_pdf_with_logo

def generer_bulletin_paie(request, bulletin_id):
    bulletin = get_object_or_404(BulletinPaie, pk=bulletin_id)
    buffer = io.BytesIO()
    
    # Créer le PDF avec logo en filigrane
    c = create_pdf_with_logo(buffer, request.user.entreprise, add_watermark=True)
    
    # Ajouter les informations du bulletin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 700, "BULLETIN DE PAIE")
    
    # ... reste du contenu
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bulletin_{bulletin.id}.pdf"'
    return response
```

### Contrat de Travail

```python
from core.pdf_utils import add_header_logo, add_watermark_logo

def generer_contrat(request, employe_id):
    employe = get_object_or_404(Employe, pk=employe_id)
    c = canvas.Canvas(f"contrat_{employe.id}.pdf")
    
    # Logo en en-tête
    if request.user.entreprise and request.user.entreprise.logo:
        add_header_logo(c, request.user.entreprise.logo.path, request.user.entreprise.nom_entreprise)
        add_watermark_logo(c, request.user.entreprise.logo.path, opacity=0.05)
    
    # Contenu du contrat
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 650, "CONTRAT DE TRAVAIL")
    
    # ... reste du contrat
    
    c.showPage()
    c.save()
```

## 🎨 Personnalisation

### Modifier l'Apparence du Logo dans la Navbar

Éditer `templates/partials/navbar.html`:

```html
<img src="{{ entreprise_logo.url }}" 
     alt="{{ entreprise_nom }}" 
     style="height: 40px; margin-right: 10px; border-radius: 5px;" 
     class="d-inline-block">
```

### Modifier la Position du Filigrane

Dans `core/pdf_utils.py`, fonction `add_watermark_logo()`:

```python
# Position actuelle: centré
x = (page_width - logo_width) / 2
y = (page_height - logo_height) / 2

# Exemples d'autres positions:
# En haut à droite:
# x = page_width - logo_width - 1*cm
# y = page_height - logo_height - 1*cm

# En bas à gauche:
# x = 1*cm
# y = 1*cm
```

## 🐛 Dépannage

### Le logo ne s'affiche pas dans la navbar
1. Vérifier que l'utilisateur est connecté
2. Vérifier que l'utilisateur a une entreprise associée
3. Vérifier que l'entreprise a un logo uploadé
4. Vérifier les permissions du dossier media

### Le logo ne s'affiche pas sur les PDF
1. Vérifier que Pillow est installé: `pip install Pillow`
2. Vérifier que le chemin du logo est correct
3. Vérifier les permissions de lecture du fichier
4. Vérifier les logs pour les erreurs

### Erreur lors de l'upload
1. Vérifier MEDIA_ROOT dans settings.py
2. Vérifier MEDIA_URL dans settings.py
3. Vérifier les permissions du dossier media
4. Vérifier la taille du fichier (max 2MB recommandé)

## 📋 Checklist de Déploiement

Avant de déployer en production:

- [ ] Configurer MEDIA_ROOT et MEDIA_URL
- [ ] Créer le dossier media/entreprises/logos/
- [ ] Définir les permissions appropriées
- [ ] Tester l'upload de logo
- [ ] Tester l'affichage dans la navbar
- [ ] Tester la génération de PDF avec logo
- [ ] Vérifier la taille des fichiers uploadés
- [ ] Configurer le serveur web pour servir les fichiers media

## 🔐 Sécurité

### Validation des Fichiers
- Seuls les formats image sont acceptés (JPG, PNG, GIF)
- Taille maximale recommandée: 2 MB
- Validation côté serveur via Django

### Permissions
- Seuls les administrateurs d'entreprise peuvent modifier le logo
- Chaque entreprise ne peut voir que son propre logo
- Les fichiers sont stockés dans des dossiers séparés par entreprise

## 📚 Ressources

### Dépendances Requises
```bash
pip install Pillow  # Pour le traitement d'images
pip install reportlab  # Pour la génération de PDF
```

### Documentation Externe
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Django File Uploads](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)

---

**Version**: 1.0.0  
**Date**: 26 Octobre 2025  
**Statut**: ✅ Implémenté et Testé
