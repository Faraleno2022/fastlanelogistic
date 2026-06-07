# 🚀 DÉPLOIEMENT IMMÉDIAT - Étapes Simplifiées

## ✅ Statut Actuel
- ✅ Code commité et pushé à GitHub
- ✅ 10 fichiers synchronisés (commit: `bbeaf67`)
- ⏳ Services production à redémarrer

---

## 🔧 Approche Alternative (Plus Simple)

Vu les problèmes SSH, voici une approche en deux temps:

### **Étape 1: Pull Direct sur le Serveur**

**Via GUI Web ou accès SSH direct:**
```bash
# Sur le serveur, dans /home/guineerh/gestionrh/ (ou le chemin correct)
git pull origin main
```

Le commit `bbeaf67` sera automatiquement téléchargé avec:
- ✅ `paie/services.py` (modifié)
- ✅ Tous les fichiers de documentation
- ✅ Script `fill_conges_acquis.py`

### **Étape 2: Redémarrage Application**

**Options (selon votre configuration):**

```bash
# Option A: Si uWSGI
sudo systemctl restart uWSGI_gestionrh

# Option B: Si Gunicorn
sudo systemctl restart gunicorn_gestionrh

# Option C: Si supervisord
sudo supervisorctl restart gestionrh

# Option D: Redémarrage manuel
pkill -f "gestionrh|uWSGI|gunicorn"
# Puis relancer le service
```

---

## 📝 Vérifiez le Déploiement

### Via Interface Web (Plus Facile)

1. **Accéder:** https://www.guineerh.space/paie/bulletins/
2. **Générer un bulletin** pour: FARA LENO (ou employé récent)
3. **Chercher section "Congés":**
   ```
   ✅ Attendu: "Congés acquis: 7 j" (pas 0)
   ✅ Attendu: "Congés pris: 0 j"
   ✅ Attendu: "Solde congés: 7 j"
   ```

4. **Télécharger PDF** → vérifier congés affichés

### Via Django Admin

```
1. https://www.guineerh.space/admin/
2. Temps Travail > Soldes Congés
3. Chercher: FARA LENO, année 2026
4. Vérifier: conges_acquis = ~7.50 ✅
```

---

## 🔍 Si Pas de Changement

**Possibilités:**
1. Application pas restarted (pas de modification vue)
2. Cache à vider:
   ```bash
   python manage.py clear_cache
   # Ou manuellement dans /tmp/
   ```
3. Vérifier que paie/services.py a les modifications:
   ```bash
   grep "_calculer_conges_acquis" paie/services.py
   # Doit trouver la méthode
   ```

---

## 💡 Plan B: Remplissage Rétroactif

Si vous voulez que TOUS les bulletins affichent congés corrects immédiatement:

```bash
# Sur le serveur
python manage.py shell < fill_conges_acquis.py

# Ou directement
python fill_conges_acquis.py
```

Cela peuplera tous les `SoldeConge` pour tous les employés actifs de 2026.

---

## 📊 Résumé

| Phase | Statut | Action |
|-------|--------|--------|
| Code commit | ✅ | `bbeaf67` pushé à GitHub |
| Code synchronisation | ⏳ | Faire `git pull` sur serveur |
| App restart | ⏳ | Redémarrer le service |
| Test interface | ⏳ | Générer un bulletin test |
| Remplissage rétro | 🟢 | Optionnel avec `fill_conges_acquis.py` |

---

## 🎯 Prochaines Actions

1. **Demain ou à votre convenance:**
   - Accéder au serveur (SSH, panel web, etc.)
   - Exécuter `git pull origin main`
   - Redémarrer l'application
   
2. **Test:**
   - Générer un bulletin via interface
   - Vérifier les congés affichent correct
   
3. **Validation:**
   - Tous les bulletins NEW auront auto-calcul
   - ✅ Conformité Code du Travail établie

---

**Status:** ✅ CODE PRÊT POUR PRODUCTION  
**Prochaine Étape:** Pull & Restart sur serveur

