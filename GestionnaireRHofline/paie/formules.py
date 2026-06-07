"""
Moteur d'évaluation de formules de paie — sécurisé via simpleeval.

Aucun eval()/exec() — utilise simpleeval qui ne permet pas :
  - import, accès fichier, accès réseau
  - accès à __builtins__, os, sys, subprocess
  - boucles infinies (limité en profondeur)

Variables disponibles dans les formules :
  brut, cnss, indemnites, salaire_base, primes, heures_sup,
  total_gains, total_retenues, cnss_base, net,
  anciennete_mois, anciennete_ans, nb_enfants, nb_conjoints, plafond_cnss

Phases de calcul (restreignent les variables accessibles) :
  gains       → salaire_base, anciennete_*, nb_*, plafond_cnss
  cotisations → + brut, total_gains, cnss_base, indemnites, primes, heures_sup
  fiscal      → + cnss
  retenues    → + total_retenues (tout sauf net)
  net         → toutes les variables
"""
import re
from decimal import Decimal

from simpleeval import simple_eval, NameNotDefined, InvalidExpression

# ---------------------------------------------------------------------------
# Variables & phases
# ---------------------------------------------------------------------------

VARIABLES_AUTORISEES = {
    'brut', 'cnss', 'indemnites', 'salaire_base', 'primes',
    'heures_sup', 'total_gains', 'total_retenues', 'cnss_base', 'net',
    'anciennete_mois', 'anciennete_ans',
    'nb_enfants', 'nb_conjoints', 'plafond_cnss',
}

_VARS_EMPLOYE = {'salaire_base', 'anciennete_mois', 'anciennete_ans',
                 'nb_enfants', 'nb_conjoints', 'plafond_cnss'}
VARIABLES_PAR_PHASE = {
    'gains':       _VARS_EMPLOYE,
    'cotisations': _VARS_EMPLOYE | {'brut', 'total_gains', 'cnss_base',
                                     'indemnites', 'primes', 'heures_sup'},
    'fiscal':      _VARS_EMPLOYE | {'brut', 'total_gains', 'cnss_base',
                                     'indemnites', 'primes', 'heures_sup', 'cnss'},
    'retenues':    VARIABLES_AUTORISEES - {'net'},
    'net':         VARIABLES_AUTORISEES,
}

# Fonctions autorisées dans les formules
FONCTIONS_AUTORISEES = {
    'min': min,
    'max': max,
    'abs': abs,
    'round': round,
    'int': int,
    'float': float,
}

# Mots interdits dans les formules (double sécurité en plus de simpleeval)
MOTS_INTERDITS = [
    'import', 'exec', 'eval', 'open', 'file', '__',
    'os', 'sys', 'subprocess', 'builtins', 'globals',
    'locals', 'vars', 'dir', 'getattr', 'setattr',
    'delattr', 'hasattr', 'compile', 'input', 'print',
]


# ---------------------------------------------------------------------------
# Évaluation sécurisée
# ---------------------------------------------------------------------------

def evaluer_formule(formule: str, variables: dict, phase: str = None) -> Decimal:
    """
    Évalue une formule de paie via simpleeval (sandboxé, pas de eval/exec).

    :param formule: Expression simple (ex: ``brut * 0.25``, ``min(indemnites, brut * 0.25)``)
    :param variables: Dictionnaire des valeurs (clés = noms de variables)
    :param phase: Phase de calcul (gains/cotisations/fiscal/retenues/net).
                  Restreint les variables accessibles pour éviter les dépendances circulaires.
    :raises ValueError: Si la formule est vide, contient des mots interdits ou est invalide
    """
    if not formule or not formule.strip():
        raise ValueError("Formule vide")

    formule_lower = formule.lower()
    for mot in MOTS_INTERDITS:
        if mot in formule_lower:
            raise ValueError(f"Mot interdit dans la formule : '{mot}'")

    # Déterminer les variables accessibles selon la phase
    vars_autorisees = VARIABLES_PAR_PHASE.get(phase, VARIABLES_AUTORISEES) if phase else VARIABLES_AUTORISEES

    # Construire le namespace filtré
    names = {}
    for var in vars_autorisees:
        names[var] = float(variables.get(var, 0))

    try:
        resultat = simple_eval(
            formule,
            names=names,
            functions=FONCTIONS_AUTORISEES,
        )
        return Decimal(str(max(0.0, float(resultat))))
    except ZeroDivisionError:
        return Decimal('0')
    except NameNotDefined as exc:
        if phase:
            raise ValueError(
                f"Variable indisponible en phase '{phase}' dans la formule '{formule}'. "
                f"Variables autorisées : {', '.join(sorted(vars_autorisees))}"
            ) from exc
        raise ValueError(f"Erreur dans la formule '{formule}' : {exc}") from exc
    except (InvalidExpression, SyntaxError, TypeError) as exc:
        raise ValueError(f"Formule invalide '{formule}' : {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Erreur dans la formule '{formule}' : {exc}") from exc


