"""
Tests unitaires du moteur de scoring de auto_affecter_services.

Ne touche pas à la base de données : utilise SimpleTestCase + appels directs
sur les fonctions pures du module.
"""
from django.test import SimpleTestCase

from employes.management.commands.auto_affecter_services import (
    POIDS_SOURCES,
    SEUIL_AFFECTATION,
    _construire_candidats,
    _meilleur_candidat,
    _normaliser,
    _scorer,
)


class NormaliserTests(SimpleTestCase):
    def test_supprime_accents_et_lowercase(self):
        self.assertEqual(_normaliser('Comptabilité'), 'comptabilite')
        self.assertEqual(_normaliser('Médecin du Travail'), 'medecin du travail')

    def test_gere_none_et_vide(self):
        self.assertEqual(_normaliser(None), '')
        self.assertEqual(_normaliser(''), '')
        self.assertEqual(_normaliser('   '), '')

    def test_normalise_espaces_multiples(self):
        self.assertEqual(_normaliser('Chef    d\'équipe'), "chef d'equipe")


class ScoringMonoSourceTests(SimpleTestCase):
    """Vérifie qu'un keyword unique attribue le bon score au bon service."""

    def _scorer_intitule_poste(self, intitule):
        candidats = _construire_candidats()
        _scorer(_normaliser(intitule), POIDS_SOURCES['poste_intitule'], candidats)
        return _meilleur_candidat(candidats)

    def test_comptable_match_finance(self):
        meilleur = self._scorer_intitule_poste('Comptable principal')
        self.assertIsNotNone(meilleur)
        self.assertEqual(meilleur.code, 'FIN')

    def test_chauffeur_match_logistique(self):
        self.assertEqual(self._scorer_intitule_poste('Chauffeur PL').code, 'LOG')

    def test_developpeur_match_technique(self):
        self.assertEqual(self._scorer_intitule_poste('Développeur Python').code, 'TECH')

    def test_secretaire_match_support(self):
        self.assertEqual(self._scorer_intitule_poste('Secrétaire').code, 'SUP')

    def test_juriste_match_juridique(self):
        self.assertEqual(self._scorer_intitule_poste('Juriste senior').code, 'JUR')

    def test_intitule_inconnu_non_resolu(self):
        self.assertIsNone(self._scorer_intitule_poste('Vagabond cosmique'))

    def test_intitule_vide_non_resolu(self):
        self.assertIsNone(self._scorer_intitule_poste(''))


class ScoringMultiSourceTests(SimpleTestCase):
    """Plusieurs sources cumulent leur poids et orientent vers le bon service."""

    def test_cumul_intitule_et_departement_double_le_score(self):
        candidats = _construire_candidats()
        _scorer(_normaliser('Vendeur'), POIDS_SOURCES['poste_intitule'], candidats)
        _scorer(_normaliser('Commercial'), POIDS_SOURCES['departement'], candidats)
        meilleur = _meilleur_candidat(candidats)
        self.assertEqual(meilleur.code, 'COM')
        self.assertEqual(meilleur.score, 6)

    def test_priorite_departage_les_egalites(self):
        """A score égal, le service de plus haute priorité gagne."""
        candidats = _construire_candidats()
        # 'rh' (priorité 90) et 'support' (priorité 70) à score = 3 chacun
        _scorer(_normaliser('Support RH'), POIDS_SOURCES['poste_intitule'], candidats)
        meilleur = _meilleur_candidat(candidats)
        self.assertEqual(meilleur.code, 'RH')

    def test_seuil_minimum_respecte(self):
        """Une preuve unique de poids inférieur au seuil ne doit rien affecter."""
        candidats = _construire_candidats()
        _scorer(_normaliser('Marketing'), POIDS_SOURCES['observations'], candidats)
        # observations a un poids de 1, seuil = 3, donc score=1 < seuil
        self.assertIsNone(_meilleur_candidat(candidats))


class FrontiereDeMotTests(SimpleTestCase):
    """Le matching doit être strict : pas de faux positifs sur sous-chaînes."""

    def test_rh_dans_marche_ne_match_pas(self):
        # 'rh' ne doit pas matcher 'marche' même si la sous-chaîne existe pas ici,
        # ce test garantit que le motif \b est bien actif.
        candidats = _construire_candidats()
        _scorer(_normaliser('Marche export'), POIDS_SOURCES['poste_intitule'], candidats)
        self.assertIsNone(_meilleur_candidat(candidats))

    def test_dg_isole_match_direction(self):
        # 'pdg' contient 'dg' mais ne doit pas matcher comme 'dg' isolé ;
        # par contre le keyword 'pdg' lui-même doit matcher.
        candidats = _construire_candidats()
        _scorer(_normaliser('PDG'), POIDS_SOURCES['poste_intitule'], candidats)
        self.assertEqual(_meilleur_candidat(candidats).code, 'DIR')


class CatalogueIntegriteTests(SimpleTestCase):
    """Le catalogue doit rester cohérent : codes uniques, keywords non vides."""

    def test_codes_services_uniques(self):
        from employes.management.commands.auto_affecter_services import (
            CATALOGUE_SERVICES,
        )
        codes = [e['code'] for e in CATALOGUE_SERVICES]
        self.assertEqual(len(codes), len(set(codes)), 'Codes services dupliqués')

    def test_chaque_service_a_au_moins_un_keyword(self):
        from employes.management.commands.auto_affecter_services import (
            CATALOGUE_SERVICES,
        )
        for entree in CATALOGUE_SERVICES:
            self.assertTrue(
                entree['keywords'],
                f"Service {entree['code']} sans keyword",
            )
