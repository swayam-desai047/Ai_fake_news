"""Builds docs/Final_Project_Report.docx and docs/Final_Project_Report.pdf (identical content).

    python3 -I docs/final_report/build_final.py

Steps: (1) the title page, four certificates, acknowledgement and index are copied paragraph-by-paragraph
from the college templates (docs/final_report/templates/*.docx, copies of the supplied files) so that their
formatting is identical, and only the placeholders are replaced; (2) the chapters come from
report_content.py; (3) the DOCX is converted to PDF with LibreOffice, the page of every heading and
caption is read back with pypdf, the static Index / List of Figures / List of Tables are filled with those
page numbers, and the DOCX is rebuilt until the numbers are stable; (4) the final PDF is produced from the
final DOCX.
"""
import copy
import sys as _sys
_sys.dont_write_bytecode = True
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import report_content as RC  # noqa: E402

TPL = HERE / "templates"
LOGO_DIR = ROOT / "research_notes" / "News aggregator report audit" / "assets"
OUT_DOCX = ROOT / "docs" / "Final_Project_Report.docx"
OUT_PDF = ROOT / "docs" / "Final_Project_Report.pdf"
TNR = "Times New Roman"
MONO = "Courier New"
CONTENT_W = 15.92  # cm (A4 21 cm - 2 x 2.54 cm)

TITLE = "AI-Powered News Aggregator with Advanced Credibility and Content Analysis"
STUDENTS = [("Swayam Desai", "1272260064"), ("Vinit Mistry", "1272260066"),
            ("Hetvi Patel", "1272260131"), ("Tapaswini Nayak", "1272262064")]
GUIDE = "Prof. Pradeep Tiwari"


# ─── low-level XML helpers ──────────────────────────────────────────────────────────────────

def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


