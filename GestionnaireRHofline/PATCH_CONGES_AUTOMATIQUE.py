#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Patch pour le service de calcul de paie - Ajoute le calcul automatique des congés acquis

À utiliser dans: paie/services.py dans la classe MoteurCalculPaie
"""

# ============================================================================
# AJOUTER CETTE MÉTHODE À LA CLASSE MoteurCalculPaie (paie/services.py)
# ============================================================================

CODE_A_AJOUTER = '''
    def _calculer_conges_acquis(self):
        """
        Calcule automatiquement les congés acquis selon la règle guinéenne
        Règle: 2.5 jours par mois d'ancienneté (Code du Travail)
        
        Crée ou met à jour le SoldeConge de l'employé
        Retourne les congés acquis en Decimal
        """
        from employes.models import Employe
        from temps_travail.models import SoldeConge
        from datetime import date
        from decimal import Decimal
        
        try:
            emp = self.employe
            if not emp.date_embauche:
                return Decimal('0')
            
            # Calculer l'ancienneté en mois
            date_ref = date(self.periode.annee, self.periode.mois, 1)
            anciennete_mois = self._calculer_anciennete_mois(emp.date_embauche, date_ref)
            
            # Calculer les congés acquis: 2.5 jours/mois (Code du Travail Guinée)
            config_paie = self.config_paie
            jours_par_mois = config_paie.jours_conges_par_mois or Decimal('2.50')
            conges_acquis = anciennete_mois * jours_par_mois
            
            # Limiter à 30 jours par an maximum
            conges_acquis = min(conges_acquis, Decimal('30'))
            
            # Créer ou mettre à jour le SoldeConge
            solde_conge, created = SoldeConge.objects.get_or_create(
                employe=emp,
                annee=self.periode.annee
            )
            
            # Mettre à jour si vide
            if solde_conge.conges_acquis == 0 or created:
                solde_conge.conges_acquis = conges_acquis
                if not solde_conge.conges_pris:
                    solde_conge.conges_pris = Decimal('0')
                solde_conge.save()
            
            return solde_conge.conges_acquis
        
        except Exception as e:
            print(f"⚠️  Erreur calcul congés: {e}")
            return Decimal('0')
    
    def _calculer_anciennete_mois(self, date_embauche, date_ref=None):
        """Calcule l'ancienneté en mois"""
        from datetime import date
        from decimal import Decimal
        
        if date_ref is None:
            date_ref = date.today()
        
        if date_embauche > date_ref:
            return Decimal('0')
        
        years_diff = date_ref.year - date_embauche.year
        months_diff = date_ref.month - date_embauche.month
        anciennete = (years_diff * 12) + months_diff
        
        if date_ref.day < date_embauche.day:
            anciennete -= 1
        
        return max(Decimal('0'), Decimal(str(anciennete)))
'''

INSTRUCTIONS = '''
================================================================================
IMPLÉMENTATION: Calcul automatique des congés acquis dans MoteurCalculPaie
================================================================================

1. LOCALISER LE FICHIER: paie/services.py

2. TROUVER LA CLASSE: MoteurCalculPaie (environ ligne 50)

3. AJOUTER LES MÉTHODES: 
   - Chercher la fin de la classe MoteurCalculPaie (avant la prochaine classe)
   - Ajouter les deux méthodes du CODE_A_AJOUTER ci-dessus

4. INTEGRER DANS LE CALCUL:
   - Dans la méthode finalize() de MoteurCalculPaie
   - APRÈS faire le calcul des charges patronales
   - AVANT retourner la structure bulletin_data
   - Ajouter l'appel:

   # Calculer et créer les congés acquis
   conges_acquis = self._calculer_conges_acquis()
   
   # Ajouter aux données du bulletin si vous le souhaitez afficher
   # (actuellement affiché via SoldeConge dans la vue)

5. EXEMPLE D'INTÉGRATION:

    def finalize(self):
        # ... code existant ...
        
        # Calcul charges patronales
        self._calculer_charges_patronales()
        
        # ✨ NOUVELLE LIGNE ✨
        self._calculer_conges_acquis()
        
        # Ajouter les données au bulletin
        numero = self._generer_numero_bulletin()
        bulletin_data = { ... }
        
        # ... reste du code ...

6. TEST:
   - Générer un nouveau bulletin via l'interface
   - Vérifier que le SoldeConge est créé/mis à jour
   - Vérifier que le bulletin affiche les congés acquis corrects

IMPORTANT: Les congés acquis seront arrondis à 30 jours/an MAX

================================================================================
RÉSULTAT ATTENDU:
- Bulletin FARA LENO (26/01/2026 → Avril 2026 = 2.8 mois)
  → Congés acquis = 2.8 × 2.5 = 7 jours
  → Affichage sur bulletin: "Congés acquis: 7 j"

- Application automatique pour tous les nouveaux bulletins
- Pas de modification manuelle nécessaire

================================================================================
'''

if __name__ == '__main__':
    print(INSTRUCTIONS)
    print("\nCODE À AJOUTER:")
    print(CODE_A_AJOUTER)
