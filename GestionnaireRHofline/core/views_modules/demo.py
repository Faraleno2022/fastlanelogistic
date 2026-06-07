"""
Vues de démonstration commerciale GuineeRH
Accessibles sans authentification pour les prospects.
"""
import os
from pathlib import Path
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.decorators.cache import cache_control


EMPLOYES_DEMO = [
    {
        'matricule': 'SGPH-001',
        'nom': 'CAMARA Alpha Oumar',
        'poste': 'Directeur Général',
        'service': 'Direction Générale',
        'type_contrat': 'CDI',
        'salaire_brut': 10_850_000,
        'cnss_salarie': 467_500,
        'rts': 1_107_625,
        'net_a_payer': 9_274_875,
        'cnss_employeur': 1_683_000,
        'vf': 651_000,
        'ta': 217_000,
    },
    {
        'matricule': 'SGPH-002',
        'nom': 'DIALLO Fatoumata',
        'poste': 'Responsable RH Senior',
        'service': 'Ressources Humaines',
        'type_contrat': 'CDI',
        'salaire_brut': 4_170_000,
        'cnss_salarie': 176_000,
        'rts': 220_200,
        'net_a_payer': 3_773_800,
        'cnss_employeur': 633_600,
        'vf': 250_200,
        'ta': 83_400,
    },
    {
        'matricule': 'SGPH-003',
        'nom': 'BALDE Mamadou Cellou',
        'poste': 'Chargé Commercial',
        'service': 'Commercial & Ventes',
        'type_contrat': 'CDI',
        'salaire_brut': 3_450_000,
        'cnss_salarie': 160_000,
        'rts': 129_500,
        'net_a_payer': 3_160_500,
        'cnss_employeur': 561_000,
        'vf': 207_000,
        'ta': 69_000,
    },
    {
        'matricule': 'SGPH-004',
        'nom': 'KOUROUMA Sekou',
        'poste': 'Technicien Réseaux',
        'service': 'Technique & Réseaux',
        'type_contrat': 'CDI',
        'salaire_brut': 2_450_000,
        'cnss_salarie': 112_500,
        'rts': 59_250,
        'net_a_payer': 2_278_250,
        'cnss_employeur': 378_000,
        'vf': 147_000,
        'ta': 49_000,
    },
    {
        'matricule': 'SGPH-005',
        'nom': 'SOUMAH Aminata',
        'poste': 'Stagiaire',
        'service': 'Ressources Humaines',
        'type_contrat': 'Stage',
        'salaire_brut': 800_000,
        'cnss_salarie': 35_000,
        'rts': 0,
        'net_a_payer': 765_000,
        'cnss_employeur': 126_000,
        'vf': 48_000,
        'ta': 16_000,
    },
]


def fmt_gnf(montant):
    """Formate un montant en GNF."""
    return f"{montant:,.0f}".replace(',', '\u202f')


@cache_control(no_cache=True, no_store=True)
def demo_accueil(request):
    """Page d'accueil de la démonstration commerciale."""
    # Calculs totaux
    total_brut = sum(e['salaire_brut'] for e in EMPLOYES_DEMO)
    total_cnss = sum(e['cnss_salarie'] for e in EMPLOYES_DEMO)
    total_rts = sum(e['rts'] for e in EMPLOYES_DEMO)
    total_net = sum(e['net_a_payer'] for e in EMPLOYES_DEMO)

    # Vérifier si le PDF existe
    pdf_path = Path(settings.BASE_DIR) / 'demo' / 'GuineeRH_Demo_Commercial.pdf'
    pdf_disponible = pdf_path.exists()

    employes_fmt = []
    for emp in EMPLOYES_DEMO:
        employes_fmt.append({
            **emp,
            'salaire_brut_fmt': fmt_gnf(emp['salaire_brut']),
            'cnss_salarie_fmt': fmt_gnf(emp['cnss_salarie']),
            'rts_fmt': fmt_gnf(emp['rts']) if emp['rts'] > 0 else '—',
            'net_a_payer_fmt': fmt_gnf(emp['net_a_payer']),
        })

    context = {
        'entreprise': {
            'nom': 'SOGUIPHONE SARL',
            'secteur': 'Télécommunications',
            'ville': 'Conakry, Guinée',
            'nif': 'NIF-DEMO-001',
            'cnss': 'CNSS-DEMO-001',
        },
        'periode': 'Mars 2026',
        'employes': employes_fmt,
        'employe_detail': employes_fmt[0],  # Directeur pour détail bulletin
        'totaux': {
            'brut': fmt_gnf(total_brut),
            'cnss': fmt_gnf(total_cnss),
            'rts': fmt_gnf(total_rts),
            'net': fmt_gnf(total_net),
        },
        'pdf_disponible': pdf_disponible,
        'fonctionnalites': [
            {'icone': '📊', 'titre': 'Paie & Bulletins',
             'desc': 'Calcul automatique CNSS, RTS, charges patronales. Bulletins PDF multi-modèles.'},
            {'icone': '👥', 'titre': 'Gestion RH',
             'desc': 'Dossiers employés complets, contrats, historique, suivi des congés.'},
            {'icone': '⏱', 'titre': 'Temps de Travail',
             'desc': 'Pointage, heures supplémentaires 30%/60%, primes nuit & fériés.'},
            {'icone': '📋', 'titre': 'Déclarations Légales',
             'desc': 'Télédéclaration CNSS, déclarations fiscales RTS/VF/TA, rapports Inspection.'},
            {'icone': '🔒', 'titre': 'Sécurisé & Hors Ligne',
             'desc': 'Multi-utilisateurs, droits par module, fonctionne 100% sans internet.'},
            {'icone': '✅', 'titre': 'Conforme Guinée',
             'desc': 'Code du Travail guinéen, barème RTS 2026, CNSS actualisé.'},
        ],
    }
    return render(request, 'demo/accueil.html', context)


@cache_control(no_cache=True, no_store=True)
def demo_telecharger_pdf(request):
    """Télécharge le PDF de présentation commerciale."""
    pdf_path = Path(settings.BASE_DIR) / 'demo' / 'GuineeRH_Demo_Commercial.pdf'
    if not pdf_path.exists():
        raise Http404(
            "Le PDF de démonstration n'est pas encore généré. "
            "Exécutez: python manage.py generer_demo_pdf"
        )
    with open(pdf_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="GuineeRH_Demo_Commercial.pdf"'
        )
        return response
