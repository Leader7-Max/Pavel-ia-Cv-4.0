"""Exports PDF (reportlab), Word (python-docx) et TXT — 11 maquettes de CV."""
import io
import re
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, FrameBreak, HRFlowable, KeepInFrame,
                                KeepTogether, PageTemplate, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

# layout : single | sidebar | euro ; header : left | center | band ; heading : line | plain | caps | tint | bar
STYLES = {
    "CLASSIC": dict(layout="single", header="left", heading="line", color="#1f2937", font="sans", rule="thin"),
    "MODERN": dict(layout="single", header="band", heading="line", color="#1d4ed8", font="sans"),
    "PREMIUM": dict(layout="single", header="band", heading="line", color="#111827", accent="#b8860b",
                    font="serif"),
    "EUROPEAN": dict(layout="euro", header="left", heading="line", color="#003399", font="sans", rule="thin"),
    "ATS": dict(layout="single", header="left", heading="plain", color="#000000", font="sans"),
    "EXECUTIVE": dict(layout="single", header="left", heading="bar", color="#0f2c4a", font="serif",
                      rule="thick"),
    "ELEGANT": dict(layout="single", header="center", heading="line", color="#7f1d3a", font="serif",
                    rule="thin"),
    "TEAL": dict(layout="sidebar", header="left", heading="line", color="#0f766e", font="sans"),
    "NAVY": dict(layout="sidebar", header="left", heading="line", color="#1e293b", font="sans"),
    "CORAL": dict(layout="sidebar", header="left", heading="line", color="#c2410c", font="sans"),
    "EMERALD": dict(layout="single", header="band", heading="tint", color="#047857", font="sans"),
    "MINIMAL": dict(layout="single", header="left", heading="caps", color="#475569", font="sans"),
}
DEFAULT = "CLASSIC"
SIDE_WORDS = ("compétence", "competence", "langue", "intérêt", "interet", "loisir", "certification", "permis",
              "complémentaire", "complementaire", "outil", "logiciel", "skills", "languages", "interests",
              "kenntnisse", "sprachen", "hobbys", "habilidades", "idiomas", "intereses", "competenze",
              "lingue", "interessi")
PAGE_W, PAGE_H = A4
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def style_of(key):
    return STYLES.get(key) or STYLES[DEFAULT]


def clean(s):
    s = _CTRL.sub("", str(s)).replace("\u00a0", " ").replace("\u202f", " ")
    return s.encode("cp1252", "replace").decode("cp1252")


def _esc(s):
    return escape(clean(s))


# ------------------------------------------------------------------ analyse du texte
def structure(text):
    """Découpe un CV en {name, title, contacts, sections}. None si ce n'est pas un CV structuré."""
    lines = [l.strip() for l in text.replace("\r", "").replace("**", "").split("\n")]
    if not any(l.startswith("## ") for l in lines):
        return None
    while lines and not lines[0]:
        lines.pop(0)
    start = 0 if lines[0].startswith("## ") else 1
    name = "" if start == 0 else lines[0].lstrip("# ").strip()
    head, sections, cur = [], [], None
    for l in lines[start:]:
        if not l:
            continue
        if l.startswith("## "):
            cur = (l[3:].strip(), [])
            sections.append(cur)
        elif cur is None:
            head.append(l)
        else:
            m = re.match(r"^[-*•]\s+(.*)", l)
            cur[1].append(("li", m.group(1)) if m else ("p", l))
    title, contacts = "", []
    for l in head:
        is_contact = "@" in l or " | " in l or sum(c.isdigit() for c in l) >= 6
        if not title and not is_contact:
            title = l
        else:
            contacts += [x.strip() for x in l.split("|") if x.strip()]
    return {"name": name, "title": title, "contacts": contacts, "sections": sections}


def to_txt(text):
    return text.replace("**", "")


def _is_side(title):
    t = title.lower()
    return any(w in t for w in SIDE_WORDS)


# ------------------------------------------------------------------ PDF (reportlab)
def _fonts(t):
    return ("Times-Roman", "Times-Bold") if t["font"] == "serif" else ("Helvetica", "Helvetica-Bold")


def _hex(h):
    return colors.HexColor(h)


def _mix(hex_a, amount, base=colors.white):
    c = _hex(hex_a)
    return colors.Color(base.red + (c.red - base.red) * amount, base.green + (c.green - base.green) * amount,
                        base.blue + (c.blue - base.blue) * amount)


