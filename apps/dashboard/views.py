import calendar
import json
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.urls import reverse

from apps.flotte.models import Camion
from apps.rh.models import Employe
from apps.operations.models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport
from apps.facturation.models import Facture, Contrat
from .rapports import rapport_mensuel as _rapport_mensuel_service
from .bilans import bilan_contrat as _bilan_contrat, bilan_entreprise as _bilan_entreprise


def _filtre_periode(request):
    today = date.today()
    try:
        mois = int(request.GET.get("mois", today.month))
        annee = int(request.GET.get("annee", today.year))
    except (ValueError, TypeError):
        mois, annee = today.month, today.year
    return mois, annee


@login_required
def home(request):
    mois, annee = _filtre_periode(request)

    # --- FLOTTE ---
    camions = Camion.objects.all()
    flotte_nb = camions.count()
    flotte_prix = sum((c.prix_achat for c in camions), Decimal(0))
    flotte_capacite = sum((c.capacite_tonnes for c in camions), Decimal(0))
    amort_mensuel = sum((c.amortissement_mensuel for c in camions), Decimal(0))
    amort_annuel = sum((c.amortissement_annuel for c in camions), Decimal(0))
    vr_totale = sum((c.valeur_residuelle for c in camions), Decimal(0))

    # --- CARBURANT (mois) ---
    prises = Carburant.objects.filter(date__month=mois, date__year=annee)
    car_litres = sum((p.litres_pris for p in prises), Decimal(0))
    car_km = sum((p.km_parcourus for p in prises), 0)
    car_montant = sum((p.montant_total for p in prises), Decimal(0))
    car_conso = (car_litres / car_km * 100) if car_km else Decimal(0)
    car_gnf_km = (car_montant / car_km) if car_km else Decimal(0)

    # --- PANNES ---
    pannes = Panne.objects.filter(date__month=mois, date__year=annee)
    pan_count = pannes.count()
    pan_pieces = sum((p.cout_pieces for p in pannes), Decimal(0))
    pan_mo = sum((p.cout_main_oeuvre for p in pannes), Decimal(0))
    pan_total = pan_pieces + pan_mo
    pan_immo = sum((p.duree_immobilisation for p in pannes), 0)

    # --- TRANSPORT BAUXITE ---
    voyages = TransportBauxite.objects.filter(date__month=mois, date__year=annee)
    trans_nb = voyages.count()
    trans_tonnage = sum((v.tonnage for v in voyages), Decimal(0))
    trans_distance = sum((v.distance_km for v in voyages), Decimal(0))
    trans_ca = sum((v.chiffre_affaires for v in voyages), Decimal(0))

    # --- BONS TRANSPORT ---
    bons = BonTransport.objects.filter(date__month=mois, date__year=annee)
    bons_count = bons.count()
    bons_tonnage = sum((b.quantite for b in bons), Decimal(0))

    # --- DÉPENSES ADMIN ---
    dep_admin = DepenseAdmin.objects.filter(date__month=mois, date__year=annee)
    dep_total = sum((d.montant for d in dep_admin), Decimal(0))

    # --- SALAIRES ---
    employes_actifs = Employe.objects.filter(actif=True)
    masse_salariale = sum((e.salaire_total_mensuel for e in employes_actifs), Decimal(0))

    # --- SYNTHÈSE FINANCIÈRE ---
    charges_totales = car_montant + pan_total + dep_total + masse_salariale + amort_mensuel
    resultat_net = trans_ca - charges_totales
    marge = (resultat_net / trans_ca) if trans_ca else Decimal(0)

    # --- Données pour graphiques (CA par camion, tonnage par chauffeur) ---
    ca_par_camion = {}
    for v in voyages:
        ca_par_camion[v.camion.code] = ca_par_camion.get(v.camion.code, Decimal(0)) + v.chiffre_affaires

    tonnage_par_chauffeur = {}
    for b in bons:
        key = f"{b.prenom} {b.nom}"
        tonnage_par_chauffeur[key] = tonnage_par_chauffeur.get(key, Decimal(0)) + b.quantite

    # Série mensuelle (12 mois glissants)
    serie_mensuelle = []
    for m in range(1, 13):
        vs = TransportBauxite.objects.filter(date__month=m, date__year=annee)
        serie_mensuelle.append({
            "mois": calendar.month_abbr[m],
            "ca": float(sum((x.chiffre_affaires for x in vs), Decimal(0))),
            "tonnage": float(sum((x.tonnage for x in vs), Decimal(0))),
        })

    ctx = {
        "mois": mois, "annee": annee,
        "mois_label": calendar.month_name[mois].capitalize(),
        # Flotte
        "flotte_nb": flotte_nb, "flotte_prix": flotte_prix,
        "flotte_capacite": flotte_capacite, "amort_mensuel": amort_mensuel,
        "amort_annuel": amort_annuel, "vr_totale": vr_totale,
        # Carburant
        "car_litres": car_litres, "car_km": car_km,
        "car_montant": car_montant, "car_conso": car_conso,
        "car_gnf_km": car_gnf_km,
        # Pannes
        "pan_count": pan_count, "pan_total": pan_total,
        "pan_pieces": pan_pieces, "pan_mo": pan_mo, "pan_immo": pan_immo,
        # Transport
        "trans_nb": trans_nb, "trans_tonnage": trans_tonnage,
        "trans_distance": trans_distance, "trans_ca": trans_ca,
        # Bons
        "bons_count": bons_count, "bons_tonnage": bons_tonnage,
        # Dépenses
        "dep_total": dep_total,
        # Salaires
        "masse_salariale": masse_salariale,
        # Finances
        "charges_totales": charges_totales,
        "resultat_net": resultat_net, "marge": marge,
        # Graphiques
        "ca_par_camion_json": json.dumps({
            "labels": list(ca_par_camion.keys()),
            "values": [float(v) for v in ca_par_camion.values()],
        }),
        "tonnage_par_chauffeur_json": json.dumps({
            "labels": list(tonnage_par_chauffeur.keys()),
            "values": [float(v) for v in tonnage_par_chauffeur.values()],
        }),
        "serie_mensuelle_json": json.dumps(serie_mensuelle),
    }
    return render(request, "dashboard/home.html", ctx)


