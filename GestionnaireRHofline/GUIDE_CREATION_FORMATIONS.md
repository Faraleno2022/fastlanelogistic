# 📝 GUIDE : CRÉER DES FORMATIONS

**Date** : 22 Octobre 2025

---

## 🎯 MÉTHODE 1 : VIA L'INTERFACE WEB (Recommandé)

### **Étape 1 : Accéder au formulaire**
```
http://127.0.0.1:8000/formation/catalogue/creer/
```

### **Étape 2 : Remplir le formulaire**

#### **Informations Générales**
- **Intitulé** : Nom de la formation (Ex: "Management d'équipe")
- **Type** : Interne, Externe, En ligne, ou Certifiante
- **Domaine** : Technique, Management, Sécurité, etc.

#### **Description**
- **Description** : Présentation générale
- **Objectifs** : Ce que les participants vont apprendre
- **Contenu** : Programme détaillé
- **Prérequis** : Conditions nécessaires

#### **Durée et Coût**
- **Durée en jours** : Ex: 3
- **Durée en heures** : Ex: 21
- **Coût unitaire** : Ex: 500000 GNF

#### **Organisme**
- **Organisme formateur** : Nom du formateur ou centre

### **Étape 3 : Valider**
- Cliquer sur "Créer la Formation"
- Un code unique est généré automatiquement (FORM-XXX)

---

## 🎯 MÉTHODE 2 : VIA LE SHELL DJANGO

### **Ouvrir le shell**
```bash
python manage.py shell
```

### **Créer une formation simple**
```python
from formation.models import CatalogueFormation

# Créer une formation
formation = CatalogueFormation.objects.create(
    code_formation='FORM-001',
    intitule='Management d\'équipe',
    type_formation='interne',
    domaine='management',
    description='Formation sur les techniques de management',
    objectifs='Apprendre à gérer une équipe efficacement',
    duree_jours=3,
    duree_heures=21,
    cout_unitaire=500000,
    actif=True
)

print(f"Formation créée : {formation}")
```

### **Créer plusieurs formations d'un coup**
```python
from formation.models import CatalogueFormation

formations = [
    {
        'code_formation': 'FORM-001',
        'intitule': 'Management d\'équipe',
        'type_formation': 'interne',
        'domaine': 'management',
        'description': 'Techniques de management moderne',
        'duree_jours': 3,
        'duree_heures': 21,
        'cout_unitaire': 500000,
    },
    {
        'code_formation': 'FORM-002',
        'intitule': 'Excel Avancé',
        'type_formation': 'externe',
        'domaine': 'informatique',
        'description': 'Maîtriser Excel niveau avancé',
        'duree_jours': 2,
        'duree_heures': 14,
        'cout_unitaire': 300000,
    },
    {
        'code_formation': 'FORM-003',
        'intitule': 'Sécurité au Travail',
        'type_formation': 'certifiante',
        'domaine': 'securite',
        'description': 'Formation HSE certifiante',
        'duree_jours': 5,
        'duree_heures': 35,
        'cout_unitaire': 800000,
    },
    {
        'code_formation': 'FORM-004',
        'intitule': 'Communication Efficace',
        'type_formation': 'interne',
        'domaine': 'soft_skills',
        'description': 'Améliorer sa communication',
        'duree_jours': 2,
        'duree_heures': 14,
        'cout_unitaire': 250000,
    },
    {
        'code_formation': 'FORM-005',
        'intitule': 'Anglais Professionnel',
        'type_formation': 'externe',
        'domaine': 'langues',
        'description': 'Anglais pour le milieu professionnel',
        'duree_jours': 10,
        'duree_heures': 30,
        'cout_unitaire': 600000,
    },
]

for data in formations:
    formation = CatalogueFormation.objects.create(**data)
    print(f"✅ Créé : {formation.intitule}")

print(f"\n🎉 {len(formations)} formations créées !")
```

---

## 🎯 MÉTHODE 3 : SCRIPT PYTHON

