from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, ProtectedError, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

from apps.core.utils import format_protected_error
from apps.operations.models import Carburant, Panne, DepenseAdmin, TransportBauxite

from .models import Camion
from .forms import CamionForm


DEC18 = DecimalField(max_digits=18, decimal_places=2)
DEC14 = DecimalField(max_digits=14, decimal_places=2)
ZERO = Decimal("0")


def _benefice_vide():
    return {
        "ca": ZERO,
        "carburant": ZERO,
        "pannes": ZERO,
        "depenses": ZERO,
        "charges": ZERO,
        "benefice": ZERO,
        "marge_pct": ZERO,
    }


def _benefices_camions(camions):
    camion_ids = [camion.id for camion in camions]
    if not camion_ids:
        return {}

    ca_expr = ExpressionWrapper(F("tonnage") * F("tarif_unitaire"), output_field=DEC18)
    carburant_expr = ExpressionWrapper(
        (F("litres_apres") - F("litres_avant")) * F("prix_unitaire"),
        output_field=DEC18,
    )
    panne_expr = ExpressionWrapper(F("cout_pieces") + F("cout_main_oeuvre"), output_field=DEC14)

    def par_camion(queryset, aggregate):
        rows = (
            queryset.filter(camion_id__in=camion_ids)
            .values("camion_id")
            .annotate(total=Coalesce(aggregate, ZERO, output_field=DEC18))
        )
        return {row["camion_id"]: row["total"] or ZERO for row in rows}

    ca_map = par_camion(TransportBauxite.objects, Sum(ca_expr))
    carburant_map = par_camion(Carburant.objects, Sum(carburant_expr))
    pannes_map = par_camion(Panne.objects, Sum(panne_expr))
    depenses_map = par_camion(DepenseAdmin.objects, Sum("montant"))

    resultats = {}
    for camion_id in camion_ids:
        ca = ca_map.get(camion_id, ZERO)
        carburant = carburant_map.get(camion_id, ZERO)
        pannes = pannes_map.get(camion_id, ZERO)
        depenses = depenses_map.get(camion_id, ZERO)
        charges = carburant + pannes + depenses
        benefice = ca - charges
        marge_pct = (benefice / ca * Decimal(100)) if ca else ZERO
        resultats[camion_id] = {
            "ca": ca,
            "carburant": carburant,
            "pannes": pannes,
            "depenses": depenses,
            "charges": charges,
            "benefice": benefice,
            "marge_pct": marge_pct,
        }
    return resultats


def _benefice_camion(camion):
    return _benefices_camions([camion]).get(camion.id, _benefice_vide())


@login_required
def liste_camions(request):
    camions_qs = Camion.objects.all().order_by("-created_at", "code")
    totaux = camions_qs.aggregate(
        total_prix=Sum("prix_achat"),
        total_capacite=Sum("capacite_tonnes"),
        nombre=Count("id"),
    )
    camions = list(camions_qs)
    benefices = _benefices_camions(camions)
    for camion in camions:
        camion.benefice_data = benefices.get(camion.id, _benefice_vide())
    total_ca = sum((c.benefice_data["ca"] for c in camions), ZERO)
    total_charges = sum((c.benefice_data["charges"] for c in camions), ZERO)
    total_benefice = sum((c.benefice_data["benefice"] for c in camions), ZERO)
    return render(request, "flotte/liste_camions.html", {
        "camions": camions,
        "totaux": totaux,
        "total_ca": total_ca,
        "total_charges": total_charges,
        "total_benefice": total_benefice,
    })


@login_required
def detail_camion(request, code):
    camion = get_object_or_404(Camion, code=code)
    tableau = camion.tableau_amortissement()
    return render(request, "flotte/detail_camion.html", {
        "camion": camion,
        "tableau": tableau,
        "benefice": _benefice_camion(camion),
    })


@login_required
def amortissement_global(request):
    camions = Camion.objects.all()
    data = []
    for c in camions:
        data.append({
            "camion": c,
            "rows": c.tableau_amortissement(),
        })
    return render(request, "flotte/amortissement.html", {"data": data})


@login_required
def camion_create(request):
    form = CamionForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Camion ajouté avec succès.")
        return redirect("flotte:liste")
    return render(request, "flotte/form_camion.html", {"form": form, "titre": "Ajouter un camion"})


@login_required
def camion_edit(request, code):
    camion = get_object_or_404(Camion, code=code)
    form = CamionForm(request.POST or None, instance=camion)
    if form.is_valid():
        form.save()
        messages.success(request, f"Camion {camion.code} mis à jour.")
        return redirect("flotte:liste")
    return render(request, "flotte/form_camion.html", {"form": form, "titre": f"Modifier {camion.code}", "camion": camion})


@login_required
def camion_delete(request, code):
    camion = get_object_or_404(Camion, code=code)
    if request.method == "POST":
        try:
            camion.delete()
        except ProtectedError as e:
            messages.error(request, format_protected_error(e))
            return redirect("flotte:liste")
        messages.success(request, f"Camion {code} supprimé.")
        return redirect("flotte:liste")
    return render(request, "confirm_delete.html", {
        "objet": camion, "titre": "Supprimer le camion",
        "message": f"Êtes-vous sûr de vouloir supprimer le camion {camion.code} — {camion.immatriculation} ?",
        "retour_url": "flotte:liste",
    })