@login_required
def rapport_mensuel(request):
    """Rapport mensuel intelligent : podiums, anomalies, synthèse, factures."""
    mois, annee = _filtre_periode(request)
    ctx = _rapport_mensuel_service(mois, annee)

    # Données JSON pour graphiques
    ctx["chart_car_par_camion_json"] = json.dumps({
        "labels": [c["code"] for c in ctx["car_par_camion"]],
        "montants": [float(c["montant"]) for c in ctx["car_par_camion"]],
        "conso": [float(c["conso"]) for c in ctx["car_par_camion"]],
    })
    ctx["chart_tonnage_par_camion_json"] = json.dumps({
        "labels": [c["code"] for c in ctx["trans_par_camion"]],
        "tonnage": [float(c["tonnage"]) for c in ctx["trans_par_camion"]],
        "voyages": [c["nb_voyages"] for c in ctx["trans_par_camion"]],
    })
    ctx["chart_charges_json"] = json.dumps(ctx["charges_repartition"])

    # Liste des périodes récentes pour le sélecteur
    periodes = []
    d = date(annee, mois, 1)
    for i in range(12):
        m = d.month - i
        y = d.year
        while m <= 0:
            m += 12
            y -= 1
        periodes.append({"mois": m, "annee": y, "label": f"{calendar.month_name[m].capitalize()} {y}"})
    ctx["periodes_recentes"] = periodes

    return render(request, "dashboard/rapport_mensuel.html", ctx)


@login_required
def generer_factures_mois(request):
    """Déclenche la génération manuelle des factures pour le mois en cours."""
    if request.method != "POST":
        return redirect("dashboard:rapport")

    mois = int(request.POST.get("mois") or date.today().month)
    annee = int(request.POST.get("annee") or date.today().year)
    force = request.POST.get("force") == "1"

    resultats = Facture.generer_pour_periode(mois, annee, force=force)

    if not resultats:
        messages.warning(request, f"Aucun contrat actif éligible pour {mois:02d}/{annee}.")
    else:
        nb_crees = sum(1 for _, c in resultats if c)
        nb_maj = len(resultats) - nb_crees
        total_ttc = sum(float(f.montant_ttc) for f, _ in resultats)
        messages.success(
            request,
            f"Factures {mois:02d}/{annee} : {nb_crees} créée(s), {nb_maj} mise(s) à jour. "
            f"Total TTC = {total_ttc:,.0f} GNF"
        )

    url = reverse("dashboard:rapport") + f"?mois={mois}&annee={annee}"
    return redirect(url)


