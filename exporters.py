"""Exports PDF (fpdf2), DOCX (python-docx) à partir d'un texte structuré."""
import io
import re

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from fpdf import FPDF

STYLES = {
    "CLASSIC": (31, 41, 55),
    "MODERN": (37, 99, 235),
    "PREMIUM": (120, 53, 15),
    "EUROPEAN": (0, 51, 153),
    "ATS": (0, 0, 0),
}
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_REPL = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
         "•": "-", "…": "...", "\u00a0": " ", "€": "EUR", "\u202f": " "}


def clean(s):
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return _CTRL.sub("", s).encode("latin-1", "replace").decode("latin-1")


def parse(text):
    """Retourne une liste de (type, texte) : name, sub, h2, li, p."""
    lines = text.replace("\r", "").replace("**", "").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return []
    if not any(l.startswith("## ") for l in lines):
        return [("p", l.strip()) for l in lines]
    out = [("name", lines[0].strip("# ").strip())]
    seen_h2 = False
    for l in lines[1:]:
        s = l.strip()
        if not s:
            continue
        if s.startswith("## "):
            out.append(("h2", s[3:].strip()))
            seen_h2 = True
        elif re.match(r"^[-*•]\s+", s):
            out.append(("li", re.sub(r"^[-*•]\s+", "", s)))
        else:
            out.append(("p" if seen_h2 else "sub", s))
    return out


def to_txt(text):
    return text.replace("**", "")


def to_pdf(text, style="CLASSIC"):
    r, g, b = STYLES.get(style, STYLES["CLASSIC"])
    fam = "Times" if style == "PREMIUM" else "Helvetica"
    pdf = FPDF(format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(True, 16)
    pdf.add_page()

    def line(h, t, size, bold=False, color=(0, 0, 0), x=None):
        pdf.set_font(fam, "B" if bold else "", size)
        pdf.set_text_color(*color)
        if x:
            pdf.set_x(x)
        pdf.multi_cell(0, h, clean(t), new_x="LMARGIN", new_y="NEXT")

    for kind, t in parse(text):
        if kind == "name":
            line(9, t, 20, True, (r, g, b))
        elif kind == "sub":
            line(5, t, 10, False, (90, 90, 90))
        elif kind == "h2":
            pdf.ln(3)
            line(7, t.upper(), 12, True, (r, g, b))
            if style != "ATS":
                pdf.set_draw_color(r, g, b)
                y = pdf.get_y()
                pdf.line(18, y, 192, y)
                pdf.ln(1.5)
        elif kind == "li":
            line(5.5, "- " + t, 10, x=22)
        elif not t.strip():
            pdf.ln(3)
        else:
            line(5.5, t, 10)
    return bytes(pdf.output())


def to_docx(text, style="CLASSIC"):
    rgb = RGBColor(*STYLES.get(style, STYLES["CLASSIC"]))
    doc = Document()
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2)
    for kind, t in parse(text):
        t = _CTRL.sub("", t)
        if kind == "li":
            doc.add_paragraph(t, style="List Bullet")
            continue
        run = doc.add_paragraph().add_run(t.upper() if kind == "h2" else t)
        if kind == "name":
            run.bold, run.font.size, run.font.color.rgb = True, Pt(20), rgb
        elif kind == "h2":
            run.bold, run.font.size, run.font.color.rgb = True, Pt(12), rgb
        elif kind == "sub":
            run.font.size = Pt(10)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
  
