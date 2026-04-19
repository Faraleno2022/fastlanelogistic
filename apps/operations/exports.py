"""Définit, pour chaque entité du module opérations, les specs d'export/import.

Chaque spec expose :
  - ``columns_pdf_xlsx`` : colonnes affichées dans un export tabulaire
  - ``build_rows(queryset)`` : itérable de lignes à partir d'un QuerySet
  - ``schema_import`` : colonnes attendues pour un import Excel
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal

from apps.core.imports import Column
from apps.flotte.models import Camion
from apps.rh.models import Employe
from apps.facturation.models import Contrat

from .models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport


# ---------------------------------------------------------------------------
# Resolvers pour l'import (code -> instance)
# ---------------------------------------------------------------------------

def _resolve_camion(code):
    if not code:
        return None
    return Camion.objects.filter(code__iexact=str(code).strip()).first()


def _resolve_employe(code):
    if not code:
        return None
    return Employe.objects.filter(code__iexact=str(code).strip()).first()


def _resolve_contrat(code):
    if not code:
        return None
    return Contrat.objects.filter(code__iexact=str(code).strip()).first()


def _resolve_choice(choices):
    """Retourne une fonction qui mappe libellé OU code -> code choice."""
    code_to_label = {c: l for c, l in choices}
    label_to_code = {l.lower(): c for c, l in choices}

    def resolver(v):
        if not v:
            return None
        s = str(v).strip()
        if s in code_to_label:
            return s
        return label_to_code.get(s.lower())
    return resolver


# ---------------------------------------------------------------------------
# Carburant
# ---------------------------------------------------------------------------

CARBURANT_COLUMNS = [
    "Date", "Heure", "Camion", "Chauffeur", "Contrat",
    "Km tableau", "Km avant", "Km parcourus",
    "L avant", "L après", "L pris",
    "Prix/L", "Montant total", "L/100km", "Station", "Observations",
]


def carburant_rows(qs):
    for p in qs:
        yield [
            p.date, p.heure, p.camion.code,
            p.chauffeur.nom_complet if p.chauffeur else "",
            p.contrat.code if p.contrat else "",
            p.km_tableau_bord, p.km_avant, p.km_parcourus,
            p.litres_avant, p.litres_apres, p.litres_pris,
            p.prix_unitaire, p.montant_total, p.consommation_100km,
            p.station, p.observations,
        ]


CARBURANT_IMPORT = [
    Column("date", "Date (jj/mm/aaaa)", "date", required=True),
    Column("heure", "Heure (HH:MM)", "time"),
    Column("camion", "Camion (code)", "str", required=True, resolve=_resolve_camion,
           help="Code du camion dans la flotte (ex: CAM-01)."),
    Column("chauffeur", "Chauffeur (code)", "str", resolve=_resolve_employe,
           help="Code employé — peut être vide."),
    Column("contrat", "Contrat (code)", "str", resolve=_resolve_contrat,
           help="Code contrat — si vide, imputation au prorata."),
    Column("km_tableau_bord", "Km tableau de bord", "int", required=True),
    Column("km_avant", "Km avant prise", "int"),
    Column("litres_avant", "L avant", "decimal"),
    Column("litres_apres", "L après", "decimal", required=True),
    Column("prix_unitaire", "Prix unitaire (GNF/L)", "decimal",
           help="Laisser vide pour utiliser la valeur par défaut."),
    Column("station", "Station / Lieu", "str"),
    Column("observations", "Observations", "str"),
]


# ---------------------------------------------------------------------------
# Pannes
# ---------------------------------------------------------------------------

PANNES_COLUMNS = [
    "Date", "Camion", "Contrat", "Type",
    "Pièce remplacée", "Fournisseur",
    "Coût pièces", "Coût M.O.", "Coût total",
    "Jours immo.", "Observations",
]


def pannes_rows(qs):
    for p in qs:
        yield [
            p.date, p.camion.code, p.contrat.code if p.contrat else "",
            p.get_type_panne_display(), p.piece_remplacee, p.fournisseur,
            p.cout_pieces, p.cout_main_oeuvre, p.cout_total,
            p.duree_immobilisation, p.observations,
        ]


PANNES_IMPORT = [
    Column("date", "Date (jj/mm/aaaa)", "date", required=True),
    Column("camion", "Camion (code)", "str", required=True, resolve=_resolve_camion),
    Column("contrat", "Contrat (code)", "str", resolve=_resolve_contrat),
    Column("type_panne", "Type", "str", required=True,
           resolve=_resolve_choice(Panne.Type.choices),
           help="Valeurs possibles : " + ", ".join(l for _, l in Panne.Type.choices)),
    Column("piece_remplacee", "Pièce remplacée", "str"),
    Column("fournisseur", "Fournisseur / Garage", "str"),
    Column("cout_pieces", "Coût pièces (GNF)", "decimal"),
    Column("cout_main_oeuvre", "Coût main d'œuvre (GNF)", "decimal"),
    Column("duree_immobilisation", "Durée immo. (jours)", "int"),
    Column("observations", "Observations", "str"),
]


# ---------------------------------------------------------------------------
# Dépenses admin
# ---------------------------------------------------------------------------

DEPENSES_COLUMNS = [
    "Date", "Camion", "Contrat", "Type", "Description",
    "Référence", "Montant", "Échéance", "Statut",
]


def depenses_rows(qs):
    for d in qs:
        yield [
            d.date, d.camion.code if d.camion else "",
            d.contrat.code if d.contrat else "",
            d.get_type_depense_display(), d.description, d.reference,
            d.montant, d.echeance, d.get_statut_display(),
        ]


DEPENSES_IMPORT = [
    Column("date", "Date (jj/mm/aaaa)", "date", required=True),
    Column("camion", "Camion (code)", "str", resolve=_resolve_camion),
    Column("contrat", "Contrat (code)", "str", resolve=_resolve_contrat),
    Column("type_depense", "Type", "str", required=True,
           resolve=_resolve_choice(DepenseAdmin.Type.choices),
           help="Immatriculation, Assurance, Visite technique, Taxe, Licence, Frais bancaires, Autre"),
    Column("description", "Description", "str", required=True),
    Column("reference", "Référence", "str"),
    Column("montant", "Montant (GNF)", "decimal", required=True),
    Column("echeance", "Échéance (jj/mm/aaaa)", "date"),
    Column("statut", "Statut", "str", resolve=_resolve_choice(DepenseAdmin.Statut.choices)),
]


# ---------------------------------------------------------------------------
# Transport bauxite
# ---------------------------------------------------------------------------

TRANSPORT_COLUMNS = [
    "Date", "Camion", "Chauffeur", "Contrat", "Client", "Trajet",
    "Distance (km)", "Tonnage (T)", "Tarif (GNF/T)", "CA (GNF)",
    "N° Bon", "Observations",
]


def transport_rows(qs):
    for v in qs:
        yield [
            v.date, v.camion.code,
            v.chauffeur.nom_complet if v.chauffeur else "",
            v.contrat.code if v.contrat else "",
            v.client, v.trajet, v.distance_km, v.tonnage,
            v.tarif_unitaire, v.chiffre_affaires, v.num_bon, v.observations,
        ]


TRANSPORT_IMPORT = [
    Column("date", "Date (jj/mm/aaaa)", "date", required=True),
    Column("camion", "Camion (code)", "str", required=True, resolve=_resolve_camion),
    Column("chauffeur", "Chauffeur (code)", "str", resolve=_resolve_employe),
    Column("contrat", "Contrat (code)", "str", resolve=_resolve_contrat),
    Column("client", "Client", "str", required=True),
    Column("trajet", "Trajet (départ → arrivée)", "str", required=True),
    Column("distance_km", "Distance (km)", "decimal"),
    Column("tonnage", "Tonnage (T)", "decimal", required=True),
    Column("tarif_unitaire", "Tarif (GNF/T)", "decimal",
           help="Laisser vide pour utiliser le tarif du contrat / la valeur par défaut."),
    Column("num_bon", "N° Bon de livraison", "str"),
    Column("observations", "Observations", "str"),
]


# ---------------------------------------------------------------------------
# Bons de transport
# ---------------------------------------------------------------------------

BONS_COLUMNS = [
    "Date", "N° Bon", "Prénom", "Nom", "Téléphone", "Plaque",
    "Carte d'entrée", "Lieu chargement",
    "Départ", "Pesée début", "Pesée fin",
    "Quantité (T)", "Contrat", "Camion", "Observations",
]


def bons_rows(qs):
    for b in qs:
        yield [
            b.date, b.num_bon, b.prenom, b.nom, b.telephone, b.plaque,
            b.carte_entree, b.lieu_chargement,
            b.heure_depart, b.heure_pesee_start, b.heure_pesee_end,
            b.quantite,
            b.contrat.code if b.contrat else "",
            b.camion.code if b.camion else "",
            b.observation,
        ]


BONS_IMPORT = [
    Column("date", "Date (jj/mm/aaaa)", "date", required=True),
    Column("num_bon", "N° Bon", "str",
           help="Laisser vide pour génération automatique."),
    Column("prenom", "Prénom chauffeur", "str", required=True),
    Column("nom", "Nom chauffeur", "str", required=True),
    Column("telephone", "Téléphone", "str"),
    Column("plaque", "Plaque", "str", required=True),
    Column("carte_entree", "Carte d'entrée", "str"),
    Column("lieu_chargement", "Lieu de chargement", "str", required=True),
    Column("heure_depart", "Heure départ (HH:MM)", "time"),
    Column("heure_pesee_start", "Pesée début (HH:MM)", "time"),
    Column("heure_pesee_end", "Pesée fin (HH:MM)", "time"),
    Column("quantite", "Quantité (T)", "decimal", required=True),
    Column("contrat", "Contrat (code)", "str", resolve=_resolve_contrat),
    Column("camion", "Camion (code)", "str", resolve=_resolve_camion),
    Column("observation", "Observations", "str"),
]


# ---------------------------------------------------------------------------
# Registre (dispatcher)
# ---------------------------------------------------------------------------

REGISTRY = {
    "carburant": {
        "titre": "Suivi carburant",
        "Model": Carburant,
        "columns": CARBURANT_COLUMNS,
        "build_rows": carburant_rows,
        "import_schema": CARBURANT_IMPORT,
        "select_related": ("camion", "chauffeur", "contrat"),
        "fiche_type": "carburant",
    },
    "pannes": {
        "titre": "Pannes & réparations",
        "Model": Panne,
        "columns": PANNES_COLUMNS,
        "build_rows": pannes_rows,
        "import_schema": PANNES_IMPORT,
        "select_related": ("camion", "contrat"),
        "fiche_type": "panne",
    },
    "depenses": {
        "titre": "Dépenses administratives",
        "Model": DepenseAdmin,
        "columns": DEPENSES_COLUMNS,
        "build_rows": depenses_rows,
        "import_schema": DEPENSES_IMPORT,
        "select_related": ("camion", "contrat"),
        "fiche_type": None,
    },
    "transport": {
        "titre": "Transport bauxite",
        "Model": TransportBauxite,
        "columns": TRANSPORT_COLUMNS,
        "build_rows": transport_rows,
        "import_schema": TRANSPORT_IMPORT,
        "select_related": ("camion", "chauffeur", "contrat"),
        "fiche_type": "voyage_bauxite",
    },
    "bons": {
        "titre": "Bons de transport",
        "Model": BonTransport,
        "columns": BONS_COLUMNS,
        "build_rows": bons_rows,
        "import_schema": BONS_IMPORT,
        "select_related": ("camion", "contrat"),
        "fiche_type": "bon_transport",
    },
}
