from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\Hayom\Documents\CheckpointDevOps")
OUT = ROOT / "evidencias"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1800, 1000
NAVY = "#071A2F"
NAVY_2 = "#0B2744"
PANEL = "#0D2238"
PANEL_2 = "#102C49"
CYAN = "#38D4E8"
BLUE = "#4EA1FF"
GREEN = "#41D69A"
AMBER = "#FFB547"
RED = "#FF637A"
WHITE = "#F4F8FC"
MUTED = "#9DB2C8"
GRID = "#163A5D"


def font(size, bold=False, mono=False):
    if mono:
        name = "consolab.ttf" if bold else "consola.ttf"
    else:
        name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


F_TITLE = font(42, True)
F_SUB = font(22)
F_METRIC = font(50, True)
F_METRIC_LABEL = font(20, True)
F_MONO = font(25, mono=True)
F_MONO_SMALL = font(22, mono=True)
F_SMALL = font(18)
F_TAG = font(18, True)


def round_rect(draw, box, fill, outline=None, radius=18, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def base(title, subtitle, accent=CYAN):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 90):
        d.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 90):
        d.line((0, y, W, y), fill=GRID, width=1)
    d.rectangle((0, 0, W, 16), fill=accent)
    d.text((72, 54), title, font=F_TITLE, fill=WHITE)
    d.text((74, 112), subtitle, font=F_SUB, fill=MUTED)
    return img, d


def tag(draw, x, y, text, color):
    bbox = draw.textbbox((0, 0), text, font=F_TAG)
    tw = bbox[2] - bbox[0]
    round_rect(draw, (x, y, x + tw + 32, y + 40), color, radius=20)
    draw.text((x + 16, y + 9), text, font=F_TAG, fill=NAVY)
    return x + tw + 44


def metric(draw, x, y, w, value, label, color=CYAN):
    round_rect(draw, (x, y, x + w, y + 132), PANEL_2, outline=GRID)
    draw.text((x + 24, y + 18), str(value), font=F_METRIC, fill=color)
    draw.text((x + 26, y + 88), label.upper(), font=F_METRIC_LABEL, fill=MUTED)


def terminal(draw, x, y, w, h, lines, highlights=None, source=None):
    round_rect(draw, (x, y, x + w, y + h), PANEL, outline=GRID, radius=20)
    draw.rectangle((x, y, x + w, y + 54), fill=PANEL_2)
    for i, c in enumerate((RED, AMBER, GREEN)):
        draw.ellipse((x + 22 + i * 30, y + 19, x + 36 + i * 30, y + 33), fill=c)
    draw.text((x + 132, y + 15), "saída registrada", font=F_SMALL, fill=MUTED)
    highlights = highlights or {}
    ty = y + 76
    for idx, line in enumerate(lines):
        color = highlights.get(idx, WHITE)
        draw.text((x + 30, ty), line, font=F_MONO_SMALL, fill=color)
        ty += 34
    if source:
        draw.text((x + 28, y + h - 38), f"Fonte: {source}", font=F_SMALL, fill=MUTED)


def save(img, name):
    img.save(OUT / name, quality=96)


# 1. Semgrep em modo geral, sem regra customizada.
img, d = base("SEMGREP · varredura geral", "Configuração automática da comunidade — sem regra criada pelo grupo")
tag(d, 1370, 62, "SEM CUSTOM RULE", CYAN)
metric(d, 72, 176, 310, "1.027", "arquivos")
metric(d, 405, 176, 310, "408", "regras executadas")
metric(d, 738, 176, 310, "69", "achados")
metric(d, 1071, 176, 310, "99,9%", "linhas analisadas")
terminal(d, 72, 340, 1656, 574, [
    "Scanning 1027 files tracked by git with 1074 Code rules",
    "Language      Rules   Files",
    "ts              163     507",
    "terraform       101      11",
    "",
    "Scan completed successfully.",
    "Findings: 69 (69 blocking)",
    "Rules run: 408",
    "Targets scanned: 1027",
    "Parsed lines: ~99.9%",
    "Ran 408 rules on 1027 files: 69 findings.",
], {5: GREEN, 6: AMBER, 10: CYAN}, "reports/semgrep-auto.log")
save(img, "01-semgrep-geral.png")


