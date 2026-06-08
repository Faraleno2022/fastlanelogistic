"""
Storage statique personnalisé pour la production (WhiteNoise).

Problème résolu :
Certains fichiers JS/CSS vendorés (ex: chart.umd.min.js) contiennent une
référence `//# sourceMappingURL=...map` ou `url(...)` vers un fichier
non livré. En mode strict, le post-traitement de
CompressedManifestStaticFilesStorage lève MissingFileError et fait
échouer `collectstatic`.

Ce storage tolère ces références manquantes : il laisse la référence
inchangée au lieu de planter, tout en conservant le hashing/compression
pour tous les fichiers réellement présents.
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class ToleranteStaticFilesStorage(CompressedManifestStaticFilesStorage):
    # Ne pas lever d'erreur si une entrée du manifeste est absente au runtime.
    manifest_strict = False

    def url_converter(self, name, hashed_files, template=None):
        """Enveloppe le convertisseur d'URL pour ignorer les fichiers
        référencés mais absents (sourcemaps, polices optionnelles, etc.)."""
        base_converter = super().url_converter(name, hashed_files, template)

        def converter(matchobj):
            try:
                return base_converter(matchobj)
            except ValueError:
                # Référence introuvable -> on garde le texte d'origine.
                return matchobj.group(0)

        return converter
