from django.contrib import admin
from . import models

for _name in ['Depot', 'CategorieArticle', 'Fournisseur', 'Demandeur', 'Article',
              'EntreeStock', 'SortieStock', 'MouvementStock', 'Inventaire',
              'LigneInventaire', 'CommandeAchat', 'LigneCommande']:
    _m = getattr(models, _name, None)
    if _m is not None:
        try:
            admin.site.register(_m)
        except admin.sites.AlreadyRegistered:
            pass
