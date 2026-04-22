"""Utilitaires communs pour exports Excel/PDF et génération de fiches vierges.

Deux briques :
  - ``build_excel(title, columns, rows)`` -> HttpResponse XLSX
  - ``build_pdf(title, columns, rows, orientation)`` -> HttpResponse PDF

Chaque app (operations, facturation, rh, flotte) importe ces fonctions et
y pousse ses propres colonnes.
"""
from __future__ import annotations
import io
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Callable, Iterable, Sequence

from django.conf import settings
from django.http import HttpResponse
from django.utils.text import slugify

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import Parametres


# ---------------------------------------------------------------------------
# Identité de l'entreprise (logo + nom)
# ---------------------------------------------------------------------------

LOGO_CANDIDATE_PATHS = [
    os.path.join(settings.BASE_DIR, "static", "images", "logo_fastlane.png"),
    os.path.join(settings.BASE_DIR, "static", "images", "logo.png"),
    os.path.join(settings.BASE_DIR, "media", "logo_fastlane.png"),
]


def find_logo_path() -> str | None:
    for p in LOGO_CANDIDATE_PATHS:
        if os.path.exists(p):
            return p
    return None


# Cache mémoire pour le logo en filigrane (ImageReader avec alpha réduit).
_WATERMARK_CACHE: dict = {}


def _get_watermark_image() -> "ImageReader | None":
    """Retourne une version translucide du logo pour usage en filigrane.

    Le fichier est lu une seule fois puis mis en cache (on retourne un
    ImageReader prêt à passer à ``canvas.drawImage``). Si Pillow n'est
    pas disponible ou si aucun logo n'est trouvé, retourne ``None``.
    """
    if "img" in _WATERMARK_CACHE:
        return _WATERMARK_CACHE["img"]
    path = find_logo_path()
    if not path:
        _WATERMARK_CACHE["img"] = None
        return None
    try:
        from PIL import Image as PILImage
        img = PILImage.open(path).convert("RGBA")
        # Réduit l'opacité à ~8% pour un filigrane discret.
        alpha = img.split()[-1].point(lambda p: int(p * 0.08))
        img.putalpha(alpha)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        reader = ImageReader(buf)
        _WATERMARK_CACHE["img"] = reader
        return reader
    except Exception:
        _WATERMARK_CACHE["img"] = None
        return None


def draw_watermark(canvas, pagesize, size_mm: float = 130) -> None:
    """Dessine le logo en filigrane centré sur la page (léger, rotation 25°)."""
    wm = _get_watermark_image()
    if not wm:
        return
    page_w, page_h = pagesize
    size = size_mm * mm
    canvas.saveState()
    try:
        canvas.translate(page_w / 2, page_h / 2)
        canvas.rotate(25)
        canvas.drawImage(
            wm, -size / 2, -size / 2, width=size, height=size,
            mask="auto", preserveAspectRatio=True,
        )
    finally:
        canvas.restoreState()


def get_company_info() -> dict:
    try:
        params = Parametres.load()
        return {
            "nom": params.societe_nom,
            "activite": params.activite,
            "devise": params.devise,
            "logo": find_logo_path(),
        }
    except Exception:
        return {
            "nom": getattr(settings, "SOCIETE_NOM", "Fastlane Logistic"),
            "activite": "Transport de Bauxite",
            "devise": getattr(settings, "SOCIETE_DEVISE", "GNF"),
            "logo": find_logo_path(),
        }


# ---------------------------------------------------------------------------
# Helpers de formatage
# ---------------------------------------------------------------------------

def fmt_value(v):
    """Rend une valeur directement exploitable par Excel et PDF."""
    if v is None:
        return ""
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, Decimal):
        return float(v)
    return v


def fmt_cell_pdf(v) -> str:
    """Rend une chaîne imprimable pour le PDF."""
    if v is None:
        return ""
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, Decimal):
        # nombres >= 1000 : séparateur d'espaces
        as_float = float(v)
        if as_float == int(as_float):
            return f"{int(as_float):,}".replace(",", " ")
        return f"{as_float:,.2f}".replace(",", " ")
    if isinstance(v, (int, float)):
        if float(v) == int(v):
            return f"{int(v):,}".replace(",", " ")
        return f"{float(v):,.2f}".replace(",", " ")
    return str(v)


