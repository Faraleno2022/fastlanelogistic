from datetime import date
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, ProtectedError
from apps.core.session_helpers import get_contrat_actif
from apps.core.utils import format_protected_error
from .models import Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport
from .forms import (
    CarburantForm, PanneForm, DepenseAdminForm,
    TransportBauxiteForm, BonTransportForm,
)


def _build_initial(request):
    """Retourne le dict `initial` pour pré-remplir le formulaire en fonction
    du contrat actif en session et du querystring.

    Priorité :
      1. `?contrat=<code>` dans l'URL (surcharge ponctuelle)
      2. Contrat actif en session
      3. Aucun (None)
    """
    initial = {}
    code_url = (request.GET.get("contrat") or "").strip()
    if code_url:
        from apps.facturation.models import Contrat
        c = Contrat.objects.filter(code=code_url, actif=True).first()
        if c:
            initial["contrat"] = c
            return initial
    contrat_actif = get_contrat_actif(request)
    if contrat_actif:
        initial["contrat"] = contrat_actif
    return initial


def _pre_fill_client_and_tarif(initial, Model):
    """Pour TransportBauxite : si on a un contrat dans initial, on pré-remplit
    aussi le client et le tarif_unitaire pour éviter une double saisie."""
    if Model is TransportBauxite and "contrat" in initial and initial["contrat"]:
        initial.setdefault("client", initial["contrat"].client)
        initial.setdefault("tarif_unitaire", initial["contrat"].tarif)