# 2. Semgrep red.
img, d = base("SEMGREP · cenário vulnerável", "Recorte determinístico para demonstrar o quality gate")
tag(d, 1425, 62, "BUILD RED", RED)
metric(d, 72, 176, 310, "1", "arquivo")
metric(d, 405, 176, 310, "3", "regras")
metric(d, 738, 176, 310, "1", "HIGH")
metric(d, 1071, 176, 310, "BLOQUEADO", "resultado", RED)
terminal(d, 72, 340, 1656, 574, [
    "Scan completed successfully.",
    "Findings: 1 (1 blocking)",
    "Ran 3 rules on 1 file: 1 finding.",
    "",
    "Gate DevSecOps — limiar HIGH",
    "Achados totais: 1 | Bloqueadores: 1",
    "[HIGH] Query SQL construída com interpolação de template",
    "routes/search.ts:23 · CWE-89",
    "",
    "SUCESSO DO TESTE: o gate bloqueou o cenário vulnerável.",
], {0: GREEN, 1: RED, 4: CYAN, 5: AMBER, 6: RED, 9: GREEN}, "reports/semgrep-red-execution.log")
save(img, "02-semgrep-red.png")


# 3. Semgrep green.
img, d = base("SEMGREP · cenário corrigido", "Consulta parametrizada com replacements do Sequelize")
tag(d, 1420, 62, "BUILD GREEN", GREEN)
metric(d, 72, 176, 310, "1", "arquivo")
metric(d, 405, 176, 310, "3", "regras")
metric(d, 738, 176, 310, "0", "HIGH")
metric(d, 1071, 176, 310, "APROVADO", "resultado", GREEN)
terminal(d, 72, 340, 1656, 574, [
    "Scan completed successfully.",
    "Findings: 0 (0 blocking)",
    "Ran 3 rules on 1 file: 0 findings.",
    "",
    "Gate DevSecOps — limiar HIGH",
    "Achados totais: 0 | Bloqueadores: 0",
    "",
    "GATE APROVADO: nenhum HIGH/CRITICAL nos relatórios informados.",
], {0: GREEN, 1: GREEN, 4: CYAN, 5: GREEN, 7: GREEN}, "reports/semgrep-green-execution.log")
save(img, "03-semgrep-green.png")


# 4. Dependency-Check.
img, d = base("OWASP DEPENDENCY-CHECK", "Execução registrada — resultado tecnicamente inconclusivo")
tag(d, 1375, 62, "COBERTURA BAIXA", AMBER)
metric(d, 72, 176, 310, "15", "dependências")
metric(d, 405, 176, 310, "0", "CVEs reportadas")
metric(d, 738, 176, 310, "7 s", "duração")
metric(d, 1071, 176, 310, "4", "erros de análise", RED)
terminal(d, 72, 340, 1656, 574, [
    "Analysis Started",
    "[WARN] No lock file exists — this will result in false negatives",
    "[WARN] node_modules directory does not exist",
    "[WARN] Archive contains path outside target directory",
    "[WARN] encrypted ZIP entry not supported",
    "",
    "Analysis Complete (7 seconds)",
    "Dependencies scanned: 15",
    "Vulnerabilities identified: 0",
    "",
    "INTERPRETAÇÃO: zero CVEs não significa ausência de risco.",
], {0: CYAN, 1: AMBER, 2: AMBER, 3: RED, 4: RED, 6: GREEN, 8: AMBER, 10: RED}, "reports/dependency-check.log + report JSON")
save(img, "04-dependency-check.png")


