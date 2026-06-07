# Instructions de déploiement - Fix colonnes manquantes

## 🚨 Problème URGENT
L'erreur `(1054, "Colonne inconnue 'bulletins_paie.abattement_forfaitaire'")` indique que les colonnes ajoutées en développement n'existent pas sur le serveur de production.

**Impact:** La page `/paie/periodes/{id}/` est cassée et les bulletins ne s'affichent pas.

---

## ✅ SOLUTION RAPIDE (5 minutes)

### Étape 1: Télécharger les fichiers de correction

Les fichiers de correction sont disponibles sur GitHub:
- `fix_deployment.py` - Script Python automatisé (RECOMMANDÉ)
- `add_missing_columns.sql` - Script SQL manuel (Alternative)

### Étape 2: Exécuter le script de correction (OPTION 1 - Préféré)

```bash
# Connectez-vous au serveur
ssh www-guineerh

# Naviguez vers le répertoire du projet
cd /home/guineerh/gestionrh

# Activez l'environnement virtuel
source venv/bin/activate

# Exécutez le script de correction
python fix_deployment.py
```

**Le script va:**
- ✓ Vérifier quelles colonnes existent
- ✓ Ajouter les colonnes manquantes
- ✓ Créer les index pour performance
- ✓ Appliquer la migration Django
- ✓ Vérifier le succès avec un rapport final

**Résultat attendu:**
```
✓✓✓ SUCCÈS ! Toutes les colonnes sont présentes
    Colonnes confirmées: {'abattement_forfaitaire', 'base_vf', 'nombre_salaries'}

🎉 Le système est prêt à fonctionner!

📌 Prochaines étapes:
   1. Redémarrer uWSGI/WSGI
   2. Accéder à /paie/periodes/ pour vérifier
```

---

## �️ SOLUTION via Script SQL (OPTION 3 - Si Python échoue)

Si les deux options précédentes échouent, exécutez le script SQL directement:

```bash
# Via MySQL CLI
mysql -h localhost -u root -p gestionrh < /home/guineerh/gestionrh/add_missing_columns.sql
```

Ou via PhpMyAdmin / Client MySQL GUI:

```sql
ALTER TABLE bulletins_paie 
ADD COLUMN IF NOT EXISTS abattement_forfaitaire DECIMAL(15, 2) DEFAULT 0.00;

ALTER TABLE bulletins_paie 
ADD COLUMN IF NOT EXISTS base_vf DECIMAL(15, 2) DEFAULT 0.00;

ALTER TABLE bulletins_paie 
ADD COLUMN IF NOT EXISTS nombre_salaries INT DEFAULT 0;

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_abattement_forfaitaire ON bulletins_paie(abattement_forfaitaire);
CREATE INDEX IF NOT EXISTS idx_base_vf ON bulletins_paie(base_vf);
CREATE INDEX IF NOT EXISTS idx_nombre_salaries ON bulletins_paie(nombre_salaries);
```

---

## ✔️ VÉRIFICATION

### Vérifier que les colonnes existent

```sql
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'bulletins_paie' 
AND COLUMN_NAME IN ('abattement_forfaitaire', 'base_vf', 'nombre_salaries');
```

**Résultat attendu (3 lignes):**
| COLUMN_NAME | COLUMN_TYPE | IS_NULLABLE |
|---|---|---|
| abattement_forfaitaire | decimal(15,2) | YES |
| base_vf | decimal(15,2) | YES |
| nombre_salaries | int | YES |

---

## 🔄 REDÉMARRER L'APPLICATION

Après la correction, redémarrez les services:

```bash
# Redémarrer uWSGI
sudo systemctl restart uwsgi-gestionrh

# Redémarrer nginx (ou apache2)
sudo systemctl restart nginx

# Vérifier le statut
sudo systemctl status uwsgi-gestionrh
sudo systemctl status nginx
```

---

## ✅ TEST FINAL

Accédez à l'URL qui causait l'erreur:

```
https://www.guineerh.space/paie/periodes/11/
```

**Résultats attendus:**
- ✓ Page s'affiche sans erreur
- ✓ Tableau des bulletins apparaît
- ✓ Chaque ligne montre: Matricule | Nom | Brut | CNSS | RTS | Net | Statut | Actions

Si la page s'affiche correctement, **la correction est réussie! 🎉**

---

## 📝 NOTES DE DÉPLOIEMENT

### Colonnes ajoutées
Ces colonnes améliorent la **transparence** du bulletin de paie:

| Colonne | Signification | Utilisée pour |
|---------|---|---|
| `abattement_forfaitaire` | Déduction 25% sur RTS base | Afficher les détails RTS |
| `base_vf` | Base de calcul VF | Expliquer le montant VF |
| `nombre_salaries` | Effectif entreprise | Justifier TA vs ONFPP |

### Migration Django
**Fichier:** `paie/migrations/0110_bulletinpaie_abattement_forfaitaire_and_more.py`

Cette migration a été créée lors du dernier commit et doit être appliquée sur production.

### Vérifier la migration appliquée

```bash
python manage.py showmigrations paie
# Chercher "[X] 0110_bulletinpaie_abattement_forfaitaire_and_more"
# Le [X] indique qu'elle est appliquée
```

---

## ❓ DÉPANNAGE

### Erreur: "Duplicate column name"
✓ Colonnes existent déjà - C'est normal, ignorez le script/erreur

### Erreur: "Access denied"
✗ Vérifiez les permissions MySQL et le user:password

### Erreur: "Table doesn't exist"
✗ Assurez-vous d'utiliser la bonne base de données `gestionrh`

### Toujours des erreurs?
Contactez le support avec:
- Output exact du script ou erreur
- Résultat de `SELECT DATABASE(); DESCRIBE bulletins_paie;`
