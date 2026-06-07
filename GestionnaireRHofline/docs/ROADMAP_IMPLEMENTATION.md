# 🗺️ Roadmap d'Implémentation - Gestionnaire RH Guinée

## 📊 État Actuel du Projet

### ✅ Modules Implémentés (Phase 1)

#### 1. **Système et Sécurité**
- [x] Modèle Utilisateur personnalisé (`Utilisateur`)
- [x] Profils utilisateurs avec niveaux d'accès
- [x] Authentification et gestion des sessions
- [x] Interface de connexion aux couleurs guinéennes

#### 2. **Configuration Entreprise**
- [x] Modèle Société
- [x] Établissements multiples
- [x] Paramètres système

#### 3. **Organisation**
- [x] Services hiérarchiques
- [x] Postes et classifications
- [x] Structure organisationnelle

#### 4. **Employés (Base)**
- [x] Fiche employé complète
- [x] État civil et contact
- [x] Informations professionnelles
- [x] CRUD employés
- [x] Liste et détails
- [x] Export Excel

#### 5. **Dashboard**
- [x] Tableau de bord principal
- [x] Statistiques de base
- [x] Rapports avec graphiques (Chart.js)
- [x] Indicateurs RH

#### 6. **Interface Utilisateur**
- [x] Design aux couleurs guinéennes 🇬🇳
- [x] Navigation responsive
- [x] Templates de base
- [x] Sidebar avec tous les modules

---

## 🚀 Phase 2 : Temps de Travail (En cours)

### Objectif : Gestion complète du temps et des absences

#### 2.1 Calendrier et Horaires
- [ ] Modèle `JourFerie` (jours fériés guinéens)
- [ ] Modèle `HoraireTravail` (horaires standards)
- [ ] Affectation horaires aux employés
- [ ] Calendrier annuel interactif

#### 2.2 Pointages
- [ ] Modèle `Pointage` complet
- [ ] Interface de saisie quotidienne
- [ ] Calcul automatique heures travaillées
- [ ] Détection retards et absences
- [ ] Validation par superviseur
- [ ] Export feuilles de présence

#### 2.3 Congés
- [ ] Modèle `Conge` avec workflow
- [ ] Modèle `SoldeConge` (26 jours/an)
- [ ] Demande de congé en ligne
- [ ] Validation hiérarchique
- [ ] Calendrier des congés
- [ ] Calcul automatique soldes
- [ ] Alertes congés non pris

#### 2.4 Absences et Arrêts
- [ ] Modèle `Absence`
- [ ] Modèle `ArretTravail`
- [ ] Gestion certificats médicaux
- [ ] Suivi INAM
- [ ] Statistiques absentéisme

**Durée estimée : 3-4 semaines**

---

## 💰 Phase 3 : Module Paie Complet

### Objectif : Calcul automatique de la paie conforme à la législation guinéenne

#### 3.1 Paramétrage Paie
- [ ] Modèle `ParametrePaie` (SMIG, plafonds)
- [ ] Modèle `TrancheIRG` (barème IRG)
- [ ] Modèle `RubriquePaie` (gains, retenues)
- [ ] Formules de calcul
- [ ] Constantes (CNSS 5%/18%, INAM 2.5%)

#### 3.2 Éléments Salariaux
- [ ] Modèle `ElementSalaire`
- [ ] Modèle `GrilleSalariale`
- [ ] Salaire de base
- [ ] Primes (ancienneté, fonction, rendement)
- [ ] Indemnités (transport, logement, nourriture)
- [ ] Avantages en nature

#### 3.3 Calcul Bulletins
- [ ] Modèle `PeriodePaie`
- [ ] Modèle `BulletinPaie`
- [ ] Modèle `LigneBulletin`
- [ ] Moteur de calcul automatique :
  - Salaire brut
  - Base CNSS (avec plafond)
  - CNSS employé (5%)
  - INAM (2.5%)
  - Base IRG (brut - CNSS - INAM - abattement)
  - IRG par tranches
  - Net à payer
  - Charges patronales (CNSS 18%)