# 5. Checkov.
img, d = base("CHECKOV · Terraform oficial do Juice Shop", "Políticas nativas da ferramenta — sem política customizada")
tag(d, 1382, 62, "REGRAS NATIVAS", CYAN)
metric(d, 72, 176, 310, "42", "checks aprovados", GREEN)
metric(d, 405, 176, 310, "24", "checks reprovados", RED)
metric(d, 738, 176, 310, "0", "erros de parsing", GREEN)
metric(d, 1071, 176, 310, "9 s", "duração")
terminal(d, 72, 340, 1656, 574, [
    "By Prisma Cloud | version: 3.3.11",
    "terraform scan results:",
    "Passed checks: 42, Failed checks: 24, Skipped checks: 0",
    "",
    "[FAIL] CKV_AWS_333 · ECS service assigns public IP",
    "[FAIL] CKV_AWS_260 · port 80 open to 0.0.0.0/0",
    "[FAIL] CKV_AWS_2   · ALB listener uses HTTP",
    "[FAIL] CKV_AWS_91  · load balancer access logs disabled",
    "[FAIL] CKV2_AWS_28 · public ALB without WAF",
    "[FAIL] CKV2_AWS_11 · VPC flow logs disabled",
], {0: CYAN, 2: AMBER, 4: RED, 5: RED, 6: RED, 7: RED, 8: RED, 9: RED}, "reports/checkov.log")
save(img, "05-checkov.png")


# 6. ZAP execution.
img, d = base("OWASP ZAP · varredura dinâmica", "Juice Shop v20.2.0 em rede Docker isolada")
tag(d, 1435, 62, "DAST REAL", CYAN)
metric(d, 72, 176, 310, "101", "URLs spider")
metric(d, 405, 176, 310, "234", "URLs AJAX spider")
metric(d, 738, 176, 310, "11", "tipos de alerta")
metric(d, 1071, 176, 310, "1", "HIGH", RED)
terminal(d, 72, 340, 1656, 574, [
    "Job spider found 101 URLs · 00:00:18",
    "Job spiderAjax found 234 URLs · 00:00:37",
    "Job activeScan set rule 40012 · Reflected XSS",
    "Job activeScan set rule 40018 · SQL Injection",
    "Job activeScan finished · 00:03:48",
    "",
    "Alertas: 1 High · 4 Medium · 3 Low · 3 Informational",
    "Instâncias registradas: 39",
    "",
    "Relatórios gerados: HTML · JSON · SARIF",
], {0: CYAN, 1: CYAN, 2: AMBER, 3: RED, 4: GREEN, 6: AMBER, 7: CYAN, 9: GREEN}, "reports/zap-execution.log + zap-juice-shop.json")
save(img, "06-zap-scan.png")


# 7. ZAP gate.
img, d = base("OWASP ZAP · quality gate", "O alerta HIGH interrompe a promoção do cenário vulnerável")
tag(d, 1392, 62, "GATE BLOQUEADO", RED)
metric(d, 72, 176, 310, "11", "achados totais")
metric(d, 405, 176, 310, "1", "bloqueador", RED)
metric(d, 738, 176, 310, "40018", "plugin ZAP")
metric(d, 1071, 176, 310, "CWE-89", "classe")
terminal(d, 72, 340, 1656, 574, [
    "Gate DevSecOps — limiar HIGH",
    "Achados totais: 11 | Bloqueadores: 1",
    "",
    "[HIGH] OWASP ZAP 40018 — SQL Injection",
    "http://juice-shop:3000/rest/products/search?q=...",
    "",
    "SUCESSO DO TESTE: o gate bloqueou o cenário vulnerável.",
], {0: CYAN, 1: AMBER, 3: RED, 4: WHITE, 6: GREEN}, "reports/zap-execution.log")
save(img, "07-zap-gate.png")


