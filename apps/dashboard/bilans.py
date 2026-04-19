"""
Service de bilan multi-contrats.

Offre deux fonctions principales :
  - `bilan_contrat(contrat, mois=None, annee=None)`
      Bilan complet d'un contrat pour la période (ou depuis le début si None).
      Inclut CA, charges directes (FK), quote-part des charges partagées (prorata tonnage),
      résultat net, marge, nb bons, tonnage, nb voyages, KPI flotte.

  - `bilan_entreprise(mois=None, annee=None)`
      Consolidation de tous les contrats actifs + charges résiduelles non-imputées.
      Retourne la synthèse entreprise (CA, charges, résultat, marge) + tableau par projet.

La règle d'imputation des charges :
  1. Si l'opération (Carburant/Panne/Depense/Transport) a un FK `contrat` → imputée à ce contrat.
  2. Sinon → répartie AU PRORATA du tonnage réalisé par chaque contrat sur la période.
  3. Si aucun contrat n'a de tonnage, on répartit à parts égales entre contrats actifs.
"""
import calendar
from decimal import Decimal
from datetime import date
from django.db.models import Sum, Count, F, DecimalField, Q, ExpressionWrapper
from django.db.models.functions import Coalesce

from apps.flotte.models import Camion
from apps.operations.models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport
from apps.facturation.models import Contrat, Facture


DEC18 = DecimalField(max_digits=18, decimal_places=2)
DEC14 = DecimalField(max_digits=14, decimal_places=2)
ZERO = Decimal("0")


def _period_filter(mois=None, annee=None, field="date"):
    """Retourne un Q filtrant par mois/annee sur le champ donné, ou tout si les 2 sont None."""
    q = Q()
    if annee is not None:
        q &= Q(**{f"{field}__year": annee})
    if mois is not None:
        q &= Q(**{f"{field}__month": mois})
    return q


def _safe_div(n, d):
    return (n / d) if d else ZERO


def _pct(n, d):
    return (n / d * Decimal(100)) if d else ZERO


# ---------------------------------------------------------------------------
# CALCULS DES CHARGES PARTAGÉES
# ---------------------------------------------------------------------------
def _charges_partagees(mois=None, annee=None):
    """Retourne un dict avec les charges SANS contrat (à répartir au prorata).

    Returns:
        {
            "carburant": Decimal,
            "pannes": Decimal,
            "depenses_admin": Decimal,
        }
    """
    q_date_car = _period_filter(mois, annee, "date")
    q_date_pan = _period_filter(mois, annee, "date")
    q_date_dep = _period_filter(mois, annee, "date")

    montant_car_expr = ExpressionWrapper(
        (F("litres_apres") - F("litres_avant")) * F("prix_unitaire"),
        output_field=DEC18,
    )
    cout_pan_expr = ExpressionWrapper(F("cout_pieces") + F("cout_main_oeuvre"), output_field=DEC14)

    car = Carburant.objects.filter(q_date_car, contrat__isnull=True).aggregate(
        t=Coalesce(Sum(montant_car_expr), ZERO, output_field=DEC18)
    )["t"]
    pan = Panne.objects.filter(q_date_pan, contrat__isnull=True).aggregate(
        t=Coalesce(Sum(cout_pan_expr), ZERO, output_field=DEC18)
    )["t"]
    dep = DepenseAdmin.objects.filter(q_date_dep, contrat__isnull=True).aggregate(
        t=Coalesce(Sum("montant"), ZERO, output_field=DEC18)
    )["t"]
    return {"carburant": car, "pannes": pan, "depenses_admin": dep}


def _tonnage_par_contrat(mois=None, annee=None):
    """Retourne {contrat_id: tonnage_total} + total global (pour clés de prorata)."""
    q = _period_filter(mois, annee, "date")
    # On considère le tonnage imputé via FK OU via client (fallback historique)
    rows = (
        TransportBauxite.objects.filter(q)
        .values("contrat_id", "client")
        .annotate(t=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14))
    )
    par_id = {}
    for r in rows:
        cid = r["contrat_id"]
        if cid is not None:
            par_id[cid] = par_id.get(cid, ZERO) + (r["t"] or ZERO)
        else:
            # Tentative de mappage par nom client
            client = (r["client"] or "").strip().lower()
            if client:
                c = Contrat.objects.filter(client__iexact=client, actif=True).first()
                if c:
                    par_id[c.id] = par_id.get(c.id, ZERO) + (r["t"] or ZERO)
    total = sum(par_id.values(), ZERO)
    return par_id, total