- [ ] Génération PDF bulletins
- [ ] Envoi email automatique
- [ ] Signature électronique

#### 3.4 Cumuls et Historique
- [ ] Modèle `CumulPaie`
- [ ] Cumuls mensuels/annuels
- [ ] Livre de paie
- [ ] Historique modifications

**Durée estimée : 5-6 semaines**

---

## 📋 Phase 4 : Déclarations Sociales

### Objectif : Génération automatique des déclarations CNSS, INAM, IRG

#### 4.1 Déclarations CNSS
- [ ] Modèle `DeclarationSociale`
- [ ] Modèle `LigneDeclaration`
- [ ] Déclaration mensuelle CNSS
- [ ] Déclaration annuelle CNSS
- [ ] Export format requis
- [ ] Bordereau de paiement

#### 4.2 Déclarations INAM
- [ ] Déclaration mensuelle INAM
- [ ] Liste nominative
- [ ] Export format requis

#### 4.3 Déclarations IRG
- [ ] Déclaration mensuelle IRG
- [ ] État récapitulatif annuel
- [ ] Certificat de retenue

#### 4.4 Comptabilité
- [ ] Modèle `JournalPaie`
- [ ] Modèle `EcritureComptable`
- [ ] Génération écritures automatiques
- [ ] Export vers logiciel comptable

**Durée estimée : 4 semaines**

---

## 💼 Phase 5 : Recrutement et Carrière

### Objectif : Gestion du cycle de vie complet de l'employé

#### 5.1 Recrutement
- [ ] Modèle `OffreEmploi`
- [ ] Modèle `Candidature`
- [ ] Modèle `EntretienRecrutement`
- [ ] Publication offres
- [ ] Réception candidatures
- [ ] Évaluation et scoring
- [ ] Workflow validation
- [ ] Intégration nouvel employé

#### 5.2 Formation
- [ ] Modèle `FormationEmploye`
- [ ] Plan de formation annuel
- [ ] Suivi formations
- [ ] Budget formation
- [ ] Évaluation post-formation
- [ ] Certificats et attestations

#### 5.3 Carrière
- [ ] Modèle `CarriereEmploye`
- [ ] Promotions
- [ ] Mutations
- [ ] Reclassements
- [ ] Historique complet

#### 5.4 Évaluations
- [ ] Modèle `EvaluationEmploye`
- [ ] Entretiens annuels
- [ ] Grilles d'évaluation
- [ ] Objectifs et KPI
- [ ] Plans de développement

#### 5.5 Départs
- [ ] Modèle `TypeDepart`
- [ ] Modèle `DepartEmploye`
- [ ] Démissions
- [ ] Licenciements
- [ ] Retraites
- [ ] Calcul indemnités
- [ ] Certificat de travail
- [ ] Solde de tout compte

**Durée estimée : 5 semaines**

---

## 🔐 Phase 6 : Portail Employé

### Objectif : Self-service pour les employés

#### 6.1 Espace Personnel
- [ ] Tableau de bord employé
- [ ] Consultation fiche personnelle
- [ ] Modification coordonnées
- [ ] Téléchargement bulletins
- [ ] Historique paie

#### 6.2 Demandes en Ligne
- [ ] Modèle `DemandeEmploye`
- [ ] Demande de congé
- [ ] Demande d'acompte
- [ ] Demande d'attestation
- [ ] Demande de prêt
- [ ] Workflow d'approbation

#### 6.3 Notifications
- [ ] Modèle `NotificationEmploye`
- [ ] Notifications push
- [ ] Emails automatiques
- [ ] Rappels et alertes

#### 6.4 Documents
- [ ] Modèle `DocumentEmploye`
- [ ] Coffre-fort numérique
- [ ] Téléchargement sécurisé
- [ ] Signature électronique

**Durée estimée : 4 semaines**

---

## 📊 Phase 7 : Reporting Avancé et BI

### Objectif : Tableaux de bord et analyses avancées

#### 7.1 Indicateurs RH
- [ ] Modèle `IndicateurRH`
- [ ] Modèle `ValeurIndicateur`
- [ ] Effectif et turnover
- [ ] Masse salariale
- [ ] Absentéisme
- [ ] Formation
- [ ] Âge et ancienneté
- [ ] Ratios sociaux