def _styles(t, mode):
    """mode : main | side | band"""
    f, fb = _fonts(t)
    light = mode in ("side", "band")
    ink = colors.white if light else _hex("#1f2937")
    sub = _mix(t["color"], 0.18) if light and mode == "side" else (_hex("#e5e7eb") if light else _hex("#4b5563"))
    head_col = _hex(t.get("accent", t["color"]))
    S = {}
    S["p"] = ParagraphStyle("p", fontName=f, fontSize=9.6, leading=13.2, textColor=ink, spaceAfter=2)
    S["role"] = ParagraphStyle("role", parent=S["p"], fontName=fb, spaceBefore=4, spaceAfter=1)
    S["li"] = ParagraphStyle("li", parent=S["p"], leftIndent=11, bulletIndent=1, spaceAfter=1.5)
    S["h2"] = ParagraphStyle("h2", fontName=fb, fontSize=10.5, leading=13, textColor=head_col,
                             spaceBefore=11, spaceAfter=2)
    name_col = colors.white if mode == "band" else _hex(t["color"])
    S["name"] = ParagraphStyle("name", fontName=fb, fontSize=25, leading=29, textColor=name_col)
    S["name_c"] = ParagraphStyle("name_c", parent=S["name"], alignment=TA_CENTER)
    S["title"] = ParagraphStyle("title", fontName=f, fontSize=12.5, leading=16,
                                textColor=(_hex("#e5e7eb") if mode == "band" else _hex("#4b5563")))
    S["title_c"] = ParagraphStyle("title_c", parent=S["title"], alignment=TA_CENTER)
    S["contact"] = ParagraphStyle("contact", fontName=f, fontSize=9, leading=12.5, textColor=sub, spaceBefore=2)
    S["contact_c"] = ParagraphStyle("contact_c", parent=S["contact"], alignment=TA_CENTER)
    S["euro"] = ParagraphStyle("euro", fontName=fb, fontSize=9.5, leading=12.5, textColor=head_col)
    return S


def _heading(title, t, S, width, light=False):
    txt = _esc(title).upper()
    kind = "line" if light else t["heading"]
    hc = _hex(t.get("accent", t["color"]))
    if light:
        hs = ParagraphStyle("hl", parent=S["h2"], textColor=colors.white, fontSize=9.5, spaceBefore=12)
        return [Paragraph(txt, hs), HRFlowable(width="100%", thickness=0.7, color=_mix(t["color"], 0.45),
                                               spaceBefore=1, spaceAfter=4)]
    if kind == "plain":
        return [Paragraph(txt, ParagraphStyle("hp", parent=S["h2"], textColor=colors.black))]
    if kind == "caps":
        hs = ParagraphStyle("hc", parent=S["h2"], charSpace=1.6, fontSize=9.5)
        return [Paragraph(txt, hs), HRFlowable(width="100%", thickness=0.4, color=_hex("#cbd5e1"),
                                               spaceBefore=1, spaceAfter=4)]
    if kind == "tint":
        hs = ParagraphStyle("ht", parent=S["h2"], backColor=_mix(t["color"], 0.13), borderPadding=(3, 4, 3, 6),
                            leftIndent=6, spaceBefore=13, spaceAfter=7)
        return [Paragraph(txt, hs)]
    if kind == "bar":
        tb = Table([["", Paragraph(txt, S["h2"])]], colWidths=[3.2, width - 3.2], spaceBefore=9, spaceAfter=3)
        tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), hc), ("LEFTPADDING", (1, 0), (1, 0), 7),
                                ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                                ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0)]))
        return [tb]
    return [Paragraph(txt, S["h2"]), HRFlowable(width="100%", thickness=0.9, color=hc, spaceBefore=1,
                                                spaceAfter=4)]


def _items(items, S):
    out = []
    for i, (kind, txt) in enumerate(items):
        if kind == "li":
            out.append(Paragraph(_esc(txt), S["li"], bulletText="•"))
        else:
            nxt = items[i + 1][0] if i + 1 < len(items) else None
            out.append(Paragraph(_esc(txt), S["role"] if nxt == "li" else S["p"]))
    return out


def _section(title, items, t, S, width, light=False):
    head = _heading(title, t, S, width, light)
    body = _items(items, S)
    if not body or light:  # KeepInFrame (colonne latérale) n'accepte pas KeepTogether
        return head + body
    return [KeepTogether(head + [body[0]])] + body[1:]


