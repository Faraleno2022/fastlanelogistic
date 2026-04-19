"""Vues d'import / export / fiches vierges pour le module opérations."""
from __future__ import annotations
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect

from apps.core.exports import build_excel, build_pdf, build_blank_fiches
from apps.core.imports import read_excel_rows, generate_import_template

from .exports import REGISTRY


def _filtre_periode(request):
    today = date.today()
    try:
        mois = int(request.GET.get("mois", today.month))
        annee = int(request.GET.get("annee", today.year))
    except (ValueError, TypeError):
        mois, annee = today.month, today.year
    return mois, annee


def _get_spec(module: str):
    spec = REGISTRY.get(module)
    if spec is None:
        raise Http404(f"Module inconnu : {module}")
    return spec


def _filtered_queryset(request, spec):
    mois, annee = _filtre_periode(request)
    qs = spec["Model"].objects.filter(date__month=mois, date__year=annee)
    if spec.get("select_related"):
        qs = qs.select_related(*spec["select_related"])
    return qs, mois, annee


# ---------------------------------------------------------------------------
# Export Excel / PDF
# ---------------------------------------------------------------------------

@login_required
def export_excel(request, module: str):
    spec = _get_spec(module)
    qs, mois, annee = _filtered_queryset(request, spec)
    return build_excel(
        title=f"{spec['titre']} — {mois:02d}/{annee}",
        columns=spec["columns"],
        rows=spec["build_rows"](qs),
        filename=f"{module}_{mois:02d}_{annee}",
        sous_titre=f"Période : {mois:02d}/{annee} — {qs.count()} ligne(s)",
    )


@login_required
def export_pdf(request, module: str):
    spec = _get_spec(module)
    qs, mois, annee = _filtered_queryset(request, spec)
    return build_pdf(
        title=f"{spec['titre']} — {mois:02d}/{annee}",
        columns=spec["columns"],
        rows=list(spec["build_rows"](qs)),
        filename=f"{module}_{mois:02d}_{annee}",
        sous_titre=f"Période : {mois:02d}/{annee} — {qs.count()} ligne(s)",
        orientation="landscape",
    )


# ---------------------------------------------------------------------------
# Import Excel
# ---------------------------------------------------------------------------

@login_required
def import_template(request, module: str):
    spec = _get_spec(module)
    return generate_import_template(
        title=spec["titre"],
        schema=spec["import_schema"],
        filename=f"modele_import_{module}",
    )


@login_required
def import_upload(request, module: str):
    spec = _get_spec(module)
    schema = spec["import_schema"]

    context = {
        "module": module,
        "titre": spec["titre"],
        "schema": schema,
        "errors": [],
        "created": 0,
        "preview": [],
    }

    if request.method != "POST":
        return render(request, "operations/import_form.html", context)

    f = request.FILES.get("fichier")
    if not f:
        context["errors"] = [(0, "Aucun fichier reçu.")]
        return render(request, "operations/import_form.html", context)

    try:
        rows, errors = read_excel_rows(f, schema)
    except Exception as e:
        context["errors"] = [(0, f"Fichier illisible : {e}")]
        return render(request, "operations/import_form.html", context)

    if errors:
        context["errors"] = errors
        context["preview"] = [(r, data) for r, data in rows[:15]]
        return render(request, "operations/import_form.html", context)

    # Aperçu uniquement ? (bouton "Vérifier")
    if request.POST.get("action") == "preview":
        context["preview"] = [(r, data) for r, data in rows[:20]]
        context["total_rows"] = len(rows)
        return render(request, "operations/import_form.html", context)

    # Import réel — création atomique
    Model = spec["Model"]
    created = 0
    try:
        with transaction.atomic():
            for _r, data in rows:
                Model.objects.create(**data)
                created += 1
    except Exception as e:
        context["errors"] = [(0, f"Erreur lors de l'enregistrement : {e}")]
        return render(request, "operations/import_form.html", context)

    messages.success(
        request,
        f"Import réussi : {created} ligne(s) ajoutée(s) dans « {spec['titre']} »."
    )
    return redirect(f"operations:{module_to_list_name(module)}")


def module_to_list_name(module: str) -> str:
    """Le slug d'URL module -> nom de la vue liste correspondante."""
    return {
        "carburant": "carburant",
        "pannes": "pannes",
        "depenses": "depenses_admin",
        "transport": "transport_bauxite",
        "bons": "bons_transport",
    }.get(module, "carburant")


# ---------------------------------------------------------------------------
# Fiches vierges terrain
# ---------------------------------------------------------------------------

@login_required
def fiche_vierge(request, fiche_type: str):
    try:
        nb = int(request.GET.get("n", "1"))
    except (ValueError, TypeError):
        nb = 1
    nb = max(1, min(50, nb))
    try:
        return build_blank_fiches(fiche_type, nb_copies=nb)
    except ValueError:
        raise Http404(f"Type de fiche inconnu : {fiche_type}")