### **Créer un fichier : `creer_formations_test.py`**
```python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionnaire_rh.settings')
django.setup()

from formation.models import CatalogueFormation

def creer_formations_test():
    """Créer des formations de test"""
    
    formations_data = [
        {
            'code_formation': 'FORM-001',
            'intitule': 'Leadership et Management',
            'type_formation': 'interne',
            'domaine': 'management',
            'description': 'Développer ses compétences en leadership',
            'objectifs': 'Maîtriser les techniques de management moderne',
            'contenu': 'Module 1: Bases du leadership\nModule 2: Gestion d\'équipe\nModule 3: Prise de décision',
            'prerequis': 'Aucun prérequis',
            'duree_jours': 3,
            'duree_heures': 21,
            'organisme_formateur': 'Centre de Formation Interne',
            'cout_unitaire': 500000,
            'actif': True
        },
        {
            'code_formation': 'FORM-002',
            'intitule': 'Excel Avancé - Tableaux Croisés',
            'type_formation': 'externe',
            'domaine': 'informatique',
            'description': 'Maîtriser Excel niveau avancé',
            'objectifs': 'Créer des tableaux croisés dynamiques et des macros',
            'contenu': 'Tableaux croisés\nFormules avancées\nMacros VBA',
            'prerequis': 'Connaissances de base d\'Excel',
            'duree_jours': 2,
            'duree_heures': 14,
            'organisme_formateur': 'IT Training Center',
            'cout_unitaire': 300000,
            'actif': True
        },
        {
            'code_formation': 'FORM-003',
            'intitule': 'HSE - Sécurité au Travail',
            'type_formation': 'certifiante',
            'domaine': 'securite',
            'description': 'Formation certifiante en HSE',
            'objectifs': 'Obtenir la certification HSE niveau 1',
            'contenu': 'Réglementation\nÉvaluation des risques\nPrévention',
            'prerequis': 'Aucun',
            'duree_jours': 5,
            'duree_heures': 35,
            'organisme_formateur': 'Centre HSE Guinée',
            'cout_unitaire': 800000,
            'actif': True
        },
        {
            'code_formation': 'FORM-004',
            'intitule': 'Communication Interpersonnelle',
            'type_formation': 'interne',
            'domaine': 'soft_skills',
            'description': 'Améliorer sa communication',
            'objectifs': 'Communiquer efficacement en entreprise',
            'contenu': 'Écoute active\nCommunication non-verbale\nGestion des conflits',
            'prerequis': 'Aucun',
            'duree_jours': 2,
            'duree_heures': 14,
            'organisme_formateur': 'Formation Interne',
            'cout_unitaire': 250000,
            'actif': True
        },
        {
            'code_formation': 'FORM-005',
            'intitule': 'Anglais Professionnel',
            'type_formation': 'externe',
            'domaine': 'langues',
            'description': 'Anglais pour le milieu professionnel',
            'objectifs': 'Communiquer en anglais dans un contexte professionnel',
            'contenu': 'Vocabulaire professionnel\nRédaction d\'emails\nPrésentations',
            'prerequis': 'Niveau A2 minimum',
            'duree_jours': 10,
            'duree_heures': 30,
            'organisme_formateur': 'English Training Center',
            'cout_unitaire': 600000,
            'actif': True
        },
        {
            'code_formation': 'FORM-006',
            'intitule': 'Gestion de Projet Agile',
            'type_formation': 'certifiante',
            'domaine': 'management',
            'description': 'Méthodologie Agile et Scrum',
            'objectifs': 'Maîtriser la gestion de projet Agile',
            'contenu': 'Principes Agile\nScrum\nKanban',
            'prerequis': 'Expérience en gestion de projet',
            'duree_jours': 3,
            'duree_heures': 21,
            'organisme_formateur': 'Agile Academy',
            'cout_unitaire': 700000,
            'actif': True
        },
        {
            'code_formation': 'FORM-007',
            'intitule': 'Maintenance Préventive',
            'type_formation': 'interne',
            'domaine': 'technique',
            'description': 'Techniques de maintenance préventive',
            'objectifs': 'Mettre en place un plan de maintenance',
            'contenu': 'Diagnostic\nPlanification\nSuivi',
            'prerequis': 'Connaissances techniques de base',
            'duree_jours': 4,
            'duree_heures': 28,
            'organisme_formateur': 'Service Maintenance',
            'cout_unitaire': 400000,
            'actif': True
        },
        {
            'code_formation': 'FORM-008',
            'intitule': 'Python pour Débutants',
            'type_formation': 'en_ligne',
            'domaine': 'informatique',
            'description': 'Apprendre la programmation Python',
            'objectifs': 'Maîtriser les bases de Python',
            'contenu': 'Syntaxe\nStructures de données\nProgrammation orientée objet',
            'prerequis': 'Aucun',
            'duree_jours': 5,
            'duree_heures': 20,
            'organisme_formateur': 'Online Academy',
            'cout_unitaire': 350000,
            'actif': True
        },
    ]
    
    created_count = 0
    for data in formations_data:
        try:
            formation, created = CatalogueFormation.objects.get_or_create(
                code_formation=data['code_formation'],
                defaults=data
            )
            if created:
                print(f"✅ Créé : {formation.intitule}")
                created_count += 1
            else:
                print(f"ℹ️  Existe déjà : {formation.intitule}")
        except Exception as e:
            print(f"❌ Erreur pour {data['intitule']}: {e}")
    
    print(f"\n🎉 {created_count} nouvelles formations créées !")
    print(f"📊 Total formations : {CatalogueFormation.objects.count()}")

if __name__ == '__main__':
    creer_formations_test()
```