# ---------------------------------------------------------------------------
# Export Excel
# ---------------------------------------------------------------------------

def build_excel(
    title: str,
    columns: Sequence[str],
    rows: Iterable[Sequence],
    *,
    filename: str | None = None,
    sheet_name: str = "Données",
    sous_titre: str | None = None,
    totaux: dict | None = None,
) -> HttpResponse:
    """Génère un fichier XLSX avec en-tête Fastlane Logistic.

    - ``columns`` : liste de libellés de colonnes
    - ``rows``    : iterable de tuples/listes de valeurs
    - ``totaux``  : {index_colonne: libelle_ou_valeur} ajouté en pied de tableau
    """
    info = get_company_info()
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:30]

    # Styles
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    title_font = Font(bold=True, size=16, color="1F4E78")
    subtitle_font = Font(italic=True, size=10, color="555555")
    total_fill = PatternFill("solid", fgColor="E7E6E6")
    total_font = Font(bold=True)
    thin = Side(border_style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    n_cols = len(columns)
    last_col = get_column_letter(n_cols)

    # Logo (facultatif)
    row_title = 1
    if info["logo"]:
        try:
            from openpyxl.drawing.image import Image as XLImage
            img = XLImage(info["logo"])
            img.width, img.height = 120, 60
            ws.add_image(img, "A1")
            ws.row_dimensions[1].height = 50
            ws.row_dimensions[2].height = 20
            row_title = 2
        except Exception:
            pass

    # En-tête société + titre
    ws.cell(row=row_title, column=2, value=info["nom"]).font = title_font
    ws.merge_cells(start_row=row_title, start_column=2, end_row=row_title, end_column=n_cols)
    ws.cell(row=row_title + 1, column=2, value=f"{info['activite']} — {title}").font = subtitle_font
    ws.merge_cells(start_row=row_title + 1, start_column=2, end_row=row_title + 1, end_column=n_cols)
    if sous_titre:
        ws.cell(row=row_title + 2, column=2, value=sous_titre).font = subtitle_font
        ws.merge_cells(start_row=row_title + 2, start_column=2, end_row=row_title + 2, end_column=n_cols)
        row_title += 1
    ws.cell(row=row_title + 2, column=2,
            value=f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}").font = subtitle_font

    header_row = row_title + 4

    # En-tête de colonnes
    for i, label in enumerate(columns, start=1):
        c = ws.cell(row=header_row, column=i, value=label)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border

    ws.row_dimensions[header_row].height = 24

    # Lignes de données
    r = header_row + 1
    col_widths = [max(12, len(str(lbl)) + 2) for lbl in columns]
    for row in rows:
        for i, v in enumerate(row, start=1):
            cell = ws.cell(row=r, column=i, value=fmt_value(v))
            cell.border = border
            if isinstance(v, (int, float, Decimal)):
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right")
            text = str(fmt_value(v))
            col_widths[i - 1] = max(col_widths[i - 1], min(40, len(text) + 2))
        r += 1

    # Pied de totaux
    if totaux:
        for i in range(1, n_cols + 1):
            cell = ws.cell(row=r, column=i, value=totaux.get(i, ""))
            cell.fill = total_fill
            cell.font = total_font
            cell.border = border
            if isinstance(totaux.get(i), (int, float, Decimal)):
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right")

    # Largeur des colonnes
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Figer la ligne d'en-tête
    ws.freeze_panes = f"A{header_row + 1}"

    # Mise en page impression
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"{header_row}:{header_row}"
    ws.print_options.horizontalCentered = True

    # Réponse HTTP
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    fname = (filename or slugify(title) or "export") + ".xlsx"
    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{fname}"'
    return response


# ---------------------------------------------------------------------------
# Export PDF
# ---------------------------------------------------------------------------

def _pdf_header_flowables(title: str, sous_titre: str | None = None) -> list:
    """Bloc d'en-tête (logo + nom société + titre) réutilisable."""
    info = get_company_info()
    styles = getSampleStyleSheet()

    style_nom = ParagraphStyle(
        "CompanyName", parent=styles["Title"], fontSize=16, leading=18,
        textColor=colors.HexColor("#1F4E78"), alignment=TA_LEFT, spaceAfter=0,
    )
    style_sub = ParagraphStyle(
        "Sub", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#555555"), alignment=TA_LEFT,
    )
    style_title = ParagraphStyle(
        "Titre", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#1F4E78"), alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
    )

    # Ligne haut : [ logo | société + activité ] puis titre centré dessous
    left_cell = ""
    if info["logo"]:
        try:
            left_cell = Image(info["logo"], width=35 * mm, height=17 * mm)
        except Exception:
            left_cell = ""

    right_cell = [
        Paragraph(info["nom"], style_nom),
        Paragraph(f"{info['activite']}", style_sub),
        Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_sub),
    ]

    header_tbl = Table(
        [[left_cell, right_cell]],
        colWidths=[40 * mm, None],
    )
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    flow = [header_tbl, Spacer(1, 4 * mm),
            Paragraph(title, style_title)]
    if sous_titre:
        flow.append(Paragraph(sous_titre, style_sub))
    flow.append(Spacer(1, 3 * mm))
    return flow


