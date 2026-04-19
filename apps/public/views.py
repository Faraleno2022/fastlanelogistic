from django.db.models import Sum, Count, Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Evenement, AppelOffre, PageAPropos


def home(request):
    aujourdhui = timezone.localdate()
    prochains_events = (Evenement.objects
                        .filter(statut="publie", date_evenement__gte=aujourdhui)
                        .order_by("date_evenement")[:3])
    derniers_events = (Evenement.objects
                       .filter(statut="publie")
                       .order_by("-date_evenement")[:3])
    appels_ouverts = (AppelOffre.objects
                      .filter(statut="ouvert", date_limite__gte=aujourdhui)
                      .order_by("date_limite")[:3])

    # Flotte — aperçu public (masque volontairement les prix / infos sensibles)
    camions = []
    stats_flotte = {"nb_total": 0, "nb_service": 0, "capacite_totale": 0}
    try:
        from apps.flotte.models import Camion
        qs = Camion.objects.exclude(statut="VENDU").order_by("code")
        camions = list(qs[:8])
        agg = qs.aggregate(
            nb=Count("id"),
            nb_service=Count("id", filter=Q(statut="SERVICE")),
            cap=Sum("capacite_tonnes"),
        )
        stats_flotte = {
            "nb_total": agg["nb"] or 0,
            "nb_service": agg["nb_service"] or 0,
            "capacite_totale": int(agg["cap"] or 0),
        }
    except Exception:
        pass

    return render(request, "public/home.html", {
        "prochains_events": prochains_events,
        "derniers_events": derniers_events,
        "appels_ouverts": appels_ouverts,
        "camions": camions,
        "stats_flotte": stats_flotte,
    })


def a_propos(request):
    page = PageAPropos.load()
    return render(request, "public/a_propos.html", {"page": page})


def evenements_liste(request):
    evts = Evenement.objects.filter(statut="publie")
    return render(request, "public/evenements_liste.html", {"evenements": evts})


def evenement_detail(request, slug):
    evt = get_object_or_404(Evenement, slug=slug, statut="publie")
    return render(request, "public/evenement_detail.html", {"evt": evt})


def appels_offres_liste(request):
    aujourdhui = timezone.localdate()
    appels = AppelOffre.objects.exclude(statut="brouillon")
    ouverts = appels.filter(statut="ouvert", date_limite__gte=aujourdhui)
    clos = appels.exclude(pk__in=ouverts.values("pk"))
    return render(request, "public/appels_offres_liste.html", {
        "ouverts": ouverts,
        "clos": clos,
    })


def appel_offre_detail(request, slug):
    ao = get_object_or_404(AppelOffre, slug=slug)
    if ao.statut == "brouillon":
        # Les brouillons ne sont pas accessibles au public
        from django.http import Http404
        raise Http404
    return render(request, "public/appel_offre_detail.html", {"ao": ao})
