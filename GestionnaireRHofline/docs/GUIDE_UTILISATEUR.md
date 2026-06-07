# Guide Utilisateur - Gestionnaire RH Guinée

## 📖 Table des Matières

1. [Introduction](#introduction)
2. [Premiers Pas](#premiers-pas)
3. [Gestion des Employés](#gestion-des-employés)
4. [Temps de Travail](#temps-de-travail)
5. [Module Paie](#module-paie)
6. [Congés et Absences](#congés-et-absences)
7. [Prêts et Acomptes](#prêts-et-acomptes)
8. [Recrutement](#recrutement)
9. [Formation et Carrière](#formation-et-carrière)
10. [Rapports et Statistiques](#rapports-et-statistiques)

---

## 🎯 Introduction

Le **Gestionnaire RH Guinée** est un système complet de gestion des ressources humaines conçu spécifiquement pour les entreprises en Guinée. Il respecte le Code du Travail guinéen et les réglementations locales (CNSS, RTS, INAM).

### Modules Principaux

- **Employés** : Gestion complète des dossiers employés
- **Paie** : Calcul automatique des bulletins de paie
- **Temps** : Pointages, congés, absences
- **Recrutement** : Gestion des candidatures
- **Formation** : Suivi des formations
- **Déclarations** : CNSS, RTS, INAM

---

## 🚀 Premiers Pas

### Connexion

1. Ouvrir le navigateur à l'adresse : **http://localhost:8000**
2. Cliquer sur **Connexion**
3. Entrer vos identifiants (login et mot de passe)
4. Cliquer sur **Se connecter**

### Interface Principale

Après connexion, vous accédez au **Tableau de bord** qui affiche :
- Effectif total
- Employés en congé aujourd'hui
- Bulletins de paie du mois
- Alertes importantes
- Statistiques clés

### Navigation

Le menu principal se trouve à gauche et contient :
- 🏠 **Tableau de bord**
- 👥 **Employés**
- ⏰ **Temps de Travail**
- 💰 **Paie**
- 📊 **Rapports**
- ⚙️ **Configuration**

---

## 👥 Gestion des Employés

### Ajouter un Nouvel Employé

1. **Menu** > **Employés** > **Nouveau**
2. Remplir le formulaire en 5 onglets :

#### Onglet 1 : État Civil
- Civilité (M., Mme, Mlle)
- Nom et prénoms
- Date et lieu de naissance
- Sexe
- Situation matrimoniale
- Nombre d'enfants
- Photo (optionnel)

#### Onglet 2 : Identification
- Nationalité
- Type de pièce d'identité (CNI, Passeport)
- Numéro de pièce
- Dates de délivrance et expiration
- **Numéro CNSS individuel** (obligatoire)

#### Onglet 3 : Contact
- Adresse actuelle
- Commune et préfecture de résidence
- Téléphones (principal et secondaire)
- Emails (personnel et professionnel)
- Contact d'urgence

#### Onglet 4 : Informations Professionnelles
- Matricule (généré automatiquement)
- Établissement
- Service
- Poste
- Date d'embauche
- Type de contrat (CDI, CDD, Stage)
- Supérieur hiérarchique

#### Onglet 5 : Informations Bancaires
- Mode de paiement (Virement, Mobile Money, Chèque)
- Banque et agence
- Numéro de compte / RIB
- Opérateur Mobile Money (Orange Money, MTN, etc.)

3. Cliquer sur **Enregistrer**

### Consulter un Dossier Employé

1. **Menu** > **Employés** > **Liste**
2. Rechercher l'employé (par nom, matricule, service)
3. Cliquer sur le nom pour ouvrir la fiche

La fiche employé affiche :
- **Informations générales**
- **Contrats** : Historique des contrats
- **Salaire** : Grille salariale actuelle
- **Congés** : Solde et historique
- **Formations** : Formations suivies
- **Carrière** : Promotions, mutations
- **Documents** : Contrats, attestations, etc.

### Modifier un Employé

1. Ouvrir la fiche employé
2. Cliquer sur **Modifier**
3. Apporter les modifications
4. Cliquer sur **Enregistrer**

### Créer un Contrat

1. Ouvrir la fiche employé
2. Onglet **Contrats** > **Nouveau contrat**
3. Remplir :
   - Type de contrat (CDI, CDD)
   - Date de début
   - Date de fin (pour CDD)
   - Période d'essai
   - Salaire de base
4. Joindre le contrat scanné (PDF)
5. Cliquer sur **Enregistrer**

### Définir le Salaire

1. Ouvrir la fiche employé
2. Onglet **Salaire** > **Nouvelle grille**
3. Remplir :
   - Date d'effet
   - Salaire de base
   - Primes (ancienneté, fonction, etc.)
   - Indemnités (transport, logement, nourriture)
4. Le système calcule automatiquement le brut mensuel
5. Cliquer sur **Enregistrer**

---

## ⏰ Temps de Travail

### Pointages

#### Saisir un Pointage

1. **Menu** > **Temps** > **Pointages** > **Nouveau**
2. Sélectionner l'employé
3. Sélectionner la date
4. Entrer :
   - Heure d'entrée
   - Heure de sortie
5. Le système calcule automatiquement :
   - Heures travaillées
   - Heures supplémentaires
   - Retards
6. Cliquer sur **Enregistrer**

#### Importer des Pointages

Pour importer depuis une pointeuse :

1. **Menu** > **Temps** > **Pointages** > **Importer**
2. Télécharger le fichier Excel/CSV
3. Mapper les colonnes
4. Cliquer sur **Importer**

#### Valider les Pointages

Les managers doivent valider les pointages :

1. **Menu** > **Temps** > **Pointages à valider**
2. Cocher les pointages à valider
3. Cliquer sur **Valider la sélection**

### Horaires de Travail

#### Affecter un Horaire

1. Ouvrir la fiche employé
2. Onglet **Horaires** > **Affecter un horaire**
3. Sélectionner l'horaire (Normal, Équipe, Nuit)
4. Date de début
5. Date de fin (optionnel)
6. Cliquer sur **Enregistrer**

---

## 💰 Module Paie

### Créer une Période de Paie

1. **Menu** > **Paie** > **Périodes** > **Nouvelle période**
2. Sélectionner :
   - Année
   - Mois
3. Le système génère automatiquement :
   - Dates de début et fin
   - Nombre de jours travaillés (22 par défaut)
4. Cliquer sur **Créer**

### Calculer les Bulletins

1. **Menu** > **Paie** > **Bulletins** > **Calculer**
2. Sélectionner la période
3. Sélectionner les employés (ou tous)
4. Cliquer sur **Lancer le calcul**

Le système calcule automatiquement :
- ✅ Salaire brut (base + primes + indemnités)
- ✅ Base CNSS (plafonnée à 3 000 000 GNF)
- ✅ CNSS employé (5%)
- ✅ INAM (2,5%)
- ✅ Base RTS (brut - CNSS - INAM)
- ✅ Abattement RTS (20%, max 300 000 GNF)
- ✅ RTS selon barème progressif
- ✅ Retenues (acomptes, prêts, sanctions)
- ✅ Net à payer
- ✅ CNSS employeur (18%)
- ✅ Coût total employeur

### Consulter un Bulletin

1. **Menu** > **Paie** > **Bulletins**
2. Filtrer par période, employé, service
3. Cliquer sur le bulletin pour le consulter

Le bulletin affiche :
- **En-tête** : Société, employé, période
- **Gains** : Détail des éléments de rémunération
- **Retenues** : CNSS, INAM, RTS, autres
- **Net à payer** : Montant final
- **Charges patronales** : CNSS employeur

### Modifier un Bulletin

1. Ouvrir le bulletin
2. Cliquer sur **Modifier**
3. Ajouter/modifier des lignes
4. Recalculer
5. Cliquer sur **Enregistrer**

### Valider les Bulletins

1. **Menu** > **Paie** > **Bulletins** > **À valider**
2. Vérifier les bulletins
3. Cocher les bulletins corrects
4. Cliquer sur **Valider la sélection**

### Générer les Bulletins PDF

1. **Menu** > **Paie** > **Bulletins**
2. Sélectionner la période
3. Cliquer sur **Générer PDF**
4. Choisir :
   - Un employé
   - Tous les employés
   - Par service
5. Les PDF sont générés et téléchargeables

### Livre de Paie

1. **Menu** > **Paie** > **Livre de paie**
2. Sélectionner la période
3. Le livre affiche tous les bulletins du mois
4. Export possible en Excel/PDF

---

## 🏖️ Congés et Absences

### Soldes de Congés

Chaque employé a un solde de congés :
- **Congés acquis** : 26 jours/an (Code du Travail guinéen)
- **Congés pris** : Cumulé dans l'année
- **Congés restants** : Disponible
- **Reports** : De l'année précédente

### Demander un Congé (Employé)

1. **Menu** > **Mes Demandes** > **Nouveau congé**
2. Remplir :
   - Type de congé (Annuel, Maladie, Maternité, etc.)
   - Date de début
   - Date de fin
   - Motif
   - Remplaçant (optionnel)
3. Le système calcule le nombre de jours ouvrables
4. Cliquer sur **Soumettre**

### Approuver un Congé (Manager)

1. **Menu** > **Congés** > **À approuver**
2. Consulter la demande
3. Vérifier le solde disponible
4. Cliquer sur :
   - **Approuver** : Le congé est validé
   - **Rejeter** : Avec commentaire

### Calendrier des Congés

1. **Menu** > **Congés** > **Calendrier**
2. Vue mensuelle/annuelle
3. Affiche tous les congés approuvés
4. Filtrable par service

### Saisir une Absence

1. **Menu** > **Temps** > **Absences** > **Nouvelle**
2. Sélectionner l'employé
3. Date d'absence
4. Type (Maladie, Accident, Injustifiée)
5. Justifiée ? (Oui/Non)
6. Joindre le justificatif (certificat médical)
7. Impact paie :
   - Payé
   - Non payé
   - Partiellement payé (%)
8. Cliquer sur **Enregistrer**

### Arrêts de Travail

Pour les arrêts maladie prolongés :

1. **Menu** > **Temps** > **Arrêts de travail** > **Nouveau**
2. Remplir :
   - Employé
   - Type (Maladie, Accident de travail)
   - Date de début
   - Durée prévue
   - Médecin prescripteur
   - Numéro de certificat
   - Organisme payeur (INAM, Employeur)
3. Joindre le certificat médical
4. Cliquer sur **Enregistrer**

---

## 💳 Prêts et Acomptes

### Demander un Acompte

1. **Menu** > **Mes Demandes** > **Acompte**
2. Remplir :
   - Montant demandé
   - Motif
   - Mois de déduction souhaité
3. Cliquer sur **Soumettre**

### Approuver un Acompte (RH)

1. **Menu** > **Paie** > **Acomptes** > **En attente**
2. Consulter la demande
3. Vérifier l'éligibilité
4. Cliquer sur **Approuver** ou **Rejeter**

### Demander un Prêt

1. **Menu** > **Mes Demandes** > **Prêt**
2. Sélectionner le type de prêt :
   - Prêt personnel (max 5 000 000 GNF)
   - Prêt scolaire (max 3 000 000 GNF)
   - Prêt logement (max 10 000 000 GNF)
   - Prêt santé (max 2 000 000 GNF)
3. Remplir :
   - Montant
   - Durée (en mois)
   - Motif
4. Le système calcule :
   - Taux d'intérêt
   - Mensualité
   - Échéancier
5. Cliquer sur **Soumettre**

### Approuver un Prêt (RH)

1. **Menu** > **Paie** > **Prêts** > **En attente**
2. Consulter la demande
3. Vérifier :
   - Ancienneté
   - Capacité de remboursement
   - Prêts en cours
4. Cliquer sur **Approuver** ou **Rejeter**

### Suivi des Prêts

1. **Menu** > **Paie** > **Prêts** > **En cours**
2. Affiche pour chaque prêt :
   - Montant initial
   - Montant remboursé
   - Montant restant
   - Échéances payées
   - Prochaine échéance

Les remboursements sont automatiquement déduits des bulletins de paie.

---

## 🎓 Recrutement

### Créer une Offre d'Emploi

1. **Menu** > **Recrutement** > **Offres** > **Nouvelle**
2. Remplir :
   - Intitulé du poste
   - Service
   - Type de contrat
   - Nombre de postes
   - Date limite de candidature
   - Description du poste
   - Profil recherché
   - Compétences requises
   - Salaire proposé (fourchette)
3. Cliquer sur **Publier**

### Gérer les Candidatures

1. **Menu** > **Recrutement** > **Candidatures**
2. Filtrer par offre, statut
3. Pour chaque candidature :
   - Consulter le CV
   - Lire la lettre de motivation
   - Changer le statut :
     - Reçue
     - Présélectionnée
     - Entretien
     - Retenue
     - Rejetée

### Planifier un Entretien

1. Ouvrir la candidature
2. Cliquer sur **Planifier entretien**
3. Remplir :
   - Type (Téléphonique, Présentiel, Visio)
   - Date et heure
   - Lieu
   - Intervieweurs
4. Envoyer une notification au candidat
5. Cliquer sur **Enregistrer**

### Évaluer un Candidat

Après l'entretien :

1. Ouvrir la candidature
2. Onglet **Entretiens**
3. Cliquer sur **Évaluer**
4. Noter :
   - Compétences techniques (/100)
   - Compétences comportementales (/100)
   - Motivation (/100)
5. Ajouter des commentaires
6. Décision : Favorable / Défavorable
7. Cliquer sur **Enregistrer**

### Embaucher un Candidat

1. Candidature retenue > **Embaucher**
2. Le système crée automatiquement :
   - Fiche employé
   - Contrat
   - Grille salariale
3. Compléter les informations manquantes
4. Générer le contrat de travail

---

## 📚 Formation et Carrière

### Enregistrer une Formation

1. Ouvrir la fiche employé
2. Onglet **Formations** > **Nouvelle**
3. Remplir :
   - Type (Initiale, Continue, Certification)
   - Intitulé
   - Organisme
   - Dates
   - Durée (heures)
   - Coût
   - Résultat (Acquis, En cours)
4. Joindre l'attestation
5. Cliquer sur **Enregistrer**

### Enregistrer un Mouvement de Carrière

Pour une promotion, mutation, reclassement :

1. Ouvrir la fiche employé
2. Onglet **Carrière** > **Nouveau mouvement**
3. Sélectionner le type :
   - Promotion
   - Mutation
   - Reclassement
   - Détachement
4. Remplir :
   - Date du mouvement
   - Ancien/Nouveau poste
   - Ancien/Nouveau service
   - Ancien/Nouveau salaire
   - Motif
   - Référence de la décision
5. Cliquer sur **Enregistrer**

Le système met automatiquement à jour :
- Le poste actuel
- Le service actuel
- La grille salariale

### Évaluation Annuelle

1. **Menu** > **Formation** > **Évaluations** > **Nouvelle**
2. Sélectionner l'employé
3. Année d'évaluation
4. Évaluateur (supérieur hiérarchique)
5. Noter :
   - Objectifs atteints (/100)
   - Compétences techniques (/100)
   - Compétences comportementales (/100)
6. Appréciation globale :
   - Excellent
   - Bien
   - Satisfaisant
   - Insuffisant
7. Rédiger :
   - Points forts
   - Points à améliorer
   - Plan de développement
8. Planifier le prochain entretien
9. Cliquer sur **Enregistrer**

---

## 📊 Rapports et Statistiques

### Tableau de Bord

Le tableau de bord affiche en temps réel :
- **Effectif** : Total, par sexe, par type de contrat
- **Pyramide des âges**
- **Ancienneté moyenne**
- **Masse salariale**
- **Congés en cours**
- **Alertes** : Contrats à échéance, documents expirés

### Rapports Prédéfinis

#### Effectif

1. **Menu** > **Rapports** > **Effectif**
2. Choisir :
   - Effectif global
   - Par service
   - Par catégorie professionnelle
   - Par établissement
3. Export Excel/PDF

#### Paie

1. **Menu** > **Rapports** > **Paie**
2. Rapports disponibles :
   - Livre de paie mensuel
   - Récapitulatif annuel
   - Masse salariale
   - Charges sociales
   - Journal comptable
3. Sélectionner la période
4. Export Excel/PDF

#### Temps de Travail

1. **Menu** > **Rapports** > **Temps**
2. Rapports disponibles :
   - Pointages du mois
   - Heures supplémentaires
   - Absences
   - Taux d'absentéisme
3. Filtrer par service, employé, période
4. Export Excel/PDF

#### Congés

1. **Menu** > **Rapports** > **Congés**
2. Rapports disponibles :
   - Soldes de congés
   - Congés pris
   - Planning des congés
3. Export Excel/PDF

### Déclarations Sociales

#### CNSS Mensuelle

1. **Menu** > **Déclarations** > **CNSS** > **Nouvelle**
2. Sélectionner la période
3. Le système génère automatiquement :
   - Liste des employés
   - Bases de cotisation
   - Montants CNSS employé/employeur
4. Vérifier et valider
5. Générer le fichier XML/Excel
6. Déposer à la CNSS

#### RTS Mensuelle

1. **Menu** > **Déclarations** > **RTS** > **Nouvelle**
2. Sélectionner la période
3. Le système génère :
   - Bases imposables
   - RTS par employé
   - Total RTS à reverser
4. Générer le fichier de déclaration
5. Déposer à la DGI

#### INAM

1. **Menu** > **Déclarations** > **INAM** > **Nouvelle**
2. Sélectionner la période
3. Génération automatique
4. Export et dépôt à l'INAM

---

## ⚙️ Configuration

### Paramètres de Paie

1. **Menu** > **Configuration** > **Paramètres de paie**
2. Modifier si nécessaire :
   - SMIG
   - Plafonds CNSS/INAM
   - Taux de cotisations
   - Abattement RTS
3. Ces paramètres sont pré-configurés selon la législation guinéenne

### Rubriques de Paie

1. **Menu** > **Configuration** > **Rubriques**
2. Ajouter/Modifier des rubriques personnalisées
3. Définir :
   - Code et libellé
   - Type (Gain, Retenue, Cotisation)
   - Formule de calcul
   - Soumission CNSS/RTS/INAM

### Jours Fériés

1. **Menu** > **Configuration** > **Jours fériés**
2. Ajouter les jours fériés de l'année
3. Pré-configuré pour la Guinée

### Utilisateurs et Droits

1. **Menu** > **Configuration** > **Utilisateurs**
2. Créer un utilisateur
3. Affecter un profil :
   - **Admin** : Accès complet
   - **RH** : Gestion RH et paie
   - **Manager** : Validation congés et pointages
   - **Opérateur** : Saisie des données
   - **Consultation** : Lecture seule

---

## 💡 Conseils et Bonnes Pratiques

### Saisie des Données

- ✅ Toujours vérifier le numéro CNSS
- ✅ Compléter tous les champs obligatoires
- ✅ Joindre les documents scannés
- ✅ Vérifier les dates (cohérence)

### Paie

- ✅ Valider les pointages avant le calcul
- ✅ Vérifier les soldes de congés
- ✅ Contrôler les bulletins avant validation
- ✅ Sauvegarder avant clôture de période

### Sécurité

- ✅ Changer régulièrement le mot de passe
- ✅ Se déconnecter après utilisation
- ✅ Ne pas partager ses identifiants
- ✅ Signaler toute anomalie

### Sauvegardes

- ✅ Sauvegarde quotidienne automatique
- ✅ Conserver 3 mois de sauvegardes
- ✅ Tester la restauration régulièrement

---

## 🆘 Aide et Support

### FAQ

**Q : Comment réinitialiser mon mot de passe ?**
R : Cliquer sur "Mot de passe oublié" sur la page de connexion.

**Q : Le calcul de paie est-il conforme à la législation guinéenne ?**
R : Oui, le système respecte le Code du Travail et les taux CNSS/RTS/INAM en vigueur.

**Q : Puis-je modifier un bulletin validé ?**
R : Non, il faut d'abord le dé-valider (droits Admin/RH requis).

**Q : Comment exporter les données ?**
R : Tous les rapports ont un bouton "Export Excel" ou "Export PDF".

### Contact Support

- **Email** : support@votre-entreprise.com
- **Téléphone** : +224 XXX XXX XXX
- **Documentation** : http://docs.votre-entreprise.com

---

**Bonne utilisation du Gestionnaire RH Guinée ! 🎉**