#### 7.2 Alertes Automatiques
- [ ] Modèle `AlerteRH`
- [ ] Fin de contrat CDD
- [ ] Documents expirés
- [ ] Congés non pris
- [ ] Formations obligatoires
- [ ] Évaluations à faire

#### 7.3 Rapports Personnalisés
- [ ] Générateur de rapports
- [ ] Export multi-formats
- [ ] Planification automatique
- [ ] Envoi programmé

#### 7.4 Tableaux de Bord
- [ ] Dashboard Direction
- [ ] Dashboard RH
- [ ] Dashboard Manager
- [ ] Graphiques interactifs
- [ ] Drill-down

**Durée estimée : 3 semaines**

---

## 🔒 Phase 8 : Sécurité et Audit

### Objectif : Traçabilité et conformité

#### 8.1 Audit Trail
- [ ] Modèle `HistoriqueModification`
- [ ] Logs détaillés
- [ ] Traçabilité complète
- [ ] Consultation historique

#### 8.2 Droits d'Accès
- [ ] Modèle `DroitAcces`
- [ ] Permissions granulaires
- [ ] Profils personnalisés
- [ ] Matrice de droits

#### 8.3 Sauvegardes
- [ ] Modèle `Sauvegarde`
- [ ] Backup automatique
- [ ] Restauration
- [ ] Archivage

#### 8.4 Conformité RGPD
- [ ] Consentements
- [ ] Droit à l'oubli
- [ ] Export données personnelles
- [ ] Anonymisation

**Durée estimée : 3 semaines**

---

## 🚀 Phase 9 : Optimisation et Production

### Objectif : Mise en production

#### 9.1 Performance
- [ ] Optimisation requêtes
- [ ] Cache Redis
- [ ] CDN pour statiques
- [ ] Compression

#### 9.2 Migration PostgreSQL
- [ ] Configuration production
- [ ] Migration données
- [ ] Tests de charge

#### 9.3 Déploiement
- [ ] Configuration serveur
- [ ] SSL/HTTPS
- [ ] Monitoring
- [ ] Logs centralisés

#### 9.4 Documentation
- [ ] Manuel utilisateur
- [ ] Guide administrateur
- [ ] Documentation technique
- [ ] Vidéos tutoriels

**Durée estimée : 4 semaines**

---

## 📅 Planning Global

| Phase | Durée | Dates estimées |
|-------|-------|----------------|
| Phase 1 : Base | ✅ Complété | Oct 2025 |
| Phase 2 : Temps de travail | 4 semaines | Nov 2025 |
| Phase 3 : Paie | 6 semaines | Déc 2025 - Jan 2026 |
| Phase 4 : Déclarations | 4 semaines | Fév 2026 |
| Phase 5 : Recrutement | 5 semaines | Mar 2026 |
| Phase 6 : Portail | 4 semaines | Avr 2026 |
| Phase 7 : Reporting | 3 semaines | Mai 2026 |
| Phase 8 : Sécurité | 3 semaines | Mai-Juin 2026 |
| Phase 9 : Production | 4 semaines | Juin 2026 |

**Durée totale estimée : 8-9 mois**

---

## 🎯 Priorités Immédiates

1. **Temps de travail** (Phase 2) - Essentiel pour la paie
2. **Module Paie** (Phase 3) - Cœur du système
3. **Déclarations sociales** (Phase 4) - Obligation légale

---

## 📝 Notes Techniques

### Technologies
- **Backend** : Django 5.2.7 + Python 3.14
- **Frontend** : Bootstrap 5 + Chart.js
- **Base de données** : SQLite (dev) → PostgreSQL (prod)
- **Couleurs** : Rouge (#ce1126), Jaune (#fcd116), Vert (#009460) 🇬🇳

### Conformité Légale
- Code du Travail Guinéen
- Décrets CNSS
- Réglementation INAM
- Barème IRG officiel

---

**Fier d'être Guinéen 🇬🇳**
*Système de Gestion RH Made in Guinea*
