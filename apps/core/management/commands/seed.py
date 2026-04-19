"""
Commande : python manage.py seed
Remplit la base avec des données de démonstration réalistes pour Fastlane Logistic.
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.core.models import Parametres
from apps.flotte.models import Camion
from apps.rh.models import Employe, Attendance, HeureSup
from apps.operations.models import (
    Carburant, Panne, DepenseAdmin, TransportBauxite, BonTransport,
)
from apps.facturation.models import Contrat, Facture


class Command(BaseCommand):
    help = "Charge un jeu de données de démonstration pour Fastlane Logistic."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Vider les tables métier avant de semer.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write(self.style.WARNING("Vidage des tables…"))
            Facture.objects.all().delete()
            Contrat.objects.all().delete()
            BonTransport.objects.all().delete()
            TransportBauxite.objects.all().delete()
            DepenseAdmin.objects.all().delete()
            Panne.objects.all().delete()
            Carburant.objects.all().delete()
            HeureSup.objects.all().delete()
            Attendance.objects.all().delete()
            Employe.objects.all().delete()
            Camion.objects.all().delete()

        # Paramètres (singleton)
        p = Parametres.load()
        p.societe_nom = "Fastlane Logistic"
        p.save()
        self.stdout.write(self.style.SUCCESS(f"OK — Paramètres : {p.societe_nom}"))

        # Utilisateur admin si absent
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", password="admin", email="admin@fastlane.gn",
                role=User.Role.ADMIN, first_name="Admin", last_name="Fastlane",
            )
            self.stdout.write(self.style.SUCCESS("OK — Superuser admin / admin créé"))

        # Camions (8)
        camions_data = [
            ("CAM-01", "RC-1234-A", "SINOTRUK HOWO 371", 40, 2023, 650_000_000),
            ("CAM-02", "RC-1235-A", "SINOTRUK HOWO 371", 40, 2023, 650_000_000),
            ("CAM-03", "RC-1236-B", "SHACMAN F3000", 38, 2022, 620_000_000),
            ("CAM-04", "RC-1237-B", "SHACMAN F3000", 38, 2022, 620_000_000),
            ("CAM-05", "RC-1238-C", "MERCEDES ACTROS 4144", 45, 2024, 780_000_000),
            ("CAM-06", "RC-1239-C", "MERCEDES ACTROS 4144", 45, 2024, 780_000_000),
            ("CAM-07", "RC-1240-D", "SCANIA P410", 42, 2023, 720_000_000),
            ("CAM-08", "RC-1241-D", "VOLVO FMX 500", 44, 2024, 800_000_000),
        ]
        camions = []
        for code, imat, modele, cap, annee, prix in camions_data:
            c, _ = Camion.objects.update_or_create(
                code=code,
                defaults={
                    "immatriculation": imat, "marque_modele": modele,
                    "capacite_tonnes": Decimal(cap),
                    "date_acquisition": date(annee, 1, 15),
                    "prix_achat": Decimal(prix), "duree_amortissement": 5,
                    "statut": Camion.Statut.EN_SERVICE,
                },
            )
            camions.append(c)
        self.stdout.write(self.style.SUCCESS(f"OK — {len(camions)} camions"))

        # Employés
        employes_data = [
            ("EMP-001", "Mamadou",   "Diallo",    "CHAUFFEUR",   "+224 621 11 11 01", camions[0]),
            ("EMP-002", "Ibrahima",  "Bah",       "CHAUFFEUR",   "+224 621 11 11 02", camions[1]),
            ("EMP-003", "Alpha",     "Camara",    "CHAUFFEUR",   "+224 621 11 11 03", camions[2]),
            ("EMP-004", "Sekou",     "Sylla",     "CHAUFFEUR",   "+224 621 11 11 04", camions[3]),
            ("EMP-005", "Ousmane",   "Barry",     "CHAUFFEUR",   "+224 621 11 11 05", camions[4]),
            ("EMP-006", "Thierno",   "Sow",       "CHAUFFEUR",   "+224 621 11 11 06", camions[5]),
            ("EMP-007", "Moussa",    "Touré",     "CHAUFFEUR",   "+224 621 11 11 07", camions[6]),
            ("EMP-008", "Fodé",      "Condé",     "CHAUFFEUR",   "+224 621 11 11 08", camions[7]),
            ("EMP-009", "Lamine",    "Keïta",     "MECANICIEN",  "+224 622 22 22 01", None),
            ("EMP-010", "Bakary",    "Fofana",    "MECANICIEN",  "+224 622 22 22 02", None),
            ("EMP-011", "Ismaël",    "Traoré",    "PNEUMATICIEN","+224 622 22 22 03", None),
            ("EMP-012", "Kadiatou",  "Doumbouya", "ADMIN",       "+224 623 33 33 01", None),
            ("EMP-013", "Mariama",   "Soumah",    "ADMIN",       "+224 623 33 33 02", None),
            ("EMP-014", "Amadou",    "Cissé",     "SUPERVISEUR", "+224 624 44 44 01", None),
            ("EMP-015", "Saliou",    "Diakité",   "ELECTRICIEN", "+224 622 22 22 04", None),
            ("EMP-016", "Morlaye",   "Kaba",      "SOUDEUR",     "+224 622 22 22 05", None),
            ("EMP-017", "Abdoulaye", "Savané",    "AGENT",       "+224 624 44 44 02", None),
            ("EMP-018", "Ahmed",     "Bangoura",  "GARDIEN",     "+224 625 55 55 01", None),
        ]
        salaires = {
            "CHAUFFEUR": (150_000, 3_500_000, 400_000),
            "MECANICIEN": (120_000, 2_800_000, 200_000),
            "PNEUMATICIEN": (100_000, 2_400_000, 150_000),
            "ELECTRICIEN": (120_000, 2_800_000, 200_000),
            "SOUDEUR": (110_000, 2_600_000, 150_000),
            "SUPERVISEUR": (200_000, 5_000_000, 800_000),
            "AGENT": (90_000, 2_100_000, 100_000),
            "ADMIN": (110_000, 2_600_000, 200_000),
            "GARDIEN": (70_000, 1_700_000, 50_000),
        }
        employes = []
        for code, prenom, nom, fonction, tel, camion in employes_data:
            sj, sb, prime = salaires[fonction]
            e, _ = Employe.objects.update_or_create(
                code=code,
                defaults={
                    "prenom": prenom, "nom": nom, "fonction": fonction,
                    "telephone": tel, "site_prestation": "Sangarédi",
                    "camion": camion, "salaire_jour": Decimal(sj),
                    "salaire_base_mensuel": Decimal(sb),
                    "primes": Decimal(prime), "taux_charges": Decimal("0.18"),
                    "date_embauche": date(2023, 1, 10), "actif": True,
                },
            )
            employes.append(e)
        self.stdout.write(self.style.SUCCESS(f"OK — {len(employes)} employés"))

        # Date de référence : le mois courant
        today = date.today()
        mois = today.month
        annee = today.year
        random.seed(42)

        # Attendance pour chauffeurs + mécaniciens sur le mois courant
        import calendar
        nb_jours = calendar.monthrange(annee, mois)[1]
        staff = [e for e in employes if e.fonction in ("CHAUFFEUR", "MECANICIEN", "PNEUMATICIEN", "ELECTRICIEN", "SOUDEUR", "ADMIN", "SUPERVISEUR")]
        count_att = 0
        for e in staff:
            for d in range(1, min(nb_jours, today.day) + 1):
                dt = date(annee, mois, d)
                wd = dt.weekday()  # 0=Lun, 6=Dim
                # Logique : dimanche = D si chauffeur, sinon R; sinon P avec 10% d'absence
                if wd == 6:
                    code = "D" if e.fonction == "CHAUFFEUR" and random.random() < 0.4 else "R"
                else:
                    r = random.random()
                    if r < 0.05: code = "A"
                    elif r < 0.08: code = "M"
                    elif r < 0.1:  code = "C"
                    else: code = "P"
                Attendance.objects.update_or_create(
                    employe=e, date=dt, defaults={"code": code},
                )
                count_att += 1
        self.stdout.write(self.style.SUCCESS(f"OK — {count_att} pointages (attendance)"))

        # ---------------------------------------------------------------
        # CONTRATS MULTIPLES (CBG, SMB, GAC) — créés tôt pour être utilisés
        # plus bas lors de la création des voyages/bons/carburant.
        # ---------------------------------------------------------------
        contrats_data = [
            ("CTR-2026-CBG", "CBG",
             "Sangarédi → Port Kamsar",
             "TONNE", 85_000, date(2026, 1, 1),
             "Contrat annuel transport bauxite vers port de Kamsar"),
            ("CTR-2026-SMB", "SMB",
             "Boké → Port Dapilon",
             "TONNE", 78_000, date(2026, 1, 1),
             "Contrat transport bauxite SMB-Winning, route Dapilon"),
            ("CTR-2026-GAC", "GAC",
             "Sangarédi → Kamsar",
             "TONNE", 82_000, date(2026, 2, 1),
             "Contrat Guinea Alumina Corporation"),
        ]
        contrats = {}
        for code, client, _trajet, type_fac, tarif, debut, obs in contrats_data:
            c, _ = Contrat.objects.update_or_create(
                code=code,
                defaults={
                    "client": client, "type_facturation": type_fac,
                    "tarif": Decimal(tarif), "date_debut": debut,
                    "actif": True, "observations": obs,
                },
            )
            contrats[client] = c
        self.stdout.write(self.style.SUCCESS(f"OK — {len(contrats)} contrats ({', '.join(contrats)})"))

        # Répartition des camions par contrat (non exclusif, rotation possible)
        camion_contrat = {
            camions[0]: contrats["CBG"], camions[1]: contrats["CBG"],
            camions[2]: contrats["CBG"], camions[3]: contrats["SMB"],
            camions[4]: contrats["SMB"], camions[5]: contrats["SMB"],
            camions[6]: contrats["GAC"], camions[7]: contrats["GAC"],
        }

        # Carburant : 2 prises / camion / mois
        # — 70% des prises imputées au contrat du camion ; 30% laissées sans contrat
        #   pour tester la répartition au prorata.
        count_carb = 0
        for c in camions:
            km_depart = random.randint(50_000, 200_000)
            for i in range(2):
                d_carb = date(annee, mois, random.randint(1, min(nb_jours, today.day)))
                km_av = km_depart + i * random.randint(800, 1500)
                km_tb = km_av + random.randint(600, 1200)
                l_av = Decimal(random.randint(20, 80))
                l_ap = l_av + Decimal(random.randint(250, 400))
                chauffeur = c.chauffeurs.first()
                contrat_car = camion_contrat.get(c) if random.random() < 0.7 else None
                Carburant.objects.create(
                    date=d_carb, heure=time(random.randint(6, 17), random.choice([0, 15, 30, 45])),
                    camion=c, chauffeur=chauffeur, contrat=contrat_car,
                    km_avant=km_av, km_tableau_bord=km_tb,
                    litres_avant=l_av, litres_apres=l_ap,
                    prix_unitaire=Decimal("12000"),
                    station="Station Total — Sangarédi",
                )
                count_carb += 1
        self.stdout.write(self.style.SUCCESS(f"OK — {count_carb} prises de carburant"))

        # Pannes
        pannes_data = [
            (camions[0], "PNEUS", "Pneu AV gauche", 2_500_000, 300_000, 1),
            (camions[1], "MOTEUR", "Filtre à huile + huile moteur", 800_000, 400_000, 0),
            (camions[2], "FREINAGE", "Plaquettes de frein AV", 1_200_000, 500_000, 1),
            (camions[3], "PNEUS", "Pneu AR droit", 2_500_000, 300_000, 1),
            (camions[0], "TRANSMISSION", "Huile boîte", 600_000, 400_000, 0),
            (camions[4], "SUSPENSION", "Amortisseur AV", 1_800_000, 600_000, 2),
            (camions[5], "ELECTRICITE", "Alternateur", 2_200_000, 700_000, 1),
            (camions[6], "PNEUS", "Pneu AV droit", 2_500_000, 300_000, 1),
            (camions[7], "HYDRAULIQUE", "Vérin de benne", 3_500_000, 800_000, 3),
            (camions[2], "CARROSSERIE", "Redressage aile AV", 500_000, 600_000, 2),
        ]
        for c, type_p, piece, cp, cmo, jours in pannes_data:
            # 60% des pannes imputées au contrat du camion ; 40% sans (prorata)
            contrat_pan = camion_contrat.get(c) if random.random() < 0.6 else None
            Panne.objects.create(
                date=date(annee, mois, random.randint(1, min(nb_jours, today.day))),
                camion=c, contrat=contrat_pan, type_panne=type_p,
                piece_remplacee=piece, fournisseur="Garage Sidibé",
                cout_pieces=Decimal(cp), cout_main_oeuvre=Decimal(cmo),
                duree_immobilisation=jours,
            )
        self.stdout.write(self.style.SUCCESS(f"OK — {len(pannes_data)} pannes"))

        # Dépenses admin : certaines imputées à un contrat spécifique, d'autres
        # laissées sans contrat (seront réparties au prorata).
        dep_data = [
            # (type, description, montant, statut, client_contrat_ou_None)
            ("IMMAT",   "Immatriculation annuelle",     2_500_000, "PAYE",   None),
            ("ASSU",    "Assurance RC flotte",          15_000_000, "PAYE",  None),
            ("VT",      "Visite technique — 8 camions",  1_600_000, "PAYE",  None),
            ("TAXE",    "Taxe transport minier CBG",     3_000_000, "ATTENTE", "CBG"),
            ("TAXE",    "Taxe transport minier SMB",     2_000_000, "ATTENTE", "SMB"),
            ("LICENCE", "Licence exploitation",          3_500_000, "PAYE",   None),
            ("BANQUE",  "Frais bancaires mensuels",        450_000, "PAYE",   None),
            ("AUTRE",   "Contrôle qualité GAC",          1_200_000, "PAYE",   "GAC"),
        ]
        for type_d, desc, mont, stat, client in dep_data:
            DepenseAdmin.objects.create(
                date=date(annee, mois, random.randint(1, min(nb_jours, today.day))),
                type_depense=type_d, description=desc,
                contrat=contrats.get(client) if client else None,
                montant=Decimal(mont), statut=stat,
            )
        self.stdout.write(self.style.SUCCESS(f"OK — {len(dep_data)} dépenses administratives"))

        # Transport bauxite : 4 voyages par camion, tous reliés au contrat du camion
        trajets_par_client = {
            "CBG": ("Sangarédi → Port Kamsar", Decimal("98")),
            "SMB": ("Boké → Port Dapilon", Decimal("72")),
            "GAC": ("Sangarédi → Kamsar", Decimal("95")),
        }
        count_tr = 0
        for c in camions:
            ch = c.chauffeurs.first()
            contrat_tr = camion_contrat[c]
            trajet, distance = trajets_par_client[contrat_tr.client]
            for _ in range(4):
                d_tr = date(annee, mois, random.randint(1, min(nb_jours, today.day)))
                tonnage = Decimal(random.randint(35, int(c.capacite_tonnes)))
                TransportBauxite.objects.create(
                    date=d_tr, camion=c, chauffeur=ch, contrat=contrat_tr,
                    trajet=trajet, distance_km=distance, tonnage=tonnage,
                    tarif_unitaire=contrat_tr.tarif, client=contrat_tr.client,
                )
                count_tr += 1
        self.stdout.write(self.style.SUCCESS(f"OK — {count_tr} voyages bauxite (répartis sur {len(contrats)} contrats)"))

        # Bons de transport : 3 par chauffeur
        chauffeurs = [e for e in employes if e.fonction == "CHAUFFEUR"]
        count_bon = 0
        for ch in chauffeurs:
            for _ in range(3):
                d_bon = date(annee, mois, random.randint(1, min(nb_jours, today.day)))
                h_dep = time(random.randint(6, 10), random.choice([0, 15, 30, 45]))
                h_start = time(random.randint(11, 13), random.choice([0, 15, 30]))
                h_end = time(h_start.hour, h_start.minute + 15 if h_start.minute < 45 else 0)
                contrat_bon = camion_contrat.get(ch.camion)
                BonTransport.objects.create(
                    date=d_bon, prenom=ch.prenom, nom=ch.nom,
                    telephone=ch.telephone, plaque=ch.camion.immatriculation,
                    carte_entree=f"CE-{random.randint(1000, 9999)}",
                    lieu_chargement="Trémie 3 — Sangarédi",
                    heure_depart=h_dep, heure_pesee_start=h_start, heure_pesee_end=h_end,
                    quantite=Decimal(random.randint(35, 45)),
                    camion=ch.camion, chauffeur=ch, contrat=contrat_bon,
                )
                count_bon += 1
        self.stdout.write(self.style.SUCCESS(f"OK — {count_bon} bons de transport"))

        # Heures supplémentaires : 5 entrées
        for _ in range(5):
            e = random.choice(staff)
            d_hs = date(annee, mois, random.randint(1, min(nb_jours, today.day)))
            HeureSup.objects.create(
                employe=e, date=d_hs,
                heure_debut=time(18, 0), heure_fin=time(22, 0),
                type_hs=random.choice(["OUVRE", "NUIT", "DIMANCHE"]),
                majoration=Decimal("0.25"), motif="Rotation supplémentaire",
                valide_par="Amadou Cissé",
            )
        self.stdout.write(self.style.SUCCESS(f"OK — 5 heures supplémentaires"))

        # Factures mensuelles : une par contrat actif via le service intelligent
        resultats = Facture.generer_pour_periode(mois, annee, force=True)
        total_ttc = sum((f.montant_ttc for f, _ in resultats), Decimal(0))
        self.stdout.write(self.style.SUCCESS(
            f"OK — {len(resultats)} facture(s) générée(s) pour {mois:02d}/{annee} "
            f"— Total : {total_ttc:,.0f} GNF TTC"
        ))
        for f, created in resultats:
            tag = "créée" if created else "maj"
            self.stdout.write(
                f"   · {f.numero} — {f.contrat.client} ({tag}) — {f.montant_ttc:,.0f} GNF TTC "
                f"[{f.nb_rotations} voyages / {f.tonnage_total:,.1f} T]"
            )

        self.stdout.write(self.style.SUCCESS("\n=== Seed terminé avec succès ==="))
        self.stdout.write(self.style.WARNING("Identifiants : admin / admin"))
        self.stdout.write(self.style.HTTP_INFO(
            "-> /projets/ et /bilan-entreprise/ pour la vue consolidee multi-contrats"
        ))