# ===========================================================================
# MULTI-CONTRATS : /projets/, /projets/<code>/, /bilan-entreprise/
# ===========================================================================
def _periode_optionnelle(request):
    """Retourne (mois, annee) avec support pour 'toute-periode' (None).

    - mois=0 ou annee=0 → None (= tout)
    - sinon → valeur int
    - par défaut → mois/année courants
    """
    today = date.today()
    raw_mois = request.GET.get("mois")
    raw_annee = request.GET.get("annee")
    try:
        mois = None if raw_mois in (None, "", "0", "all") else int(raw_mois)
    except (ValueError, TypeError):
        mois = today.month
    try:
        annee = None if raw_annee == "all" else (int(raw_annee) if raw_annee else today.year)
    except (ValueError, TypeError):
        annee = today.year
    if raw_mois is None and raw_annee is None:
        mois, annee = today.month, today.year
    return mois, annee


def _periodes_recentes(mois_ref, annee_ref, count=12):
    today = date.today()
    m_ref = mois_ref or today.month
    a_ref = annee_ref or today.year
    out = []
    d = date(a_ref, m_ref, 1)
    for i in range(count):
        m = d.month - i
        y = d.year
        while m <= 0:
            m += 12
            y -= 1
        out.append({"mois": m, "annee": y, "label": f"{calendar.month_name[m].capitalize()} {y}"})
    return out


@login_required
def projets_liste(request):
    """Vue tableau : bilan par projet pour la période + KPIs entreprise."""
    mois, annee = _periode_optionnelle(request)
    bilan = _bilan_entreprise(mois=mois, annee=annee)
    bilan["periodes_recentes"] = _periodes_recentes(mois, annee)
    bilan["chart_ca_json"] = json.dumps(bilan["repartition_ca"])
    bilan["chart_charges_json"] = json.dumps(bilan["repartition_charges"])
    return render(request, "dashboard/projets_liste.html", bilan)


@login_required
def projet_detail(request, code):
    """Bilan détaillé d'un contrat / projet."""
    contrat = get_object_or_404(Contrat, code=code)
    mois, annee = _periode_optionnelle(request)
    b = _bilan_contrat(contrat, mois=mois, annee=annee)
    b["periodes_recentes"] = _periodes_recentes(mois, annee)

    # Charges détaillées (donut)
    b["chart_charges_json"] = json.dumps([
        {"label": "Carburant", "value": float(b["charges_carburant"])},
        {"label": "Pannes", "value": float(b["charges_pannes"])},
        {"label": "Dépenses admin.", "value": float(b["charges_depenses"])},
    ])
    # Évolution mensuelle du CA sur l'année (contrat)
    year = annee or date.today().year
    serie = []
    for m in range(1, 13):
        bm = _bilan_contrat(contrat, mois=m, annee=year)
        serie.append({
            "mois": calendar.month_abbr[m],
            "ca": float(bm["ca"]),
            "charges": float(bm["charges_totales"]),
            "resultat": float(bm["resultat_net"]),
        })
    b["serie_mensuelle_json"] = json.dumps(serie)
    b["annee_serie"] = year

    # Factures du contrat
    fq = Facture.objects.filter(contrat=contrat)
    if annee:
        fq = fq.filter(periode_annee=annee)
    if mois:
        fq = fq.filter(periode_mois=mois)
    b["factures"] = fq.order_by("-periode_annee", "-periode_mois")
    return render(request, "dashboard/projet_detail.html", b)


@login_required
def bilan_entreprise_vue(request):
    """Synthèse entreprise : somme de tous les projets + graphiques."""
    mois, annee = _periode_optionnelle(request)
    bilan = _bilan_entreprise(mois=mois, annee=annee)
    bilan["periodes_recentes"] = _periodes_recentes(mois, annee)
    bilan["chart_ca_json"] = json.dumps(bilan["repartition_ca"])
    bilan["chart_charges_json"] = json.dumps(bilan["repartition_charges"])

    # Série mensuelle entreprise sur l'année courante
    year = annee or date.today().year
    serie = []
    for m in range(1, 13):
        bm = _bilan_entreprise(mois=m, annee=year)
        serie.append({
            "mois": calendar.month_abbr[m],
            "ca": float(bm["tot_ca"]),
            "charges": float(bm["charges_totales"]),
            "resultat": float(bm["resultat"]),
        })
    bilan["serie_mensuelle_json"] = json.dumps(serie)
    bilan["annee_serie"] = year
    return render(request, "dashboard/bilan_entreprise.html", bilan)
