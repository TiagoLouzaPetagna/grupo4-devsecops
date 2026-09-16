from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "entrega"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCX_PATH = OUTPUT_DIR / "Relatorio_Checkpoint_DevSecOps_Grupo4.docx"

EVIDENCE = ROOT / "evidencias"
SEMGRP_SCREEN = EVIDENCE / "real-semgrep-terminal.png"
CHECKOV_SCREEN = EVIDENCE / "real-checkov-terminal.png"
DEPENDENCY_SCREEN = EVIDENCE / "real-dependency-check.png"
ZAP_SCREEN = EVIDENCE / "real-zap-resumo.png"

# Estes números são atualizados após a primeira renderização e conferidos no PDF.
TOC_PAGES = {
    "1 Introdução": 5,
    "2 Fundamentos e posicionamento no pipeline": 6,
    "3 Metodologia do laboratório": 8,
    "4 Semgrep": 9,
    "5 OWASP Dependency Check": 14,
    "6 Checkov": 17,
    "7 OWASP ZAP": 20,
    "8 Análise dos achados": 24,
    "9 Comparação e escolha do toolchain": 26,
    "10 Integração contínua e quality gate": 27,
    "11 Limitações e conclusão": 28,
    "Referências": 30,
    "Apêndices": 31,
}

NAVY = "0B2545"
NAVY_2 = "153B5B"
CYAN = "00A6C8"
PALE_BLUE = "EAF5F8"
PALE_GRAY = "F4F6F7"
MID_GRAY = "66737D"
LIGHT_BORDER = "D9D9D9"
BLACK = "000000"
WHITE = "FFFFFF"
GREEN = "2E7D32"
AMBER = "B26A00"


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=120, start=130, bottom=120, end=130) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=LIGHT_BORDER, size="6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def remove_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "nil")


def set_run_font(run, name="Arial", size=11, bold=None, color=BLACK, italic=None) -> None:
    run.font.name = name
    r_pr = run._element.get_or_add_rPr()
    r_pr.rFonts.set(qn("w:ascii"), name)
    r_pr.rFonts.set(qn("w:hAnsi"), name)
    r_pr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_paragraph_keep(paragraph, keep_next=False, keep_lines=True) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    if keep_next:
        p_pr.append(OxmlElement("w:keepNext"))
    if keep_lines:
        p_pr.append(OxmlElement("w:keepLines"))


def set_paragraph_shading(paragraph, fill: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def set_paragraph_border(paragraph, color=LIGHT_BORDER) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "4")
        element.set(qn("w:color"), color)
        p_bdr.append(element)
    p_pr.append(p_bdr)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    set_run_font(run, size=9, color=MID_GRAY)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)


doc = Document()
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(3)
section.left_margin = Cm(3)
section.right_margin = Cm(2)
section.bottom_margin = Cm(2)
section.header_distance = Cm(1.25)
section.footer_distance = Cm(0.6)
section.different_first_page_header_footer = True

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Arial"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
normal.font.size = Pt(11)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.first_line_indent = Cm(1.25)
normal.paragraph_format.widow_control = True

title_style = styles["Title"]
title_style.font.name = "Arial"
title_style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
title_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
title_style.font.size = Pt(24)
title_style.font.bold = True
title_style.font.color.rgb = RGBColor(0, 0, 0)
title_style.paragraph_format.space_after = Pt(14)
title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

for style_name, size, before, after in (
    ("Heading 1", 16, 0, 12),
    ("Heading 2", 13, 14, 7),
    ("Heading 3", 11.5, 10, 5),
):
    style = styles[style_name]
    style.font.name = "Arial"
    style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True

if "Caption" not in [s.name for s in styles]:
    styles.add_style("Caption", WD_STYLE_TYPE.PARAGRAPH)
caption_style = styles["Caption"]
caption_style.font.name = "Arial"
caption_style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
caption_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
caption_style.font.size = Pt(9)
caption_style.font.color.rgb = RGBColor.from_string(MID_GRAY)
caption_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
caption_style.paragraph_format.line_spacing = 1.0
caption_style.paragraph_format.space_before = Pt(4)
caption_style.paragraph_format.space_after = Pt(10)

header_p = section.header.paragraphs[0]
header_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
header_p.paragraph_format.space_after = Pt(0)
set_run_font(header_p.add_run("CHECKPOINT 01   |   DEVSECOPS   |   GRUPO 4"), size=8.5, bold=True, color=MID_GRAY)

footer_intro = section.footer.paragraphs[0]
footer_table = section.footer.add_table(rows=1, cols=2, width=Cm(16))
footer_intro._element.getparent().remove(footer_intro._element)
footer_table.autofit = False
footer_table.columns[0].width = Cm(13.8)
footer_table.columns[1].width = Cm(2.2)
remove_table_borders(footer_table)
left = footer_table.cell(0, 0).paragraphs[0]
left.alignment = WD_ALIGN_PARAGRAPH.LEFT
left.paragraph_format.space_after = Pt(0)
set_run_font(left.add_run("Relatório DevSecOps | Grupo 4"), size=8.3, color=MID_GRAY)
right = footer_table.cell(0, 1).paragraphs[0]
right.paragraph_format.space_after = Pt(0)
add_page_number(right)


def add_para(text: str, *, bold_lead: str | None = None, indent=True, align=None, space_after=6):
    p = doc.add_paragraph()
    p.style = styles["Normal"]
    p.paragraph_format.space_after = Pt(space_after)
    if not indent:
        p.paragraph_format.first_line_indent = Cm(0)
    if align is not None:
        p.alignment = align
    if bold_lead and text.startswith(bold_lead):
        set_run_font(p.add_run(bold_lead), bold=True)
        set_run_font(p.add_run(text[len(bold_lead):]))
    else:
        set_run_font(p.add_run(text))
    return p


