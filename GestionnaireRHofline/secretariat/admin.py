from django.contrib import admin
from .models import (
    Courrier, RendezVous, Visiteur, Appel,
    DocumentSecretariat, Tache, Contact, Reunion,
)

for _m in (Courrier, RendezVous, Visiteur, Appel,
           DocumentSecretariat, Tache, Contact, Reunion):
    try:
        admin.site.register(_m)
    except admin.sites.AlreadyRegistered:
        pass
