"""
Recalcule la contribution ONFPP des bulletins historiques.

Convention retenue : ONFPP = base VF/ONFPP × 1,5%.

Ne touche QUE le champ `contribution_onfpp`. Le `net_a_payer` n'est pas affecté
car l'ONFPP est une charge patronale (côté employeur), pas une retenue salariée.
Aucune autre rubrique du bulletin n'est recalculée.

Usage:
    # Aperçu sur tout l'historique (RECOMMANDÉ AVANT TOUT)
    python manage.py recalculer_onfpp_historique --dry-run

    # Appliquer aux bulletins non verrouillés (brouillon / calculé)
    python manage.py recalculer_onfpp_historique

    # Appliquer même aux bulletins validés/payés (recalcul historique complet)
    python manage.py recalculer_onfpp_historique --force

    # Filtrer par année / mois / entreprise
    python manage.py recalculer_onfpp_historique --annee 2026 --dry-run
"""
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from paie.models import BulletinPaie


TAUX_ONFPP = Decimal('1.5')


class Command(BaseCommand):
    help = "Recalcule la contribution ONFPP sur la base VF/ONFPP pour les bulletins historiques"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Aperçu sans écriture en base')
        parser.add_argument('--force', action='store_true',
                            help='Inclure les bulletins validés / payés (verrouillés)')
        parser.add_argument('--annee', type=int, help='Limiter à une année')
        parser.add_argument('--mois', type=int, help='Limiter à un mois (à combiner avec --annee)')
        parser.add_argument('--entreprise', type=int, help="Limiter à une entreprise (id)")

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        qs = BulletinPaie.objects.filter(contribution_onfpp__gt=0)

        if options.get('annee'):
            annee = options['annee']
            qs = qs.filter(Q(annee_paie=annee) | Q(periode__annee=annee))
        if options.get('mois'):
            mois = options['mois']
            qs = qs.filter(Q(mois_paie=mois) | Q(periode__mois=mois))
        if options.get('entreprise'):
            qs = qs.filter(employe__entreprise_id=options['entreprise'])

        if not force:
            qs = qs.exclude(statut_bulletin__in=BulletinPaie.STATUTS_VERROUILLES)

        qs = qs.select_related('employe', 'periode').order_by(
            'annee_paie', 'mois_paie', 'numero_bulletin'
        )

        total = qs.count()
        self.stdout.write(self.style.NOTICE('=' * 78))
        self.stdout.write(self.style.NOTICE('RECALCUL ONFPP HISTORIQUE — convention : base VF/ONFPP × 1,5 %'))
        self.stdout.write(self.style.NOTICE('=' * 78))
        self.stdout.write(f"Bulletins ciblés (ONFPP > 0) : {total}")
        if dry_run:
            self.stdout.write(self.style.WARNING('MODE DRY-RUN — aucune écriture ne sera effectuée'))
        if force:
            self.stdout.write(self.style.WARNING('MODE --force — bulletins validés / payés inclus'))
        else:
            self.stdout.write('Bulletins validés / payés exclus (utiliser --force pour les inclure)')
        self.stdout.write('')

        modifies = 0
        deja_corrects = 0
        ecart_total = Decimal('0')

        for b in qs.iterator(chunk_size=200):
            ancien = b.contribution_onfpp or Decimal('0')
            base_onfpp = b.base_vf or Decimal('0')
            nouveau = (base_onfpp * TAUX_ONFPP / Decimal('100')).quantize(
                Decimal('1'), rounding=ROUND_HALF_UP
            )
            ecart = nouveau - ancien

            if ecart == 0:
                deja_corrects += 1
                continue

            modifies += 1
            ecart_total += ecart

            employe_label = f"{b.employe.nom} {b.employe.prenoms or ''}".strip()[:30]
            self.stdout.write(
                f"  {b.numero_bulletin:<28} {b.annee_paie}-{b.mois_paie:02d}  "
                f"{employe_label:<32}  "
                f"ONFPP {ancien:>11,.0f} -> {nouveau:>11,.0f}  ({ecart:+,.0f})"
            )

            if not dry_run:
                # Bypass du verrou via queryset.update() — opération de migration
                # systeme, pas une modification utilisateur.
                BulletinPaie.objects.filter(pk=b.pk).update(
                    contribution_onfpp=nouveau
                )

        self.stdout.write('')
        self.stdout.write('=' * 78)
        self.stdout.write(f"Bulletins déjà corrects : {deja_corrects}")
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"Bulletins qui seraient modifiés : {modifies}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Bulletins modifiés : {modifies}"
            ))
        signe = '+' if ecart_total >= 0 else ''
        self.stdout.write(f"Écart total ONFPP : {signe}{ecart_total:,.0f} GNF")
        self.stdout.write('=' * 78)
