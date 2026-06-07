#!/usr/bin/env python
"""
GÉNÉRATEUR DE CLÉS DE LICENCE - Gestionnaire RH Guinée
========================================================
Outil réservé au vendeur pour générer des clés de licence

Usage:
    python generer_licence.py

Format des clés: XXXX-XXXX-XXXX-XXXX
    - Segment 1: Plan (ST=Starter, PR=Pro, EN=Enterprise)
    - Segment 2: Durée (TR=Trial, ME=Mensuel, AN=Annuel, PE=Perpétuel)
    - Segments 3-4: Identifiant unique

Tarification suggérée:
    - Starter (10 employés):    500 000 GNF/mois  |  5 000 000 GNF/an
    - Pro (50 employés):      1 500 000 GNF/mois  | 15 000 000 GNF/an
    - Enterprise (illimité):  3 000 000 GNF/mois  | 30 000 000 GNF/an
"""

import secrets
import datetime
import os
import sys
import hashlib
import hmac as hmac_module

# ─── Protection anti-vol : vérification machine propriétaire ─────────────────
try:
    from project_guardian import guard_license_generation
    guard_license_generation()
except PermissionError as _pe:
    print(str(_pe))
    sys.exit(1)
except ImportError:
    print("\n⛔ ERREUR DE SÉCURITÉ : Module de protection introuvable.")
    print("Le générateur de licences ne peut pas s'exécuter sans project_guardian.py.")
    sys.exit(1)
# ─── Fin protection anti-vol ──────────────────────────────────────────────────

# Caractères utilisés (sans I, O, 0, 1 pour éviter confusion)
CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

# Clé secrète HMAC - IDENTIQUE à celle dans core/models_licence.py
# NE JAMAIS PARTAGER CE FICHIER
_HMAC_KEY = 'GRH-Guinee-2025-SecretKey-Faraleno'


def generer_segment():
    """Génère un segment aléatoire de 4 caractères"""
    return ''.join(secrets.choice(CHARS) for _ in range(4))


def calculer_signature_hmac(payload):
    """
    Calcule la signature HMAC pour un payload donné.
    Retourne 4 caractères du jeu de licence.
    """
    key = _HMAC_KEY.encode('utf-8')
    sig_hex = hmac_module.new(key, payload.encode('utf-8'), hashlib.sha256).hexdigest()[:4].upper()
    
    sig_finale = ''
    for c in sig_hex:
        idx = int(c, 16) % len(CHARS)
        sig_finale += CHARS[idx]
    
    return sig_finale


def generer_cle(plan='starter', duree='annuel'):
    """
    Génère une clé de licence signée par HMAC
    
    Args:
        plan: 'starter', 'pro', ou 'enterprise'
        duree: 'trial', 'mensuel', 'annuel', ou 'perpetuel'
    
    Returns:
        Clé de licence au format PPDD-XXXX-XXXX-HHHH
        où HHHH est la signature HMAC
    """
    # Préfixe du plan
    prefixes_plan = {
        'starter': 'ST',
        'pro': 'PR',
        'enterprise': 'EN'
    }
    
    # Préfixe de durée
    prefixes_duree = {
        'trial': 'TR',
        'mensuel': 'ME',
        'annuel': 'AN',
        'perpetuel': 'PE'
    }
    
    prefix_plan = prefixes_plan.get(plan, 'ST')
    prefix_duree = prefixes_duree.get(duree, 'AN')
    
    # Générer les segments
    segment1 = prefix_plan + generer_segment()[:2]
    segment2 = prefix_duree + generer_segment()[:2]
    segment3 = generer_segment()
    
    # Calculer la signature HMAC sur les 3 premiers segments
    payload = f"{segment1}-{segment2}-{segment3}"
    segment4 = calculer_signature_hmac(payload)
    
    return f"{payload}-{segment4}"


def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "=" * 60)
    print("   GÉNÉRATEUR DE LICENCES - Gestionnaire RH Guinée")
    print("=" * 60)
    print("\n📋 PLANS DISPONIBLES:")
    print("   1. Starter    - 10 employés max  (500 000 GNF/mois)")
    print("   2. Pro        - 50 employés max  (1 500 000 GNF/mois)")
    print("   3. Enterprise - Illimité         (3 000 000 GNF/mois)")
    print("\n⏱️  DURÉES:")
    print("   a. Essai (30 jours gratuit)")
    print("   b. Mensuel")
    print("   c. Annuel")
    print("   d. Perpétuel")
    print("\n" + "-" * 60)


def sauvegarder_licence(cle, plan, duree, client=""):
    """Sauvegarde la licence dans un fichier de suivi"""
    fichier = "licences_generees.txt"
    
    with open(fichier, 'a', encoding='utf-8') as f:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{date} | {cle} | {plan.upper()} | {duree.upper()} | {client}\n")
    
    print(f"\n✅ Licence sauvegardée dans {fichier}")


def main():
    """Programme principal"""
    
    while True:
        afficher_menu()
        
        # Choix du plan
        print("Choisissez le plan (1-3) ou 'q' pour quitter:")
        choix_plan = input("> ").strip().lower()
        
        if choix_plan == 'q':
            print("\nAu revoir!")
            break
        
        plans = {'1': 'starter', '2': 'pro', '3': 'enterprise'}
        plan = plans.get(choix_plan)
        
        if not plan:
            print("❌ Choix invalide")
            continue
        
        # Choix de la durée
        print("\nChoisissez la durée (a-d):")
        choix_duree = input("> ").strip().lower()
        
        durees = {'a': 'trial', 'b': 'mensuel', 'c': 'annuel', 'd': 'perpetuel'}
        duree = durees.get(choix_duree)
        
        if not duree:
            print("❌ Choix invalide")
            continue
        
        # Nom du client (optionnel)
        print("\nNom du client (optionnel):")
        client = input("> ").strip()
        
        # Générer la clé
        cle = generer_cle(plan, duree)
        
        # Afficher le résultat
        print("\n" + "=" * 60)
        print("   🔑 LICENCE GÉNÉRÉE")
        print("=" * 60)
        print(f"\n   Clé:     {cle}")
        print(f"   Plan:    {plan.upper()}")
        print(f"   Durée:   {duree.upper()}")
        if client:
            print(f"   Client:  {client}")
        
        # Calculer le prix
        prix_mensuel = {'starter': 500000, 'pro': 1500000, 'enterprise': 3000000}
        prix = prix_mensuel[plan]
        
        if duree == 'trial':
            print(f"   Prix:    GRATUIT (essai)")
        elif duree == 'mensuel':
            print(f"   Prix:    {prix:,} GNF".replace(',', ' '))
        elif duree == 'annuel':
            print(f"   Prix:    {prix * 10:,} GNF (10 mois = 2 mois offerts)".replace(',', ' '))
        elif duree == 'perpetuel':
            print(f"   Prix:    {prix * 24:,} GNF (équivalent 2 ans)".replace(',', ' '))
        
        print("\n" + "=" * 60)
        
        # Sauvegarder
        sauvegarder_licence(cle, plan, duree, client)
        
        # Copier dans le presse-papier si possible
        try:
            import pyperclip
            pyperclip.copy(cle)
            print("📋 Clé copiée dans le presse-papier!")
        except:
            pass
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == '__main__':
    main()