def build_pdf(
    title: str,
    columns: Sequence[str],
    rows: Iterable[Sequence],
    *,
    filename: str | None = None,
    orientation: str = "landscape",
    sous_titre: str | None = None,
    totaux: list | None = None,
    col_widths: Sequence[float] | None = None,
) -> HttpResponse:
    """Génère un PDF tabulaire avec en-tête société.

    - ``totaux`` : liste de cellules formant la dernière ligne (mise en gras)
    - ``col_widths`` : si fourni, liste en mm pour chaque colonne
    """
    pagesize = landscape(A4) if orientation == "landscape" else A4
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=pagesize,
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
        title=title,
    )

    flow = _pdf_header_flowables(title, sous_titre)

    # Préparation des données
    data = [list(columns)]
    for row in rows:
        data.append([fmt_cell_pdf(v) for v in row])
    if totaux:
        data.append([fmt_cell_pdf(v) for v in totaux])

    widths = None
    if col_widths:
        widths = [w * mm for w in col_widths]
    tbl = Table(data, colWidths=widths, repeatRows=1)

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BFBFBF")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2 if totaux else -1),
         [colors.white, colors.HexColor("#F7F9FB")]),
    ])
    if totaux:
        style.add("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E7E6E6"))
        style.add("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold")
    tbl.setStyle(style)

    flow.append(tbl)

    # Pied de page avec pagination
    def _on_page(canvas, d):
        draw_watermark(canvas, pagesize)
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#888888"))
        footer = f"{get_company_info()['nom']} — Page {canvas.getPageNumber()}"
        canvas.drawRightString(pagesize[0] - 10 * mm, 6 * mm, footer)
        canvas.restoreState()

    doc.build(flow, onFirstPage=_on_page, onLaterPages=_on_page)

    fname = (filename or slugify(title) or "export") + ".pdf"
    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{fname}"'
    return response


# ---------------------------------------------------------------------------
# Fiches vierges terrain (pré-imprimées pour agents)
# ---------------------------------------------------------------------------

