import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Universidad Católica de Oriente (UCO) — Manual de Usuario Final")
            self.drawRightString(558, 750, "Sistema Analítico SPADIES 3.0")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawString(54, 32, "Confidencial - Uso Interno UCO | Versión 3.0.0")
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def build_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    c_primary = colors.HexColor("#047857") # Emerald UCO
    c_secondary = colors.HexColor("#0f172a") # Slate Dark
    c_accent = colors.HexColor("#1d4ed8") # Blue
    c_text = colors.HexColor("#1e293b")
    c_muted = colors.HexColor("#475569")

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_secondary,
        alignment=1, # Center
        spaceAfter=6
    )
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        alignment=1,
        spaceAfter=15
    )
    style_h1 = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    style_h3 = ParagraphStyle(
        'Header3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_muted,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=5
    )
    style_bullet = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        leftIndent=15,
        spaceAfter=3
    )
    style_callout = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#854d0e")
    )
    style_th = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=0
    )
    style_td = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text,
        alignment=0
    )

    story = []

    # Title Banner Box
    title_box_data = [
        [
            Paragraph("UNIVERSIDAD CATÓLICA DE ORIENTE - UCO", ParagraphStyle('UBanner', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, alignment=1)),
        ],
        [
            Paragraph("MANUAL DE USUARIO FINAL", style_title)
        ],
        [
            Paragraph("SISTEMA ANALÍTICO DE DESERCIÓN Y PERMANENCIA ESTUDIANTIL<br/><font size=9 color='#64748b'>Metodología Oficial SPADIES 3.0 — Versión 3.0.0</font>", style_subtitle)
        ]
    ]
    t_banner = Table(title_box_data, colWidths=[504])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 15))

    in_table = False
    table_rows = []

    def clean_text(t):
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Helvetica estándar no dibuja estos símbolos: se sustituyen por texto equivalente
        for src, dst in (('→', '&gt;'), ('☰', '(tres rayas)'), ('＋', '+'), ('⬇', ''), ('⟶', '&gt;')):
            t = t.replace(src, dst)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
        t = re.sub(r'`(.+?)`', r'<font face="Courier" color="#047857"><b>\1</b></font>', t)
        t = re.sub(r'\\longrightarrow', r'➔', t)
        t = re.sub(r'\\dots', r'...', t)
        t = re.sub(r'\\text\{(.+?)\}', r'\1', t)
        t = re.sub(r'\$\$(.+?)\$\$', r'<b>\1</b>', t)
        t = re.sub(r'\$(.+?)\$', r'<b>\1</b>', t)
        return t

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        col_count = len(table_rows[0])
        avail_width = 504
        if col_count == 2:
            col_widths = [160, 344]
        elif col_count == 3:
            col_widths = [150, 150, 204]
        elif col_count == 4:
            col_widths = [90, 110, 130, 174]
        else:
            col_widths = [avail_width / col_count] * col_count

        formatted_rows = []
        for r_idx, row in enumerate(table_rows):
            f_row = []
            for c_idx, cell in enumerate(row):
                c_clean = clean_text(cell.strip())
                if r_idx == 0:
                    p = Paragraph(f"<b>{c_clean}</b>", style_th)
                else:
                    p = Paragraph(c_clean, style_td)
                f_row.append(p)
            formatted_rows.append(f_row)

        t = Table(formatted_rows, colWidths=col_widths)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#047857")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]
        for row_i in range(1, len(formatted_rows)):
            bg = colors.HexColor("#f8fafc") if row_i % 2 == 1 else colors.white
            t_style.append(('BACKGROUND', (0, row_i), (-1, row_i), bg))

        t.setStyle(TableStyle(t_style))
        story.append(t)
        story.append(Spacer(1, 8))
        table_rows = []
        in_table = False

    style_code = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        leftIndent=24,
        borderPadding=3,
        spaceAfter=0
    )
    in_code = False

    for line in lines:
        raw_l = line.strip()

        if raw_l.startswith('```'):
            in_code = not in_code
            story.append(Spacer(1, 4))
            continue
        if in_code:
            code_txt = line.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if code_txt:
                story.append(Paragraph(code_txt.replace(' ', '&nbsp;'), style_code))
            continue

        # Skip main markdown title since banner covers it
        if raw_l.startswith('# MANUAL DE USUARIO FINAL') or raw_l.startswith('## SISTEMA ANALÍTICO') or raw_l.startswith('### Universidad Católica'):
            continue

        if raw_l.startswith('|'):
            if '---' in raw_l:
                continue
            cells = [c for c in raw_l.split('|')[1:-1]]
            if cells:
                in_table = True
                table_rows.append(cells)
            continue
        elif in_table:
            flush_table()

        if not raw_l:
            continue

        if raw_l == '---':
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
            continue

        if raw_l.startswith('## '):
            story.append(Spacer(1, 6))
            txt = clean_text(raw_l[3:].strip())
            story.append(Paragraph(txt, style_h1))
        elif raw_l.startswith('### '):
            story.append(Spacer(1, 4))
            txt = clean_text(raw_l[4:].strip())
            story.append(Paragraph(txt, style_h2))
        elif raw_l.startswith('#### '):
            story.append(Spacer(1, 3))
            txt = clean_text(raw_l[5:].strip())
            story.append(Paragraph(txt, style_h3))
        elif raw_l.startswith('> '):
            txt = clean_text(raw_l[2:].strip())
            t_call = Table([[Paragraph(txt, style_callout)]], colWidths=[504])
            t_call.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fefce8")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#fde047")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(Spacer(1, 3))
            story.append(t_call)
            story.append(Spacer(1, 4))
        elif raw_l.startswith('* ') or raw_l.startswith('- '):
            txt = clean_text(raw_l[2:].strip())
            story.append(Paragraph(f"• {txt}", style_bullet))
        elif re.match(r'^\d+\.\s', raw_l):
            num = raw_l.split('.')[0]
            txt = clean_text(raw_l[len(num)+2:].strip())
            story.append(Paragraph(f"<b>{num}.</b> {txt}", style_bullet))
        else:
            txt = clean_text(raw_l)
            story.append(Paragraph(txt, style_body))

    if in_table:
        flush_table()

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {pdf_path}")

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md = os.path.join(root, 'Documentacion', 'Manual_Usuario_Final.md')
    pdf = os.path.join(root, 'Documentacion', 'Manual_Usuario_Final.pdf')
    build_pdf(md, pdf)