class _Band(Flowable):
    """Bandeau d'en-tête pleine largeur, collé au haut de la page."""

    def __init__(self, paras, color, bleed, pad=8 * mm):
        super().__init__()
        self.paras, self.color, self.bleed, self.pad = paras, color, bleed, pad

    def wrap(self, aw, ah):
        self.hs, h = [], self.pad
        for p in self.paras:
            hh = p.wrap(aw, ah)[1]
            self.hs.append(hh)
            h += hh + 2
        self.h = h + self.pad * 0.8
        return aw, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.color)
        c.rect(-self.bleed, 0, PAGE_W, self.h, stroke=0, fill=1)
        c.restoreState()
        y = self.h - self.pad
        for p, hh in zip(self.paras, self.hs):
            y -= hh + 2
            p.drawOn(c, 0, y + 2)


def _header(data, t, width, bleed):
    mode = t["header"]
    S = _styles(t, "band" if mode == "band" else "main")
    center = mode == "center"
    paras = [Paragraph(_esc(data["name"]), S["name_c" if center else "name"])] if data["name"] else []
    if data["title"]:
        paras.append(Paragraph(_esc(data["title"]), S["title_c" if center else "title"]))
    if data["contacts"]:
        paras.append(Paragraph("  |  ".join(_esc(c) for c in data["contacts"]),
                               S["contact_c" if center else "contact"]))
    if mode == "band":
        return [_Band(paras, _hex(t["color"]), bleed), Spacer(1, 4 * mm)]
    out = list(paras)
    rule = t.get("rule")
    if rule == "thick":
        out.append(HRFlowable(width="28%", thickness=3, color=_hex(t["color"]), hAlign="LEFT",
                              spaceBefore=4, spaceAfter=2))
    elif rule == "thin":
        out.append(HRFlowable(width="100%" if not center else "40%", thickness=0.8, color=_hex(t["color"]),
                              hAlign="CENTER" if center else "LEFT", spaceBefore=5, spaceAfter=2))
    return out + [Spacer(1, 2 * mm)]


def _frame(x, y, w, h):
    return Frame(x, y, w, h, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)


def _euro_story(sections, t, S, width):
    out, cw = [], 36 * mm
    for title, items in sections:
        flows = _items(items, S) or [Spacer(1, 1)]
        rows = [[Paragraph(_esc(title).upper(), S["euro"]) if i == 0 else "", f] for i, f in enumerate(flows)]
        tb = Table(rows, colWidths=[cw, width - cw], spaceBefore=7)
        tb.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEAFTER", (0, 0), (0, -1), 0.9, _hex(t["color"])),
            ("LINEABOVE", (0, 0), (-1, 0), 0.4, _hex("#cbd5e1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, -1), 8),
            ("LEFTPADDING", (1, 0), (1, -1), 11), ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, 0), 6)]))
        out.append(tb)
    return out


def _letter_pdf(text, t):
    f = _fonts(t)[0]
    st = ParagraphStyle("l", fontName=f, fontSize=10.5, leading=15, textColor=colors.black)
    story = [Paragraph(_esc(l), st) if l.strip() else Spacer(1, 7)
             for l in text.replace("\r", "").replace("**", "").split("\n")]
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=22 * mm,
                      bottomMargin=20 * mm, title="Lettre de motivation", author="Pavel IA").build(story)
    return buf.getvalue()