### **Exécuter le script**
```bash
python creer_formations_test.py
```

---

## 📊 EXEMPLES DE FORMATIONS PAR DOMAINE

### **Management**
- Leadership et Management
- Gestion de Projet Agile
- Gestion du Temps
- Délégation Efficace

### **Informatique**
- Excel Avancé
- Python pour Débutants
- Cybersécurité
- Power BI

### **Sécurité**
- HSE - Sécurité au Travail
- Premiers Secours
- Gestion des Risques
- Sécurité Incendie

### **Soft Skills**
- Communication Interpersonnelle
- Gestion du Stress
- Travail d'Équipe
- Résolution de Conflits

### **Langues**
- Anglais Professionnel
- Français des Affaires
- Espagnol Commercial

### **Technique**
- Maintenance Préventive
- Électricité Industrielle
- Mécanique
- Soudure

---

## ✅ VÉRIFIER LES FORMATIONS CRÉÉES

### **Via l'interface web**
```
http://127.0.0.1:8000/formation/catalogue/
```

### **Via le shell**
```python
from formation.models import CatalogueFormation

# Compter les formations
print(f"Total : {CatalogueFormation.objects.count()}")

# Lister toutes les formations
for f in CatalogueFormation.objects.all():
    print(f"- {f.code_formation}: {f.intitule} ({f.get_domaine_display()})")

# Formations par domaine
from django.db.models import Count
stats = CatalogueFormation.objects.values('domaine').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['domaine']}: {stat['count']} formations")
```

---

## 🎯 CRÉER UN PLAN DE FORMATION

```python
from formation.models import PlanFormation
from datetime import date

# Créer le plan 2025
plan = PlanFormation.objects.create(
    annee=2025,
    budget_total=50000000,  # 50 millions GNF
    objectifs='Développer les compétences des employés',
    statut='valide'
)

print(f"✅ Plan de formation {plan.annee} créé")
print(f"Budget : {plan.budget_total} GNF")
```

---

## 🚀 WORKFLOW COMPLET

### **1. Créer des formations**
```
Via interface : /formation/catalogue/creer/
ou
Via shell : CatalogueFormation.objects.create(...)
```

### **2. Planifier des sessions**
```
/formation/sessions/planifier/
```

### **3. Inscrire des employés**
```
/formation/sessions/<id>/inscrire/
```

### **4. Évaluer les participants**
```
/formation/inscriptions/<id>/evaluer/
```

---

## 📝 CHAMPS OBLIGATOIRES

- ✅ **intitule** - Nom de la formation
- ✅ **type_formation** - Type (interne, externe, en_ligne, certifiante)
- ✅ **domaine** - Domaine (technique, management, etc.)
- ✅ **duree_jours** - Durée en jours
- ✅ **duree_heures** - Durée en heures

## 📝 CHAMPS OPTIONNELS

- description
- objectifs
- contenu
- prerequis
- organisme_formateur
- cout_unitaire

---

## ✅ RÉSUMÉ

**3 méthodes pour créer des formations** :

1. ✅ **Interface Web** - Simple et visuel
2. ✅ **Shell Django** - Rapide pour tests
3. ✅ **Script Python** - Pour créer beaucoup de données

**Choisissez la méthode qui vous convient !**

---

**Développé avec ❤️ pour la Guinée**