def build_blank_fiches(
    fiche_type: str,
    nb_copies: int = 1,
    nb_lignes: int = 12,
) -> HttpResponse:
    """Génère un PDF de fiches vierges à remplir à la main.

    ``fiche_type`` ∈ {"bon_transport", "voyage_bauxite", "carburant", "panne"}

    Mise en page : tableau multi-lignes en A4 paysage. Chaque colonne = un champ,
    chaque ligne = une saisie (ex: une prise de carburant). ``nb_copies`` est
    le nombre de pages à générer, ``nb_lignes`` le nombre de lignes vides
    par page.
    """
    buf = io.BytesIO()
    pagesize = landscape(A4)
    doc = SimpleDocTemplate(
        buf, pagesize=pagesize,
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
        title=f"Fiche vierge — {fiche_type}",
    )
    flow = []
    definitions = {
        "bon_transport": {
            "titre": "BON DE TRANSPORT",
            "champs": [
                ("N° Bon", 8), ("Date", 6),
                ("Prénom chauffeur", 8), ("Nom chauffeur", 8),
                ("Téléphone", 8),
                ("Plaque camion", 8), ("Carte d'entrée", 8),
                ("Lieu de chargement", 12),
                ("Heure départ", 6), ("Pesée début", 6), ("Pesée fin", 6),
                ("Quantité (T)", 6),
                ("Client / Projet", 10),
                ("Observations", 15),
            ],
            "signatures": ["Signature chauffeur", "Signature agent de terrain"],
        },
        "voyage_bauxite": {
            "titre": "VOYAGE BAUXITE — FICHE DE SUIVI",
            "champs": [
                ("Date", 6),
                ("Camion (code)", 8), ("Chauffeur", 10),
                ("Client", 8), ("Contrat", 8),
                ("Trajet (départ → arrivée)", 15),
                ("Distance (km)", 6), ("Tonnage (T)", 6),
                ("Tarif (GNF/T)", 8),
                ("N° Bon de livraison", 8),
                ("Observations", 15),
            ],
            "signatures": ["Signature chauffeur", "Signature chef de chantier"],
        },
        "carburant": {
            "titre": "PRISE DE CARBURANT",
            "champs": [
                ("Date", 6), ("Heure", 4),
                ("Camion (code)", 8), ("Chauffeur", 10),
                ("Km au tableau de bord", 8), ("Km avant prise", 8),
                ("Nb L avant prise", 8), ("Nb L après prise", 8),
                ("Prix unitaire (GNF/L)", 8),
                ("Station / Lieu", 10),
                ("Contrat / Projet", 10),
                ("Observations", 15),
            ],
            "signatures": ["Signature chauffeur", "Signature pompiste"],
        },
        "panne": {
            "titre": "PANNE / RÉPARATION",
            "champs": [
                ("Date", 6),
                ("Camion (code)", 8),
                ("Type de panne", 10),
                ("Pièce remplacée", 12),
                ("Fournisseur / Garage", 12),
                ("Coût pièces (GNF)", 8),
                ("Coût main d'œuvre (GNF)", 8),
                ("Durée immobilisation (jours)", 6),
                ("Contrat / Projet", 10),
                ("Observations", 15),
            ],
            "signatures": ["Signature mécanicien", "Signature responsable"],
        },
    }
    spec = definitions.get(fiche_type)
    if not spec:
        raise ValueError(f"Type de fiche inconnu: {fiche_type}")

    styles = getSampleStyleSheet()
    style_titre = ParagraphStyle(
        "T", parent=styles["Heading1"], fontSize=14, alignment=TA_CENTER,
        textColor=colors.HexColor("#1F4E78"), spaceAfter=3,
    )
    style_header = ParagraphStyle(
        "TH", parent=styles["Normal"], fontSize=7.5, leading=9,
        textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold",
    )
    style_label = ParagraphStyle(
        "L", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#333333"),
    )

    # Largeur utile du corps (A4 paysage, marges 10mm * 2) = 277 mm.
    body_width = pagesize[0] - 20 * mm
    # Colonne "#" fixe pour numéroter les lignes.
    col_num_width = 8 * mm
    # Répartition des colonnes au prorata des poids fournis dans `champs`.
    champs = spec["champs"]
    total_poids = sum(p for _, p in champs) or 1
    remaining_width = body_width - col_num_width
    col_widths = [col_num_width] + [
        (p / total_poids) * remaining_width for _, p in champs
    ]

    for copy_index in range(nb_copies):
        flow.extend(_pdf_header_flowables(spec["titre"]))

        # Construction du tableau :
        #   - Ligne 0 : en-têtes (bandeau bleu, texte blanc)
        #   - N lignes vides à remplir à la main
        header_row = [Paragraph("<b>#</b>", style_header)] + [
            Paragraph(f"<b>{label}</b>", style_header) for label, _ in champs
        ]
        data = [header_row]
        for i in range(1, nb_lignes + 1):
            data.append([str(i)] + [""] * len(champs))

        header_height = 9 * mm
        row_height = 8.5 * mm
        row_heights = [header_height] + [row_height] * nb_lignes

        tbl = Table(
            data,
            colWidths=col_widths,
            rowHeights=row_heights,
            repeatRows=1,
        )
        tbl.setStyle(TableStyle([
            # En-tête
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            # Numéros de ligne (colonne 0 hors en-tête)
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F2F6FA")),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
            ("FONTSIZE", (0, 1), (0, -1), 8),
            ("TEXTCOLOR", (0, 1), (0, -1), colors.HexColor("#666666")),
            # Grille générale
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#1F4E78")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BFBFBF")),
            # Alternance lignes
            ("ROWBACKGROUNDS", (1, 1), (-1, -1),
             [colors.white, colors.HexColor("#FAFBFD")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, 0), 3),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ]))

        flow.append(tbl)
        flow.append(Spacer(1, 3 * mm))

        # Bloc signatures : deux colonnes de largeur égale
        half = body_width / 2
        sig_data = [[Paragraph(f"<b>{s}</b>", style_label) for s in spec["signatures"]],
                    ["", ""]]
        sig_tbl = Table(sig_data, colWidths=[half, half])
        sig_tbl.setStyle(TableStyle([
            ("LINEBELOW", (0, 1), (-1, 1), 0.6, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 1), (-1, 1), 10),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ]))
        flow.append(sig_tbl)

        if copy_index < nb_copies - 1:
            flow.append(PageBreak())

    def _on_page(canvas, d):
        draw_watermark(canvas, pagesize)
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#888888"))
        footer = f"{get_company_info()['nom']} — Fiche terrain"
        canvas.drawRightString(pagesize[0] - 10 * mm, 6 * mm, footer)
        canvas.restoreState()

    doc.build(flow, onFirstPage=_on_page, onLaterPages=_on_page)

    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="fiche_{fiche_type}.pdf"'
    )
    return response