def to_pdf(text, style="CLASSIC"):
    t = style_of(style)
    data = structure(text)
    if data is None:
        return _letter_pdf(text, t)
    buf = io.BytesIO()
    M, TM, BM = 18 * mm, 15 * mm, 15 * mm
    doc = BaseDocTemplate(buf, pagesize=A4, title=data["name"] or "CV", author="Pavel IA CV")
    if t["layout"] == "sidebar":
        SW = 66 * mm
        side_col = _hex(t["color"])

        def bg(canvas, _doc):
            canvas.saveState()
            canvas.setFillColor(side_col)
            canvas.rect(0, 0, SW, PAGE_H, stroke=0, fill=1)
            canvas.restoreState()

        lw, lh = SW - 14 * mm, PAGE_H - BM - 14 * mm
        mx = SW + 9 * mm
        mw = PAGE_W - mx - 14 * mm
        doc.addPageTemplates([
            PageTemplate("first", [_frame(7 * mm, BM, lw, lh), _frame(mx, BM, mw, lh)], onPage=bg,
                         autoNextPageTemplate="later"),
            PageTemplate("later", [_frame(mx, BM, mw, lh)], onPage=bg)])
        SM, SS = _styles(t, "main"), _styles(t, "side")
        data_side = [(a, b) for a, b in data["sections"] if _is_side(a)]
        data_main = [(a, b) for a, b in data["sections"] if not _is_side(a)]
        side = []
        if data["contacts"]:
            side += _heading("Contact", t, SS, lw, light=True)
            side += [Paragraph(_esc(c), SS["p"]) for c in data["contacts"]]
        for title, items in data_side:
            side += _section(title, items, t, SS, lw, light=True)
        story = [KeepInFrame(lw, lh, side, mode="shrink"), FrameBreak()]
        if data["name"]:
            story.append(Paragraph(_esc(data["name"]), SM["name"]))
        if data["title"]:
            story.append(Paragraph(_esc(data["title"]), SM["title"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=_hex(t["color"]), spaceBefore=5, spaceAfter=3))
        for title, items in data_main:
            story += _section(title, items, t, SM, mw)
    else:
        band = t["header"] == "band"
        W = PAGE_W - 2 * M
        doc.addPageTemplates([
            PageTemplate("first", [_frame(M, BM, W, PAGE_H - BM - (0 if band else TM))],
                         autoNextPageTemplate="later"),
            PageTemplate("later", [_frame(M, BM, W, PAGE_H - BM - TM)])])
        S = _styles(t, "main")
        story = _header(data, t, W, M)
        if t["layout"] == "euro":
            story += _euro_story(data["sections"], t, S, W)
        else:
            for title, items in data["sections"]:
                story += _section(title, items, t, S, W)
    doc.build(story)
    return buf.getvalue()


# ------------------------------------------------------------------ DOCX (python-docx)
def _rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _hexmix(hex_a, amount):
    h = hex_a.lstrip("#")
    ch = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{int(255 + (c - 255) * amount):02X}" for c in ch)


def _shade(cell, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill.lstrip("#"))
    cell._tc.get_or_add_tcPr().append(shd)


def _cell_margins(cell, top=0, start=0, bottom=0, end=0):
    mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(int(val)))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    cell._tc.get_or_add_tcPr().append(mar)


def _cell_border(cell, side, color, sz):
    b = OxmlElement("w:tcBorders")
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:color"), color.lstrip("#"))
    b.append(el)
    cell._tc.get_or_add_tcPr().append(b)


def _par_border(par, side, color, sz, space=1):
    pPr = par._p.get_or_add_pPr()
    pb = OxmlElement("w:pBdr")
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color.lstrip("#"))
    pb.append(el)
    pPr.append(pb)


def _par_shade(par, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill.lstrip("#"))
    par._p.get_or_add_pPr().append(shd)


def _par(container):
    if hasattr(container, "_tc") and len(container.paragraphs) == 1 and not container.paragraphs[0].runs:
        return container.paragraphs[0]
    return container.add_paragraph()


def _run(par, text, size, bold=False, color=None, italic=False):
    r = par.add_run(_CTRL.sub("", text))
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color:
        r.font.color.rgb = _rgb(color)
    return r


def _dx_heading(c, title, t, light=False):
    hc = t.get("accent", t["color"])
    kind = "line" if light else t["heading"]
    p = _par(c)
    txt = title.upper()
    if light:
        _par_border(p, "bottom", _hexmix(t["color"], 0.45), 6)
        _run(p, txt, 10, True, "#FFFFFF")
    elif kind == "plain":
        _run(p, txt, 11, True, "#000000")
    elif kind == "caps":
        _par_border(p, "bottom", "#CBD5E1", 4)
        _run(p, txt, 10, True, hc)
    elif kind == "tint":
        _par_shade(p, _hexmix(t["color"], 0.13))
        _run(p, " " + txt, 11, True, hc)
    elif kind == "bar":
        _par_border(p, "left", hc, 36, space=6)
        _run(p, txt, 11, True, hc)
    else:
        _par_border(p, "bottom", hc, 8)
        _run(p, txt, 11, True, hc)
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True