def set_run_fonts(rpr, name=TNR):
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = el("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]


def style_font(style, size, bold=False, italic=False, name=TNR, color="000000"):
    f = style.font
    f.name = name
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = RGBColor.from_string(color)
    set_run_fonts(style.element.get_or_add_rPr(), name)


def para_format(style, before=0, after=0, line=1.0, align=None, keep_next=False, page_break=False, indent=None):
    pf = style.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if align is not None:
        pf.alignment = align
    pf.keep_with_next = keep_next
    pf.page_break_before = page_break
    pf.widow_control = True
    if indent is not None:
        pf.left_indent = indent


# ─── document setup ─────────────────────────────────────────────────────────────────────────

def setup_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, side, Cm(2.54))
    sec.header_distance = sec.footer_distance = Cm(1.25)
    st = doc.styles

    # document defaults: Times New Roman 12 pt, single, no spacing (template-copied paragraphs rely on it)
    rpr_def = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    set_run_fonts(rpr_def)
    for tag in ("w:sz", "w:szCs"):
        e = rpr_def.find(qn(tag))
        if e is None:
            e = el(tag)
            rpr_def.append(e)
        e.set(qn("w:val"), "24")
    lang = rpr_def.find(qn("w:lang"))
    if lang is None:
        lang = el("w:lang")
        rpr_def.append(lang)
    lang.set(qn("w:val"), "en-GB")
    ppr_def = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:pPrDefault"))
    if ppr_def is not None:
        ppr = ppr_def.find(qn("w:pPr"))
        sp = ppr.find(qn("w:spacing"))
        if sp is None:
            sp = el("w:spacing")
            ppr.append(sp)
        sp.set(qn("w:after"), "0")
        sp.set(qn("w:line"), "240")
        sp.set(qn("w:lineRule"), "auto")

    normal = st["Normal"]
    style_font(normal, 12)
    para_format(normal, after=6, line=1.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    for name, size, before, after, align, pb in (("Heading 1", 16, 0, 18, WD_ALIGN_PARAGRAPH.CENTER, True),
                                                 ("Heading 2", 14, 14, 6, WD_ALIGN_PARAGRAPH.LEFT, False),
                                                 ("Heading 3", 12, 10, 4, WD_ALIGN_PARAGRAPH.LEFT, False)):
        h = st[name]
        style_font(h, size, bold=True)
        para_format(h, before=before, after=after, line=1.15, align=align, keep_next=True, page_break=pb)
        h.element.get_or_add_pPr()
        # no theme colour / italics carried from the default template
        h.font.italic = False

    cap = st["Caption"]
    style_font(cap, 11, bold=True)
    para_format(cap, before=4, after=12, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)

    def new_par_style(name, base="Normal"):
        s = st.add_style(name, 1)
        s.base_style = st[base]
        s.quick_style = True
        return s

    tt = new_par_style("Table Text")
    style_font(tt, 10.5)
    para_format(tt, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.LEFT)
    code = new_par_style("Code")
    style_font(code, 9, name=MONO)
    para_format(code, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.LEFT)
    tcap = new_par_style("Table Caption", "Caption")
    para_format(tcap, before=10, after=4, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
    fig = new_par_style("Figure")
    para_format(fig, before=6, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
    pre = new_par_style("Prelim Heading")
    style_font(pre, 18, bold=True)
    para_format(pre, before=0, after=12, line=1.15, align=WD_ALIGN_PARAGRAPH.CENTER, keep_next=True)
    ref = new_par_style("Reference")
    para_format(ref, after=4, line=1.15, align=WD_ALIGN_PARAGRAPH.LEFT)
    ref.paragraph_format.left_indent = Cm(1.0)
    ref.paragraph_format.first_line_indent = Cm(-1.0)

    lb = st["List Bullet"]
    style_font(lb, 12)
    para_format(lb, after=3, line=1.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # template styles: "Default" (title page / certificate), and plain Calibri "Normal" equivalents
    d = new_par_style("Default")
    d.base_style = None
    style_font(d, 12)
    para_format(d, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.LEFT)
    d.paragraph_format.alignment = None
    d.element.get_or_add_pPr()
    tn = new_par_style("TplNormal")
    tn.base_style = None
    style_font(tn, 11, name="Calibri")
    pf = tn.paragraph_format
    pf.space_after, pf.space_before = Pt(8), Pt(0)
    pf.line_spacing = 1.08
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fn = new_par_style("TplNormalIndex")
    fn.base_style = None
    style_font(fn, 11, name="Calibri")
    pf = fn.paragraph_format
    pf.space_after, pf.space_before = Pt(10), Pt(0)
    pf.line_spacing = 1.15
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    an = new_par_style("AckNormal")
    an.base_style = None
    style_font(an, 11)
    pf = an.paragraph_format
    pf.space_after, pf.space_before = Pt(0), Pt(0)
    pf.line_spacing = 1.0
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    an.paragraph_format.widow_control = False
    bt = st["Body Text"]
    bt.base_style = an
    style_font(bt, 12)
    para_format(bt, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.LEFT)
    bt.paragraph_format.widow_control = False
    return doc


# ─── template copying ───────────────────────────────────────────────────────────────────────

class Templates:
    def __init__(self, doc):
        self.doc = doc
        self.src = {}
        work = Path(tempfile.mkdtemp(prefix="tpl_"))
        for k in ("title", "cert", "ack", "fmt"):
            d = work / k
            d.mkdir()
            shutil.copy(TPL / f"{k}.docx", d / f"{k}.docx")
            self.src[k] = Document(str(d / f"{k}.docx"))
        self.logo_wide = str(LOGO_DIR / "mitwpu_logo_wide_1081x177.png")
        self.logo_ack = str(LOGO_DIR / "mitwpu_logo_ack_500x144.png")
        self.docpr = 100

    def body_children(self, k):
        return [c for c in self.src[k].element.body.iterchildren() if c.tag != qn("w:sectPr")]

    def fix(self, e, normal_style, logo):
        """Re-target image relationships, unique drawing ids, and map unstyled paragraphs."""
        for blip in e.iter(qn("a:blip")):
            rid, _ = self.doc.part.get_or_add_image(logo)
            blip.set(qn("r:embed"), rid)
        for dp in e.iter(qn("wp:docPr")):
            self.docpr += 1
            dp.set("id", str(self.docpr))
        paras = [e] if e.tag == qn("w:p") else list(e.iter(qn("w:p")))
        in_table = e.tag == qn("w:tbl")
        for p in paras:
            ppr = p.find(qn("w:pPr"))
            if ppr is None:
                ppr = el("w:pPr")
                p.insert(0, ppr)
            ps = ppr.find(qn("w:pStyle"))
            if ps is None:
                target = "Table Text" if (in_table and normal_style == "TplNormalIndex") else normal_style
                if in_table and normal_style == "TplNormal":
                    target = "TplNormal"
                ps = el("w:pStyle")
                ps.set(qn("w:val"), self.style_id(target))
                ppr.insert(0, ps)
            else:
                ps.set(qn("w:val"), self.style_id({"Default": "Default", "BodyText": "Body Text"}.get(ps.get(qn("w:val")), ps.get(qn("w:val")))))
        return e

    def style_id(self, name):
        return self.doc.styles[name].style_id

    def copy(self, k, normal_style, logo):
        return [self.fix(copy.deepcopy(c), normal_style, logo) for c in self.body_children(k)]


def runs(p):
    return p.findall(qn("w:r"))


def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def set_text(p, text, black=False):
    """Keep the first run (its formatting), drop the others, set the text."""
    rs = runs(p)
    first = rs[0]
    for r in rs[1:]:
        p.remove(r)
    for t in first.findall(qn("w:t")):
        first.remove(t)
    for tab in first.findall(qn("w:tab")):
        first.remove(tab)
    t = el("w:t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    first.append(t)
    if black:
        make_black(first)
    return first


def make_black(r):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        return
    c = rpr.find(qn("w:color"))
    if c is not None:
        c.set(qn("w:val"), "000000")


def rebuild(p, segments):
    """segments: [(text, template_run_element, black)] -> replace all runs of p."""
    proto = [(t, copy.deepcopy(r), b) for t, r, b in segments]
    for r in runs(p):
        p.remove(r)
    for text, r, black in proto:
        for t in r.findall(qn("w:t")):
            r.remove(t)
        t = el("w:t")
        t.text = text
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        if black:
            make_black(r)
        p.append(r)


def page_break_before(p):
    ppr = p.find(qn("w:pPr"))
    pb = el("w:pageBreakBefore")
    # pageBreakBefore must follow pStyle/keepNext/keepLines in the schema order
    ps = ppr.find(qn("w:pStyle"))
    if ps is not None:
        ps.addnext(pb)
    else:
        ppr.insert(0, pb)


def find_para(elems, text):
    for e in elems:
        if e.tag == qn("w:p") and ptext(e).strip().startswith(text):
            return e
    raise KeyError(text)


def title_page(T):
    els = T.copy("title", "TplNormal", T.logo_wide)
    set_text(find_para(els, "FYM"), "FYMScCS Sem - I")
    set_text(find_para(els, "Year -"), "Year - 2026-27")
    set_text(find_para(els, "“Project Title”"), f"“{TITLE}”", black=True)
    stu = find_para(els, "Student Full Name")
    set_text(stu, f"{STUDENTS[0][0]} – {STUDENTS[0][1]}", black=True)
    pos = els.index(stu)
    for k, (name, prn) in enumerate(STUDENTS[1:], start=1):
        n = copy.deepcopy(stu)
        set_text(n, f"{name} – {prn}", black=True)
        els.insert(pos + k, n)
    set_text(find_para(els, "Mr. Navnath Shete"), GUIDE)
    drop = find_para(els, "Dr. Meenal Jabde")
    els.remove(drop)
    # The filled page has three more student lines and a two-line title, so it would spill onto a second
    # page. Remove one blank line from each double blank line between the department and "Mini Project Report".
    start, end = els.index(find_para(els, "Department")), els.index(find_para(els, "Mini"))
    doubles = [e for a, e in zip(els[start:end], els[start + 1:end])
               if not ptext(a).strip() and not ptext(e).strip() and e.tag == a.tag == qn("w:p")]
    for e in doubles[:2]:
        els.remove(e)
    return els


def certificate(T, student):
    els = T.copy("cert", "TplNormal", T.logo_wide)
    body = find_para(els, "This is to certify")
    rs = runs(body)
    normal_r = rs[0]
    bold_r = next(r for r in rs if (r.find(qn("w:rPr")) is not None and r.find(qn("w:rPr")).find(qn("w:b")) is not None))
    rebuild(body, [
        ("This is to certify that, ", normal_r, False),
        (student, bold_r, True),
        (" has successfully completed his/her mini project entitled ", normal_r, False),
        (f"“{TITLE}”", bold_r, True),
        (" in partial fulfillment of FYMScCS Sem – I, for the year 2026-27. He/She has worked under our guidance and direction.", normal_r, False),
    ])
    set_text(find_para(els, "Place:"), "Place: Pune")
    tbl = next(e for e in els if e.tag == qn("w:tbl"))
    for p in tbl.iter(qn("w:p")):
        if ptext(p).strip() == "Prof. Navnath Shete":
            set_text(p, GUIDE)
    page_break_before(els[0])
    return els


def acknowledgement(T):
    els = T.copy("ack", "AckNormal", T.logo_ack)
    p1 = find_para(els, "I wish")
    set_text(p1, "We wish to express our gratitude for providing the facilities of the Institute and for encouragement "
                 "of this work. We would also like to gratefully acknowledge the enthusiastic supervision of our project "
                 f"guide {GUIDE} for his continuous, valuable guidance, patience, constant care and kind encouragement "
                 "throughout the mini project work that made us present this mini project report in an efficient manner.")
    p2 = find_para(els, "I would like")
    set_text(p2, "We would like to thank Dr. P. S. Metkewar, Program Head for providing us with guidance and help on every "
                 "step of the way during this mini project and for imparting us with invaluable knowledge and teaching us "
                 "the etiquettes of a professional employee.")
    sn = find_para(els, "Student Name")
    prn = find_para(els, "PRN")
    # one line per student: "Student Name - ...<tab>PRN - ..." (the template block is too narrow for four pairs)
    lines = []
    for name, number in STUDENTS:
        n = copy.deepcopy(sn)
        set_text(n, f"Student Name - {name}")
        r = runs(n)[0]
        r.append(el("w:tab"))
        t = el("w:t")
        t.text = f"PRN - {number}"
        r.append(t)
        ppr = n.find(qn("w:pPr"))
        ind = ppr.find(qn("w:ind"))
        if ind is not None:
            ind.set(qn("w:right"), "0")
        tabs = el("w:tabs")
        tabs.append(el("w:tab", **{"w:val": "left", "w:pos": "5670"}))
        ppr.find(qn("w:pStyle")).addnext(tabs)
        sp = ppr.find(qn("w:spacing"))
        if sp is not None:
            sp.set(qn("w:line"), "400")
        lines.append(n)
    pos = els.index(sn)
    for k, n in enumerate(lines):
        els.insert(pos + 1 + k, n)
    els.remove(sn)
    els.remove(prn)
    # template keeps five empty paragraphs before the names; three are enough with four name lines
    idx = els.index(lines[0])
    empties = [e for e in els[idx - 5:idx] if e.tag == qn("w:p") and not ptext(e).strip()]
    for e in empties[:2]:
        els.remove(e)
    page_break_before(els[0])
    return els


def index_page(T, numbers):
    els = T.copy("fmt", "TplNormalIndex", T.logo_wide)
    tbl = next(e for e in els if e.tag == qn("w:tbl"))
    rows = tbl.findall(qn("w:tr"))
    for tr in rows[1:]:
        cells = tr.findall(qn("w:tc"))
        no = ptext(cells[0]).strip()
        title = re.sub(r"\s+", " ", ptext(cells[1])).strip()
        # trim the template's typing artefacts (trailing spaces, double space)
        p_title = cells[1].find(qn("w:p"))
        if runs(p_title):
            set_text(p_title, title)
        p_no = cells[2].find(qn("w:p"))
        val = str(numbers.get(no, ""))
        # use a run formatted like the number cell of the same row
        proto = runs(cells[0].find(qn("w:p")))[0]
        r = copy.deepcopy(proto)
        for t in r.findall(qn("w:t")):
            r.remove(t)
        t = el("w:t")
        t.text = val
        r.append(t)
        for old in runs(p_no):
            p_no.remove(old)
        p_no.append(r)
        jc = p_no.find(qn("w:pPr")).find(qn("w:jc")) if p_no.find(qn("w:pPr")) is not None else None
    # cell paragraphs: single spacing like the template's TableGrid paragraphs
    for p in tbl.iter(qn("w:p")):
        ppr = p.find(qn("w:pPr"))
        ps = ppr.find(qn("w:pStyle"))
        ps.set(qn("w:val"), T.style_id("Table Text"))
    for tr in rows:
        trpr = tr.find(qn("w:trPr"))
        if trpr is None:
            trpr = el("w:trPr")
            tr.insert(0 if tr.find(qn("w:tblPrEx")) is None else 1, trpr)
        trpr.append(el("w:cantSplit"))
    rows[0].find(qn("w:trPr")).append(el("w:tblHeader"))
    return els, [ptext(tr.findall(qn("w:tc"))[1]).strip() for tr in rows[1:]], [ptext(tr.findall(qn("w:tc"))[0]).strip() for tr in rows[1:]]


# ─── content rendering ──────────────────────────────────────────────────────────────────────

INLINE = re.compile(r"(\*\*.+?\*\*|`.+?`|\*[^*\s][^*]*?\*)")


LONG_TOKEN = re.compile(r"\S{16,}")


def soft_breaks(text):
    """Allow line breaks inside long file names and identifiers (zero-width space after / and _)."""
    return LONG_TOKEN.sub(lambda m: re.sub(r"([/_])(?=\w)", "\\1\u200b", m.group(0)), text)


def add_inline(p, text, size=None):
    text = soft_breaks(text)
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = MONO
            set_run_fonts(r._element.get_or_add_rPr(), MONO)
            r.font.size = Pt((size or 12) - 1.5)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = p.add_run(part[1:-1])
            r.italic = True
        else:
            r = p.add_run(part)
        if size and not (part.startswith("`")):
            r.font.size = Pt(size)


def shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    s = el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": fill})
    tcpr.append(s)


def cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblpr = table._tbl.tblPr
    m = el("w:tblCellMar")
    for side, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        m.append(el(f"w:{side}", **{"w:w": v, "w:type": "dxa"}))
    tblpr.append(m)


def set_col_widths(table, widths):
    tbl = table._tbl
    grid = tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(widths[i] / 2.54 * 1440)))
    for row in table.rows:
        for i, c in enumerate(row.cells):
            c.width = Cm(widths[i])


class Builder:
    def __init__(self, doc, numbers):
        self.doc = doc
        self.numbers = numbers  # computed page numbers (key -> page)
        self.items = []  # (kind, key, search text) in document order, for page lookup

    def p(self, text, style=None, align=None, size=None):
        par = self.doc.add_paragraph(style=style)
        add_inline(par, text, size)
        if align is not None:
            par.alignment = align
        return par

    def heading(self, level, num, title):
        text = f"{num}. {title}" if level == 1 else f"{num} {title}" if num else title
        h = self.doc.add_heading(text, level=level)
        for r in h.runs:
            r.font.color.rgb = RGBColor(0, 0, 0)
            r.font.name = TNR
        if num:
            self.items.append(("head", num, text))
        return h

    def bullets(self, items):
        for it in items:
            self.p(it, style="List Bullet")

    def caption(self, text, style="Caption"):
        c = self.doc.add_paragraph(style=style)
        add_inline(c, text)
        return c

    def table(self, num, caption, header, rows, widths, size=10.5, first_bold=False):
        self.caption(f"Table {num}: {caption}", style="Table Caption")
        self.items.append(("tab", num, f"Table {num}:"))
        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        hdr = t.rows[0]
        for i, h in enumerate(header):
            c = hdr.cells[i]
            c.paragraphs[0].style = self.doc.styles["Table Text"]
            add_inline(c.paragraphs[0], f"**{h}**", size)
            shade(c, "D9D9D9")
        trpr = hdr._tr.get_or_add_trPr()
        trpr.append(el("w:tblHeader"))
        for row in rows:
            r = t.add_row()
            r._tr.get_or_add_trPr().append(el("w:cantSplit"))
            for i, val in enumerate(row):
                c = r.cells[i]
                lines = val.split("\n") if isinstance(val, str) else [str(val)]
                for j, line in enumerate(lines):
                    par = c.paragraphs[0] if j == 0 else c.add_paragraph()
                    par.style = self.doc.styles["Table Text"]
                    add_inline(par, f"**{line}**" if (first_bold and i == 0 and line) else line, size)
        set_col_widths(t, widths)
        cell_margins(t)
        # small gap after a table
        gap = self.doc.add_paragraph(style="Table Text")
        gap.paragraph_format.space_after = Pt(6)
        return t

    def figure(self, num, path, caption, width=None, max_h=19.5):
        from PIL import Image
        im = Image.open(path)
        w_px, h_px = im.size
        width = width or CONTENT_W
        if width * h_px / w_px > max_h:
            width = max_h * w_px / h_px
        par = self.doc.add_paragraph(style="Figure")
        par.add_run().add_picture(str(path), width=Cm(width))
        self.caption(f"Figure {num}: {caption}")
        self.items.append(("fig", num, f"Figure {num}:"))

    def code(self, num, caption, text, size=8.5, width=92):
        self.caption(f"Listing {num}: {caption}", style="Table Caption")
        self.items.append(("lst", num, f"Listing {num}:"))
        t = self.doc.add_table(rows=1, cols=1)
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t.rows[0].cells[0]
        shade(c, "F2F2F2")
        t.rows[0]._tr.get_or_add_trPr().append(el("w:cantSplit"))
        lines = []
        for line in text.rstrip("\n").split("\n"):
            ind = len(line) - len(line.lstrip())
            while len(line) > width:
                cut = max(line.rfind(" ", 0, width), line.rfind(",", 0, width) + 1)
                cut = cut if cut > ind + 10 else width
                lines.append(line[:cut].rstrip())
                line = " " * (ind + 4) + line[cut:].lstrip()
            lines.append(line)
        for j, line in enumerate(lines):
            par = c.paragraphs[0] if j == 0 else c.add_paragraph()
            par.style = self.doc.styles["Code"]
            r = par.add_run(line if line else " ")
            r.font.size = Pt(8)
        set_col_widths(t, [CONTENT_W - 0.2])
        cell_margins(t, 60, 60, 120, 120)
        gap = self.doc.add_paragraph(style="Table Text")
        gap.paragraph_format.space_after = Pt(6)

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_page_number_footer(section, fmt, start):
    section.footer.is_linked_to_previous = False
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.style = section.footer.part.document.styles["Table Text"] if False else fp.style
    r = fp.add_run()
    r.font.name = TNR
    r.font.size = Pt(11)
    for tag, extra in (("begin", None), ("instr", " PAGE "), ("separate", None), ("text", "1"), ("end", None)):
        if tag == "instr":
            it = el("w:instrText")
            it.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            it.text = extra
            r._element.append(it)
        elif tag == "text":
            t = el("w:t")
            t.text = extra
            r._element.append(t)
        else:
            r._element.append(el("w:fldChar", **{"w:fldCharType": tag}))
    fp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sectpr = section._sectPr
    for old in sectpr.findall(qn("w:pgNumType")):
        sectpr.remove(old)  # add_section() copies the previous section's settings
    pg = el("w:pgNumType", **{"w:fmt": fmt, "w:start": start})
    cols = sectpr.find(qn("w:cols"))
    if cols is not None:
        cols.addprevious(pg)
    else:
        sectpr.append(pg)


def list_table(B, header, rows, widths):
    """List of Figures / Tables in the style of the college Index table."""
    t = B.doc.add_table(rows=1, cols=3)
    t.style = B.doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        par = t.rows[0].cells[i].paragraphs[0]
        par.style = B.doc.styles["Table Text"]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline(par, f"**{h}**", 12)
    t.rows[0]._tr.get_or_add_trPr().append(el("w:tblHeader"))
    for row in rows:
        r = t.add_row()
        r._tr.get_or_add_trPr().append(el("w:cantSplit"))
        for i, v in enumerate(row):
            par = r.cells[i].paragraphs[0]
            par.style = B.doc.styles["Table Text"]
            par.paragraph_format.space_before = Pt(1)
            par.paragraph_format.space_after = Pt(1)
            if i != 1:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(par, str(v), 11)
    set_col_widths(t, widths)



# ─── schema order of property elements (Word rejects out-of-order children) ────────────────

PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
             "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW",
               "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
               "tblCaption", "tblDescription"]
RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow",
             "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
             "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs",
             "em", "lang", "eastAsianLayout", "specVanish", "oMath"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark"]


def _reorder(parent, order):
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    rank = {W + n: i for i, n in enumerate(order)}
    kids = list(parent)
    known = [k for k in kids if k.tag in rank]
    if [k.tag for k in known] == sorted((k.tag for k in known), key=lambda t: rank[t]):
        return
    others = [k for k in kids if k.tag not in rank]
    for k in kids:
        parent.remove(k)
    for k in sorted(known, key=lambda k: rank[k.tag]) + others:
        parent.append(k)


def fix_schema_order(root):
    for tag, order in (("w:pPr", PPR_ORDER), ("w:tblPr", TBLPR_ORDER), ("w:rPr", RPR_ORDER), ("w:tcPr", TCPR_ORDER)):
        for e in root.iter(qn(tag)):
            _reorder(e, order)

# ─── build ──────────────────────────────────────────────────────────────────────────────────

def build(numbers):
    doc = setup_document()
    T = Templates(doc)
    body = doc.element.body
    sectpr = body.find(qn("w:sectPr"))

    def put(elements):
        for e in elements:
            sectpr.addprevious(e)

    # Section 1: title page, four certificates, acknowledgement (no page numbers, as in the templates)
    put(title_page(T))
    for name, _ in STUDENTS:
        put(certificate(T, name))
    put(acknowledgement(T))
    # remove the empty paragraph python-docx starts with
    first = body.find(qn("w:p"))
    if first is not None and not ptext(first) and first.find(qn("w:r")) is None and first.find(qn("w:pPr")) is None:
        body.remove(first)

    # Section 2: Index, List of Figures, List of Tables (roman page numbers)
    s2 = doc.add_section(WD_SECTION.NEW_PAGE)
    add_page_number_footer(s2, "lowerRoman", 1)
    sectpr = body.find(qn("w:sectPr"))
    idx_els, idx_titles, idx_nums = index_page(T, numbers)
    put(idx_els)

    B = Builder(doc, numbers)
    figs, tabs = RC.collect_captions()
    B.page_break()
    B.p("List of Figures", style="Prelim Heading")
    list_table(B, ["Figure No.", "Title", "Page No."],
               [(n, cap, numbers.get(f"fig:{n}", "")) for n, cap in figs], [2.6, 10.8, 2.5])
    B.page_break()
    B.p("List of Tables", style="Prelim Heading")
    list_table(B, ["Table No.", "Title", "Page No."],
               [(n, cap, numbers.get(f"tab:{n}", "")) for n, cap in tabs], [2.6, 10.8, 2.5])

    # Section 3: chapters (arabic numbers from 1)
    s3 = doc.add_section(WD_SECTION.NEW_PAGE)
    add_page_number_footer(s3, "decimal", 1)
    RC.write_chapters(B)
    fix_schema_order(doc.element.body)
    fix_schema_order(doc.styles.element)
    for sec in doc.sections:
        fix_schema_order(sec.footer._element)
    # the first chapter heading needs no page break (the section break already starts a page)
    doc.save(str(OUT_DOCX))
    return B.items, idx_titles, idx_nums


def to_pdf(docx_path, out_dir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    return Path(out_dir) / (Path(docx_path).stem + ".pdf")


def norm(s):
    return re.sub(r"\s+", "", s)


def page_numbers(pdf_path, items):
    from pypdf import PdfReader
    pages = [norm(p.extract_text() or "") for p in PdfReader(str(pdf_path)).pages]
    lot = max(i for i, t in enumerate(pages) if "ListofTables" in t[:40])
    start = next(i for i in range(lot + 1, len(pages)) if norm("1. Introduction") in pages[i])
    cur = start
    out = {}
    missing = []
    for kind, num, text in items:
        key = norm(text)
        j = cur
        while j < len(pages) and key not in pages[j]:
            j += 1
        if j == len(pages):
            missing.append(text)
            continue
        cur = j
        page = j - start + 1
        if kind == "head":
            out[num] = page
        else:
            out[f"{kind}:{num}"] = page
    return out, missing, len(pages), start


def main():
    work = Path(tempfile.mkdtemp(prefix="final_report_"))
    numbers = {}
    for it in range(4):
        items, _, _ = build(numbers)
        pdf = to_pdf(OUT_DOCX, work)
        new, missing, total, start = page_numbers(pdf, items)
        print(f"pass {it + 1}: {total} pages, chapters start at PDF page {start + 1}, missing={missing}")
        if new == numbers:
            break
        numbers = new
    shutil.copy(pdf, OUT_PDF)
    import json
    (HERE / "page_numbers.json").write_text(json.dumps(numbers, indent=1))
    print("written", OUT_DOCX, OUT_PDF)


if __name__ == "__main__":
    main()