# 8. Before/after correction.
img, d = base("CORREÇÃO · separação entre código e dados", "CWE-89 — interpolação substituída por parâmetro nomeado")
left = (72, 190, 856, 860)
right = (944, 190, 1728, 860)
round_rect(d, left, PANEL, outline=RED, radius=20, width=3)
round_rect(d, right, PANEL, outline=GREEN, radius=20, width=3)
d.text((104, 224), "ANTES · vulnerável", font=font(28, True), fill=RED)
d.text((976, 224), "DEPOIS · corrigido", font=font(28, True), fill=GREEN)
before = [
    "const criteria = req.query.q === 'undefined'",
    "  ? '' : req.query.q ?? ''",
    "",
    "sequelize.query(`SELECT * FROM Products",
    "  WHERE ((name LIKE '%${criteria}%'",
    "  OR description LIKE '%${criteria}%')",
    "  AND deletedAt IS NULL)`)",
]
after = [
    "const criteria = req.query.q === 'undefined'",
    "  ? '' : req.query.q ?? ''",
    "",
    "sequelize.query(`SELECT * FROM Products",
    "  WHERE ((name LIKE :criteria",
    "  OR description LIKE :criteria)",
    "  AND deletedAt IS NULL)",
    "  { replacements: {",
    "      criteria: `%${criteria}%` } })",
]
for i, line in enumerate(before):
    d.text((104, 294 + i * 48), line, font=F_MONO_SMALL, fill=RED if "${criteria}" in line else WHITE)
for i, line in enumerate(after):
    d.text((976, 294 + i * 48), line, font=F_MONO_SMALL, fill=GREEN if ":criteria" in line or "replacements" in line else WHITE)
d.text((104, 792), "Dado inserido na instrução SQL", font=F_SMALL, fill=MUTED)
d.text((976, 792), "Dado enviado separadamente", font=F_SMALL, fill=MUTED)
d.text((72, 920), "Fonte: target/juice-shop/routes/search.ts e target/juice-shop-fixed/routes/search.ts", font=F_SMALL, fill=MUTED)
save(img, "08-correcao-sqli.png")


# 9. Pipeline overview.
img, d = base("PIPELINE DEVSECOPS · cobertura complementar", "Cada ferramenta responde a uma pergunta diferente")
steps = [
    ("CÓDIGO", "Semgrep", "SAST", CYAN),
    ("DEPENDÊNCIAS", "Dependency-Check", "SCA", BLUE),
    ("INFRAESTRUTURA", "Checkov", "IaC", AMBER),
    ("APLICAÇÃO", "OWASP ZAP", "DAST", RED),
    ("DECISÃO", "Quality gate", "HIGH / CRITICAL", GREEN),
]
box_w, gap = 300, 42
start_x = 66
for i, (stage, tool, kind, color) in enumerate(steps):
    x = start_x + i * (box_w + gap)
    round_rect(d, (x, 260, x + box_w, 620), PANEL_2, outline=color, radius=24, width=3)
    d.rectangle((x, 260, x + box_w, 274), fill=color)
    d.text((x + 24, 308), f"0{i+1}", font=F_METRIC, fill=color)
    d.text((x + 24, 394), stage, font=F_METRIC_LABEL, fill=MUTED)
    d.text((x + 24, 448), tool, font=font(27, True), fill=WHITE)
    d.text((x + 24, 520), kind, font=F_TAG, fill=color)
    if i < len(steps) - 1:
        d.line((x + box_w + 8, 440, x + box_w + gap - 8, 440), fill=MUTED, width=4)
        d.polygon([(x + box_w + gap - 8, 440), (x + box_w + gap - 25, 430), (x + box_w + gap - 25, 450)], fill=MUTED)
d.text((72, 720), "Cobertura geral", font=font(26, True), fill=WHITE)
d.text((72, 770), "Semgrep --config auto · Dependency-Check · Checkov · ZAP Automation Framework", font=F_MONO_SMALL, fill=MUTED)
d.text((72, 840), "Demonstração red/green", font=font(26, True), fill=WHITE)
d.text((72, 890), "Regra Semgrep específica + gate normalizado · evidência de correção", font=F_MONO_SMALL, fill=MUTED)
save(img, "09-pipeline.png")


print(f"Evidências geradas em {OUT}")
