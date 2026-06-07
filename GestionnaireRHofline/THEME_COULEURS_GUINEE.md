# Thème des Couleurs - Gestionnaire RH Guinée

## 🇬🇳 Palette de Couleurs Guinéennes

Ce projet utilise les couleurs officielles du drapeau de la République de Guinée pour créer une identité visuelle patriotique et professionnelle.

### Couleurs Principales

| Couleur | Code Hex | Usage | Signification |
|---------|----------|-------|---------------|
| **Rouge** | `#ce1126` | Couleur primaire, boutons d'action, liens | Représente le sacrifice du peuple guinéen |
| **Jaune** | `#fcd116` | Alertes, avertissements | Symbolise le soleil et les richesses du sous-sol |
| **Vert** | `#009460` | Succès, validation, couleur secondaire | Évoque l'agriculture et les forêts de Guinée |

### Application des Couleurs

#### 1. **Navigation et En-tête**
- Navbar : Dégradé rouge → vert
- Logo et branding : Rouge dominant

#### 2. **Boutons**
- **Boutons primaires** : Dégradé rouge avec effet hover
- **Boutons de succès** : Dégradé vert avec effet hover
- **Boutons d'avertissement** : Jaune guinéen

#### 3. **Cartes et Conteneurs**
- En-têtes de cartes : Dégradé subtil rouge-vert (5% opacité)
- Bordures : Rouge pour les éléments importants
- Ombres au survol : Rouge avec opacité

#### 4. **Formulaires**
- Focus des champs : Bordure rouge
- Validation réussie : Vert
- Erreurs : Rouge

#### 5. **Page de Connexion**
- Fond : Dégradé rouge → vert
- En-tête : Dégradé rouge → vert
- Drapeau guinéen : Rouge (33%) | Jaune (33%) | Vert (33%)

#### 6. **Éléments Interactifs**
- Liens : Rouge au survol
- Sidebar active : Bordure rouge
- Pagination : Rouge pour la page active
- Barre de défilement : Dégradé rouge → vert

### Variables CSS

```css
:root {
    --primary-color: #ce1126;      /* Rouge Guinée */
    --secondary-color: #009460;    /* Vert Guinée */
    --success-color: #009460;      /* Vert Guinée */
    --danger-color: #ce1126;       /* Rouge Guinée */
    --warning-color: #fcd116;      /* Jaune Guinée */
    --info-color: #009460;         /* Vert Guinée */
    --guinea-red: #ce1126;
    --guinea-yellow: #fcd116;
    --guinea-green: #009460;
}
```

### Dégradés Utilisés

1. **Dégradé Principal** : `linear-gradient(135deg, #ce1126 0%, #009460 100%)`
   - Utilisé pour : Navbar, page de connexion, boutons importants

2. **Dégradé Subtil** : `linear-gradient(135deg, rgba(206, 17, 38, 0.05) 0%, rgba(0, 148, 96, 0.05) 100%)`
   - Utilisé pour : En-têtes de cartes, arrière-plans légers

3. **Dégradé Vertical** : `linear-gradient(180deg, #ce1126 0%, #009460 100%)`
   - Utilisé pour : Barre de défilement

### Accessibilité

- Tous les contrastes respectent les normes WCAG 2.1 niveau AA
- Le rouge et le vert ne sont jamais utilisés seuls pour transmettre une information (icônes et texte accompagnent toujours)
- Les dégradés sont suffisamment contrastés pour être lisibles

### Personnalisation

Pour modifier les couleurs, éditez le fichier :
```
static/css/custom.css
```

Les variables CSS dans `:root` permettent une personnalisation facile et cohérente dans tout le projet.

---

**Fier d'être Guinéen 🇬🇳**
