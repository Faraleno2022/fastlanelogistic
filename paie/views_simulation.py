"""
Vues du module de simulation fiscale comparative multi-barèmes
"""
import csv
import json
from decimal import Decimal, InvalidOperation
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from employes.models import Employe
from contrats.models import Contrat
from paie.models import BulletinPaie
from paie.models_simulation import SimulationFiscale
from paie.services_simulation import (
    simuler_multi_baremes,
    get_baremes_disponibles,
    optimiser_net,
    simuler_scenario_augmentation,
    _charger_constantes,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(val: str) -> Decimal:
    """Parse un montant saisi (espaces, virgules décimales)."""
    try:
        cleaned = str(val).replace('\u202f', '').replace(' ', '').replace(',', '.').strip()
        return Decimal(cleaned) if cleaned else Decimal('0')
    except InvalidOperation:
        return Decimal('0')


def _export_csv_response(brut: Decimal, indemnites: Decimal, resultats: list) -> HttpResponse:
    """Génère un HttpResponse CSV des résultats de simulation."""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="simulation_fiscale.csv"'

    writer = csv.writer(response, delimiter=';')

    # En-tête
    writer.writerow(['SIMULATION FISCALE MULTI-BAREMES — GuineeRH'])
    writer.writerow([
        f'Brut: {int(brut):,} GNF'.replace(',', ' '),
        f'Indemnités: {int(indemnites):,} GNF'.replace(',', ' '),
        f'Date: {date.today().strftime("%d/%m/%Y")}',
    ])
    writer.writerow([])

    # Tableau comparatif
    writer.writerow([
        'Barème', 'Brut (GNF)', 'Indemnités (GNF)',
        'CNSS employé (GNF)', 'Plafond exon. 25% (GNF)',
        'Exonéré (GNF)', 'Dépassement (GNF)',
        'Base RTS (GNF)', 'RTS (GNF)', 'Taux effectif (%)', 'Net (GNF)',
        'CNSS employeur (GNF)', 'VF (GNF)', 'TA/ONFPP (GNF)', 'Total charges pat. (GNF)',
    ])
    for r in resultats:
        ta_onfpp = r.get('ta', 0) or r.get('onfpp', 0)
        writer.writerow([
            r['bareme_label'],
            r['brut'],
            int(indemnites),
            r['cnss'],
            r['plafond_exon'],
            r['exon'],
            r['depasse'],
            r['base_rts'],
            r['rts'],
            f"{r['taux_effectif']:.2f}",
            r['net'],
            r.get('cnss_employeur', 0),
            r.get('vf', 0),
            ta_onfpp,
            r.get('total_charges_pat', 0),
        ])

    # Détail par tranches pour chaque barème
    for r in resultats:
        writer.writerow([])
        writer.writerow([f'=== DÉTAIL TRANCHES — {r["bareme_label"]} ==='])
        writer.writerow(['Tranche', 'Borne inf. (GNF)', 'Borne sup. (GNF)', 'Taux (%)', 'Base taxable (GNF)', 'Impôt tranche (GNF)'])
        for i, t in enumerate(r.get('detail_tranches', []), 1):
            writer.writerow([
                f'Tranche {i}',
                t['borne_inf'],
                t['borne_sup'] if t['borne_sup'] else 'Illimité',
                f"{t['taux']:.0f}",
                t['base_tranche'],
                t['impot_tranche'],
            ])

    return response


# ---------------------------------------------------------------------------
# Vues principales
# ---------------------------------------------------------------------------

@login_required
def simulation_comparative(request):
    """
    Simulation fiscale comparative multi-barèmes.
    - GET : affiche le formulaire vide avec la liste des barèmes disponibles.
    - POST (action=simuler) : calcule et affiche les résultats.
    - POST (action=sauvegarder) : calcule + sauvegarde en historique.
    - POST (action=csv) : calcule + télécharge le CSV.
    """
    entreprise   = request.user.entreprise
    employes     = Employe.objects.filter(
        entreprise=entreprise
    ).order_by('nom', 'prenoms')
    baremes_dispo = get_baremes_disponibles()

    resultats  = []
    form_data  = {}
    sauvegarde = False

    if request.method == 'POST':
        action         = request.POST.get('action', 'simuler')
        brut_raw       = request.POST.get('salaire_brut', '0')
        indemnites_raw = request.POST.get('total_indemnites', '0')
        employe_id     = request.POST.get('employe', '').strip()
        label_sim      = request.POST.get('label_simulation', '').strip()
        baremes_choisis = request.POST.getlist('baremes_choisis')

        brut       = _parse(brut_raw)
        indemnites = _parse(indemnites_raw)
        brut       = max(Decimal('0'), brut)
        indemnites = max(Decimal('0'), indemnites)

        nb_salaries = 0
        emp = None
        if employe_id:
            try:
                emp = Employe.objects.get(pk=int(employe_id), entreprise=entreprise)
                nb_salaries = Employe.objects.filter(
                    entreprise=entreprise, statut_employe='actif'
                ).count()
            except (Employe.DoesNotExist, ValueError):
                emp = None

        if not baremes_choisis:
            # Défaut : officiel de l'année courante + barème intégré
            annee_c = date.today().year
            baremes_choisis = [f'{annee_c}-officiel', 'fallback']

        resultats = simuler_multi_baremes(
            brut, indemnites, baremes_choisis,
            annee_ref=date.today().year,
            nb_salaries=nb_salaries,
        )

        # Calculer les deltas vs premier barème et le coût employeur
        if resultats:
            ref = resultats[0]
            for r in resultats:
                r['delta_net'] = r['net'] - ref['net']
                r['delta_rts'] = r['rts'] - ref['rts']
                r['cout_employeur'] = r['brut'] + r['total_charges_pat']

        form_data = {
            'salaire_brut':      brut_raw,
            'total_indemnites':  indemnites_raw,
            'employe_id':        employe_id,
            'label_simulation':  label_sim,
            'baremes_choisis':   baremes_choisis,
            'employe':           emp,
        }

        # Export CSV direct
        if action == 'csv' and resultats:
            return _export_csv_response(brut, indemnites, resultats)

        # Sauvegarder en historique
        if action == 'sauvegarder' and resultats:
            constantes = _charger_constantes()
            SimulationFiscale.objects.create(
                entreprise=entreprise,
                utilisateur=request.user,
                salaire_brut=brut,
                total_indemnites=indemnites,
                label=label_sim or f'Simulation du {date.today().strftime("%d/%m/%Y")}',
                baremes_compares=[r['bareme_label'] for r in resultats],
                parametres_json={
                    'baremes_ids': baremes_choisis,
                    'constantes': {k: str(v) for k, v in constantes.items()},
                },
                resultats_json=resultats,
            )
            sauvegarde = True
            messages.success(request, 'Simulation sauvegardée dans l\'historique.')

    return render(request, 'paie/simulation/comparative.html', {
        'employes':        employes,
        'baremes_dispo':   baremes_dispo,
        'resultats':       resultats,
        'form_data':       form_data,
        'sauvegarde':      sauvegarde,
        'annee_courante':  date.today().year,
    })


@login_required
def historique_simulations(request):
    """Liste paginée des simulations sauvegardées."""
    entreprise  = request.user.entreprise
    simulations = SimulationFiscale.objects.filter(
        entreprise=entreprise
    ).order_by('-date_simulation')

    paginator = Paginator(simulations, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'paie/simulation/historique.html', {
        'simulations': page_obj,
    })


@login_required
def detail_simulation(request, pk):
    """Affiche le détail complet d'une simulation sauvegardée."""
    simulation = get_object_or_404(
        SimulationFiscale, pk=pk, entreprise=request.user.entreprise
    )
    return render(request, 'paie/simulation/detail.html', {
        'simulation': simulation,
        'resultats':  simulation.resultats_json,
    })


@login_required
def supprimer_simulation(request, pk):
    """Supprime une simulation sauvegardée (POST requis)."""
    sim = get_object_or_404(
        SimulationFiscale, pk=pk, entreprise=request.user.entreprise
    )
    if request.method == 'POST':
        sim.delete()
        messages.success(request, 'Simulation supprimée.')
    return redirect('paie:historique_simulations')


@login_required
def export_simulation_csv(request, pk):
    """Télécharge le CSV d'une simulation historisée."""
    sim = get_object_or_404(
        SimulationFiscale, pk=pk, entreprise=request.user.entreprise
    )
    return _export_csv_response(
        sim.salaire_brut, sim.total_indemnites, sim.resultats_json
    )


@login_required
def api_baremes_disponibles(request):
    """API JSON : liste des barèmes disponibles (pour rechargement dynamique)."""
    return JsonResponse({'baremes': get_baremes_disponibles()})


# ---------------------------------------------------------------------------
# API : données employé (salaire du contrat + dernier bulletin)
# ---------------------------------------------------------------------------

@login_required
def api_employe_salaire(request, pk):
    """Retourne brut et indemnités d'un employé (contrat actif + dernier bulletin)."""
    entreprise = request.user.entreprise
    try:
        emp = Employe.objects.get(pk=pk, entreprise=entreprise)
    except Employe.DoesNotExist:
        return JsonResponse({'error': 'Employé introuvable'}, status=404)

    data = {'employe': f'{emp.nom} {emp.prenoms}', 'brut': 0, 'indemnites': 0, 'source': ''}

    # Dernier bulletin calculé/validé/payé
    dernier_bulletin = (
        BulletinPaie.objects
        .filter(employe=emp, statut_bulletin__in=['calcule', 'valide', 'paye'])
        .order_by('-annee_paie', '-mois_paie')
        .first()
    )
    if dernier_bulletin:
        data['brut'] = int(dernier_bulletin.salaire_brut)
        # Indemnités = brut - salaire_base (approximation)
        base = int(dernier_bulletin.salaire_base or 0)
        data['indemnites'] = max(0, data['brut'] - base)
        data['source'] = f'Bulletin {dernier_bulletin.mois_paie:02d}/{dernier_bulletin.annee_paie}'
    else:
        # Fallback : contrat actif
        contrat = (
            Contrat.objects
            .filter(employe=emp, statut='actif')
            .order_by('-date_debut')
            .first()
        )
        if contrat and contrat.salaire_base:
            data['brut'] = int(contrat.salaire_base)
            data['source'] = 'Contrat actif'

    return JsonResponse(data)


# ---------------------------------------------------------------------------
# API : optimiser le net
# ---------------------------------------------------------------------------

@login_required
@require_POST
def api_optimiser_net(request):
    """
    Trouve la répartition brut/indemnités optimale pour maximiser le net.
    Body JSON : {enveloppe, bareme_id?}
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        body = request.POST

    enveloppe = _parse(str(body.get('enveloppe', '0')))
    bareme_id = str(body.get('bareme_id', 'fallback')).strip()

    if enveloppe <= 0:
        return JsonResponse({'error': 'Enveloppe doit être > 0'}, status=400)
    if enveloppe > Decimal('999999999'):
        return JsonResponse({'error': 'Montant irréaliste'}, status=400)

    nb_salaries = Employe.objects.filter(
        entreprise=request.user.entreprise, statut_employe='actif'
    ).count()

    result = optimiser_net(enveloppe, bareme_id, nb_salaries=nb_salaries)
    return JsonResponse(result)


# ---------------------------------------------------------------------------
# API : simulation scénario augmentation
# ---------------------------------------------------------------------------

@login_required
@require_POST
def api_scenario_augmentation(request):
    """
    Simule l'impact d'une augmentation (%).
    Body JSON : {brut, indemnites, pourcentage, baremes_ids[]}
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        body = request.POST

    brut = _parse(str(body.get('brut', '0')))
    indemnites = _parse(str(body.get('indemnites', '0')))
    try:
        pourcentage = float(body.get('pourcentage', 10))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Pourcentage invalide'}, status=400)
    baremes_ids = body.get('baremes_ids', ['fallback'])
    if not isinstance(baremes_ids, list) or len(baremes_ids) > 5:
        return JsonResponse({'error': 'baremes_ids invalide (liste, max 5)'}, status=400)

    if brut <= 0:
        return JsonResponse({'error': 'Brut doit être > 0'}, status=400)
    if brut > Decimal('999999999'):
        return JsonResponse({'error': 'Montant irréaliste'}, status=400)
    if indemnites < 0:
        return JsonResponse({'error': 'Indemnités ne peuvent pas être négatives'}, status=400)
    if indemnites > brut:
        return JsonResponse({'error': 'Indemnités ne peuvent pas dépasser le brut'}, status=400)
    if not (-50 <= pourcentage <= 100):
        return JsonResponse({'error': 'Pourcentage doit être entre -50% et +100%'}, status=400)

    nb_salaries = Employe.objects.filter(
        entreprise=request.user.entreprise, statut_employe='actif'
    ).count()

    result = simuler_scenario_augmentation(
        brut, indemnites, pourcentage, baremes_ids, nb_salaries=nb_salaries
    )
    return JsonResponse(result)
