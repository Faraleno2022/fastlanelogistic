from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import ContactForm
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


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def contact(request):
    page = PageAPropos.load()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ip = _client_ip(request)
            msg.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            msg.save()

            # Tentative d'envoi d'e-mail (silencieux si SMTP non configuré)
            try:
                dest = page.email or getattr(settings, "DEFAULT_FROM_EMAIL", "") \
                       or "contact@fastlanelogisticgn.com"
                from_addr = getattr(settings, "DEFAULT_FROM_EMAIL",
                                    "no-reply@fastlanelogisticgn.com")
                subject = f"[Contact site] {msg.get_sujet_display()} — {msg.nom}"
                body = (
                    f"Nouveau message depuis le site public.\n\n"
                    f"Nom        : {msg.nom}\n"
                    f"Entreprise : {msg.entreprise or '—'}\n"
                    f"E-mail     : {msg.email}\n"
                    f"Téléphone  : {msg.telephone or '—'}\n"
                    f"Sujet      : {msg.get_sujet_display()}\n"
                    f"Reçu le    : {msg.created_at:%d/%m/%Y %H:%M}\n\n"
                    f"Message :\n{msg.message}\n"
                )
                send_mail(subject, body, from_addr, [dest], fail_silently=True)
            except Exception:
                pass

            messages.success(
                request,
                "Votre message a bien été envoyé. Notre équipe vous recontactera "
                "dans les meilleurs délais."
            )
            return redirect("public:contact")
    else:
        form = ContactForm()

    return render(request, "public/contact.html", {
        "form": form,
        "page": page,
    })


def robots_txt(request):
    """
    /robots.txt — autorise les moteurs sur tout le site public, bloque
    les zones privées (admin, dashboard, espace authentifié) et annonce
    l'emplacement du sitemap.
    """
    site_url = getattr(settings, "SEO_SITE_URL", "").rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /connexion/",
        "Disallow: /dashboard/",
        "Disallow: /core/",
        "Disallow: /flotte/",
        "Disallow: /rh/",
        "Disallow: /operations/",
        "Disallow: /facturation/",
        "",
        # Crawl-delay raisonnable pour ne pas surcharger le serveur PA
        "Crawl-delay: 2",
        "",
        f"Sitemap: {site_url}/sitemap.xml" if site_url else "Sitemap: /sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def google_site_verification(request):
    """
    Fichier de validation de propriété Google Search Console.
    Doit répondre exactement :
        google-site-verification: google10babad53f3eade7.html
    à l'URL https://www.fastlanelogisticgn.com/google10babad53f3eade7.html
    """
    return HttpResponse(
        "google-site-verification: google10babad53f3eade7.html",
        content_type="text/html",
    )
