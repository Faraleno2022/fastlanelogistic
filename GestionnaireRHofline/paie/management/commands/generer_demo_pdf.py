"""
Commande de management : generer_demo_pdf
Génère un PDF de présentation commerciale de GuineeRH avec ReportLab.
Autonome : ne nécessite pas la base de données.
Sauvegardé dans : BASE_DIR/demo/GuineeRH_Demo_Commercial.pdf
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from decimal import Decimal


# Palette couleurs
BLEU = (0.10, 0.32, 0.40)        # #1a5276
BLEU_CLAIR = (0.21, 0.47, 0.57)
ORANGE = (0.95, 0.61, 0.07)       # #f39c12
GRIS_FOND = (0.96, 0.96, 0.96)
GRIS_LIGNE = (0.85, 0.85, 0.85)
BLANC = (1, 1, 1)
NOIR = (0.10, 0.10, 0.10)
VERT = (0.07, 0.53, 0.26)


EMPLOYES_DEMO = [
    {
        'nom': 'CAMARA Alpha Oumar',
        'poste': 'Directeur Général',
        'brut': 10_850_000,
        'cnss': 467_500,
        'rts': 1_107_625,
        'net': 9_274_875,
    },
    {
        'nom': 'DIALLO Fatoumata',
        'poste': 'Responsable RH Senior',
        'brut': 4_170_000,
        'cnss': 176_000,
        'rts': 220_200,
        'net': 3_773_800,
    },
    {
        'nom': 'BALDE Mamadou Cellou',
        'poste': 'Chargé Commercial',
        'brut': 3_450_000,
        'cnss': 160_000,
        'rts': 129_500,
        'net': 3_160_500,
    },
    {
        'nom': 'KOUROUMA Sekou',
        'poste': 'Technicien Réseaux',
        'brut': 2_450_000,
        'cnss': 112_500,
        'rts': 59_250,
        'net': 2_278_250,
    },
    {
        'nom': 'SOUMAH Aminata',
        'poste': 'Stagiaire',
        'brut': 800_000,
        'cnss': 35_000,
        'rts': 0,
        'net': 765_000,
    },
]

FONCTIONNALITES = [
    ('Paie & Bulletins', [
        'Calcul automatique CNSS & RTS',
        'Bulletins PDF multi-modèles',
        'Gestion des rubriques personnalisées',
        'Historique & cumuls annuels',
    ]),
    ('Gestion RH', [
        'Dossiers employés complets',
        'Contrats & avenants',
        'Suivi des congés payés',
        'Alertes échéances contrats',
    ]),
    ('Temps de Travail', [
        'Pointage & heures supplémentaires',
        'Calcul automatique HS 30% / 60%',
        'Primes de nuit & jours fériés',
        'Exports Excel & PDF',
    ]),
    ('Déclarations Légales', [
        'Télédéclaration CNSS (format officiel)',
        'Déclarations fiscales RTS/VF/TA',
        'Rapports Inspection du Travail',
        'Registre du personnel',
    ]),
    ('Sécurité & Multi-entreprise', [
        'Accès multi-utilisateurs sécurisé',
        'Gestion des droits par module',
        'Sauvegarde automatique locale',
        'Fonctionnement 100% hors ligne',
    ]),
    ('Support & Conformité', [
        'Conforme Code du Travail Guinéen',
        'Barème RTS & CNSS actualisé 2026',
        'Support technique local (Conakry)',
        'Mises à jour régulières gratuites',
    ]),
]


def _fmt(montant):
    """Formate un montant en GNF avec séparateurs de milliers."""
    return f"{montant:,.0f} GNF".replace(',', ' ')


class Command(BaseCommand):
    help = 'Génère le PDF de présentation commerciale GuineeRH'

    def handle(self, *args, **options):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                HRFlowable, PageBreak
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        except ImportError:
            self.stderr.write(self.style.ERROR(
                'ReportLab non installe. Lancez: pip install reportlab'
            ))
            return

        # Dossier de destination
        demo_dir = Path(settings.BASE_DIR) / 'demo'
        demo_dir.mkdir(exist_ok=True)
        output_path = demo_dir / 'GuineeRH_Demo_Commercial.pdf'

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title='GuineeRH — Démonstration Commerciale',
            author='GuineeRH',
            subject='Logiciel de Gestion RH & Paie Guinée',
        )

        rl_bleu = colors.Color(*BLEU)
        rl_bleu_clair = colors.Color(*BLEU_CLAIR)
        rl_orange = colors.Color(*ORANGE)
        rl_gris = colors.Color(*GRIS_FOND)
        rl_gris_ligne = colors.Color(*GRIS_LIGNE)
        rl_blanc = colors.white
        rl_vert = colors.Color(*VERT)

        styles = getSampleStyleSheet()

        def style(name, **kwargs):
            base = kwargs.pop('parent', 'Normal')
            return ParagraphStyle(name=name, parent=styles[base], **kwargs)

        # Styles personnalisés
        s_titre_couv = style('TitreCouv', fontSize=38, textColor=rl_blanc,
                             alignment=TA_CENTER, spaceAfter=6, leading=44,
                             fontName='Helvetica-Bold')
        s_sous_titre_couv = style('SousTitreCouv', fontSize=16, textColor=rl_orange,
                                  alignment=TA_CENTER, spaceAfter=4, leading=20,
                                  fontName='Helvetica-Bold')
        s_tagline = style('Tagline', fontSize=12, textColor=rl_blanc,
                          alignment=TA_CENTER, spaceAfter=4, leading=16,
                          fontName='Helvetica')
        s_titre_page = style('TitrePage', fontSize=18, textColor=rl_bleu,
                             spaceAfter=8, spaceBefore=4, leading=22,
                             fontName='Helvetica-Bold')
        s_corps = style('Corps', fontSize=9, textColor=colors.Color(*NOIR),
                        spaceAfter=4, leading=13)
        s_entete_table = style('EnteteTable', fontSize=9, textColor=rl_blanc,
                               alignment=TA_CENTER, fontName='Helvetica-Bold')
        s_cell = style('Cell', fontSize=8.5, textColor=colors.Color(*NOIR),
                       alignment=TA_LEFT)
        s_cell_right = style('CellRight', fontSize=8.5, textColor=colors.Color(*NOIR),
                              alignment=TA_RIGHT)
        s_cell_center = style('CellCenter', fontSize=8.5, textColor=colors.Color(*NOIR),
                               alignment=TA_CENTER)
        s_footer = style('Footer', fontSize=7.5, textColor=colors.grey,
                         alignment=TA_CENTER)
        s_label_bl = style('LabelBL', fontSize=8, textColor=colors.grey,
                           fontName='Helvetica')
        s_val_bl = style('ValBL', fontSize=9, textColor=colors.Color(*NOIR),
                         fontName='Helvetica-Bold')
        s_fonct_titre = style('FonctTitre', fontSize=10, textColor=rl_bleu,
                              fontName='Helvetica-Bold', spaceBefore=4, spaceAfter=2)
        s_fonct_item = style('FonctItem', fontSize=8.5, textColor=colors.Color(*NOIR),
                             leftIndent=10, spaceAfter=1, leading=12)

        story = []
        W, H = A4
        inner_w = W - 3 * cm  # largeur utile

        # ==============================================================
        # PAGE 1 : COUVERTURE
        # ==============================================================
        # Bloc fond bleu simulé avec tableau unique
        titre_data = [
            [Paragraph('GuineeRH', s_titre_couv)],
            [Paragraph('Logiciel de Gestion RH &amp; Paie', s_sous_titre_couv)],
            [Spacer(1, 0.3 * cm)],
            [Paragraph('Solution RH complète conforme au Code du Travail Guinéen', s_tagline)],
            [Spacer(1, 0.2 * cm)],
            [Paragraph('Paie · CNSS · Congés · Déclarations · Rapports', s_tagline)],
        ]
        t_couv = Table(titre_data, colWidths=[inner_w])
        t_couv.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_bleu),
            ('TOPPADDING', (0, 0), (-1, 0), 40),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 40),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 0, rl_bleu),
        ]))
        story.append(Spacer(1, 2 * cm))
        story.append(t_couv)
        story.append(Spacer(1, 1 * cm))

        # Bandeau orange
        bandeau_data = [[Paragraph('Démonstration Commerciale — Mars 2026', style(
            'Bandeau', fontSize=11, textColor=rl_blanc, alignment=TA_CENTER,
            fontName='Helvetica-Bold'))]]
        t_bandeau = Table(bandeau_data, colWidths=[inner_w])
        t_bandeau.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_orange),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_bandeau)
        story.append(Spacer(1, 1.5 * cm))

        # Infos démo
        info_data = [
            [Paragraph('<b>Entreprise de démonstration :</b> SOGUIPHONE SARL', s_corps)],
            [Paragraph('<b>Secteur :</b> Télécommunications &nbsp;|&nbsp; '
                       '<b>Ville :</b> Conakry &nbsp;|&nbsp; '
                       '<b>Effectif :</b> 5 employés (démo)', s_corps)],
            [Spacer(1, 0.3 * cm)],
            [Paragraph(
                'Ce document présente les capacités de <b>GuineeRH</b> : calcul automatique '
                'de la paie, bulletins PDF conformes, déclarations CNSS/RTS et gestion '
                'complète des ressources humaines pour les entreprises en Guinée.',
                s_corps)],
        ]
        t_info = Table(info_data, colWidths=[inner_w])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_gris),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 0.5, rl_gris_ligne),
        ]))
        story.append(t_info)

        # Contact
        story.append(Spacer(1, 4 * cm))
        contact_data = [[
            Paragraph('www.guineerh.space', style('Contact', fontSize=10,
                      textColor=rl_bleu, alignment=TA_CENTER, fontName='Helvetica-Bold')),
            Paragraph('+224 XXX XXX XXX', style('Contact2', fontSize=10,
                      textColor=colors.Color(*NOIR), alignment=TA_CENTER)),
            Paragraph('contact@guineerh.space', style('Contact3', fontSize=10,
                      textColor=rl_bleu, alignment=TA_CENTER)),
        ]]
        t_contact = Table(contact_data, colWidths=[inner_w / 3] * 3)
        t_contact.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, 0), (-1, 0), 1, rl_orange),
        ]))
        story.append(t_contact)

        story.append(PageBreak())

        # ==============================================================
        # PAGE 2 : TABLEAU COMPARATIF DES BULLETINS
        # ==============================================================
        story.append(Paragraph('Tableau Comparatif des Bulletins de Paie', s_titre_page))
        story.append(Paragraph(
            'Période : <b>Mars 2026</b> &nbsp;|&nbsp; '
            'Entreprise : <b>SOGUIPHONE SARL</b> &nbsp;|&nbsp; '
            'Devise : <b>GNF (Franc Guinéen)</b>',
            s_corps))
        story.append(Spacer(1, 0.5 * cm))

        # En-têtes tableau
        entetes = [
            Paragraph('Employé', s_entete_table),
            Paragraph('Poste', s_entete_table),
            Paragraph('Salaire Brut', s_entete_table),
            Paragraph('CNSS (5%)', s_entete_table),
            Paragraph('RTS', s_entete_table),
            Paragraph('Net à Payer', s_entete_table),
        ]
        rows = [entetes]
        for i, emp in enumerate(EMPLOYES_DEMO):
            bg = rl_gris if i % 2 == 0 else rl_blanc
            row = [
                Paragraph(emp['nom'], s_cell),
                Paragraph(emp['poste'], s_cell),
                Paragraph(_fmt(emp['brut']), s_cell_right),
                Paragraph(_fmt(emp['cnss']), s_cell_right),
                Paragraph(_fmt(emp['rts']) if emp['rts'] > 0 else '—', s_cell_right),
                Paragraph(_fmt(emp['net']), style(
                    'NetBold', fontSize=8.5, textColor=rl_vert,
                    alignment=1, fontName='Helvetica-Bold')),
            ]
            rows.append(row)

        # Ligne totaux
        total_brut = sum(e['brut'] for e in EMPLOYES_DEMO)
        total_cnss = sum(e['cnss'] for e in EMPLOYES_DEMO)
        total_rts = sum(e['rts'] for e in EMPLOYES_DEMO)
        total_net = sum(e['net'] for e in EMPLOYES_DEMO)
        rows.append([
            Paragraph('<b>TOTAL</b>', style('TotalCell', fontSize=9, textColor=rl_blanc,
                                            fontName='Helvetica-Bold')),
            Paragraph('', s_cell),
            Paragraph(_fmt(total_brut), style('TotalRight', fontSize=9, textColor=rl_blanc,
                                              alignment=1, fontName='Helvetica-Bold')),
            Paragraph(_fmt(total_cnss), style('TotalRight2', fontSize=9, textColor=rl_blanc,
                                               alignment=1, fontName='Helvetica-Bold')),
            Paragraph(_fmt(total_rts), style('TotalRight3', fontSize=9, textColor=rl_blanc,
                                              alignment=1, fontName='Helvetica-Bold')),
            Paragraph(_fmt(total_net), style('TotalNet', fontSize=9, textColor=rl_orange,
                                             alignment=1, fontName='Helvetica-Bold')),
        ])

        col_w = [4.5 * cm, 3.8 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 3 * cm]
        t_bulletins = Table(rows, colWidths=col_w, repeatRows=1)
        t_bulletins.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), rl_bleu),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_blanc),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Lignes alternées
            ('BACKGROUND', (0, 1), (-1, 1), rl_gris),
            ('BACKGROUND', (0, 3), (-1, 3), rl_gris),
            ('BACKGROUND', (0, 5), (-1, 5), rl_gris),
            # Ligne totaux
            ('BACKGROUND', (0, 6), (-1, 6), rl_bleu_clair),
            ('TOPPADDING', (0, 1), (-1, -2), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 5),
            ('TOPPADDING', (0, -1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.3, rl_gris_ligne),
            ('LINEBELOW', (0, 0), (-1, 0), 2, rl_orange),
        ]))
        story.append(t_bulletins)

        story.append(Spacer(1, 0.8 * cm))
        story.append(Paragraph(
            '<b>Note :</b> CNSS employé = 5% de la base cotisable. '
            'RTS calculé selon le barème progressif Guinée en vigueur. '
            'Charges patronales CNSS 18% + VF 6% + TA 2% non incluses dans ce tableau.',
            style('Note', fontSize=7.5, textColor=colors.grey, leading=10)
        ))

        story.append(PageBreak())

        # ==============================================================
        # PAGE 3 : BULLETIN COMPLET DU DIRECTEUR
        # ==============================================================
        dg = EMPLOYES_DEMO[0]
        story.append(Paragraph('Exemple de Bulletin de Paie Complet', s_titre_page))
        story.append(Paragraph(
            'Modèle standard GuineeRH — Directeur Général — Mars 2026',
            s_corps))
        story.append(Spacer(1, 0.3 * cm))

        # En-tête du bulletin
        entete_bl = [
            [
                Paragraph('<b>SOGUIPHONE SARL</b>', style('EntBL', fontSize=10,
                          textColor=rl_blanc, fontName='Helvetica-Bold')),
                Paragraph('<b>BULLETIN DE PAIE</b>', style('TitreBL', fontSize=13,
                          textColor=rl_orange, alignment=TA_CENTER,
                          fontName='Helvetica-Bold')),
                Paragraph('<b>N° BP-DEMO-2026-03-001</b>', style('NumBL', fontSize=8.5,
                          textColor=rl_blanc, alignment=TA_RIGHT)),
            ],
            [
                Paragraph('Commune de Kaloum, Conakry\nNIF : NIF-DEMO-001\nCNSS : CNSS-DEMO-001',
                          style('AdrBL', fontSize=7.5, textColor=colors.lightgrey, leading=11)),
                Paragraph('Période : <b>Mars 2026</b> (22 jours)',
                          style('PerBL', fontSize=9, textColor=rl_blanc, alignment=TA_CENTER)),
                Paragraph('Date paiement :<br/><b>28 Mars 2026</b>',
                          style('DateBL', fontSize=8.5, textColor=rl_blanc, alignment=TA_RIGHT)),
            ],
        ]
        t_entete_bl = Table(entete_bl, colWidths=[6 * cm, 6 * cm, 7.3 * cm])
        t_entete_bl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_bleu),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('SPAN', (1, 0), (1, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_entete_bl)

        # Infos employé
        emp_info = [
            [
                Paragraph('Employé :', s_label_bl),
                Paragraph('<b>CAMARA Alpha Oumar</b>', s_val_bl),
                Paragraph('Matricule :', s_label_bl),
                Paragraph('<b>SGPH-001</b>', s_val_bl),
            ],
            [
                Paragraph('Poste :', s_label_bl),
                Paragraph('Directeur Général', s_val_bl),
                Paragraph('Type contrat :', s_label_bl),
                Paragraph('CDI', s_val_bl),
            ],
            [
                Paragraph('Service :', s_label_bl),
                Paragraph('Direction Générale', s_val_bl),
                Paragraph('Embauche :', s_label_bl),
                Paragraph('15/01/2010', s_val_bl),
            ],
            [
                Paragraph('Mode paiement :', s_label_bl),
                Paragraph('Virement — Ecobank Guinée', s_val_bl),
                Paragraph('Situation :', s_label_bl),
                Paragraph('Marié, 3 enfants', s_val_bl),
            ],
        ]
        t_emp = Table(emp_info, colWidths=[2.5 * cm, 5.5 * cm, 2.5 * cm, 8.8 * cm])
        t_emp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_gris),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.3, rl_gris_ligne),
            ('LINEBELOW', (0, 0), (-1, 0), 0.3, rl_gris_ligne),
            ('LINEBELOW', (0, 1), (-1, 1), 0.3, rl_gris_ligne),
            ('LINEBELOW', (0, 2), (-1, 2), 0.3, rl_gris_ligne),
        ]))
        story.append(t_emp)
        story.append(Spacer(1, 0.3 * cm))

        # Tableau des rubriques
        rub_entetes = [
            Paragraph('Code', s_entete_table),
            Paragraph('Désignation', s_entete_table),
            Paragraph('Base', s_entete_table),
            Paragraph('Taux', s_entete_table),
            Paragraph('Gain', s_entete_table),
            Paragraph('Retenue', s_entete_table),
        ]
        rubriques_rows = [rub_entetes]
        lignes_bulletin_dg = [
            ('SAL-BASE', 'Salaire de Base', '8 500 000', '', '8 500 000', ''),
            ('IND-TRANS', 'Indemnité de Transport', '—', '', '500 000', ''),
            ('IND-LOG', 'Indemnité de Logement', '—', '', '1 000 000', ''),
            ('PRIME-PERF', 'Prime de Performance (10%)', '8 500 000', '10%', '850 000', ''),
            ('CNSS-SAL', 'Cotisation CNSS Salarié', '9 350 000', '5%', '', '467 500'),
            ('RTS', 'Retenue à la Source (RTS)', '9 382 500', 'Barème', '', '1 107 625'),
        ]
        for i, (code, libelle, base, taux_r, gain, retenue) in enumerate(lignes_bulletin_dg):
            bg = rl_gris if i % 2 == 0 else rl_blanc
            rubriques_rows.append([
                Paragraph(code, s_cell_center),
                Paragraph(libelle, s_cell),
                Paragraph(base, s_cell_right),
                Paragraph(taux_r, s_cell_center),
                Paragraph(gain, style('Gain', fontSize=8.5, textColor=rl_vert,
                                      alignment=1)) if gain else Paragraph('', s_cell),
                Paragraph(retenue, style('Retenue', fontSize=8.5,
                                         textColor=colors.red, alignment=1)) if retenue else Paragraph('', s_cell),
            ])

        t_rub = Table(rubriques_rows, colWidths=[2 * cm, 5.5 * cm, 2.8 * cm, 1.5 * cm, 2.8 * cm, 2.7 * cm])
        t_rub.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_bleu_clair),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, 1), rl_gris),
            ('BACKGROUND', (0, 3), (-1, 3), rl_gris),
            ('BACKGROUND', (0, 5), (-1, 5), rl_gris),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.3, rl_gris_ligne),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, rl_orange),
        ]))
        story.append(t_rub)
        story.append(Spacer(1, 0.3 * cm))

        # Récapitulatif
        recap_data = [
            [
                Paragraph('<b>Salaire Brut</b>', style('RecapLbl', fontSize=9.5,
                          textColor=rl_blanc, fontName='Helvetica-Bold')),
                Paragraph('<b>10 850 000 GNF</b>', style('RecapVal', fontSize=9.5,
                          textColor=rl_blanc, alignment=TA_RIGHT,
                          fontName='Helvetica-Bold')),
                Paragraph('<b>Cotisations Salariales</b>', style('RecapLbl2', fontSize=9.5,
                          textColor=rl_blanc, fontName='Helvetica-Bold')),
                Paragraph('<b>— 1 575 125 GNF</b>', style('RecapVal2', fontSize=9.5,
                          textColor=rl_orange, alignment=TA_RIGHT,
                          fontName='Helvetica-Bold')),
                Paragraph('<b>NET À PAYER</b>', style('RecapNet', fontSize=10,
                          textColor=rl_orange, fontName='Helvetica-Bold')),
                Paragraph('<b>9 274 875 GNF</b>', style('RecapNetVal', fontSize=10,
                          textColor=rl_orange, alignment=TA_RIGHT,
                          fontName='Helvetica-Bold')),
            ]
        ]
        t_recap = Table(recap_data, colWidths=[3 * cm, 3 * cm, 3.5 * cm, 3.5 * cm, 2.8 * cm, 3.5 * cm])
        t_recap.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_bleu),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('LINEBEFORE', (2, 0), (2, -1), 0.5, rl_bleu_clair),
            ('LINEBEFORE', (4, 0), (4, -1), 0.5, rl_orange),
        ]))
        story.append(t_recap)

        # Charges patronales
        story.append(Spacer(1, 0.3 * cm))
        charges_data = [
            [
                Paragraph('CNSS Employeur (18%) :', s_label_bl),
                Paragraph('1 683 000 GNF', s_val_bl),
                Paragraph('Versement Forfaitaire (6%) :', s_label_bl),
                Paragraph('651 000 GNF', s_val_bl),
                Paragraph('Taxe Apprentissage (2%) :', s_label_bl),
                Paragraph('217 000 GNF', s_val_bl),
            ]
        ]
        t_charges = Table(charges_data, colWidths=[3.5 * cm, 2.5 * cm, 3.8 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm])
        t_charges.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_gris),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 0.3, rl_gris_ligne),
        ]))
        story.append(t_charges)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            'Coût employeur total estimé : <b>12 750 875 GNF</b> | '
            'Ce bulletin a été généré automatiquement par <b>GuineeRH</b>.',
            style('BLFooter', fontSize=7.5, textColor=colors.grey,
                  alignment=TA_CENTER, leading=10)
        ))

        story.append(PageBreak())

        # ==============================================================
        # PAGE 4 : FONCTIONNALITÉS CLÉS
        # ==============================================================
        story.append(Paragraph('Fonctionnalités Clés de GuineeRH', s_titre_page))
        story.append(Paragraph(
            'Une solution complète, conforme au droit du travail guinéen, '
            'fonctionnant 100% hors ligne.',
            s_corps))
        story.append(Spacer(1, 0.5 * cm))

        # Tableau 2 colonnes de fonctionnalités
        fonct_col1 = FONCTIONNALITES[:3]
        fonct_col2 = FONCTIONNALITES[3:]

        def build_fonct_cell(modules):
            items = []
            for titre, pts in modules:
                items.append(Paragraph(titre, s_fonct_titre))
                for pt in pts:
                    items.append(Paragraph(f'• {pt}', s_fonct_item))
                items.append(Spacer(1, 0.2 * cm))
            return items

        fonct_data = [[build_fonct_cell(fonct_col1), build_fonct_cell(fonct_col2)]]
        t_fonct = Table(fonct_data, colWidths=[inner_w / 2, inner_w / 2])
        t_fonct.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (0, -1), 0.3, rl_gris_ligne),
            ('BOX', (1, 0), (1, -1), 0.3, rl_gris_ligne),
            ('BACKGROUND', (0, 0), (-1, -1), rl_gris),
            ('LINEABOVE', (0, 0), (-1, 0), 3, rl_bleu),
        ]))
        story.append(t_fonct)
        story.append(Spacer(1, 0.8 * cm))

        # CTA final
        cta_data = [[
            Paragraph(
                'Contactez-nous pour une démonstration personnalisée dans vos locaux',
                style('CTA', fontSize=11, textColor=rl_blanc, alignment=TA_CENTER,
                      fontName='Helvetica-Bold')),
        ]]
        t_cta = Table(cta_data, colWidths=[inner_w])
        t_cta.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), rl_orange),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_cta)
        story.append(Spacer(1, 0.4 * cm))

        contact2_data = [[
            Paragraph('www.guineerh.space', style('Cta1', fontSize=10, textColor=rl_bleu,
                      alignment=TA_CENTER, fontName='Helvetica-Bold')),
            Paragraph('+224 XXX XXX XXX', style('Cta2', fontSize=10,
                      textColor=colors.Color(*NOIR), alignment=TA_CENTER)),
            Paragraph('contact@guineerh.space', style('Cta3', fontSize=10, textColor=rl_bleu,
                      alignment=TA_CENTER)),
        ]]
        t_contact2 = Table(contact2_data, colWidths=[inner_w / 3] * 3)
        t_contact2.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_contact2)

        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=rl_gris_ligne))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            'GuineeRH © 2026 — Logiciel de Gestion RH & Paie pour la Guinée — '
            'Tous droits réservés',
            s_footer
        ))

        # Génération
        doc.build(story)
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] PDF genere : {output_path}'
        ))