def add_bullets(items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.left_indent = Cm(0.65 + level * 0.6)
        p.paragraph_format.first_line_indent = Cm(-0.35)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(4)
        set_run_font(p.add_run(item))


def add_numbered(items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.first_line_indent = Cm(-0.4)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(4)
        set_run_font(p.add_run(item))


def add_kicker(text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Cm(0)
    set_run_font(p.add_run(text.upper()), size=9, bold=True, color=CYAN)
    set_paragraph_keep(p, keep_next=True)
    return p


def add_heading(text: str, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.first_line_indent = Cm(0)
    set_paragraph_keep(p, keep_next=True)
    return p


def add_code(text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(0.25)
    p.paragraph_format.right_indent = Cm(0.25)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(8)
    set_paragraph_shading(p, PALE_GRAY)
    set_paragraph_border(p)
    set_run_font(p.add_run(text), name="Consolas", size=8.5, color=BLACK)
    return p


def add_table(headers, rows, widths=None, font_size=9.2, first_col_bold=False):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    if widths:
        for idx, width in enumerate(widths):
            table.columns[idx].width = Cm(width)
    header_row = table.rows[0]
    set_repeat_table_header(header_row)
    for idx, text in enumerate(headers):
        cell = header_row.cells[idx]
        if widths:
            cell.width = Cm(widths[idx])
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(str(text)), size=font_size, bold=True, color=WHITE)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        fill = WHITE if row_index % 2 == 0 else PALE_BLUE
        for idx, value in enumerate(values):
            cell = cells[idx]
            if widths:
                cell.width = Cm(widths[idx])
            set_cell_shading(cell, fill)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.08
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 and len(str(value)) < 18 else WD_ALIGN_PARAGRAPH.LEFT
            set_run_font(p.add_run(str(value)), size=font_size, bold=(first_col_bold and idx == 0))
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(2)
    spacer.paragraph_format.first_line_indent = Cm(0)
    return table


def add_figure(path: Path, width_cm: float, caption: str, source: str, alt_text: str):
    if not path.exists():
        raise FileNotFoundError(path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    doc_pr_nodes = run._r.xpath(".//wp:docPr")
    if doc_pr_nodes:
        doc_pr_nodes[0].set("descr", alt_text)
        doc_pr_nodes[0].set("title", caption)
    set_paragraph_keep(p, keep_next=True)
    cap = doc.add_paragraph(style="Caption")
    set_run_font(cap.add_run(caption + "."), size=9, bold=True, color=BLACK)
    cap.add_run().add_break()
    set_run_font(cap.add_run("Fonte: " + source + "."), size=9, color=MID_GRAY)
    return p


def page_break():
    doc.add_page_break()


def start_major(number: int, title: str, kicker: str):
    if number == 1:
        page_break()
    marker = add_kicker(kicker)
    marker.paragraph_format.space_before = Pt(18)
    add_heading(f"{number} {title}", 1)


def start_continuation(title: str, kicker: str):
    marker = add_kicker(kicker)
    marker.paragraph_format.space_before = Pt(14)
    add_heading(title, 2)


def add_status_table(rows):
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [3.3, 3.6, 3.3, 5.6]
    for idx, width in enumerate(widths):
        table.columns[idx].width = Cm(width)
    remove_table_borders(table)
    headers = ["Ferramenta", "Categoria", "Situação", "Resultado principal"]
    for i, text in enumerate(headers):
        c = table.rows[0].cells[i]
        set_cell_shading(c, NAVY)
        set_cell_margins(c)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(text), size=9, bold=True, color=WHITE)
    for row_index, (tool, category, status, result, status_color) in enumerate(rows):
        cells = table.add_row().cells
        values = [tool, category, status, result]
        for i, value in enumerate(values):
            c = cells[i]
            set_cell_shading(c, WHITE if row_index % 2 == 0 else PALE_BLUE)
            set_cell_margins(c)
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in (1, 2) else WD_ALIGN_PARAGRAPH.LEFT
            set_run_font(p.add_run(value), size=9, bold=(i == 0 or i == 2), color=(status_color if i == 2 else BLACK))
    doc.add_paragraph()
    return table


# Capa
band = doc.add_table(rows=1, cols=2)
band.alignment = WD_TABLE_ALIGNMENT.CENTER
band.autofit = False
band.columns[0].width = Cm(1.25)
band.columns[1].width = Cm(14.75)
remove_table_borders(band)
set_cell_shading(band.cell(0, 0), CYAN)
set_cell_shading(band.cell(0, 1), NAVY)
for c in band.rows[0].cells:
    set_cell_margins(c, 170, 150, 170, 150)
p = band.cell(0, 1).paragraphs[0]
p.paragraph_format.first_line_indent = Cm(0)
p.paragraph_format.space_after = Pt(0)
set_run_font(p.add_run("CHECKPOINT 01   DEVSECOPS"), size=11, bold=True, color=WHITE)

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph(style="Title")
p.paragraph_format.first_line_indent = Cm(0)
set_run_font(p.add_run("Ferramentas open source de SAST SCA IaC Security e DAST no pipeline DevSecOps"), size=24, bold=True)
p = doc.add_paragraph()
p.paragraph_format.first_line_indent = Cm(0)
p.paragraph_format.space_after = Pt(24)
set_run_font(p.add_run("Análise do Grupo 4 com Semgrep OWASP Dependency Check Checkov e OWASP ZAP"), size=13, color=NAVY_2)

category_table = doc.add_table(rows=1, cols=4)
category_table.alignment = WD_TABLE_ALIGNMENT.CENTER
category_table.autofit = False
remove_table_borders(category_table)
for idx, (category, tool) in enumerate((("SAST", "Semgrep"), ("SCA", "Dependency Check"), ("IaC", "Checkov"), ("DAST", "OWASP ZAP"))):
    cell = category_table.cell(0, idx)
    cell.width = Cm(4)
    set_cell_shading(cell, NAVY if idx % 2 == 0 else NAVY_2)
    set_cell_margins(cell, 180, 90, 180, 90)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(2)
    set_run_font(p.add_run(category + "\n"), size=10, bold=True, color=CYAN)
    set_run_font(p.add_run(tool), size=9.3, bold=True, color=WHITE)

for _ in range(5):
    doc.add_paragraph()

meta = doc.add_table(rows=5, cols=2)
meta.alignment = WD_TABLE_ALIGNMENT.LEFT
meta.autofit = False
meta.columns[0].width = Cm(3.5)
meta.columns[1].width = Cm(12.5)
remove_table_borders(meta)
for row_idx, (label, value) in enumerate((
    ("Disciplina", "DevSecOps preparatório E|CDE"),
    ("Turma e professor", "2TDCPF · Fabio Pires"),
    ("Líder técnico", "Tiago Louzã"),
    ("Integrantes", "Leando de Souza Silva · Luiz Fernando · Fabricio de Freitas Evangelista · Erik Gunnar"),
    ("Local e ano", "São Paulo 2026"),
)):
    for col, text in enumerate((label, value)):
        cell = meta.cell(row_idx, col)
        set_cell_margins(cell, 75, 0, 75, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(text), size=10.5, bold=(col == 0), color=(NAVY if col == 0 else BLACK))


# Identificação
page_break()
add_kicker("Dados do trabalho")
add_heading("Identificação do trabalho", 1)
add_table(["Campo", "Informação"], [
    ["Tema", "Ferramentas open source de SAST, SCA, IaC Security e DAST"],
    ["Ferramentas do Grupo 4", "Semgrep, OWASP Dependency-Check, Checkov e OWASP ZAP"],
    ["Alvo autorizado", "OWASP Juice Shop v20.2.0 em ambiente Docker local"],
    ["Laboratório principal", "Semgrep e OWASP ZAP, categorias diferentes"],
    ["Execuções complementares", "Dependency-Check e Checkov com relatórios versionados"],
    ["Política de gate", "Bloqueio de achados HIGH e CRITICAL"],
    ["Data da validação", "15 de setembro de 2026"],
], widths=[4.8, 11.2], font_size=9.6, first_col_bold=True)
add_heading("Síntese das execuções", 2)
add_status_table([
    ("Semgrep", "SAST", "Concluído", "69 achados no scan geral; red com 1 HIGH e green sem achados", GREEN),
    ("Dependency-Check", "SCA", "Inconclusivo", "15 dependências, 0 CVEs e cobertura reduzida por ausência de lockfiles", AMBER),
    ("Checkov", "IaC", "Concluído", "42 controles aprovados e 24 reprovados no Terraform oficial", GREEN),
    ("OWASP ZAP", "DAST", "Concluído", "11 tipos de alerta, com 1 HIGH; gate bloqueado", GREEN),
])
add_para("Todos os resultados foram mantidos em formatos legíveis e processáveis por máquina. Os relatórios JSON, SARIF e HTML permitem reproduzir a análise, revisar a classificação e demonstrar o gate mesmo quando o ambiente ao vivo não estiver disponível.")


# Resumo
page_break()
add_kicker("Visão executiva")
add_heading("Resumo", 1)
add_para("Este relatório compara Semgrep, OWASP Dependency-Check, Checkov e OWASP ZAP no pipeline DevSecOps e registra a execução das quatro ferramentas atribuídas ao Grupo 4. O alvo foi o OWASP Juice Shop v20.2.0, aplicação deliberadamente vulnerável e autorizada para treinamento. O ambiente foi isolado com Docker e os resultados foram preservados no repositório para auditoria e apresentação.")
add_para("O Semgrep foi executado com a configuração geral da comunidade, sem regra própria do grupo. O scan completo percorreu 1.027 arquivos, aplicou 408 regras e reportou 69 achados. A demonstração red e green manteve o mesmo --config auto e restringiu apenas o alvo a routes/search.ts: a regra comunitária de injeção via Sequelize produziu um ERROR normalizado como HIGH, a consulta foi parametrizada com replacements e a repetição do scan passou sem achados no arquivo corrigido.")
add_para("O Dependency-Check terminou em sete segundos, identificou 15 dependências e não reportou CVEs. Esse zero não foi tratado como evidência de segurança, pois o projeto analisado não continha os lockfiles nem node_modules necessários para um inventário completo, e quatro arquivos de teste geraram exceções. O Checkov, por sua vez, aplicou políticas nativas ao Terraform oficial do Juice Shop: 42 verificações passaram e 24 falharam, com problemas de exposição pública, HTTP sem redirecionamento para HTTPS, ausência de logs e falta de WAF.")
add_para("O ZAP executou spiders e active scan apenas contra o contêiner local. Foram descobertas 234 URLs pelo AJAX spider e registrados 11 tipos de alerta em 39 instâncias. A SQL Injection HIGH foi correlacionada com a linha de código identificada pelo Semgrep. O gate bloqueou os cenários vulneráveis e aprovou o recorte SAST corrigido. O resultado confirma que SAST, SCA, IaC Security e DAST respondem a perguntas diferentes e precisam coexistir, com critérios de cobertura e triagem explícitos.")
add_para("Palavras-chave: DevSecOps; SAST; SCA; IaC Security; DAST; Semgrep; Dependency-Check; Checkov; OWASP ZAP; quality gate.", indent=False)


# Sumário
page_break()
add_kicker("Navegação")
add_heading("Sumário", 1)
add_table(["Seção", "Página"], [[title, page] for title, page in TOC_PAGES.items()], widths=[13.5, 2.5], font_size=9.7, first_col_bold=True)
add_para("A numeração corresponde ao PDF validado. Os apêndices reúnem os comandos e o mapa completo das evidências versionadas.", indent=False)


# 1 Introdução
start_major(1, "Introdução", "Escopo e objetivos")
add_para("DevSecOps incorpora verificações de segurança ao desenvolvimento para reduzir o intervalo entre a introdução de uma falha e sua correção. O objetivo não é acumular scanners, mas posicionar controles com entradas, saídas e responsáveis definidos. O NIST SSDF recomenda que a organização prepare pessoas e processos, proteja o software, produza componentes seguros e responda a vulnerabilidades durante todo o ciclo [1].")
add_para("O trabalho do Grupo 4 cobre quatro frentes complementares. O Semgrep analisa o código escrito pela equipe; o Dependency-Check procura vulnerabilidades conhecidas nas dependências; o Checkov avalia configurações de infraestrutura como código; e o ZAP interage com a aplicação em execução. As quatro ferramentas são open source, automatizáveis e capazes de produzir resultados para integração contínua, mas operam sobre evidências diferentes.")
add_heading("Objetivo geral", 2)
add_para("Avaliar tecnicamente as quatro ferramentas atribuídas ao Grupo 4, executar cada uma em um alvo autorizado e demonstrar como os resultados podem interromper ou permitir a progressão de uma entrega.")
add_heading("Objetivos específicos", 2)
add_bullets([
    "Diferenciar SAST, SCA, IaC Security e DAST quanto à entrada, técnica, momento de execução e limitações.",
    "Registrar identificação, manutenção, licença, comunidade, instalação, formatos e integrações de cada ferramenta.",
    "Executar as quatro ferramentas e interpretar resultados, inclusive quando a cobertura for insuficiente.",
    "Demonstrar build red e green com Semgrep e um bloqueio DAST com OWASP ZAP.",
    "Classificar três achados como verdadeiro positivo ou falso positivo e propor correções verificáveis.",
])
page_break()
add_heading("Questão de pesquisa", 2)
add_para("Como um conjunto de ferramentas open source pode ampliar a cobertura de segurança sem transformar a pipeline em uma coleção de alertas sem contexto? A resposta adotada é combinar controles em camadas, preservar os relatórios originais e aplicar gates apenas quando a equipe consegue explicar o limiar, a cobertura e o tratamento de exceções.")


# 2 Fundamentos
start_major(2, "Fundamentos e posicionamento no pipeline", "SAST SCA IaC e DAST")
add_para("As categorias não competem pelo mesmo problema. SAST observa o código próprio antes da execução. SCA constrói um inventário de componentes de terceiros e correlaciona versões com vulnerabilidades publicadas. IaC Security interpreta arquivos declarativos que criarão recursos. DAST envia requisições a um sistema ativo e avalia respostas. A diferença entre SAST e SCA é especialmente importante: uma falha no código da equipe requer alteração de implementação; uma vulnerabilidade em dependência exige atualizar, substituir, remover ou mitigar um componente.")
add_table(["Categoria", "Pergunta respondida", "Entrada principal", "Aplicação ativa", "Estágio"], [
    ["SAST", "Existe padrão inseguro no código próprio?", "Código-fonte", "Não", "Code e Build"],
    ["SCA", "Há componente conhecido como vulnerável?", "Manifesto, lockfile e SBOM", "Não", "Build"],
    ["IaC", "A configuração provisionará recurso inseguro?", "Terraform e manifestos", "Não", "Code, Build e Deploy"],
    ["DAST", "O comportamento expõe falha acessível?", "Aplicação em execução", "Sim", "Test e Release"],
], widths=[2.2, 5.3, 3.6, 2.2, 2.7], font_size=8.7, first_col_bold=True)
add_heading("Shift left sem eliminar o DAST", 2)
add_para("Shift left antecipa feedback. Semgrep, Dependency-Check e Checkov podem rodar antes de um deploy, quando a correção tende a ser mais simples. Essa antecipação não substitui o ZAP. Um scanner estático não observa cabeçalhos emitidos pelo servidor, composição real de rotas, autenticação de sessão, proxies, variáveis de ambiente ou comportamento integrado. O DAST verifica o que ficou acessível após a montagem do sistema [2].")
add_heading("Cobertura em camadas", 2)
add_para("Uma pipeline eficiente separa verificações rápidas de verificações profundas. Regras locais e políticas de IaC podem executar em cada pull request. SCA completo exige inventário e atualização de bases. DAST precisa de um ambiente implantado e de tempo para descoberta. O gate deve considerar essas diferenças para não interpretar ausência de achados como cobertura total.")

start_continuation("SBOM e relação com SCA", "Inventário e rastreabilidade")
add_para("Uma Software Bill of Materials é uma lista estruturada de componentes, versões, fornecedores, identificadores e relações. Ela não é um scanner por si só. A SBOM fornece o inventário que permite perguntar onde um componente vulnerável aparece e quais produtos precisam de resposta. A CISA destaca elementos mínimos como autor do documento, fornecedor, nome, versão, identificadores, relações e data [3].")
add_para("O Dependency-Check pode complementar esse inventário ao tentar identificar componentes e associá-los a CPEs e CVEs. O CycloneDX fornece formatos padronizados para troca de SBOM [21]. A qualidade do SCA depende da qualidade do inventário: sem lockfile, a versão resolvida pode ser desconhecida; sem dependências instaladas, analisadores de ecossistema podem perder componentes; sem atualização da base, uma vulnerabilidade recente pode não aparecer.")
add_table(["Artefato", "O que registra", "Uso no pipeline", "Limitação"], [
    ["Manifesto", "Dependências declaradas", "Instalação e resolução", "Pode permitir intervalos de versão"],
    ["Lockfile", "Versões efetivamente resolvidas", "Reprodutibilidade e SCA", "Precisa estar atualizado"],
    ["SBOM", "Componentes e relações", "Inventário e resposta", "Não prova explorabilidade"],
    ["Relatório SCA", "Correspondências com vulnerabilidades", "Triagem e gate", "Pode ter falsos positivos e negativos"],
], widths=[3.0, 4.7, 4.0, 4.3], font_size=9.0, first_col_bold=True)
add_heading("Critério para gates", 2)
add_para("O gate deste laboratório usa severidade HIGH como limiar por ser simples de demonstrar. Em produção, a decisão precisa acrescentar confiança, alcance, exposição, existência de correção e validade da exceção. O resultado original permanece arquivado; a normalização serve para decidir a pipeline, não para apagar detalhes do scanner.")


# 3 Método
start_major(3, "Metodologia do laboratório", "Ambiente e critérios")
add_para("O laboratório foi executado em Windows com Docker Desktop. O alvo foi a release v20.2.0 do OWASP Juice Shop, autorizada pelo enunciado. O código oficial foi mantido em target/juice-shop. Uma cópia pontual de routes/search.ts foi criada em target/juice-shop-fixed para demonstrar a correção sem alterar a referência vulnerável usada pelo ZAP.")
add_heading("Escopo ético", 2)
add_para("Todos os testes ativos apontaram para o contêiner local do Juice Shop. O serviço foi publicado apenas em 127.0.0.1:3000 e o ZAP acessou o alvo pela rede interna do Compose. Nenhum domínio público, sistema de terceiros ou ambiente corporativo foi varrido. Essa restrição é parte do método, não apenas uma precaução operacional.")
add_heading("Sequência de execução", 2)
add_numbered([
    "Executar Semgrep com --config auto sobre o repositório completo e preservar JSON e log.",
    "Executar o cenário SAST red no arquivo vulnerável e confirmar que o gate bloqueia o HIGH.",
    "Aplicar a consulta parametrizada, repetir o scan e confirmar o cenário green.",
    "Executar Dependency-Check e registrar vulnerabilidades, exceções e limitações do inventário.",
    "Executar Checkov sobre o Terraform oficial com políticas nativas.",
    "Subir o Juice Shop, executar o plano de automação do ZAP e avaliar o JSON no mesmo gate.",
])
page_break()
add_table(["Ferramenta", "Versão executada", "Escopo", "Tempo observado"], [
    ["Semgrep", "1.172.0", "1.027 arquivos no geral; 1 arquivo no red e green", "cerca de 3 min no geral"],
    ["Dependency-Check", "13.0.0", "Juice Shop e exemplo SCA", "7 s"],
    ["Checkov", "3.3.11", "26 recursos Terraform", "cerca de 9 s"],
    ["OWASP ZAP", "2.17.0", "Juice Shop local", "active scan 3 min 48 s"],
], widths=[3.5, 2.8, 6.0, 3.7], font_size=9.1, first_col_bold=True)
add_para("Os tempos são medições do ambiente do grupo e não benchmarks universais. Cache de imagens, desempenho do host, quantidade de arquivos e atualização de bases alteram o resultado.", indent=False)


# 4 Semgrep
start_major(4, "Semgrep", "SAST")
add_heading("Identificação e atividade do projeto", 2)
add_table(["Atributo", "Informação"], [
    ["Mantenedor", "Semgrep Inc. e comunidade"],
    ["Licença do motor open source", "LGPL 2.1"],
    ["Início público", "2017"],
    ["Linguagens de implementação", "OCaml no motor e Python na CLI"],
    ["Comunidade em 15 set. 2026", "aprox. 16,7 mil estrelas, 1,1 mil forks e 10.297 commits"],
    ["Release atual na consulta", "v1.177.0, publicada em 10 set. 2026"],
    ["Versão do laboratório", "v1.172.0"],
], widths=[5.0, 11.0], font_size=9.4, first_col_bold=True)
add_para("O repositório oficial descreve Semgrep Community Edition como um mecanismo open source de análise estática e informa suporte a mais de 30 linguagens [5]. A sucessão de releases entre julho e setembro de 2026 indica manutenção frequente [7]. A edição comunitária cobre análise local; recursos proprietários acrescentam análise entre arquivos, regras comerciais e triagem hospedada.")
add_heading("Fundamento técnico", 2)
add_para("Semgrep transforma o código em uma representação sintática e compara essa estrutura com padrões semelhantes à própria linguagem. Isso evita depender apenas de texto ou expressão regular. As regras podem usar pattern matching, metavariáveis e, em modos compatíveis, análise de taint para representar origem, propagação, sanitização e destino de dados.")
add_para("A ferramenta detecta APIs perigosas, injeções, configurações inseguras, uso incorreto de bibliotecas e padrões específicos da equipe quando existe uma regra aplicável. A Community Edition não entende toda a semântica de execução e possui limites em fluxos entre funções e arquivos. Reflexão, geração dinâmica de código e regras ausentes podem produzir falsos negativos. Um match sintático também pode ser irrelevante quando aparece em teste, exemplo ou código inalcançável.")

start_continuation("Instalação configuração e integração", "Semgrep na prática")
add_heading("Instalação e formatos", 3)
add_para("O Semgrep pode ser instalado por pip, pipx, Homebrew e imagem Docker. O laboratório usou Docker para evitar dependências locais e fixar a versão. As saídas mais úteis para automação são JSON e SARIF; o terminal serve à execução guiada. O SARIF pode ser enviado ao GitHub Code Scanning, enquanto o JSON permite aplicar uma política própria.")
add_code("docker run --rm -v \"${ProjectDir}\\target\\juice-shop:/src/target/juice-shop\" `\n  -v \"${ProjectDir}\\reports:/src/reports\" semgrep/semgrep:1.172.0 `\n  semgrep scan --config auto --json `\n  --output /src/reports/semgrep-auto.json /src/target/juice-shop")
add_heading("Uso geral sem regra própria", 3)
add_para("A opção --config auto selecionou regras comunitárias compatíveis com as linguagens detectadas. Portanto, o scan geral não dependeu de uma regra criada pelo grupo. Essa é a forma mais próxima de um uso geral: ela oferece amplitude, mas também inclui achados de manutenção, exemplos, workflows e infraestrutura que exigem triagem.")
add_heading("Mesmo conjunto geral no red e green", 3)
add_para("O laboratório não possui arquivo de regra Semgrep criado pelo grupo. Tanto o código vulnerável quanto a cópia corrigida são analisados com --config auto. A demonstração limita somente o caminho a um arquivo para isolar o efeito da correção; o quality gate converte a severidade ERROR do Semgrep em HIGH. Em produção, o scan completo continua necessário, acompanhado de triagem, baseline e revisão de cobertura.")
add_heading("Baselines supressão IDE e pre commit", 3)
add_para("Semgrep permite ignorar trechos com nosemgrep, excluir caminhos, comparar com um commit de baseline e executar somente achados novos em CI. Supressões devem registrar justificativa e prazo; esconder um diretório inteiro reduz cobertura. Extensões de IDE e hooks de pre-commit oferecem feedback antes do push. Para repositórios grandes, recomenda-se um conjunto rápido no pre-commit e uma política mais ampla no CI [6].")

start_continuation("Execução geral e evidência de terminal", "Semgrep sem regra personalizada")
add_para("O scan geral considerou 1.074 regras comunitárias e executou 408 delas sobre 1.027 arquivos. Foram produzidos 69 achados: 18 ERROR, 46 WARNING, 2 MEDIUM e 3 INFO. O relatório também registrou 53 erros ou avisos de análise, em grande parte associados a snippets deliberadamente incompletos da aplicação de treinamento. A taxa de linhas analisadas foi próxima de 99,9%.")
add_figure(SEMGRP_SCREEN, 14.5, "Figura 1 Execução real do Semgrep com configuração auto", "captura de terminal do Grupo 4, 2026", "Terminal do PowerShell mostrando o scan geral do Semgrep concluído com 69 achados, 408 regras e 1.027 alvos")
add_para("A mensagem NativeCommandError no início da captura foi produzida pelo PowerShell 5.1 ao converter a saída stderr do processo Docker em um registro de erro durante o redirecionamento 2>&1. Ela não representa falha do scanner: a mesma captura mostra Scan completed successfully e o JSON foi gravado. Para uma apresentação mais limpa, o comando pode ser executado sem o redirecionamento combinado.", indent=False)

start_continuation("Resultados red e green correção e avaliação crítica", "Semgrep no quality gate")
add_heading("Resultado determinístico", 3)
add_table(["Cenário", "Arquivos", "Configuração", "Achados", "Decisão"], [["Red", "1", "auto", "1 HIGH", "Gate bloqueado"], ["Green", "1", "auto", "0", "Gate aprovado"]], widths=[3.2, 2.2, 2.8, 2.4, 5.4], font_size=9.3, first_col_bold=True)
add_heading("Código vulnerável", 3)
add_code("models.sequelize.query(`SELECT * FROM Products WHERE\n  ((name LIKE '%${criteria}%' OR description LIKE '%${criteria}%')\n  AND deletedAt IS NULL) ORDER BY name`)")
add_heading("Correção aplicada", 3)
add_code("models.sequelize.query(`SELECT * FROM Products WHERE\n  ((name LIKE :criteria OR description LIKE :criteria)\n  AND deletedAt IS NULL) ORDER BY name`,\n  { replacements: { criteria: `%${criteria}%` } })")
add_para("A correção separa o valor fornecido pelo usuário da estrutura da consulta. O marcador :criteria é resolvido pelo driver com replacements, reduzindo a possibilidade de o conteúdo alterar a sintaxe SQL. A validação green prova que a regra comunitária deixou de encontrar o fluxo inseguro naquele arquivo; não prova que todo o Juice Shop está seguro.")
add_heading("Falsos positivos e desempenho", 3)
add_para("As 69 ocorrências não foram integralmente classificadas, portanto não existe uma taxa geral confiável. No recorte da regra comunitária de injeção via Sequelize, seis matches foram encontrados: dois em rotas executáveis e quatro em data/static/codefixes, arquivos didáticos. Para o risco de produção, esses quatro são ruído operacional, o que corresponde a 66,7% no recorte. Ao analisar apenas a rota escolhida para o red/green, o resultado vulnerável foi um verdadeiro positivo e a versão parametrizada não gerou match. Os dois cenários executaram 210 regras comunitárias; o tempo interno foi 4,242 s no red e 3,542 s no green.")
add_para("Ponto forte: criação rápida de regras e feedback próximo ao código. Limitação: a cobertura depende do conjunto de regras e do contexto disponível. Cenário ideal: revisão de pull request, IDE e gates de padrões que a equipe consegue testar. Alternativas incluem OpenGrep, CodeQL e SonarQube; o Semgrep foi escolhido pela execução local simples, regras legíveis e bom encaixe no laboratório.")


# 5 Dependency Check
page_break()
start_major(5, "OWASP Dependency Check", "SCA")
add_heading("Identificação e atividade do projeto", 2)
add_table(["Atributo", "Informação"], [
    ["Mantenedor", "OWASP Dependency-Check, Jeremy Long e comunidade"], ["Licença", "Apache 2.0"], ["Ano de criação", "2012"], ["Linguagem principal", "Java"],
    ["Comunidade em 15 set. 2026", "aprox. 7,7 mil estrelas, 1,4 mil forks e 11.258 commits"], ["Release atual e executada", "v13.0.0, publicada em 3 ago. 2026"],
], widths=[5.0, 11.0], font_size=9.4, first_col_bold=True)
add_para("Dependency-Check é um utilitário de Software Composition Analysis que tenta identificar componentes e associá-los a CPEs para consultar vulnerabilidades publicadas [8]. A versão 13.0.0 estava atual na data do laboratório [10]. O projeto mantém CLI e integrações com Maven, Gradle, Ant e Jenkins.")
add_heading("Fundamento técnico", 2)
add_para("A ferramenta usa analisadores por tipo de arquivo e ecossistema para coletar evidências de nome, fornecedor e versão. Em seguida, tenta resolver identificadores de plataforma e consulta dados de vulnerabilidade, principalmente do NVD. A correspondência não é uma prova automática de explorabilidade. Nomes genéricos, componentes empacotados e metadados incompletos podem produzir CPEs errados ou deixar de identificar a versão real.")
add_para("O Dependency-Check detecta CVEs conhecidos quando consegue identificar o componente. Ele não encontra uma falha inédita no código próprio, não verifica configuração de nuvem e não ataca a aplicação. Também não substitui análise de alcance: uma biblioteca pode estar presente sem que a função vulnerável seja chamada. O sentido inverso também ocorre, pois um inventário incompleto gera falso negativo.")
add_heading("Bases e atualização", 2)
add_para("A documentação recomenda chave de API do NVD e cache para CI, pois downloads completos e limites de requisição podem aumentar o tempo [8]. O laboratório usou uma imagem já disponível e --noupdate para evitar dependência de rede. Essa decisão tornou a execução rápida, mas vinculou o resultado à base existente na imagem. Em produção, a base precisa de atualização controlada e monitorada.")

start_continuation("Instalação uso integração e tratamento de exceções", "Dependency Check na prática")
add_heading("Formas de execução", 3)
add_para("A ferramenta pode ser executada por CLI, Docker, Homebrew, Maven, Gradle, Ant e Jenkins. Os formatos incluem HTML, JSON, XML, CSV, JUnit, SARIF, GitLab e Jenkins. O parâmetro failOnCVSS ou seu equivalente no plugin permite falhar o build por pontuação, mas deve ser combinado com supressões revisadas e cobertura comprovada.")
add_code("dependency-check --scan /src --out /report --format ALL `\n  --project \"Checkpoint DevSecOps Grupo 4\" `\n  --noupdate --disableOssIndex --enableExperimental")
add_heading("Supressões e baselines", 3)
add_para("Falsos positivos podem ser tratados com um arquivo XML de suppression que registra CVE, CPE, pacote ou hash. Uma supressão útil inclui motivo e data de expiração. A equipe também pode comparar resultados com um baseline aprovado e bloquear apenas novas vulnerabilidades acima do limiar. Suprimir porque o build precisa passar, sem documentar alcance ou mitigação, remove o controle.")
add_heading("Integração", 3)
add_para("Maven e Gradle permitem executar a análise no ciclo de build; Jenkins possui plugin; a CLI funciona em GitHub Actions, GitLab CI e outros runners. O SARIF pode alimentar Code Scanning e plataformas que aceitam o padrão. O DefectDojo possui importadores para relatórios de Dependency-Check. A ferramenta não tem o mesmo encaixe de um linter em IDE ou pre-commit: a atualização de bases e a resolução de dependências tornam o CI ou um job agendado mais apropriado.")
add_heading("Dependência do inventário", 3)
add_para("Para Node.js, o lockfile e o diretório de dependências ajudam a determinar versões efetivas. O enunciado pede interpretação crítica, portanto um relatório vazio precisa ser confrontado com os avisos de cobertura. Esse ponto foi decisivo na execução do grupo.")

start_continuation("Resultado observado e interpretação", "Dependency Check executado")
add_para("A versão 13.0.0 analisou 15 dependências em sete segundos e reportou zero vulnerabilidades. Quatro exceções apareceram ao abrir arquivos propositalmente malformados ou ofensivos usados pelos testes do Juice Shop: dois ZIPs com tentativa de path traversal, um ZIP criptografado e um executável truncado. Esses erros não são CVEs do projeto; são limitações do processamento desses arquivos.")
add_figure(DEPENDENCY_SCREEN, 14.5, "Figura 2 Relatório HTML real do OWASP Dependency Check", "relatório gerado pelo Grupo 4, 2026", "Relatório HTML do Dependency-Check mostrando 15 dependências, zero vulnerabilidades e quatro exceções de análise")
add_heading("Por que o resultado é inconclusivo", 3)
add_para("O log informou que package-lock.json não estava presente e que node_modules não existia em dois projetos Node. A própria ferramenta alertou que essa condição pode produzir falsos negativos. Além disso, o modo --noupdate utilizou uma base previamente armazenada e o OSS Index foi desabilitado. Assim, zero CVEs significa apenas que nenhuma correspondência foi encontrada na cobertura disponível.")
page_break()
add_table(["Métrica", "Resultado", "Leitura correta"], [
    ["Dependências identificadas", "15", "Inventário parcial"], ["Vulnerabilidades", "0", "Não autoriza concluir que o projeto está seguro"],
    ["Exceções", "4", "Arquivos de teste não analisados"], ["Tempo", "7 s", "Rápido porque não atualizou as bases"],
    ["Taxa de falso positivo", "não calculável", "Não houve achado de vulnerabilidade para classificar"],
], widths=[4.0, 3.1, 8.9], font_size=9.1, first_col_bold=True)
add_para("Ponto forte: integração madura com builds Java e relatórios amplos. Limitação observada: forte dependência de inventário e bases. Cenário ideal: projeto com lockfiles, dependências resolvidas, cache atualizado e chave NVD. Alternativas incluem Trivy, Grype, OSV-Scanner e ferramentas nativas do ecossistema. O Dependency-Check permanece útil como uma fonte, mas o resultado deve ser combinado com SBOM e outro mecanismo de SCA quando a cobertura do ecossistema for limitada.")


# 6 Checkov
start_major(6, "Checkov", "IaC Security")
add_heading("Identificação e atividade do projeto", 2)
add_table(["Atributo", "Informação"], [
    ["Mantenedor", "Prisma Cloud da Palo Alto Networks e comunidade"], ["Licença", "Apache 2.0"], ["Ano de criação", "2019"], ["Linguagem principal", "Python"],
    ["Comunidade em 15 set. 2026", "aprox. 9,0 mil estrelas, 1,4 mil forks e 17.433 commits"], ["Release atual na consulta", "v3.3.17, publicada em 10 set. 2026"], ["Versão do laboratório", "v3.3.11"],
], widths=[5.0, 11.0], font_size=9.4, first_col_bold=True)
add_para("Checkov é um analisador estático de infraestrutura como código mantido pela Prisma Cloud. O projeto informa mais de mil políticas embutidas e suporte a Terraform, planos Terraform, CloudFormation, Kubernetes, Helm, Kustomize, Dockerfile, Bicep, OpenTofu e arquivos de pipelines [11]. A frequência de releases e o volume de commits mostram atividade contínua; a versão 3.3.17 foi publicada cinco dias antes da consulta [13].")
add_heading("Fundamento técnico", 2)
add_para("A ferramenta interpreta os arquivos declarativos, cria uma representação dos recursos e aplica políticas Python ou YAML. Algumas verificações examinam atributos locais; outras usam um grafo para avaliar relações, como uma sub-rede ligada a um recurso público. O resultado indica check, recurso, arquivo, linhas, orientação e documentação.")
add_para("Checkov detecta configurações incompatíveis com boas práticas ou normas codificadas: portas abertas, criptografia ausente, logs desabilitados, containers privilegiados e pipelines permissivas. Ele não prova que o recurso foi implantado, não vê alterações manuais posteriores e pode desconhecer controles externos aplicados pela organização. Variáveis não resolvidas e módulos remotos também afetam precisão.")

start_continuation("Instalação políticas integração e supressões", "Checkov na prática")
add_heading("Instalação e formatos", 3)
add_para("Checkov pode ser instalado por pip, pipx, Homebrew, Docker e action de CI. O laboratório usou a imagem ghcr.io/bridgecrewio/checkov:3.3.11. A ferramenta gera CLI, JSON, JUnit XML, CSV, SARIF, CycloneDX e Markdown para GitHub, conforme o tipo de scan [11].")
add_code("docker run --rm `\n  -v \"${ProjectDir}\\target\\juice-shop\\terraform:/tf:ro\" `\n  ghcr.io/bridgecrewio/checkov:3.3.11 -d /tf `\n  --framework terraform --quiet --compact --soft-fail")
add_heading("Políticas gerais sem regra própria", 3)
add_para("A execução utilizou somente políticas nativas. Nenhuma regra do grupo foi necessária para encontrar problemas. O argumento --framework terraform limitou a tecnologia e --compact reduziu o volume. --soft-fail fez o processo devolver sucesso para que a saída pudesse ser fotografada e analisada; ele não transformou as 24 falhas em aprovações.")
add_heading("Regras próprias e exceções", 3)
add_para("Políticas personalizadas podem ser escritas em Python ou YAML e carregadas por diretório. Uma regra pode representar um requisito interno que não existe no catálogo. O comentário checkov:skip permite suprimir um check em um recurso, e --skip-check exclui IDs. A justificativa deve acompanhar a exceção. A configuração .checkov.yml centraliza frameworks, formatos, diretórios e política de falha.")
add_heading("CI IDE e pre commit", 3)
add_para("Checkov possui exemplos de GitHub Actions, GitLab e outros sistemas, integração por SARIF com Code Scanning e suporte a pre-commit. A extensão da Prisma Cloud oferece feedback em VS Code. O melhor ponto de execução é antes do merge e novamente sobre o plano final no estágio de deploy, pois variáveis podem mudar o recurso resultante. Resultados SARIF ou JSON podem ser enviados a plataformas de gestão como DefectDojo.")

start_continuation("Resultado do Terraform oficial do Juice Shop", "Checkov executado")
add_para("O scan analisou 26 recursos Terraform e aplicou 66 verificações: 42 passaram, 24 falharam e nenhuma foi ignorada. Não houve erro de parsing. A captura abaixo mostra a execução real e os primeiros controles reprovados.")
add_figure(CHECKOV_SCREEN, 15.8, "Figura 3 Execução real do Checkov no Terraform", "captura de terminal do Grupo 4, 2026", "Terminal do PowerShell mostrando Checkov com 42 verificações aprovadas, 24 reprovadas e zero ignoradas")
page_break()
add_heading("Falhas priorizadas", 3)
add_table(["Check", "Recurso", "Condição observada", "Tratamento"], [
    ["CKV_AWS_333", "ECS service", "IP público atribuído", "Executar em sub-rede privada"],
    ["CKV_AWS_260", "Security group ALB", "Porta 80 aberta para 0.0.0.0/0", "Restringir ou redirecionar"],
    ["CKV_AWS_2", "ALB listener", "Protocolo HTTP", "Configurar HTTPS e certificado"],
    ["CKV_AWS_91", "Application Load Balancer", "Access logs ausentes", "Habilitar logs em bucket protegido"],
    ["CKV2_AWS_11", "VPC", "Flow logs ausentes", "Habilitar VPC Flow Logs"],
    ["CKV2_AWS_28", "ALB público", "WAF ausente", "Associar Web ACL"],
], widths=[2.7, 3.8, 5.0, 4.5], font_size=8.6, first_col_bold=True)
add_heading("Avaliação crítica", 3)
add_para("Os seis controles priorizados foram confirmados no Terraform e não foram classificados como falsos positivos na amostra. Os 18 restantes não passaram por validação manual completa, portanto não é correto declarar taxa zero para o conjunto inteiro. O tempo aproximado de nove segundos torna o Checkov adequado a pull requests. O ponto forte é a ampla biblioteca de políticas; a limitação é que uma recomendação genérica pode conflitar com arquitetura, compensações ou módulos externos. Alternativas incluem KICS, Terrascan, tfsec incorporado ao Trivy e Conftest/OPA.")


# 7 ZAP
start_major(7, "OWASP ZAP", "DAST")
add_heading("Identificação e atividade do projeto", 2)
add_table(["Atributo", "Informação"], [
    ["Mantenedor", "ZAP Core Team com apoio da Checkmarx e comunidade"], ["Licença", "Apache 2.0"], ["Ano de criação", "2010"], ["Linguagem principal", "Java"],
    ["Comunidade em 15 set. 2026", "aprox. 15,8 mil estrelas, 2,6 mil forks e 10.387 commits"], ["Release estável atual e executada", "v2.17.0, publicada em 15 dez. 2025"], ["Cadência adicional", "builds weekly e add-ons atualizados separadamente"],
], widths=[5.0, 11.0], font_size=9.4, first_col_bold=True)
add_para("ZAP é um proxy de interceptação e scanner de aplicações web mantido pelo ZAP Core Team [14]. Pode ser usado de forma interativa por analistas ou de modo headless em CI. A release 2.17.0 introduziu melhorias de desempenho e redução de alertas duplicados [17]. O ecossistema de add-ons atualiza spiders, regras e integrações sem depender somente de uma nova versão do core.")
add_heading("Fundamento técnico", 2)
add_para("O DAST observa HTTP e HTTPS sem ler o código-fonte. O spider tradicional segue links e formulários; o AJAX spider controla um navegador para aplicações modernas; o passive scanner analisa mensagens sem alterar requisições; o active scanner envia payloads e procura diferenças compatíveis com vulnerabilidades. O fuzzer permite variar entradas de forma controlada.")
add_para("ZAP detecta cabeçalhos ausentes, exposição de informações, configurações de cookie, injeções e outras falhas alcançáveis pelas rotas descobertas. Ele não encontra código não exposto, depende de autenticação e navegação adequadas e pode interpretar uma resposta anormal como vulnerabilidade. Rate limits, dados destrutivos e estados de negócio exigem configuração cuidadosa.")

start_continuation("Automação regras integração e controle de escopo", "ZAP na prática")
add_heading("Formas de instalação", 3)
add_para("ZAP oferece instaladores, pacotes multiplataforma, Snap, Flatpak e imagens Docker. O laboratório usou ghcr.io/zaproxy/zaproxy:2.17.0. O Automation Framework lê um plano YAML com contexto, spiders, scanners, relatórios e exit status [15]. As saídas preservadas foram HTML, JSON e SARIF.")
add_heading("Plano sem regra de detecção própria", 3)
add_para("O arquivo security/zap-juice-shop.yaml não cria uma assinatura. Ele define URL, contexto, duração e seleciona duas regras ativas já fornecidas pelo ZAP: 40012 para XSS refletido e 40018 para SQL Injection. Portanto, a detecção é geral e nativa; o YAML apenas torna a execução previsível para o laboratório.")
add_code("jobs:\n  - type: spider\n    parameters: { maxDuration: 1 }\n  - type: spiderAjax\n    parameters: { maxDuration: 2, maxCrawlDepth: 5 }\n  - type: activeScan\n    parameters: { maxScanDurationInMins: 4 }\n    policyDefinition:\n      rules: [ { id: 40012 }, { id: 40018 } ]")
add_heading("Integração e supressões", 3)
add_para("ZAP pode rodar por baseline scan, full scan, API scan, Automation Framework e GitHub Action. SARIF integra os achados ao Code Scanning, e relatórios ZAP podem ser importados no DefectDojo. A ferramenta não é adequada a pre-commit, pois exige aplicação ativa. Em IDE, o uso é indireto por proxy e testes manuais. Falsos positivos podem ser tratados com alert filters no contexto; a exceção deve indicar URL, regra, evidência e validade.")
add_heading("Segurança operacional", 3)
add_para("Active scan envia payloads potencialmente destrutivos. O alvo deve ser autorizado, isolado e descartável. Contas de teste e dados sintéticos evitam dano. O plano do grupo usa rede local, limite de tempo e apenas duas regras ativas para caber na apresentação.")

start_continuation("Resultados do scan dinâmico", "OWASP ZAP executado")
add_para("O spider tradicional encontrou 101 URLs em 18 segundos. O AJAX spider encontrou 234 URLs em 37 segundos. O active scan durou 3 minutos e 48 segundos. O relatório consolidou 11 tipos de alerta em 39 instâncias: 1 High, 4 Medium, 3 Low e 3 Informational. O gate encontrou um bloqueador e rejeitou o cenário.")
add_figure(ZAP_SCREEN, 14.0, "Figura 4 Resumo HTML real do OWASP ZAP", "relatório gerado pelo Grupo 4, 2026", "Relatório HTML do ZAP mostrando um alerta High, quatro Medium, três Low e três Informational")
add_table(["Risco", "Plugin", "Alerta", "Instâncias", "Confiança"], [
    ["High", "40018", "SQL Injection", "1", "Low"], ["Medium", "10038", "CSP Header Not Set", "5", "High"],
    ["Medium", "10098", "Cross-Domain Misconfiguration", "5", "Medium"], ["Medium", "10020", "Missing Anti-clickjacking Header", "3", "Medium"],
    ["Medium", "3", "Session ID in URL Rewrite", "5", "High"],
], widths=[2.2, 2.2, 6.7, 2.3, 2.6], font_size=8.8, first_col_bold=True)
add_para("A confiança baixa do alerta SQL Injection impede tratá-lo isoladamente como prova. A correlação com o Semgrep mostra o mesmo parâmetro chegando a uma consulta interpolada e sustenta a classificação como verdadeiro positivo. Entre os três alertas revisados manualmente, nenhum foi descartado como falso positivo; os oito restantes não foram integralmente reproduzidos. O principal ponto forte do ZAP é observar o sistema montado. As limitações são tempo, cobertura de navegação, autenticação e ruído. Alternativas incluem Wapiti, Nuclei e Nikto, com escopos e técnicas diferentes.")


# 8 Achados
start_major(8, "Análise dos achados", "Verdadeiros e falsos positivos")
add_heading("Achado 1 SQL Injection na busca", 2)
add_table(["Campo", "Análise"], [
    ["Evidência", "Semgrep em routes/search.ts:23 e ZAP plugin 40018 no parâmetro q"], ["Classificação", "Verdadeiro positivo"],
    ["CWE", "CWE-89 Improper Neutralization of Special Elements used in an SQL Command"], ["Impacto", "Alteração da lógica da consulta e possível acesso indevido a dados"],
    ["Correção", "Consulta parametrizada com :criteria e replacements; menor privilégio no banco"], ["Validação", "Semgrep green sem achados no arquivo corrigido; novo DAST recomendado"],
], widths=[4.0, 12.0], font_size=9.3, first_col_bold=True)
add_para("O código concatenava criteria dentro de um template SQL. O ZAP enviou um payload ao endpoint e observou resposta compatível com injeção, porém marcou confiança baixa. A evidência estática remove a principal ambiguidade do alerta dinâmico. A correção aplicada segue o princípio de separar dados e comando; escape manual ou blacklist de caracteres não oferecem a mesma garantia [4][19].")
add_heading("Achado 2 listener HTTP no load balancer", 2)
add_table(["Campo", "Análise"], [
    ["Evidência", "Checkov CKV_AWS_2 em aws_lb_listener.http"], ["Classificação", "Verdadeiro positivo"], ["CWE", "CWE-319 Cleartext Transmission of Sensitive Information"],
    ["Impacto", "Tráfego e credenciais podem ser expostos ou alterados em trânsito"], ["Correção", "Listener HTTPS com certificado; redirecionamento permanente de HTTP para HTTPS"],
    ["Validação", "Reexecutar Checkov no plano e testar redirecionamento no ambiente"],
], widths=[4.0, 12.0], font_size=9.3, first_col_bold=True)
add_para("O Terraform define um listener HTTP e um target group HTTP. Como o recurso está voltado para exposição pública, a ausência de TLS no frontend não é apenas uma preferência de política. A correção deve incluir certificado válido e redirecionamento, além de confirmar se o tráfego interno também precisa de criptografia.")

start_continuation("Achado 3 ocorrência em snippet didático", "Triagem de contexto")
add_table(["Campo", "Análise"], [
    ["Evidência", "Regra comunitária do Semgrep em data/static/codefixes/unionSqlInjectionChallenge_1.ts"], ["Classificação", "Falso positivo operacional para o código implantado"],
    ["CWE", "CWE-89 no padrão sintático encontrado"], ["Justificativa", "O arquivo é um exemplo didático armazenado como conteúdo de desafio, não uma rota executada pelo servidor"],
    ["Tratamento", "Excluir o caminho didático do gate, sem remover a regra das rotas reais"], ["Validação", "Confirmar no build que o arquivo não compõe o bundle executável"],
], widths=[4.0, 12.0], font_size=9.3, first_col_bold=True)
add_para("A regra encontrou corretamente uma construção insegura, mas o contexto muda a decisão. Classificar o item como falso positivo operacional não significa que a regra está errada; significa que o arquivo não representa uma superfície executável no alvo. Uma exclusão precisa ser específica para data/static/codefixes. Ignorar toda ocorrência de SQL Injection ocultaria routes/search.ts e routes/login.ts.")
add_heading("Resumo da triagem", 2)
add_table(["Achado", "Ferramenta", "VP ou FP", "Prioridade", "Próxima ação"], [
    ["SQL Injection na busca", "Semgrep e ZAP", "VP", "Alta", "Parametrizar e retestar"], ["Listener HTTP", "Checkov", "VP", "Alta", "HTTPS e redirecionamento"],
    ["SQLi em codefix didático", "Semgrep", "FP operacional", "Baixa", "Excluir somente o caminho"],
], widths=[4.3, 3.0, 2.7, 2.3, 3.7], font_size=8.9, first_col_bold=True)
add_heading("Critério de análise", 2)
add_para("A classificação considerou existência da condição, alcance no artefato implantado, evidência independente e possibilidade de reprodução. O mesmo alerta pode mudar de prioridade quando a exposição, o dado processado ou um controle compensatório muda. Por isso, a triagem deve permanecer associada à versão do código e do ambiente.")


# 9 Comparação
start_major(9, "Comparação e escolha do toolchain", "Avaliação transversal")
add_table(["Critério", "Semgrep", "Dependency Check", "Checkov", "OWASP ZAP"], [
    ["Entrada", "Código", "Dependências", "IaC", "Aplicação ativa"], ["Técnica", "AST, padrões e taint", "Evidência, CPE e CVE", "Políticas e grafo", "Spider, proxy e payloads"],
    ["Velocidade no laboratório", "~3 min geral", "7 s", "~9 s", "~4 min 48 s"], ["Formato principal", "JSON e SARIF", "HTML, JSON e SARIF", "CLI, JSON e SARIF", "HTML, JSON e SARIF"],
    ["Melhor estágio", "Code e Build", "Build", "Code e Deploy", "Test e Release"], ["Limitação observada", "Ruído em snippets", "Inventário incompleto", "Política sem contexto", "Cobertura e confiança"],
    ["Resultado", "69 geral; red 1 e green 0", "0 CVEs, inconclusivo", "42 pass e 24 fail", "11 tipos; 1 High"],
], widths=[3.0, 3.25, 3.25, 3.25, 3.25], font_size=7.8, first_col_bold=True)
add_heading("Recomendação do Grupo 4", 2)
add_para("O toolchain recomendado mantém as quatro ferramentas. Semgrep e Checkov executam em pull requests por oferecerem feedback rápido. Dependency-Check executa após a resolução das dependências, com cache atualizado e lockfiles presentes. ZAP roda contra um ambiente efêmero após o deploy de teste. Um job agendado pode ampliar regras e tempo sem atrasar todo commit.")
add_table(["Momento", "Controle", "Gate recomendado"], [
    ["Pre-commit e IDE", "Semgrep rápido e Checkov nos arquivos alterados", "Aviso local; sem depender de rede"], ["Pull request", "Semgrep e Checkov completos", "Bloquear novos HIGH e CRITICAL"],
    ["Build", "Dependency-Check com lockfile e base atualizada", "CVSS, alcance e exceções válidas"], ["Ambiente de teste", "ZAP autenticado e limitado ao alvo", "Risco, confiança e reprodução"],
    ["Agendado", "Scans amplos das quatro ferramentas", "Abrir backlog e revisar baselines"],
], widths=[3.5, 7.0, 5.5], font_size=9.0, first_col_bold=True)
add_para("A principal razão para manter ferramentas especializadas é preservar a pergunta de cada controle. Um resultado unificado ajuda a priorizar, mas não deve reduzir SCA, IaC e DAST a um único número. O relatório original continua necessário para entender cobertura e corrigir o problema certo.")


# 10 Pipeline
start_major(10, "Integração contínua e quality gate", "Build red e build green")
add_para("O workflow .github/workflows/devsecops.yml contém dois jobs independentes. O primeiro executa o Semgrep no cenário vulnerável, confirma que o gate bloqueia e depois repete sobre a cópia corrigida. O segundo sobe o Juice Shop local, executa o ZAP e confirma o bloqueio. Os relatórios são publicados com if: always para permanecerem disponíveis mesmo quando a decisão de segurança é negativa.")
add_table(["Cenário", "Relatório", "Bloqueadores", "Resultado esperado"], [
    ["SAST red", "semgrep-red.json", "1 HIGH", "Teste comprova gate bloqueado"], ["SAST green", "semgrep-green.json", "0", "Gate aprovado"], ["DAST", "zap-juice-shop.json", "1 HIGH", "Teste comprova gate bloqueado"],
], widths=[3.5, 5.0, 3.0, 4.5], font_size=9.2, first_col_bold=True)
add_heading("Normalização", 2)
add_para("O script scripts/quality-gate.mjs converte severidades do Semgrep e riskcode do ZAP para LOW, MEDIUM, HIGH e CRITICAL. O limiar padrão é HIGH. No modo expect fail, o teste termina com sucesso somente quando encontra um bloqueador; isso permite demonstrar o build vermelho sem transformar a validação do laboratório em falha acidental do workflow.")
add_heading("Ampliação para SCA e IaC", 2)
add_para("Checkov pode entrar em um terceiro job e remover --soft-fail quando a política estiver acordada. Dependency-Check deve ser adicionado depois da geração do lockfile e instalação das dependências, com dados do NVD em cache. Adicionar o SCA antes de corrigir a cobertura apenas automatizaria um falso sentimento de segurança.")
add_heading("Governança do gate", 2)
add_bullets([
    "Bloquear achados novos acima do limiar e preservar o relatório completo.", "Exigir responsável, motivo e data de expiração para exceções.",
    "Distinguir erro da ferramenta, falta de cobertura e ausência real de achados.", "Medir idade, reincidência, tempo de correção, cobertura e falsos positivos triados.",
    "Reavaliar baselines quando a regra, a versão da ferramenta ou a exposição mudar.",
])
add_para("A política técnica só funciona quando existe um caminho de correção. Um gate que bloqueia sem publicar localização, evidência e orientação transfere o problema para o fim do processo. O desenho do grupo mantém JSON para decisão automática, SARIF para revisão e HTML para leitura e plano B.")


# 11 Conclusão
start_major(11, "Limitações e conclusão", "Síntese crítica")
add_heading("Limitações do experimento", 2)
add_bullets([
    "O Semgrep geral gerou 69 achados, mas somente recortes prioritários foram triados manualmente.", "O red e green do Semgrep analisou um arquivo para garantir execução previsível durante a apresentação.",
    "O Dependency-Check não recebeu lockfiles nem node_modules e foi executado sem atualizar a base.", "O Checkov avaliou o Terraform oficial, não um plano resolvido nem recursos já implantados.",
    "O ZAP não autenticou usuários e limitou o active scan a quatro minutos e duas regras ativas.", "A imagem oficial do Juice Shop permaneceu vulnerável; o green foi uma cópia usada apenas pelo SAST.",
])
page_break()
add_heading("Conclusão", 2)
add_para("As quatro ferramentas foram executadas e produziram resultados distintos. O Semgrep ofereceu ampla visibilidade do código e comprovou uma correção específica. O Dependency-Check mostrou, pela ausência de inventário suficiente, que um scan concluído pode continuar inconclusivo. O Checkov revelou 24 desvios concretos no Terraform. O ZAP observou o sistema em execução e encontrou um alerta HIGH correlacionável ao código.")
add_para("A correlação mais forte foi a SQL Injection da busca. Semgrep mostrou a interpolação na consulta; ZAP mostrou o endpoint respondendo de forma compatível com um payload de injeção; a consulta parametrizada removeu o padrão no cenário green. Essa sequência fornece evidência de achado, correção e verificação, sem afirmar que um único teste tornou a aplicação segura.")
add_para("O Grupo 4 recomenda executar Semgrep e Checkov cedo, Dependency-Check com inventário completo no build e ZAP em um ambiente local ou efêmero de teste. Gates devem tratar HIGH e CRITICAL, mas também precisam registrar cobertura, confiança e exceções. A combinação oferece defesa em profundidade porque cada ferramenta enxerga uma parte que as outras não observam.")
add_heading("Orientação para a apresentação", 2)
add_para("Na apresentação, mostrar o Semgrep geral, o red e green da consulta e o relatório do ZAP. Checkov entra com as 24 falhas e Dependency-Check como exemplo de cobertura insuficiente. Essa leitura demonstra domínio técnico além das contagens.")


# Referências
page_break()
add_kicker("Fontes primárias e normas")
add_heading("Referências", 1)
references = [
    "[1] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Secure Software Development Framework SSDF Version 1.1: Recommendations for Mitigating the Risk of Software Vulnerabilities. Gaithersburg, 2022. Disponível em: https://csrc.nist.gov/pubs/sp/800/218/final. Acesso em: 15 set. 2026.",
    "[2] OWASP FOUNDATION. DevSecOps Guideline: Vulnerability Scanning. Disponível em: https://owasp.org/www-project-devsecops-guideline/latest/02-Vulnerability-Scanning.html. Acesso em: 15 set. 2026.",
    "[3] CYBERSECURITY AND INFRASTRUCTURE SECURITY AGENCY. 2025 Minimum Elements for a Software Bill of Materials. Washington, 2025. Disponível em: https://www.cisa.gov/resources-tools/resources/2025-minimum-elements-software-bill-materials-sbom. Acesso em: 15 set. 2026.",
    "[4] MITRE. CWE-89: Improper Neutralization of Special Elements used in an SQL Command. Disponível em: https://cwe.mitre.org/data/definitions/89.html. Acesso em: 15 set. 2026.",
    "[5] SEMGREP. Semgrep repository. GitHub, 2026. Disponível em: https://github.com/semgrep/semgrep. Acesso em: 15 set. 2026.",
    "[6] SEMGREP. Continuous integration documentation. Disponível em: https://semgrep.dev/docs/semgrep-ci/overview. Acesso em: 15 set. 2026.",
    "[7] SEMGREP. Release v1.177.0. GitHub, 10 set. 2026. Disponível em: https://github.com/semgrep/semgrep/releases/tag/v1.177.0. Acesso em: 15 set. 2026.",
    "[8] OWASP DEPENDENCY-CHECK. Official repository and usage documentation. GitHub, 2026. Disponível em: https://github.com/dependency-check/DependencyCheck. Acesso em: 15 set. 2026.",
    "[9] OWASP DEPENDENCY-CHECK. Command Line Arguments. Disponível em: https://dependency-check.github.io/DependencyCheck/dependency-check-cli/arguments.html. Acesso em: 15 set. 2026.",
    "[10] OWASP DEPENDENCY-CHECK. Version 13.0.0. GitHub, 3 ago. 2026. Disponível em: https://github.com/dependency-check/DependencyCheck/releases/tag/v13.0.0. Acesso em: 15 set. 2026.",
    "[11] BRIDGECREW. Checkov repository. GitHub, 2026. Disponível em: https://github.com/bridgecrewio/checkov. Acesso em: 15 set. 2026.",
    "[12] CHECKOV. Output formats. Disponível em: https://www.checkov.io/8.Outputs/Output%20Formats.html. Acesso em: 15 set. 2026.",
    "[13] BRIDGECREW. Checkov release 3.3.17. GitHub, 10 set. 2026. Disponível em: https://github.com/bridgecrewio/checkov/releases/tag/3.3.17. Acesso em: 15 set. 2026.",
    "[14] ZAPROXY. ZAP core repository. GitHub, 2026. Disponível em: https://github.com/zaproxy/zaproxy. Acesso em: 15 set. 2026.",
    "[15] ZAPROXY. Automation Framework. Disponível em: https://www.zaproxy.org/docs/automate/automation-framework/. Acesso em: 15 set. 2026.",
    "[16] ZAPROXY. ZAP Docker images. Disponível em: https://www.zaproxy.org/docs/docker/about/. Acesso em: 15 set. 2026.",
    "[17] ZAPROXY. ZAP 2.17.0. 15 dez. 2025. Disponível em: https://www.zaproxy.org/blog/2025-12-15-zap-2-17-0/. Acesso em: 15 set. 2026.",
    "[18] OWASP JUICE SHOP. Release v20.2.0. GitHub, 2026. Disponível em: https://github.com/juice-shop/juice-shop/releases/tag/v20.2.0. Acesso em: 15 set. 2026.",
    "[19] OWASP FOUNDATION. OWASP Top 10: A03 Injection. Disponível em: https://owasp.org/Top10/A03_2021-Injection/. Acesso em: 15 set. 2026.",
    "[20] GITHUB. Uploading a SARIF file to GitHub. Disponível em: https://docs.github.com/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github. Acesso em: 15 set. 2026.",
    "[21] OWASP FOUNDATION. CycloneDX. Disponível em: https://owasp.org/www-project-cyclonedx/. Acesso em: 15 set. 2026.",
]
for ref in references:
    p = add_para(ref, indent=False, space_after=7)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        set_run_font(run, size=9.4)


# Apêndices
add_kicker("Reprodução")
add_heading("Apêndice A Comandos principais", 1)
add_heading("Preparação", 2)
add_code("Set-ExecutionPolicy -Scope Process Bypass\nSet-Location \"C:\\Users\\Hayom\\Documents\\CheckpointDevOps\"\n$ProjectDir = (Get-Location).Path\n.\\scripts\\fetch-target.ps1\nNew-Item -ItemType Directory -Force .\\reports | Out-Null")
add_heading("Semgrep red e green por comandos", 2)
add_code("# RED: regras comunitárias gerais\ndocker compose --profile tools run --rm semgrep semgrep scan `\n  --config auto --json --output /workspace/reports/semgrep-red.json `\n  /workspace/target/juice-shop/routes/search.ts\n\ndocker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `\n  --semgrep /workspace/reports/semgrep-red.json --threshold HIGH --expect fail\n\n# CORREÇÃO E GREEN\n.\\scripts\\prepare-green.ps1\ndocker compose --profile tools run --rm semgrep semgrep scan `\n  --config auto --json --output /workspace/reports/semgrep-green.json `\n  /workspace/target/juice-shop-fixed/routes/search.ts\n\ndocker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `\n  --semgrep /workspace/reports/semgrep-green.json --threshold HIGH --expect pass")
add_heading("OWASP ZAP por comando", 2)
add_code("docker compose up -d juice-shop\ndocker compose --profile tools run --rm zap\ndocker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `\n  --zap /workspace/reports/zap-juice-shop.json --threshold HIGH --expect fail")
add_heading("Execução complementar do Checkov", 2)
add_code("docker run --rm -v \"${ProjectDir}\\target\\juice-shop\\terraform:/tf:ro\" `\n  ghcr.io/bridgecrewio/checkov:3.3.11 -d /tf --framework terraform --compact --soft-fail")
add_heading("Encerramento", 2)
add_code("docker compose --profile tools down --remove-orphans")
add_para("Os comandos completos, resultados esperados e solução de problemas estão em LAB.md. As imagens Docker permanecem em cache após o encerramento para reduzir o risco de rede durante a apresentação.")

page_break()
spacer = doc.add_paragraph()
spacer.paragraph_format.space_after = Pt(2)
add_kicker("Rastreabilidade")
add_heading("Apêndice B Mapa de evidências", 1)
add_table(["Evidência", "Arquivo", "Finalidade"], [
    ["Semgrep geral", "reports/semgrep-auto.json e semgrep-auto.log", "Cobertura geral sem regra própria"], ["Semgrep red", "reports/semgrep-red.json", "Comprovar HIGH e bloqueio"],
    ["Semgrep green", "reports/semgrep-green.json", "Comprovar ausência do padrão após correção"], ["Dependency-Check", "reports/dependency-check/", "HTML, JSON, XML, CSV e SARIF"],
    ["Checkov", "reports/checkov.json e checkov.sarif", "42 aprovados e 24 reprovados"], ["OWASP ZAP", "reports/zap-juice-shop.html e .json", "11 tipos de alerta e gate"],
    ["Captura Semgrep", "evidencias/real-semgrep-terminal.png", "Execução real no terminal"], ["Captura Checkov", "evidencias/real-checkov-terminal.png", "Execução real no terminal"],
    ["Captura Dependency-Check", "evidencias/real-dependency-check.png", "Relatório HTML real"], ["Captura ZAP", "evidencias/real-zap-resumo.png", "Relatório HTML real"],
], widths=[3.8, 6.4, 5.8], font_size=8.7, first_col_bold=True)
add_heading("Perguntas de verificação para a turma", 2)
for idx, question in enumerate([
    "Quantos achados HIGH o cenário Semgrep red produz e qual é o resultado após a correção?",
    "Qual plugin do ZAP reporta a SQL Injection e qual CWE está associado ao alerta?",
], start=1):
    p = add_para(f"{idx}. {question}", indent=False, space_after=4)
    p.paragraph_format.left_indent = Cm(0.4)

page_break()
add_kicker("Transparência acadêmica")
add_heading("Apêndice C Uso de inteligência artificial", 1)
add_para("Ferramentas de inteligência artificial apoiaram a organização inicial do repositório, a redação, a revisão do relatório e a preparação de scripts. O grupo validou as afirmações por meio dos relatórios produzidos pelas ferramentas, do código versionado e das documentações oficiais citadas.")
add_para("As decisões de escopo, execução, classificação de achados e apresentação permanecem sob responsabilidade do Grupo 4. Métricas como quantidade de arquivos, regras, checks, URLs, alertas, versões e tempos foram conferidas nos artefatos gerados em 15 de setembro de 2026. A declaração detalhada está em USO-DE-IA.md.")
add_heading("Checklist de entrega relacionado ao relatório", 2)
add_table(["Item", "Situação", "Evidência"], [
    ["Quatro ferramentas cobertas", "Atendido", "Seções 4 a 7"], ["Execução das quatro ferramentas", "Atendido", "reports e figuras 1 a 4"],
    ["Duas categorias no laboratório", "Atendido", "Semgrep e ZAP"], ["Build red e green", "Atendido", "semgrep-red.json e semgrep-green.json"],
    ["Três achados classificados", "Atendido", "Seção 8"], ["Mínimo de dez fontes", "Atendido", "21 referências, maioria primária"],
    ["Plano B", "Atendido", "Relatórios e capturas versionados"], ["Declaração de IA", "Atendido", "USO-DE-IA.md e este apêndice"],
], widths=[6.0, 3.0, 7.0], font_size=9.0, first_col_bold=True)


doc.core_properties.title = "Ferramentas open source de SAST SCA IaC Security e DAST no pipeline DevSecOps"
doc.core_properties.subject = "Checkpoint 01 do Grupo 4"
doc.core_properties.author = "Tiago Louzã; Leando de Souza Silva; Luiz Fernando; Fabricio de Freitas Evangelista; Erik Gunnar"
doc.core_properties.keywords = "DevSecOps, Semgrep, Dependency-Check, Checkov, OWASP ZAP, Juice Shop"
doc.core_properties.comments = "Relatório acadêmico validado com evidências do laboratório"

doc.save(DOCX_PATH)
print(DOCX_PATH)
