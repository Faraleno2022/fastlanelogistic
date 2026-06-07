# 🔒 Guide de Protection du Code Source

## Méthodes de Protection Disponibles

### 1. Compilation Nuitka (Protection Maximale) ⭐

**Avantages:**
- Compile Python en vrai code C/binaire
- Très difficile à décompiler
- Performance améliorée

**Prérequis:**
- Visual Studio Build Tools (gratuit)
- https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Cochez "Développement Desktop en C++"

**Commande:**
```
compiler_projet.bat
```

---

### 2. PyInstaller + Obfuscation (Protection Moyenne)

Utilisé automatiquement si Nuitka n'est pas disponible.

---

### 3. Supprimer les fichiers .py avant distribution

Après compilation, supprimez tous les fichiers `.py` du package distribué.
Gardez uniquement:
- L'exécutable `.exe`
- Les dossiers `templates/`, `static/`, `media/`
- La base de données `db.sqlite3`

---

## 🛡️ Protections Déjà en Place

1. **Système de licence** - Bloque l'accès sans clé valide
2. **Vérification machine** - Lie la licence à un PC spécifique
3. **Signature cryptographique** - Empêche la modification de la licence
4. **Expiration automatique** - Force le renouvellement

---

## ⚠️ Limitations

**Aucune protection n'est 100% infaillible.**

Un développeur très expérimenté pourrait potentiellement:
- Décompiler le bytecode Python
- Modifier la base de données
- Contourner les vérifications

**Mais ces protections:**
- Découragent 99% des tentatives
- Rendent le vol très difficile et long
- Protègent contre les utilisateurs non-techniques

---

## 📋 Checklist Avant Distribution

- [ ] Compiler avec Nuitka ou PyInstaller
- [ ] Supprimer tous les fichiers `.py`
- [ ] Supprimer le dossier `venv/`
- [ ] Supprimer les fichiers `.git/`
- [ ] Garder uniquement l'exécutable et les ressources
- [ ] Tester sur un PC vierge

---

## 💡 Conseil Business

La meilleure protection reste:
1. **Prix raisonnable** - Si c'est abordable, les gens préfèrent payer
2. **Support client** - Les pirates n'ont pas de support
3. **Mises à jour régulières** - Nouvelles fonctionnalités pour les clients légitimes
4. **Contrat légal** - Protection juridique en cas de vol