def _dx_items(c, items, light=False):
    ink = "#FFFFFF" if light else "#1F2937"
    for i, (kind, txt) in enumerate(items):
        p = _par(c)
        if kind == "li":
            _run(p, "•  " + txt, 10, color=ink)
            p.paragraph_format.left_indent = Pt(12)
            p.paragraph_format.first_line_indent = Pt(-12)
            p.paragraph_format.space_after = Pt(1.5)
        else:
            nxt = items[i + 1][0] if i + 1 < len(items) else None
            _run(p, txt, 10, nxt == "li", ink)
            p.paragraph_format.space_before = Pt(4 if nxt == "li" else 0)
            p.paragraph_format.space_after = Pt(1.5)


def _dx_header(c, data, t, light=False):
    center = t["header"] == "center"
    band = t["header"] == "band"
    white = band or light
    p = _par(c)
    if data["name"]:
        _run(p, data["name"], 24, True, "#FFFFFF" if white else t["color"])
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if data["title"]:
        p = c.add_paragraph()
        _run(p, data["title"], 12.5, color="#E5E7EB" if white else "#4B5563")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else p.alignment
    if data["contacts"]:
        p = c.add_paragraph()
        _run(p, "  |  ".join(data["contacts"]), 9, color="#E5E7EB" if white else "#4B5563")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else p.alignment
        rule = t.get("rule")
        if rule == "thin":
            _par_border(p, "bottom", t["color"], 8, space=4)
        elif rule == "thick":
            _par_border(p, "bottom", t["color"], 24, space=4)


def _fix_widths(table, widths):
    table.autofit = False
    for row in table.rows:
        for cell, w in zip(row.cells, widths):
            cell.width = w


def to_docx(text, style="CLASSIC"):
    t = style_of(style)
    data = structure(text)
    doc = Document()
    font = "Times New Roman" if t["font"] == "serif" else "Calibri"
    doc.styles["Normal"].font.name = font
    doc.styles["Normal"].font.size = Pt(10)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2)
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    if data is None:
        for line in text.replace("\r", "").replace("**", "").split("\n"):
            p = doc.add_paragraph()
            if line.strip():
                _run(p, line, 11)
            p.paragraph_format.space_after = Pt(4)
        return _save(doc)
    if t["layout"] == "sidebar":
        sec.left_margin = sec.right_margin = Cm(0.9)
        sec.top_margin = sec.bottom_margin = Cm(0.9)
        tb = doc.add_table(rows=1, cols=2)
        _fix_widths(tb, [Cm(6.4), Cm(12.8)])
        tb.rows[0].height = Cm(27.6)
        tb.rows[0].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        left, right = tb.rows[0].cells
        _shade(left, t["color"])
        _cell_margins(left, 360, 260, 200, 200)
        _cell_margins(right, 360, 330, 200, 100)
        if data["contacts"]:
            _dx_heading(left, "Contact", t, light=True)
            for c in data["contacts"]:
                p = _par(left)
                _run(p, c, 9.5, color="#FFFFFF")
                p.paragraph_format.space_after = Pt(2)
        for title, items in data["sections"]:
            if _is_side(title):
                _dx_heading(left, title, t, light=True)
                _dx_items(left, items, light=True)
        p = _par(right)
        if data["name"]:
            _run(p, data["name"], 24, True, t["color"])
        if data["title"]:
            _run(right.add_paragraph(), data["title"], 12.5, color="#4B5563")
        _par_border(right.add_paragraph(), "bottom", t["color"], 8)
        for title, items in data["sections"]:
            if not _is_side(title):
                _dx_heading(right, title, t)
                _dx_items(right, items)
        return _save(doc)
    if t["header"] == "band":
        sec.top_margin = Cm(1.0)
        tb = doc.add_table(rows=1, cols=1)
        _fix_widths(tb, [Cm(17)])
        cell = tb.rows[0].cells[0]
        _shade(cell, t["color"])
        _cell_margins(cell, 300, 380, 300, 380)
        _dx_header(cell, data, t)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
    else:
        _dx_header(doc, data, t)
    if t["layout"] == "euro":
        tb = doc.add_table(rows=0, cols=2)
        for title, items in data["sections"]:
            row = tb.add_row()
            a, b = row.cells
            a.width, b.width = Cm(3.6), Cm(13.4)
            _cell_border(a, "right", t["color"], 8)
            _cell_margins(a, 120, 0, 80, 120)
            _cell_margins(b, 120, 200, 80, 0)
            _run(_par(a), title.upper(), 10, True, t["color"])
            _dx_items(b, items)
    else:
        for title, items in data["sections"]:
            _dx_heading(doc, title, t)
            _dx_items(doc, items)
    return _save(doc)


def _save(doc):
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
                