def _part_prorata(contrat_id, ponderations, total):
    """Retourne la part (0..1) du contrat dans la répartition."""
    if total and contrat_id in ponderations:
        return ponderations[contrat_id] / total
    return ZERO


# ---------------------------------------------------------------------------
# BILAN D'UN CONTRAT
# ---------------------------------------------------------------------------
def bilan_contrat(contrat: Contrat, mois=None, annee=None) -> dict:
    """Bilan complet pour un contrat donné, sur la période (ou tout l'historique)."""
    q_date = _period_filter(mois, annee, "date")

    # -------- Voyages (CA direct) ---------------------------------------
    ca_expr = ExpressionWrapper(F("tonnage") * F("tarif_unitaire"), output_field=DEC18)
    voyages_qs = TransportBauxite.objects.filter(q_date).filter(
        Q(contrat=contrat) |
        (Q(contrat__isnull=True) & Q(client__iexact=contrat.client))
    )
    voyages_agg = voyages_qs.aggregate(
        nb_v=Count("id"),
        tonnage_sum=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14),
        distance_sum=Coalesce(Sum("distance_km"), ZERO, output_field=DEC14),
        ca_sum=Coalesce(Sum(ca_expr), ZERO, output_field=DEC18),
    )
    nb_voyages = voyages_agg["nb_v"] or 0
    tonnage = voyages_agg["tonnage_sum"] or ZERO
    distance = voyages_agg["distance_sum"] or ZERO
    ca = voyages_agg["ca_sum"] or ZERO

    # -------- Bons de transport -----------------------------------------
    nb_bons = BonTransport.objects.filter(q_date).filter(
        Q(contrat=contrat) | Q(contrat__isnull=True)
    ).count()

    # -------- Charges DIRECTES (FK == contrat) --------------------------
    montant_car_expr = ExpressionWrapper(
        (F("litres_apres") - F("litres_avant")) * F("prix_unitaire"),
        output_field=DEC18,
    )
    cout_pan_expr = ExpressionWrapper(F("cout_pieces") + F("cout_main_oeuvre"), output_field=DEC14)

    car_direct = Carburant.objects.filter(q_date, contrat=contrat).aggregate(
        m=Coalesce(Sum(montant_car_expr), ZERO, output_field=DEC18)
    )["m"]
    pan_direct = Panne.objects.filter(q_date, contrat=contrat).aggregate(
        m=Coalesce(Sum(cout_pan_expr), ZERO, output_field=DEC18)
    )["m"]
    dep_direct = DepenseAdmin.objects.filter(q_date, contrat=contrat).aggregate(
        m=Coalesce(Sum("montant"), ZERO, output_field=DEC18)
    )["m"]

    # -------- Charges PARTAGÉES au prorata ------------------------------
    partagees = _charges_partagees(mois, annee)
    tonnage_map, tonnage_total_global = _tonnage_par_contrat(mois, annee)
    part = _part_prorata(contrat.id, tonnage_map, tonnage_total_global)
    # Si aucun tonnage global, on partage à parts égales entre contrats actifs
    if tonnage_total_global == ZERO:
        nb_actifs = Contrat.objects.filter(actif=True).count() or 1
        part = Decimal("1") / Decimal(nb_actifs)

    car_prorata = partagees["carburant"] * part
    pan_prorata = partagees["pannes"] * part
    dep_prorata = partagees["depenses_admin"] * part

    charges_carburant = car_direct + car_prorata
    charges_pannes = pan_direct + pan_prorata
    charges_depenses = dep_direct + dep_prorata
    charges_totales = charges_carburant + charges_pannes + charges_depenses

    resultat_net = ca - charges_totales
    marge_pct = _pct(resultat_net, ca)

    # -------- Factures du contrat --------------------------------------
    factures_qs = Facture.objects.filter(contrat=contrat)
    if mois is not None:
        factures_qs = factures_qs.filter(periode_mois=mois)
    if annee is not None:
        factures_qs = factures_qs.filter(periode_annee=annee)
    factures_agg = factures_qs.aggregate(
        nb=Count("id"),
        ttc=Coalesce(Sum("montant_ttc"), ZERO, output_field=DEC18),
        ht=Coalesce(Sum("montant_ht"), ZERO, output_field=DEC18),
    )

    # -------- Top camions / chauffeurs du contrat -----------------------
    camions_contrat = list(
        voyages_qs.values("camion__code", "camion__immatriculation")
        .annotate(
            nb=Count("id"),
            tonnage_sum=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14),
            ca_sum=Coalesce(Sum(ca_expr), ZERO, output_field=DEC18),
        )
        .order_by("-tonnage_sum")
    )
    chauffeurs_contrat = list(
        voyages_qs.filter(chauffeur__isnull=False)
        .values("chauffeur__code", "chauffeur__prenom", "chauffeur__nom")
        .annotate(
            nb=Count("id"),
            tonnage_sum=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14),
        )
        .order_by("-tonnage_sum")
    )

    return {
        "contrat": contrat,
        "mois": mois,
        "annee": annee,
        "periode_label": _periode_label(mois, annee),
        "nb_bons": nb_bons,
        "nb_voyages": nb_voyages,
        "tonnage": tonnage,
        "distance": distance,
        "ca": ca,
        "car_direct": car_direct,
        "car_prorata": car_prorata,
        "pan_direct": pan_direct,
        "pan_prorata": pan_prorata,
        "dep_direct": dep_direct,
        "dep_prorata": dep_prorata,
        "charges_carburant": charges_carburant,
        "charges_pannes": charges_pannes,
        "charges_depenses": charges_depenses,
        "charges_totales": charges_totales,
        "resultat_net": resultat_net,
        "marge_pct": marge_pct,
        "part_prorata_pct": part * Decimal(100),
        "factures_nb": factures_agg["nb"] or 0,
        "factures_ttc": factures_agg["ttc"] or ZERO,
        "factures_ht": factures_agg["ht"] or ZERO,
        "camions_top": camions_contrat[:5],
        "chauffeurs_top": chauffeurs_contrat[:5],
    }