# ---------------------------------------------------------------------------
# Exemples de formules (aide UI)
# ---------------------------------------------------------------------------

EXEMPLES_FORMULES = {
    'exoneration': [
        ('Plafond 25% du brut (CGI strict)', 'min(indemnites, brut * 0.25)'),
        ('Plafond 30% du brut', 'min(indemnites, brut * 0.30)'),
        ('Exonération conditionnelle 25%', 'indemnites if indemnites <= brut * 0.25 else brut * 0.25'),
        ('Exonération intégrale', 'indemnites'),
    ],
    'base_vf': [
        ('Brut direct (simplifié)', 'brut'),
        ('Brut moins abattement fixe', 'brut - 150000 if brut >= 2500000 else brut'),
        ('94% du brut', 'brut * 0.94'),
        ('Brut moins CNSS', 'brut - cnss'),
    ],
    'base_rts': [
        ('Formule standard (brut - CNSS - exo 25%)', 'brut - cnss - min(indemnites, brut * 0.25)'),
        ('Avec plafond 30%', 'brut - cnss - min(indemnites, brut * 0.30)'),
        ('Base simplifiée (brut - CNSS)', 'brut - cnss'),
        ('Base avec abattement 10%', '(brut - cnss) * 0.90'),
    ],
}


# ---------------------------------------------------------------------------
# Validation & test
# ---------------------------------------------------------------------------

def valider_formule(formule: str) -> dict:
    """
    Valide une formule de paie sans l'évaluer définitivement.

    Retourne un dictionnaire avec:
      - ``valide`` (bool)
      - ``erreurs`` (list[str]) : blocages empêchant l'utilisation
      - ``avertissements`` (list[str]) : points d'attention non bloquants
      - ``resultat_test`` (Decimal|None) : résultat sur valeurs-test si valide
    """
    erreurs = []
    avertissements = []
    resultat_test = None

    if not formule or not formule.strip():
        erreurs.append("La formule est vide.")
        return {'valide': False, 'erreurs': erreurs, 'avertissements': avertissements, 'resultat_test': None}

    formule_lower = formule.lower()

    # Vérification mots interdits
    for mot in MOTS_INTERDITS:
        if mot in formule_lower:
            erreurs.append(f"Mot interdit détecté : '{mot}'")

    if erreurs:
        return {'valide': False, 'erreurs': erreurs, 'avertissements': avertissements, 'resultat_test': None}

    # Détection division par zéro potentielle
    if re.search(r'/\s*(0(?:[^.]|$)|\bbrut\b|\bsalaire_base\b)', formule_lower):
        avertissements.append(
            "Division potentielle par zéro détectée : vérifiez les diviseurs (ex. brut, salaire_base) "
            "car ils peuvent valoir 0."
        )

    # Test avec valeurs d'exemple
    test = tester_formule(formule)
    if not test.get('succes'):
        erreurs.append(test.get('erreur', "Erreur d'évaluation inconnue"))
        return {'valide': False, 'erreurs': erreurs, 'avertissements': avertissements, 'resultat_test': None}

    resultat_test = test['resultat']

    if float(resultat_test) < 0:
        avertissements.append("Le résultat calculé est négatif (sera ramené à 0).")

    PLAFOND_MAX = 100_000_000
    if float(resultat_test) > PLAFOND_MAX:
        avertissements.append(
            f"Le résultat ({float(resultat_test):,.0f} GNF) dépasse le plafond "
            f"réaliste de {PLAFOND_MAX:,.0f} GNF. Vérifiez la formule."
        )

    return {
        'valide': True,
        'erreurs': erreurs,
        'avertissements': avertissements,
        'resultat_test': resultat_test,
    }


def tester_formule(formule: str) -> dict:
    """
    Teste une formule avec des valeurs d'exemple.

    :param formule: Expression à tester
    :return: Dict avec clés ``succes`` (bool), ``resultat`` ou ``erreur``,
             et ``variables_test``
    """
    variables_test = {
        'brut': 3_000_000,
        'cnss': 125_000,
        'indemnites': 700_000,
        'salaire_base': 2_000_000,
        'primes': 300_000,
        'heures_sup': 150_000,
        'total_gains': 3_000_000,
        'total_retenues': 316_400,
        'cnss_base': 2_500_000,
        'net': 2_683_600,
        'anciennete_mois': 24,
        'anciennete_ans': 2,
        'nb_enfants': 2,
        'nb_conjoints': 1,
        'plafond_cnss': 2_500_000,
    }
    try:
        resultat = evaluer_formule(formule, variables_test)
        return {
            'succes': True,
            'resultat': resultat,
            'variables_test': variables_test,
        }
    except ValueError as exc:
        return {
            'succes': False,
            'erreur': str(exc),
        }