# ---------------------------------------------------------------------------
# Bon de transport individuel (imprimable — à remettre au chauffeur)
# ---------------------------------------------------------------------------

def build_bon_transport_pdf(bon, inline: bool = False) -> HttpResponse:
    """Génère un PDF professionnel pour un bon de transport individuel.

    ``bon`` : instance de ``apps.operations.models.BonTransport``.
    ``inline`` : si True, affiche dans le navigateur au lieu de télécharger.

    Mise en page : A4 portrait, en-tête société + logo, grand numéro de bon
    encadré, infos en 2 colonnes (chauffeur / chargement), zones pour
    signatures/tampons, filigrane logo.
    """
    buf = io.BytesIO()
    pagesize = A4
    doc = SimpleDocTemplate(
        buf, pagesize=pagesize,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
        title=f"Bon de transport {bon.num_bon}",
    )

    styles = getSampleStyleSheet()
    st_label = ParagraphStyle(
        "BtLabel", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#666666"), spaceAfter=0,
        fontName="Helvetica",
    )
    st_val = ParagraphStyle(
        "BtVal", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#1F2937"), fontName="Helvetica-Bold",
        spaceAfter=0,
    )
    st_num = ParagraphStyle(
        "BtNum", parent=styles["Title"], fontSize=22,
        textColor=colors.HexColor("#1F4E78"), alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    st_section = ParagraphStyle(
        "BtSection", parent=styles["Heading3"], fontSize=10,
        textColor=colors.white, alignment=TA_LEFT, fontName="Helvetica-Bold",
        spaceAfter=0, leading=12,
    )

    flow = []
    flow.extend(_pdf_header_flowables("BON DE TRANSPORT"))

    # Bandeau numéro + date (grand, centré)
    body_width = pagesize[0] - 30 * mm
    num_date = Table(
        [[
            Paragraph(f"N° {bon.num_bon}", st_num),
            Paragraph(
                f"<font color='#666666' size='9'>DATE</font><br/>"
                f"<font color='#1F2937' size='13'><b>{bon.date.strftime('%d/%m/%Y')}</b></font>",
                ParagraphStyle("nd", parent=styles["Normal"], alignment=TA_CENTER),
            ),
        ]],
        colWidths=[body_width * 0.60, body_width * 0.40],
        rowHeights=[18 * mm],
    )
    num_date.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#1F4E78")),
        ("LINEAFTER", (0, 0), (0, 0), 0.6, colors.HexColor("#1F4E78")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F2F6FA")),
    ]))
    flow.append(num_date)
    flow.append(Spacer(1, 5 * mm))

    # Helper pour cellule "label + valeur" utilisée partout
    def cell(label: str, value: str) -> Paragraph:
        value = value if (value is not None and value != "") else "—"
        return Paragraph(
            f"<font color='#666666' size='7'>{label.upper()}</font><br/>"
            f"<font color='#1F2937' size='10'><b>{value}</b></font>",
            ParagraphStyle("c", parent=styles["Normal"], leading=11, spaceAfter=0),
        )

    def section_header(title: str) -> Table:
        t = Table(
            [[Paragraph(f"<b>{title}</b>", st_section)]],
            colWidths=[body_width],
            rowHeights=[7 * mm],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1F4E78")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return t

    # ===== CHAUFFEUR =====
    flow.append(section_header("CHAUFFEUR"))
    chauff_data = [[
        cell("Prénom", bon.prenom),
        cell("Nom", bon.nom),
        cell("Téléphone", bon.telephone),
    ]]
    chauff_tbl = Table(chauff_data, colWidths=[body_width / 3] * 3, rowHeights=[14 * mm])
    chauff_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BFBFBF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(chauff_tbl)
    flow.append(Spacer(1, 3 * mm))

    # ===== CAMION / CHARGEMENT =====
    flow.append(section_header("CAMION & CHARGEMENT"))
    camion_code = bon.camion.code if bon.camion else "—"
    camion_data = [
        [
            cell("Plaque", bon.plaque),
            cell("Code camion", camion_code),
            cell("Carte d'entrée", bon.carte_entree),
        ],
        [
            cell("Lieu de chargement", bon.lieu_chargement),
            cell("Client / Projet",
                 bon.contrat.reference if bon.contrat else "—"),
            cell("Quantité (T)",
                 f"{bon.quantite:.2f}" if bon.quantite else "—"),
        ],
    ]
    camion_tbl = Table(
        camion_data, colWidths=[body_width / 3] * 3,
        rowHeights=[14 * mm, 14 * mm],
    )
    camion_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BFBFBF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(camion_tbl)
    flow.append(Spacer(1, 3 * mm))

    # ===== HORAIRES =====
    flow.append(section_header("HORAIRES DE PESÉE"))
    def _fmt_time(t):
        return t.strftime("%H:%M") if t else "—"
    horaires_data = [[
        cell("Heure de départ", _fmt_time(bon.heure_depart)),
        cell("Pesée — début", _fmt_time(bon.heure_pesee_start)),
        cell("Pesée — fin", _fmt_time(bon.heure_pesee_end)),
    ]]
    horaires_tbl = Table(horaires_data, colWidths=[body_width / 3] * 3, rowHeights=[14 * mm])
    horaires_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BFBFBF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(horaires_tbl)
    flow.append(Spacer(1, 3 * mm))

    # ===== OBSERVATIONS =====
    flow.append(section_header("OBSERVATIONS"))
    obs_text = bon.observation or ""
    obs_tbl = Table(
        [[Paragraph(obs_text or "&nbsp;", styles["Normal"])]],
        colWidths=[body_width],
        rowHeights=[24 * mm],
    )
    obs_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(obs_tbl)
    flow.append(Spacer(1, 8 * mm))

    # ===== SIGNATURES =====
    sig_data = [
        [
            Paragraph("<b>Signature chauffeur</b>", st_label),
            Paragraph("<b>Signature agent de terrain</b>", st_label),
            Paragraph("<b>Cachet société</b>", st_label),
        ],
        ["", "", ""],
        [
            Paragraph("Nom & date :", st_label),
            Paragraph("Nom & date :", st_label),
            "",
        ],
    ]
    sig_tbl = Table(
        sig_data, colWidths=[body_width / 3] * 3,
        rowHeights=[6 * mm, 22 * mm, 8 * mm],
    )
    sig_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#1F4E78")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BFBFBF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    flow.append(sig_tbl)

    # Footer + filigrane
    def _on_page(canvas, d):
        draw_watermark(canvas, pagesize)
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#888888"))
        footer = f"{get_company_info()['nom']} — Bon de transport {bon.num_bon}"
        canvas.drawString(15 * mm, 6 * mm, footer)
        canvas.drawRightString(
            pagesize[0] - 15 * mm, 6 * mm,
            f"Édité le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    doc.build(flow, onFirstPage=_on_page, onLaterPages=_on_page)

    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    disposition = "inline" if inline else "attachment"
    response["Content-Disposition"] = (
        f'{disposition}; filename="bon_transport_{bon.num_bon}.pdf"'
    )
    return response