# ---------------------------------------------------------------------------
# BILAN ENTREPRISE — consolidation multi-contrats
# ---------------------------------------------------------------------------
def bilan_entreprise(mois=None, annee=None) -> dict:
    """Consolide tous les contrats + charges résiduelles.

    Résultat :
      - `lignes_projets` : une ligne par contrat avec CA, charges, résultat
      - totaux entreprise (CA, charges, résultat, marge)
      - charges globales : carburant, pannes, dep_admin, salaires, amortissement
      - KPI flotte : nb camions, consommation moyenne, taux remplissage
    """
    q_date = _period_filter(mois, annee, "date")

    contrats = Contrat.objects.filter(actif=True).order_by("code")
    lignes = []
    for c in contrats:
        b = bilan_contrat(c, mois=mois, annee=annee)
        lignes.append({
            "contrat": c,
            "nb_bons": b["nb_bons"],
            "nb_voyages": b["nb_voyages"],
            "tonnage": b["tonnage"],
            "distance": b["distance"],
            "ca": b["ca"],
            "charges": b["charges_totales"],
            "carburant": b["charges_carburant"],
            "pannes": b["charges_pannes"],
            "depenses": b["charges_depenses"],
            "resultat": b["resultat_net"],
            "marge_pct": b["marge_pct"],
            "part_prorata_pct": b["part_prorata_pct"],
            "factures_nb": b["factures_nb"],
            "factures_ttc": b["factures_ttc"],
        })

    # Totaux entreprise (somme des bilans projets)
    tot_ca = sum((l["ca"] for l in lignes), ZERO)
    tot_charges_projets = sum((l["charges"] for l in lignes), ZERO)
    tot_carburant = sum((l["carburant"] for l in lignes), ZERO)
    tot_pannes = sum((l["pannes"] for l in lignes), ZERO)
    tot_depenses = sum((l["depenses"] for l in lignes), ZERO)
    tot_tonnage = sum((l["tonnage"] for l in lignes), ZERO)
    tot_voyages = sum((l["nb_voyages"] for l in lignes), 0)
    tot_bons = sum((l["nb_bons"] for l in lignes), 0)

    # Charges non réparties (masse salariale + amortissement = charges structure)
    from apps.rh.models import Employe
    masse_salariale = sum(
        (e.salaire_total_mensuel for e in Employe.objects.filter(actif=True)), ZERO
    )
    amort_mensuel = sum((c.amortissement_mensuel for c in Camion.objects.all()), ZERO)
    # Sur plusieurs mois : multiplier ces charges récurrentes
    nb_mois = _nb_mois(mois, annee)
    masse_salariale_periode = masse_salariale * nb_mois
    amort_periode = amort_mensuel * nb_mois

    charges_structure = masse_salariale_periode + amort_periode
    charges_totales_entreprise = tot_charges_projets + charges_structure
    resultat_entreprise = tot_ca - charges_totales_entreprise
    marge_entreprise = _pct(resultat_entreprise, tot_ca)

    # Facturation totale
    factures_qs = Facture.objects.all()
    if mois is not None:
        factures_qs = factures_qs.filter(periode_mois=mois)
    if annee is not None:
        factures_qs = factures_qs.filter(periode_annee=annee)
    fact_agg = factures_qs.aggregate(
        nb=Count("id"),
        ht=Coalesce(Sum("montant_ht"), ZERO, output_field=DEC18),
        tva=Coalesce(Sum("tva"), ZERO, output_field=DEC18),
        ttc=Coalesce(Sum("montant_ttc"), ZERO, output_field=DEC18),
    )

    # KPI flotte
    nb_camions = Camion.objects.count()
    capacite_totale = sum((c.capacite_tonnes or 0 for c in Camion.objects.all()), Decimal(0))

    # Répartition pour graphique
    repartition_charges = [
        {"label": "Carburant", "value": float(tot_carburant)},
        {"label": "Pannes", "value": float(tot_pannes)},
        {"label": "Dépenses admin.", "value": float(tot_depenses)},
        {"label": "Salaires", "value": float(masse_salariale_periode)},
        {"label": "Amortissement", "value": float(amort_periode)},
    ]
    repartition_ca = [
        {"label": l["contrat"].code, "value": float(l["ca"]), "client": l["contrat"].client}
        for l in lignes if l["ca"] > 0
    ]

    return {
        "mois": mois,
        "annee": annee,
        "periode_label": _periode_label(mois, annee),
        "nb_mois": nb_mois,
        "lignes_projets": lignes,
        "nb_contrats": len(lignes),
        "nb_camions": nb_camions,
        "capacite_totale": capacite_totale,
        "tot_ca": tot_ca,
        "tot_tonnage": tot_tonnage,
        "tot_voyages": tot_voyages,
        "tot_bons": tot_bons,
        "tot_carburant": tot_carburant,
        "tot_pannes": tot_pannes,
        "tot_depenses": tot_depenses,
        "masse_salariale": masse_salariale_periode,
        "amort": amort_periode,
        "charges_structure": charges_structure,
        "charges_totales": charges_totales_entreprise,
        "resultat": resultat_entreprise,
        "marge_pct": marge_entreprise,
        "factures_nb": fact_agg["nb"] or 0,
        "factures_ht": fact_agg["ht"],
        "factures_tva": fact_agg["tva"],
        "factures_ttc": fact_agg["ttc"],
        "repartition_charges": repartition_charges,
        "repartition_ca": repartition_ca,
    }


def _periode_label(mois, annee):
    if mois and annee:
        return f"{calendar.month_name[mois].capitalize()} {annee}"
    if annee:
        return f"Année {annee}"
    return "Depuis le début"


def _nb_mois(mois, annee):
    """Nombre de mois de la période (1 si mois précis, 12 si année seule, 1 sinon)."""
    if mois:
        return Decimal(1)
    if annee:
        today = date.today()
        if annee == today.year:
            return Decimal(today.month)
        return Decimal(12)
    return Decimal(1)
