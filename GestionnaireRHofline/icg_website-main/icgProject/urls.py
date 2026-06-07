"""
URL configuration for icgProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse
from icgProject import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


def google_site_verification(request):
    return HttpResponse(
        "google-site-verification: google10babad53f3eade7.html",
        content_type="text/html",
    )


def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /connexion\n"
        "Disallow: /deconnexion\n"
        "Disallow: /contact_list\n"
        "Disallow: /show_contact/\n"
        "Disallow: /delete_contact/\n"
        "\n"
        "Sitemap: https://www.icguinea.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    base = "https://www.icguinea.com"
    urls = ["/", "/about", "/contact", "/show_event"]
    items = "".join(
        f"<url><loc>{base}{u}</loc><changefreq>weekly</changefreq><priority>{'1.0' if u == '/' else '0.8'}</priority></url>"
        for u in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{items}</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('google10babad53f3eade7.html', google_site_verification),
    path('',include('appli.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

urlpatterns += staticfiles_urlpatterns()