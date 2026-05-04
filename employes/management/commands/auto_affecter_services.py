"""
Affectation intelligente des services aux employés.

Stratégie multi-sources avec scoring :
1. Si l'employé a un Poste avec un Service rattaché → on copie le Service.
2. Sinon, on score chaque service candidat à partir de :
   - intitulé du poste de l'employé (poids fort)
   - champ texte « departement » de l'employé (poids fort)
   - observations / autres champs texte (poids faible)
3. Le meilleur service au-dessus du seuil gagne.
4. Bonus : si un Poste sans service est résolu vers un service, on rattache
   aussi le Poste au Service (utile pour tous les futurs employés du même poste).

Usage :
    python manage.py auto_affecter_services                       # dry-run global
    python manage.py auto_affecter_services --entreprise 1        # une entreprise
    python manage.py auto_affecter_services --apply               # appliquer
    python manage.py auto_affecter_services --apply --create      # créer les services manquants
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Service, Poste
from employes.models import Employe


# ---------------------------------------------------------------------------
# Base de connaissance : services standards + synonymes français/anglais.
# Le code interne sert à dédupliquer ; nom_service est le libellé créé en base.
# Les keywords sont matchés en lowercase, sans accents, sur des mots entiers
# ou racines (ex. « compt » matche « comptable », « comptabilité », etc.).
# ---------------------------------------------------------------------------
CATALOGUE_SERVICES = [
    {
        'code': 'DIR',
        'nom': 'Direction Générale',
        'keywords': [
            'direction generale', 'directeur general', 'directrice generale',
            'pdg', 'ceo', 'gerant', 'gerante', 'president',
            'cabinet du dg', 'directoire',
        ],
        'priorite': 100,  # match fort = priorité élevée
    },
    {
        'code': 'RH',
        'nom': 'Ressources Humaines',
        'keywords': [
            'rh', 'ressources humaines', 'human resources', 'personnel',
            'paie', 'recrutement', 'formation', 'gestionnaire rh',
            'drh', 'responsable rh', 'chargé rh', 'chargee rh',
        ],
        'priorite': 90,
    },
    {
        'code': 'FIN',
        'nom': 'Finance & Comptabilité',
        'keywords': [
            'comptab', 'comptable', 'finance', 'financier', 'financiere',
            'tresorerie', 'tresorier', 'audit', 'auditeur',
            'controle de gestion', 'controleur de gestion',
            'caissier', 'caissiere', 'fiscaliste', 'daf',
            'directeur financier', 'directrice financiere',
        ],
        'priorite': 90,
    },
    {
        'code': 'COM',
        'nom': 'Commercial & Marketing',
        'keywords': [
            'commercial', 'commerciale', 'vente', 'vendeur', 'vendeuse',
            'sales', 'marketing', 'business development',
            'charge de clientele', 'chargee de clientele', 'kam',
            'account manager', 'directeur commercial', 'directrice commerciale',
        ],
        'priorite': 85,
    },
    {
        'code': 'LOG',
        'nom': 'Logistique & Transport',
        'keywords': [
            'logistique', 'logisticien', 'logisticienne',
            'transport', 'transporteur', 'chauffeur', 'conducteur',
            'magasinier', 'magasiniere', 'magasin', 'stock', 'stockiste',
            'flotte', 'gestionnaire de flotte', 'approvisionnement',
            'achat', 'acheteur', 'acheteuse', 'supply chain',
        ],
        'priorite': 90,
    },
    {
        'code': 'TECH',
        'nom': 'Technique & IT',
        'keywords': [
            'informatique', 'developpeur', 'developpeuse', 'developer',
            'technicien', 'technicienne', 'maintenance',
            'ingenieur', 'ingenieure', 'engineer',
            'devops', 'sysadmin', 'reseau', 'support technique',
            'data', 'analyste', 'cto', 'dsi', 'rsi',
        ],
        'priorite': 85,
    },
    {
        'code': 'OPS',
        'nom': 'Production & Opérations',
        'keywords': [
            'production', 'operations', 'usine', 'atelier',
            'chef d equipe', 'ouvrier', 'ouvriere', 'operateur', 'operatrice',
            'controle qualite', 'qualite', 'qhse', 'hse',
            'chef de chantier', 'contremaitre',
        ],
        'priorite': 80,
    },
    {
        'code': 'SUP',
        'nom': 'Support & Administration',
        'keywords': [
            'secretaire', 'assistant', 'assistante',
            'reception', 'receptionniste', 'standard', 'standardiste',
            'agent administratif', 'administratif', 'administrative',
            'support', 'office manager', 'planton',
        ],
        'priorite': 70,
    },
    {
        'code': 'JUR',
        'nom': 'Juridique',
        'keywords': [
            'juridique', 'juriste', 'avocat', 'avocate',
            'conformite', 'compliance', 'legal',
        ],
        'priorite': 80,
    },
    {
        'code': 'COMM',
        'nom': 'Communication',
        'keywords': [
            'communication', 'chargee de communication', 'charge de communication',
            'community manager', 'rp ', 'relations publiques', 'presse',
        ],
        'priorite': 75,
    },
    {
        'code': 'SECU',
        'nom': 'Sécurité',
        'keywords': [
            'securite', 'gardien', 'gardienne', 'agent de securite',
            'vigile', 'surveillance',
        ],
        'priorite': 75,
    },
    {
        'code': 'MED',
        'nom': 'Médical / Santé au travail',
        'keywords': [
            'medecin', 'medecine du travail', 'infirmier', 'infirmiere',
            'sante', 'medical',
        ],
        'priorite': 80,
    },
]

# Pondération des sources de texte (plus le poids est élevé, plus la source
# est fiable pour deviner le service).
POIDS_SOURCES = {
    'poste_intitule': 3,
    'departement': 3,
    'observations': 1,
}

# Score minimum requis pour valider une affectation par inférence.
SEUIL_AFFECTATION = 3


@dataclass
class CandidatService:
    """Service candidat avec score et preuves textuelles."""
    code: str
    nom: str
    priorite: int
    score: int = 0
    preuves: list[str] = field(default_factory=list)


def _normaliser(texte: str | None) -> str:
    """Lowercase + strip accents + espaces normalisés. Renvoie '' si None."""
    if not texte:
        return ''
    nfkd = unicodedata.normalize('NFKD', texte)
    sans_accent = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', sans_accent.lower().strip())


def _scorer(texte_normalise: str, poids: int, candidats: dict[str, CandidatService]) -> None:
    """Incrémente le score des candidats dont un keyword apparaît dans le texte."""
    if not texte_normalise:
        return
    for entree in CATALOGUE_SERVICES:
        for keyword in entree['keywords']:
            kw = _normaliser(keyword)
            # match sur frontière de mot pour éviter « rh » dans « marche »
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, texte_normalise):
                cand = candidats[entree['code']]
                cand.score += poids
                cand.preuves.append(f'« {kw} » ({poids}pt)')
                break  # un keyword suffit par source


def _meilleur_candidat(candidats: dict[str, CandidatService]) -> CandidatService | None:
    """Retourne le candidat au score max, départage par priorité du catalogue."""
    valides = [c for c in candidats.values() if c.score >= SEUIL_AFFECTATION]
    if not valides:
        return None
    return max(valides, key=lambda c: (c.score, c.priorite))


def _construire_candidats() -> dict[str, CandidatService]:
    return {
        e['code']: CandidatService(code=e['code'], nom=e['nom'], priorite=e['priorite'])
        for e in CATALOGUE_SERVICES
    }


class Command(BaseCommand):
    help = (
        "Affecte automatiquement un service à chaque employé sans service, "
        "en analysant intelligemment poste, département et observations. "
        "Dry-run par défaut ; ajouter --apply pour appliquer."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--entreprise',
            type=int,
            default=None,
            help="ID d'une entreprise spécifique (sinon, toutes).",
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help="Applique réellement les changements (sinon dry-run).",
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help="Crée les services manquants du catalogue dans l'entreprise.",
        )
        parser.add_argument(
            '--lier-postes',
            action='store_true',
            help="Rattache aussi les Postes inférés à leur Service (utile pour les futurs employés).",
        )
        parser.add_argument(
            '--seuil',
            type=int,
            default=SEUIL_AFFECTATION,
            help=f"Score minimum pour valider une affectation (défaut: {SEUIL_AFFECTATION}).",
        )

    def handle(self, *args, **options):
        entreprise_id = options['entreprise']
        apply_mode = options['apply']
        create_missing = options['create']
        lier_postes = options['lier_postes']
        seuil = options['seuil']

        global SEUIL_AFFECTATION
        SEUIL_AFFECTATION = seuil

        mode_label = 'APPLY (changements en base)' if apply_mode else 'DRY-RUN (aucun changement)'
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n=== Auto-affectation services — {mode_label} ===\n'))

        # 1. Sélection des employés à traiter (par entreprise)
        qs = Employe.objects.filter(statut_employe='actif', service__isnull=True)
        if entreprise_id:
            qs = qs.filter(entreprise_id=entreprise_id)

        employes_par_entreprise = defaultdict(list)
        for emp in qs.select_related('poste', 'poste__service', 'entreprise'):
            employes_par_entreprise[emp.entreprise_id].append(emp)

        if not employes_par_entreprise:
            self.stdout.write(self.style.SUCCESS("Aucun employé sans service. Rien à faire."))
            return

        total_global = sum(len(v) for v in employes_par_entreprise.values())
        self.stdout.write(
            f"{total_global} employé(s) actif(s) sans service réparti(s) sur "
            f"{len(employes_par_entreprise)} entreprise(s).\n"
        )

        with transaction.atomic():
            sp = transaction.savepoint()

            stats_globales = Counter()
            for ent_id, employes in employes_par_entreprise.items():
                ent_label = employes[0].entreprise.nom_entreprise if employes[0].entreprise else f'Ent#{ent_id}'
                self.stdout.write(self.style.HTTP_INFO(f'\n--- Entreprise : {ent_label} ({len(employes)} employés) ---'))
                stats = self._traiter_entreprise(
                    ent_id, employes,
                    apply_mode=apply_mode,
                    create_missing=create_missing,
                    lier_postes=lier_postes,
                )
                for k, v in stats.items():
                    stats_globales[k] += v

            # Résumé global
            self.stdout.write(self.style.MIGRATE_HEADING('\n=== Résumé global ==='))
            self.stdout.write(f"  Affectés via poste.service (héritage direct) : {stats_globales['heritage']}")
            self.stdout.write(f"  Affectés par inférence (score ≥ {seuil})     : {stats_globales['inference']}")
            self.stdout.write(f"  Postes auto-rattachés à un service           : {stats_globales['postes_lies']}")
            self.stdout.write(f"  Services créés (--create)                    : {stats_globales['services_crees']}")
            self.stdout.write(self.style.WARNING(
                f"  Non résolus (à traiter manuellement)         : {stats_globales['non_resolus']}"
            ))

            if not apply_mode:
                transaction.savepoint_rollback(sp)
                self.stdout.write(self.style.WARNING(
                    "\nDRY-RUN : aucun changement écrit. Relancez avec --apply pour appliquer."
                ))
            else:
                transaction.savepoint_commit(sp)
                self.stdout.write(self.style.SUCCESS("\n✓ Changements appliqués."))

    def _traiter_entreprise(
        self,
        entreprise_id: int,
        employes: list[Employe],
        apply_mode: bool,
        create_missing: bool,
        lier_postes: bool,
    ) -> Counter:
        stats = Counter()

        # Index des services existants par code/nom normalisé
        services_existants = list(Service.objects.filter(entreprise_id=entreprise_id))
        index_par_code = {s.code_service: s for s in services_existants}
        index_par_nom = {_normaliser(s.nom_service): s for s in services_existants}

        def get_or_create_service(code: str, nom: str) -> Service | None:
            if code in index_par_code:
                return index_par_code[code]
            nom_norm = _normaliser(nom)
            if nom_norm in index_par_nom:
                return index_par_nom[nom_norm]
            if not create_missing:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ Service « {nom} » absent de l'entreprise (utiliser --create pour le créer)."
                ))
                return None
            svc = Service.objects.create(
                entreprise_id=entreprise_id,
                code_service=code,
                nom_service=nom,
                description='Service créé automatiquement par auto_affecter_services',
            )
            index_par_code[code] = svc
            index_par_nom[_normaliser(nom)] = svc
            stats['services_crees'] += 1
            self.stdout.write(self.style.SUCCESS(f"  + Service créé : {code} - {nom}"))
            return svc

        for emp in employes:
            label = f"{emp.matricule or emp.pk} {emp.nom} {emp.prenoms or ''}".strip()

            # Stratégie 1 : héritage direct depuis le poste
            if emp.poste and emp.poste.service:
                if apply_mode:
                    emp.service = emp.poste.service
                    emp.save(update_fields=['service'])
                stats['heritage'] += 1
                self.stdout.write(
                    f"  ✓ {label} → {emp.poste.service.nom_service} (héritage poste)"
                )
                continue

            # Stratégie 2 : scoring multi-source
            candidats = _construire_candidats()
            if emp.poste:
                _scorer(_normaliser(emp.poste.intitule_poste), POIDS_SOURCES['poste_intitule'], candidats)
            _scorer(_normaliser(emp.departement), POIDS_SOURCES['departement'], candidats)
            _scorer(_normaliser(getattr(emp, 'observations', '') or ''), POIDS_SOURCES['observations'], candidats)

            meilleur = _meilleur_candidat(candidats)
            if meilleur is None:
                stats['non_resolus'] += 1
                indice = emp.poste.intitule_poste if emp.poste else (emp.departement or '∅')
                self.stdout.write(self.style.WARNING(
                    f"  ? {label} → non résolu (indice: {indice!r})"
                ))
                continue

            svc = get_or_create_service(meilleur.code, meilleur.nom)
            if svc is None:
                stats['non_resolus'] += 1
                continue

            preuves = ', '.join(meilleur.preuves[:3])
            self.stdout.write(
                f"  ✓ {label} → {svc.nom_service} (score {meilleur.score}, {preuves})"
            )
            if apply_mode:
                emp.service = svc
                emp.save(update_fields=['service'])
            stats['inference'] += 1

            # Bonus : rattacher le poste au service inféré
            if lier_postes and emp.poste and not emp.poste.service:
                if apply_mode:
                    emp.poste.service = svc
                    emp.poste.save(update_fields=['service'])
                stats['postes_lies'] += 1
                self.stdout.write(
                    f"      ↳ Poste « {emp.poste.intitule_poste} » rattaché à {svc.nom_service}"
                )

        return stats