def _crud_factory(Model, Form, list_url, label, icone):
    """Génère les vues create/edit/delete pour un modèle."""
    @login_required
    def create_view(request):
        initial = _build_initial(request) if request.method != "POST" else {}
        _pre_fill_client_and_tarif(initial, Model)
        form = Form(request.POST or None, initial=initial)
        if form.is_valid():
            form.save()
            messages.success(request, f"{label} ajouté(e).")
            return redirect(list_url)
        contrat_initial = initial.get("contrat") if initial else None
        return render(request, "_form_generic.html", {
            "form": form, "titre": f"Ajouter — {label}",
            "icone": icone, "retour_url": list_url,
            "contrat_prefill": contrat_initial,
        })

    @login_required
    def edit_view(request, pk):
        obj = get_object_or_404(Model, pk=pk)
        form = Form(request.POST or None, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{label} mis(e) à jour.")
            return redirect(list_url)
        return render(request, "_form_generic.html", {
            "form": form, "titre": f"Modifier — {label}",
            "icone": "pencil", "retour_url": list_url,
        })

    @login_required
    def delete_view(request, pk):
        obj = get_object_or_404(Model, pk=pk)
        if request.method == "POST":
            try:
                obj.delete()
            except ProtectedError as e:
                messages.error(request, format_protected_error(e))
                return redirect(list_url)
            messages.success(request, f"{label} supprimé(e).")
            return redirect(list_url)
        return render(request, "confirm_delete.html", {
            "objet": obj, "titre": f"Supprimer — {label}",
            "message": f"Supprimer définitivement cet élément ({obj}) ?",
            "retour_url": list_url,
        })

    return create_view, edit_view, delete_view


carburant_create, carburant_edit, carburant_delete = _crud_factory(
    Carburant, CarburantForm, "operations:carburant", "Prise de carburant", "fuel-pump")
panne_create, panne_edit, panne_delete = _crud_factory(
    Panne, PanneForm, "operations:pannes", "Panne", "tools")
depense_create, depense_edit, depense_delete = _crud_factory(
    DepenseAdmin, DepenseAdminForm, "operations:depenses_admin", "Dépense admin.", "file-earmark-text")
transport_create, transport_edit, transport_delete = _crud_factory(
    TransportBauxite, TransportBauxiteForm, "operations:transport_bauxite", "Voyage bauxite", "truck")
bon_create, bon_edit, bon_delete = _crud_factory(
    BonTransport, BonTransportForm, "operations:bons_transport", "Bon de transport", "receipt")


def _filtre_periode(request):
    today = date.today()
    try:
        mois = int(request.GET.get("mois", today.month))
        annee = int(request.GET.get("annee", today.year))
    except (ValueError, TypeError):
        mois, annee = today.month, today.year
    return mois, annee


@login_required
def carburant_list(request):
    mois, annee = _filtre_periode(request)
    prises = Carburant.objects.filter(date__month=mois, date__year=annee).select_related("camion", "chauffeur")
    total_km = sum((p.km_parcourus for p in prises), 0)
    total_litres = sum((p.litres_pris for p in prises), Decimal(0))
    total_montant = sum((p.montant_total for p in prises), Decimal(0))
    conso_moy = (total_litres / total_km * 100) if total_km else 0
    return render(request, "operations/carburant.html", {
        "prises": prises, "mois": mois, "annee": annee,
        "total_km": total_km, "total_litres": total_litres,
        "total_montant": total_montant, "conso_moy": conso_moy,
    })


@login_required
def pannes_list(request):
    mois, annee = _filtre_periode(request)
    pannes = Panne.objects.filter(date__month=mois, date__year=annee).select_related("camion")
    total_pieces = sum((p.cout_pieces for p in pannes), Decimal(0))
    total_mo = sum((p.cout_main_oeuvre for p in pannes), Decimal(0))
    total = total_pieces + total_mo
    total_immo = sum((p.duree_immobilisation for p in pannes), 0)
    # par type
    stats = {}
    for p in pannes:
        s = stats.setdefault(p.get_type_panne_display(), {"count": 0, "montant": Decimal(0)})
        s["count"] += 1
        s["montant"] += p.cout_total
    return render(request, "operations/pannes.html", {
        "pannes": pannes, "mois": mois, "annee": annee,
        "total_pieces": total_pieces, "total_mo": total_mo,
        "total": total, "total_immo": total_immo, "stats": stats,
    })


@login_required
def depenses_admin(request):
    mois, annee = _filtre_periode(request)
    depenses = DepenseAdmin.objects.filter(date__month=mois, date__year=annee).select_related("camion")
    total = sum((d.montant for d in depenses), Decimal(0))
    return render(request, "operations/depenses_admin.html", {
        "depenses": depenses, "total": total, "mois": mois, "annee": annee,
    })


@login_required
def transport_bauxite(request):
    mois, annee = _filtre_periode(request)
    voyages = TransportBauxite.objects.filter(date__month=mois, date__year=annee).select_related("camion", "chauffeur")
    total_tonnage = sum((v.tonnage for v in voyages), Decimal(0))
    total_distance = sum((v.distance_km for v in voyages), Decimal(0))
    total_ca = sum((v.chiffre_affaires for v in voyages), Decimal(0))
    nb_voyages = voyages.count()
    return render(request, "operations/transport_bauxite.html", {
        "voyages": voyages, "mois": mois, "annee": annee,
        "total_tonnage": total_tonnage, "total_distance": total_distance,
        "total_ca": total_ca, "nb_voyages": nb_voyages,
    })


@login_required
def bons_transport(request):
    mois, annee = _filtre_periode(request)
    bons = BonTransport.objects.filter(date__month=mois, date__year=annee)
    total_quantite = sum((b.quantite for b in bons), Decimal(0))
    nb_bons = bons.count()

    # Synthèse par chauffeur (prénom + nom)
    synth = {}
    for b in bons:
        key = (b.prenom, b.nom)
        s = synth.setdefault(key, {
            "prenom": b.prenom, "nom": b.nom, "telephone": b.telephone,
            "plaque": b.plaque, "nb_bons": 0, "nb_voyages": 0,
            "quantite_totale": Decimal(0),
        })
        s["nb_bons"] += 1
        s["nb_voyages"] += 1
        s["quantite_totale"] += b.quantite

    synth_list = list(synth.values())
    for s in synth_list:
        s["moyenne_voyage"] = (s["quantite_totale"] / s["nb_voyages"]) if s["nb_voyages"] else 0

    return render(request, "operations/bons_transport.html", {
        "bons": bons, "mois": mois, "annee": annee,
        "nb_bons": nb_bons, "total_quantite": total_quantite,
        "synth": synth_list,
    })


@login_required
def bon_imprimer(request, pk):
    """Génère le PDF professionnel du bon pour impression / remise chauffeur."""
    from apps.core.exports import build_bon_transport_pdf
    bon = get_object_or_404(BonTransport, pk=pk)
    inline = request.GET.get("inline") == "1"
    return build_bon_transport_pdf(bon, inline=inline)
