"""
Service d'analyse mensuelle intelligente.

Fournit un rapport complet pour une période (mois, annee) :
- Podiums (top 3) : consommation carburant, tonnage, voyages
- Moyennes : consommation L/100km, coût GNF/km, GNF/T
- Top chauffeurs (tonnage, voyages)
- Anomalies : camions à consommation hors-normes, pannes répétées
- Synthèse financière : CA, charges, résultat, marge
"""
import calendar
from decimal import Decimal
from django.db.models import Sum, Count, Avg, F, DecimalField, Q, ExpressionWrapper
from django.db.models.functions import Coalesce

DEC18 = DecimalField(max_digits=18, decimal_places=2)
DEC14 = DecimalField(max_digits=14, decimal_places=2)

from apps.flotte.models import Camion
from apps.rh.models import Employe
from apps.operations.models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport
from apps.facturation.models import Facture


ZERO = Decimal("0")


def _pct(n, d):
    return (n / d * 100) if d else Decimal(0)


def _safe_div(n, d):
    return (n / d) if d else Decimal(0)


def rapport_mensuel(mois: int, annee: int) -> dict:
    """Retourne un dictionnaire consolidé avec tous les indicateurs du mois."""
    ctx = {
        "mois": mois,
        "annee": annee,
        "mois_label": calendar.month_name[mois].capitalize() if 1 <= mois <= 12 else str(mois),
        "periode": f"{mois:02d}/{annee}",
    }

    # ======================================================================
    # 1. CARBURANT — consommation par camion
    # ======================================================================
    car_qs = Carburant.objects.filter(date__month=mois, date__year=annee)

    litres_expr = ExpressionWrapper(F("litres_apres") - F("litres_avant"), output_field=DEC14)
    km_expr = ExpressionWrapper(F("km_tableau_bord") - F("km_avant"), output_field=DecimalField(max_digits=12, decimal_places=0))
    montant_expr = ExpressionWrapper(
        (F("litres_apres") - F("litres_avant")) * F("prix_unitaire"),
        output_field=DEC18,
    )
    car_par_camion = (
        car_qs.values("camion__code", "camion__immatriculation", "camion__marque_modele")
        .annotate(
            nb_prises=Count("id"),
            litres=Coalesce(Sum(litres_expr), ZERO, output_field=DEC14),
            km=Coalesce(Sum(km_expr), ZERO, output_field=DecimalField(max_digits=12, decimal_places=0)),
            montant=Coalesce(Sum(montant_expr), ZERO, output_field=DEC18),
        )
        .order_by("-montant")
    )

    car_par_camion_list = []
    for row in car_par_camion:
        litres = row["litres"] or ZERO
        km = Decimal(row["km"] or 0)
        conso = _safe_div(litres, km) * Decimal(100) if km else ZERO
        gnf_km = _safe_div(row["montant"], km) if km else ZERO
        car_par_camion_list.append({
            "code": row["camion__code"],
            "immat": row["camion__immatriculation"],
            "modele": row["camion__marque_modele"],
            "nb_prises": row["nb_prises"],
            "litres": litres,
            "km": km,
            "montant": row["montant"] or ZERO,
            "conso": conso,
            "gnf_km": gnf_km,
        })

    ctx["car_par_camion"] = car_par_camion_list
    ctx["car_top3_montant"] = car_par_camion_list[:3]  # Podium des plus consommateurs

    # Totaux
    ctx["car_total_litres"] = sum((c["litres"] for c in car_par_camion_list), ZERO)
    ctx["car_total_montant"] = sum((c["montant"] for c in car_par_camion_list), ZERO)
    ctx["car_total_km"] = sum((c["km"] for c in car_par_camion_list), ZERO)
    ctx["car_conso_moyenne"] = _safe_div(ctx["car_total_litres"], ctx["car_total_km"]) * Decimal(100) if ctx["car_total_km"] else ZERO
    ctx["car_gnf_km_moyen"] = _safe_div(ctx["car_total_montant"], ctx["car_total_km"]) if ctx["car_total_km"] else ZERO

    # Détection d'anomalies : consommation > 150% de la moyenne
    if ctx["car_conso_moyenne"]:
        seuil = ctx["car_conso_moyenne"] * Decimal("1.5")
        ctx["car_anomalies"] = [c for c in car_par_camion_list if c["conso"] > seuil and c["km"] > 0]
    else:
        ctx["car_anomalies"] = []

    # ======================================================================
    # 2. TRANSPORT BAUXITE — par camion + par chauffeur
    # ======================================================================
    voyages_qs = TransportBauxite.objects.filter(date__month=mois, date__year=annee)

    ca_expr = ExpressionWrapper(F("tonnage") * F("tarif_unitaire"), output_field=DEC18)
    trans_par_camion = (
        voyages_qs.values("camion__code", "camion__immatriculation", "camion__capacite_tonnes")
        .annotate(
            nb_voyages=Count("id"),
            tonnage_sum=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14),
            distance_sum=Coalesce(Sum("distance_km"), ZERO, output_field=DEC14),
            ca_sum=Coalesce(Sum(ca_expr), ZERO, output_field=DEC18),
        )
        .order_by("-tonnage_sum")
    )

    trans_par_camion_list = [
        {
            "code": r["camion__code"],
            "immat": r["camion__immatriculation"],
            "capacite": r["camion__capacite_tonnes"],
            "nb_voyages": r["nb_voyages"],
            "tonnage": r["tonnage_sum"],
            "distance": r["distance_sum"],
            "ca": r["ca_sum"],
            "tonnage_moyen_voyage": _safe_div(r["tonnage_sum"], Decimal(r["nb_voyages"])),
            "taux_remplissage": _pct(
                _safe_div(r["tonnage_sum"], Decimal(r["nb_voyages"])),
                r["camion__capacite_tonnes"] or Decimal(1),
            ),
        }
        for r in trans_par_camion
    ]
    ctx["trans_par_camion"] = trans_par_camion_list
    ctx["trans_top3_tonnage"] = trans_par_camion_list[:3]
    ctx["trans_top3_voyages"] = sorted(trans_par_camion_list, key=lambda r: r["nb_voyages"], reverse=True)[:3]

    # Par chauffeur
    trans_par_chauffeur = (
        voyages_qs.filter(chauffeur__isnull=False)
        .values("chauffeur__code", "chauffeur__prenom", "chauffeur__nom", "chauffeur__camion__code")
        .annotate(
            nb_voyages=Count("id"),
            tonnage_sum=Coalesce(Sum("tonnage"), ZERO, output_field=DEC14),
            distance_sum=Coalesce(Sum("distance_km"), ZERO, output_field=DEC14),
            ca_sum=Coalesce(Sum(ca_expr), ZERO, output_field=DEC18),
        )
        .order_by("-tonnage_sum")
    )

    trans_par_chauffeur_list = [
        {
            "code": r["chauffeur__code"],
            "nom": f"{r['chauffeur__prenom']} {r['chauffeur__nom']}",
            "camion": r["chauffeur__camion__code"] or "—",
            "nb_voyages": r["nb_voyages"],
            "tonnage": r["tonnage_sum"],
            "distance": r["distance_sum"],
            "ca": r["ca_sum"],
        }
        for r in trans_par_chauffeur
    ]
    ctx["trans_par_chauffeur"] = trans_par_chauffeur_list
    ctx["trans_top3_chauffeurs_tonnage"] = trans_par_chauffeur_list[:3]
    ctx["trans_top3_chauffeurs_voyages"] = sorted(trans_par_chauffeur_list, key=lambda r: r["nb_voyages"], reverse=True)[:3]

    # Totaux transport
    ctx["trans_nb_voyages"] = sum((c["nb_voyages"] for c in trans_par_camion_list), 0)
    ctx["trans_tonnage_total"] = sum((c["tonnage"] for c in trans_par_camion_list), ZERO)
    ctx["trans_distance_total"] = sum((c["distance"] for c in trans_par_camion_list), ZERO)
    ctx["trans_ca_total"] = sum((c["ca"] for c in trans_par_camion_list), ZERO)

    # ======================================================================
    # 3. PANNES — par camion
    # ======================================================================
    pannes_qs = Panne.objects.filter(date__month=mois, date__year=annee)
    cout_expr = ExpressionWrapper(F("cout_pieces") + F("cout_main_oeuvre"), output_field=DEC14)
    pannes_par_camion = (
        pannes_qs.values("camion__code", "camion__immatriculation")
        .annotate(
            nb_pannes=Count("id"),
            cout=Coalesce(Sum(cout_expr), ZERO, output_field=DEC14),
            immo=Coalesce(Sum("duree_immobilisation"), 0),
        )
        .order_by("-cout")
    )
    ctx["pannes_par_camion"] = list(pannes_par_camion)
    ctx["pan_nb_total"] = pannes_qs.count()
    ctx["pan_cout_total"] = sum((p["cout"] for p in ctx["pannes_par_camion"]), ZERO)
    ctx["pan_immo_total"] = sum((p["immo"] for p in ctx["pannes_par_camion"]), 0)

    # Camions avec ≥ 3 pannes : alerte
    ctx["pan_alertes"] = [p for p in ctx["pannes_par_camion"] if p["nb_pannes"] >= 3]

    # ======================================================================
    # 4. DÉPENSES ADMIN + SALAIRES + AMORTISSEMENT
    # ======================================================================
    dep_total = DepenseAdmin.objects.filter(
        date__month=mois, date__year=annee
    ).aggregate(t=Coalesce(Sum("montant"), ZERO))["t"]
    ctx["dep_total"] = dep_total

    employes_actifs = Employe.objects.filter(actif=True)
    masse_salariale = sum((e.salaire_total_mensuel for e in employes_actifs), ZERO)
    ctx["masse_salariale"] = masse_salariale
    ctx["nb_employes"] = employes_actifs.count()

    amort_mensuel = sum((c.amortissement_mensuel for c in Camion.objects.all()), ZERO)
    ctx["amort_mensuel"] = amort_mensuel

    # ======================================================================
    # 5. SYNTHÈSE FINANCIÈRE
    # ======================================================================
    charges_totales = (
        ctx["car_total_montant"] + ctx["pan_cout_total"] + dep_total + masse_salariale + amort_mensuel
    )
    ctx["charges_totales"] = charges_totales
    ctx["resultat_net"] = ctx["trans_ca_total"] - charges_totales
    ctx["marge_pct"] = _pct(ctx["resultat_net"], ctx["trans_ca_total"])

    # Répartition des charges (pour graphique donut)
    ctx["charges_repartition"] = [
        {"label": "Carburant",   "value": float(ctx["car_total_montant"])},
        {"label": "Pannes",      "value": float(ctx["pan_cout_total"])},
        {"label": "Salaires",    "value": float(masse_salariale)},
        {"label": "Amortissement","value": float(amort_mensuel)},
        {"label": "Admin.",      "value": float(dep_total)},
    ]

    # ======================================================================
    # 6. FACTURES DU MOIS
    # ======================================================================
    factures = Facture.objects.filter(
        periode_mois=mois, periode_annee=annee
    ).select_related("contrat")
    ctx["factures"] = factures
    ctx["facture_ttc_total"] = sum((f.montant_ttc for f in factures), ZERO)

    # ======================================================================
    # 7. BONS DE TRANSPORT
    # ======================================================================
    bons_qs = BonTransport.objects.filter(date__month=mois, date__year=annee)
    ctx["bons_count"] = bons_qs.count()
    ctx["bons_tonnage"] = bons_qs.aggregate(t=Coalesce(Sum("quantite"), ZERO))["t"]

    return ctx
