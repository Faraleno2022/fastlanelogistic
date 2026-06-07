#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de remplissage automatique des congés acquire
Règle guinéenne: 2.5 jours par mois d'ancienneté (Code du Travail)
"""

import os
import sys
import django
from datetime import date, datetime
from decimal import Decimal

# Configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

from employes.models import Employe
from temps_travail.models import SoldeConge
from paie.models import BulletinPaie, ConfigPaieEntreprise

def calculer_anciennete_mois(date_embauche, date_reference=None):
    """
    Calcule l'ancienneté en mois
    Formule: (années * 12) + mois supplémentaires
    """
    if date_reference is None:
        date_reference = date.today()
    
    # Éviter les dates invalides
    if date_embauche > date_reference:
        return Decimal('0')
    
    years_diff = date_reference.year - date_embauche.year
    months_diff = date_reference.month - date_embauche.month
    
    anciennete_mois = (years_diff * 12) + months_diff
    
    # Ajuster si pas encore atteint le jour d'embauche ce mois-ci
    if date_reference.day < date_embauche.day:
        anciennete_mois -= 1
    
    return max(Decimal('0'), Decimal(str(anciennete_mois)))

def calculer_conges_acquis(anciennete_mois, config_paie=None, employe=None):
    """
    Calcule les congés acquis selon la configuration
    
    Règles:
    - Code du Travail: 1.5 j/mois (18 j/an)
    - Convention: 2.5 j/mois (30 j/an)
    - Bonus ancienneté: +2 j par tranche (généralement 5 ans)
    """
    if config_paie is None:
        config_paie = ConfigPaieEntreprise.objects.first()
    
    if config_paie is None:
        # Par défaut: utiliser la règle guinéenne (2.5 j/mois)
        jours_par_mois = Decimal('2.50')
    else:
        jours_par_mois = config_paie.jours_conges_par_mois
    
    # Calcul de base
    conges_base = anciennete_mois * jours_par_mois
    
    # Bonus d'ancienneté (optionnel)
    conges_bonus = Decimal('0')
    if config_paie and config_paie.jours_conges_anciennete > 0:
        tranche = Decimal(str(config_paie.tranche_anciennete_annees or 5))
        anciennes_annees = anciennete_mois / Decimal('12')
        nb_tranches = int(anciennes_annees / tranche)
        conges_bonus = nb_tranches * config_paie.jours_conges_anciennete
    
    total_conges = conges_base + conges_bonus
    
    # Limiter à un maximum raisonnable (généralement 30 jours par an)
    max_conges_par_an = Decimal('30')
    max_conges = max_conges_par_an
    total_conges = min(total_conges, max_conges)
    
    return total_conges

def remplir_conges_employe(employe, annee=None):
    """
    Crée ou met à jour le SoldeConge pour un employé
    """
    if annee is None:
        annee = date.today().year
    
    if not employe.date_embauche:
        print(f"  ⚠️  {employe.matricule} - {employe.nom}: Pas de date d'embauche")
        return False
    
    # Calculer l'ancienneté au 31/12 de l'année en question
    date_reference = date(annee, 12, 31)
    anciennete_mois = calculer_anciennete_mois(employe.date_embauche, date_reference)
    
    # Obtenir la config de l'entreprise
    config_paie = None
    if employe.entreprise:
        config_paie = ConfigPaieEntreprise.objects.filter(
            entreprise=employe.entreprise
        ).first()
    
    # Calculer les congés acquis
    conges_acquis = calculer_conges_acquis(anciennete_mois, config_paie, employe)
    
    # Créer ou mettre à jour le SoldeConge
    solde_conge, created = SoldeConge.objects.get_or_create(
        employe=employe,
        annee=annee
    )
    
    # Mettre à jour uniquement si les congés acquis n'avaient pas été remplis
    if solde_conge.conges_acquis == 0 or created:
        solde_conge.conges_acquis = conges_acquis
        # Garder les congés pris s'ils existent (ne pas les réinitialiser)
        if not solde_conge.conges_pris or solde_conge.conges_pris == 0:
            solde_conge.conges_pris = Decimal('0')
        solde_conge.save()
        
        status = "✓ Créé" if created else "✓ Mis à jour"
        print(f"  {status}: {employe.matricule} - {employe.nom}")
        print(f"       Ancienneté: {anciennete_mois:.1f} mois")
        print(f"       Congés acquis: {conges_acquis:.2f} jours")
        return True
    else:
        print(f"  • {employe.matricule} - {employe.nom}: Congés déjà remplis ({solde_conge.conges_acquis:.2f}j)")
        return False

def main():
    print("=" * 70)
    print("🎯 Script de remplissage automatiqueConés Acquis")
    print("=" * 70)
    print("\nRègle: Code du Travail Guinéen = 2.5 jours/mois ou selon config\n")
    
    # 1. Récupérer tous les employés actifs
    print("📋 Recherche des employés...\n")
    employes = Employe.objects.filter(
        statut_employe='actif'
    ).exclude(
        date_embauche__isnull=True
    ).order_by('entreprise', 'nom')
    
    if not employes.exists():
        print("✗ Aucun employé actif trouvé")
        return False
    
    print(f"✓ {employes.count()} employés trouvés\n")
    
    # 2. Grouper par entreprise
    entreprises = {}
    for emp in employes:
        ent = emp.entreprise.nom_entreprise if emp.entreprise else "N/A"
        if ent not in entreprises:
            entreprises[ent] = []
        entreprises[ent].append(emp)
    
    # 3. Remplir les congés par employé
    total_updated = 0
    annee_courante = date.today().year
    
    for nom_ent, emps in entreprises.items():
        print(f"🏢 Entreprise: {nom_ent}")
        print(f"   Année: {annee_courante}\n")
        
        for emp in emps:
            if remplir_conges_employe(emp, annee_courante):
                total_updated += 1
        
        print()
    
    # 4. Vérification
    print("\n" + "=" * 70)
    print(f"✅ Résumé: {total_updated} employés mis à jour")
    print("=" * 70)
    
    # 5. Afficher un exemple
    if employes.exists():
        emp_exemple = employes.first()
        solde = SoldeConge.objects.filter(
            employe=emp_exemple,
            annee=annee_courante
        ).first()
        if solde:
            anciennete_exemple = calculer_anciennete_mois(emp_exemple.date_embauche)
            print(f"\n📌 Exemple - {emp_exemple.nom}:")
            print(f"   Ancienneté: {anciennete_exemple:.1f} mois")
            print(f"   Congés acquis: {solde.conges_acquis:.2f} jours")
            print(f"   Congés pris: {solde.conges_pris:.2f} jours")
            print(f"   Solde restant: {solde.conges_restants:.2f} jours")
    
    print("\n✅ Script complété avec succès!")
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
