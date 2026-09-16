import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:\\Users\\Hayom\\Documents\\CheckpointDevOps";
const SKILL_DIR = "C:\\Users\\Hayom\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.904.11930\\skills\\presentations";
const RUNTIME_PYTHON = "C:\\Users\\Hayom\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const TMP_DIR = path.join(ROOT, ".qa", "slides-build");
const FINAL_PPTX = path.join(ROOT, "entrega", "Apresentacao_Checkpoint_DevSecOps_Grupo4_corrigida.pptx");

const {
  resolvePresentationFont,
  applyPresentationChartFont,
  makeNativeBulletParagraphs,
  finalizePresentation,
} = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href);

await fs.mkdir(TMP_DIR, { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });

const fontFamily = resolvePresentationFont();
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

const C = {
  navy: "#071A2F",
  navy2: "#0B2545",
  cyan: "#00A6C8",
  blue: "#4EA1FF",
  green: "#2FBF83",
  amber: "#F0A23B",
  red: "#E14B64",
  ink: "#13202C",
  muted: "#637383",
  pale: "#EAF5F8",
  pale2: "#F4F7F9",
  white: "#FFFFFF",
  line: "#D4DEE5",
};

const EVID = path.join(ROOT, "evidencias");
const IMAGES = {
  semgrepGeneral: path.join(EVID, "real-semgrep-terminal.png"),
  semgrepRed: path.join(EVID, "real-semgrep-red.png"),
  semgrepGreen: path.join(EVID, "real-semgrep-green.png"),
  dependency: path.join(EVID, "real-dependency-check.png"),
  checkov: path.join(EVID, "real-checkov-terminal.png"),
  zapRun: path.join(EVID, "real-zap-execucao.png"),
  zapSummary: path.join(EVID, "real-zap-resumo.png"),
};

const imageBytes = {};
for (const [key, file] of Object.entries(IMAGES)) imageBytes[key] = await fs.readFile(file);

function addText(slide, text, left, top, width, height, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: fontFamily,
    fontSize: 27,
    color: C.ink,
    autoFit: "shrinkText",
    verticalAlignment: "middle",
    ...style,
  };
  return shape;
}

function addBullets(slide, items, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = makeNativeBulletParagraphs(items, {
    marginLeftPoints: 22,
    hangingPoints: 10,
    spaceAfterPoints: options.spaceAfter ?? 9,
  });
  shape.text.style = {
    typeface: fontFamily,
    fontSize: options.fontSize ?? 26,
    color: options.color ?? C.ink,
    autoFit: "shrinkText",
    verticalAlignment: "top",
  };
  return shape;
}

function addFooter(slide, number, source = "") {
  addText(slide, "GRUPO 4  |  DEVSECOPS", 64, 674, 360, 24, {
    fontSize: 15,
    bold: true,
    color: C.muted,
  });
  if (source) addText(slide, source, 430, 674, 720, 24, {
    fontSize: 14,
    color: C.muted,
    alignment: "right",
  });
  addText(slide, String(number).padStart(2, "0"), 1170, 672, 46, 26, {
    fontSize: 16,
    bold: true,
    color: C.cyan,
    alignment: "right",
  });
}

function addHeader(slide, number, title, kicker = "", source = "") {
  slide.background.fill = C.white;
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: 1280, height: 12 },
    fill: C.cyan,
    line: { fill: C.cyan, width: 0 },
  });
  if (kicker) addText(slide, kicker.toUpperCase(), 64, 42, 520, 28, {
    fontSize: 17,
    bold: true,
    color: C.cyan,
  });
  addText(slide, title, 64, kicker ? 72 : 46, 1130, 70, {
    fontSize: 43,
    bold: true,
    color: C.navy,
  });
  addFooter(slide, number, source);
}

function addImage(slide, bytes, alt, left, top, width, height, fit = "contain") {
  return slide.images.add({
    blob: new Uint8Array(bytes),
    contentType: "image/png",
    alt,
    fit,
    position: { left, top, width, height },
  });
}

function addMetric(slide, value, label, left, top, color = C.cyan, width = 230) {
  addText(slide, value, left, top, width, 62, {
    fontSize: 48,
    bold: true,
    color,
    alignment: "center",
  });
  addText(slide, label.toUpperCase(), left, top + 58, width, 34, {
    fontSize: 16,
    bold: true,
    color: C.muted,
    alignment: "center",
  });
}

function addRule(slide, left, top, width, color = C.line, height = 2) {
  slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill: color,
    line: { fill: color, width: 0 },
  });
}

function styleTable(table, rows, cols, options = {}) {
  table.borders.assign({ style: "solid", fill: C.line, width: 1 });
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const cell = table.getCell(r, c);
      cell.fill = r === 0 ? C.navy2 : (r % 2 === 0 ? C.pale : C.white);
      cell.text.style = {
        typeface: fontFamily,
        fontSize: r === 0 ? (options.headerSize ?? 18) : (options.bodySize ?? 17),
        bold: r === 0 || (options.boldFirst && c === 0),
        color: r === 0 ? C.white : C.ink,
        alignment: c === 0 ? "left" : "center",
        verticalAlignment: "middle",
        autoFit: "shrinkText",
      };
    }
  }
}

function setNotes(slide, text) {
  slide.speakerNotes.textFrame.setText(text);
}

// 1 Capa
{
  const slide = presentation.slides.add();
  slide.background.fill = C.navy;
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 1280, height: 18 }, fill: C.cyan, line: { fill: C.cyan, width: 0 } });
  addText(slide, "CHECKPOINT 01", 72, 74, 420, 42, { fontSize: 21, bold: true, color: C.cyan });
  addText(slide, "Ferramentas open source\nno pipeline DevSecOps", 72, 154, 860, 190, { fontSize: 62, bold: true, color: C.white });
  addText(slide, "Semgrep  |  OWASP Dependency Check  |  Checkov  |  OWASP ZAP", 74, 372, 1000, 42, { fontSize: 23, color: "#BFD3E4" });
  addRule(slide, 74, 444, 1110, C.cyan, 4);
  addText(slide, "Grupo 4  ·  Turma 2TDCPF", 74, 482, 560, 44, { fontSize: 25, bold: true, color: C.white });
  addText(slide, "Professor Fabio Pires", 74, 534, 560, 36, { fontSize: 21, color: "#BFD3E4" });
  addText(slide, "São Paulo 2026", 74, 640, 300, 26, { fontSize: 17, color: "#8FA9BF" });
  setNotes(slide, "Abertura. Apresente o tema, o Grupo 4 e o objetivo de comparar quatro categorias complementares de segurança no pipeline.");
}

// 2 Equipe
{
  const slide = presentation.slides.add();
  addHeader(slide, 2, "Equipe e responsabilidades", "Grupo 4");
  addText(slide, "Tiago Louzã", 84, 174, 420, 46, { fontSize: 32, bold: true, color: C.navy });
  addText(slide, "Líder técnico e responsável pelo repositório", 84, 220, 500, 40, { fontSize: 22, color: C.muted });
  addText(slide, "Erik Gunnar  ·  RM565107", 700, 174, 430, 46, { fontSize: 32, bold: true, color: C.navy });
  addText(slide, "Relator", 700, 220, 430, 40, { fontSize: 22, color: C.muted });
  addRule(slide, 84, 294, 1040);
  addText(slide, "Leando de Souza Silva  ·  RM566485", 84, 326, 530, 42, { fontSize: 25, bold: true });
  addText(slide, "Luiz Fernando  ·  RM562652", 84, 390, 530, 42, { fontSize: 25, bold: true });
  addText(slide, "Fabricio de Freitas Evangelista  ·  RM564782", 84, 454, 670, 42, { fontSize: 25, bold: true });
  addText(slide, "Repositório", 84, 558, 190, 30, { fontSize: 18, bold: true, color: C.cyan });
  addText(slide, "github.com/TiagoLouzaPetagna/grupo4-devsecops", 84, 592, 790, 38, { fontSize: 24, color: C.navy2 });
  setNotes(slide, "Confirme que todos apresentarão uma parte. O histórico do Git deve receber contribuições reais dos integrantes.");
}

// 3 Agenda
{
  const slide = presentation.slides.add();
  addHeader(slide, 3, "Agenda e distribuição do tempo", "30 minutos");
  const agenda = [
    ["03 min", "Fundamentos e posição no pipeline"],
    ["10 min", "Semgrep, Dependency Check, Checkov e ZAP"],
    ["12 min", "Laboratório guiado com Semgrep e ZAP"],
    ["03 min", "Comparação, limitações e conclusão"],
    ["02 min", "Perguntas"],
  ];
  agenda.forEach((item, i) => {
    const y = 158 + i * 91;
    addText(slide, item[0], 90, y, 170, 55, { fontSize: 31, bold: true, color: i === 2 ? C.red : C.cyan, alignment: "right" });
    addText(slide, item[1], 300, y, 810, 55, { fontSize: 29, bold: i === 2, color: C.ink });
    if (i < agenda.length - 1) addRule(slide, 300, y + 66, 780);
  });
  setNotes(slide, "O laboratório recebe o maior bloco. Mantenha a explicação de cada ferramenta em cerca de dois minutos e meio.");
}

// 4 Categorias
{
  const slide = presentation.slides.add();
  addHeader(slide, 4, "Quatro frentes complementares", "Pipeline DevSecOps");
  const items = [
    ["SAST", "Semgrep", "Código próprio", "Code e Build", C.cyan],
    ["SCA", "Dependency Check", "Dependências", "Build", C.blue],
    ["IaC", "Checkov", "Terraform", "Code e Deploy", C.amber],
    ["DAST", "OWASP ZAP", "Aplicação ativa", "Test e Release", C.red],
  ];
  items.forEach((it, i) => {
    const x = 74 + i * 298;
    slide.shapes.add({ geometry: "rect", position: { left: x, top: 190, width: 256, height: 310 }, fill: i % 2 ? C.pale : C.pale2, line: { fill: C.line, width: 1 } });
    addText(slide, it[0], x + 20, 212, 216, 56, { fontSize: 39, bold: true, color: it[4], alignment: "center" });
    addText(slide, it[1], x + 16, 284, 224, 54, { fontSize: 24, bold: true, color: C.navy, alignment: "center" });
    addText(slide, it[2], x + 16, 362, 224, 42, { fontSize: 21, color: C.ink, alignment: "center" });
    addText(slide, it[3], x + 16, 430, 224, 42, { fontSize: 19, bold: true, color: C.muted, alignment: "center" });
  });
  addText(slide, "Cada ferramenta responde a uma pergunta diferente e preserva uma evidência diferente.", 120, 560, 1040, 58, { fontSize: 28, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fonte: NIST SSDF e OWASP DevSecOps Guideline. Explique entrada, momento do pipeline e necessidade de aplicação ativa.");
}

// 5 SAST x SCA e shift left
{
  const slide = presentation.slides.add();
  addHeader(slide, 5, "SAST, SCA e o limite do shift left", "Fundamentos");
  addText(slide, "SAST", 92, 176, 220, 50, { fontSize: 39, bold: true, color: C.cyan });
  addText(slide, "Procura padrões inseguros no código que a equipe escreveu.", 92, 236, 460, 92, { fontSize: 27 });
  addText(slide, "Correção típica: alterar a implementação.", 92, 342, 460, 48, { fontSize: 22, bold: true, color: C.muted });
  addText(slide, "SCA", 700, 176, 220, 50, { fontSize: 39, bold: true, color: C.blue });
  addText(slide, "Constrói o inventário de componentes e correlaciona versões com CVEs.", 700, 236, 460, 92, { fontSize: 27 });
  addText(slide, "Correção típica: atualizar, substituir ou mitigar.", 700, 342, 460, 48, { fontSize: 22, bold: true, color: C.muted });
  addRule(slide, 92, 430, 1068);
  addText(slide, "Shift left antecipa o feedback, mas não enxerga o comportamento final da aplicação.", 142, 470, 980, 64, { fontSize: 31, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "O ZAP permanece necessário para observar rotas, cabeçalhos, sessões e configurações em execução.", 170, 550, 920, 60, { fontSize: 25, color: C.ink, alignment: "center" });
  setNotes(slide, "Fonte: OWASP DevSecOps Guideline. Esta é a distinção conceitual mais importante do trabalho.");
}

// 6 Metodologia
{
  const slide = presentation.slides.add();
  addHeader(slide, 6, "Metodologia e escopo autorizado", "Laboratório");
  addText(slide, "OWASP Juice Shop v20.2.0", 82, 170, 550, 56, { fontSize: 38, bold: true, color: C.navy });
  addBullets(slide, [
    "Código e imagem oficial na mesma versão",
    "Aplicação publicada somente em 127.0.0.1:3000",
    "Rede interna do Docker Compose",
    "Dados sintéticos da aplicação de treinamento",
  ], 82, 246, 540, 290, { fontSize: 25 });
  addText(slide, "Escopo ético", 720, 170, 380, 50, { fontSize: 34, bold: true, color: C.red });
  addBullets(slide, [
    "Nenhuma varredura em site público",
    "Nenhum sistema corporativo ou de terceiros",
    "Active scan limitado por tempo e por regras",
    "Relatórios preservados para auditoria",
  ], 720, 246, 470, 290, { fontSize: 25 });
  addText(slide, "Alvo autorizado e isolado", 82, 584, 1090, 42, { fontSize: 25, bold: true, color: C.green, alignment: "center" });
  setNotes(slide, "Fonte: enunciado do Check Point e OWASP Juice Shop v20.2.0. Reforce que a demonstração não pode apontar para a instância pública.");
}

// 7 Semgrep técnica
{
  const slide = presentation.slides.add();
  addHeader(slide, 7, "Semgrep", "SAST");
  addText(slide, "O que analisa", 82, 170, 400, 42, { fontSize: 27, bold: true, color: C.cyan });
  addBullets(slide, ["AST e padrões estruturais", "Metavariáveis e regras específicas", "Taint analysis em modos compatíveis"], 82, 222, 480, 220, { fontSize: 27 });
  addText(slide, "Uso no laboratório", 690, 170, 430, 42, { fontSize: 27, bold: true, color: C.cyan });
  addBullets(slide, ["Scan geral com --config auto", "Regra local para o red e green", "JSON processado pelo quality gate"], 690, 222, 470, 220, { fontSize: 27 });
  addRule(slide, 82, 474, 1078);
  addText(slide, "Ponto forte", 90, 510, 230, 34, { fontSize: 20, bold: true, color: C.green });
  addText(slide, "Feedback rápido e regras legíveis", 90, 548, 430, 54, { fontSize: 27, bold: true });
  addText(slide, "Limitação", 700, 510, 230, 34, { fontSize: 20, bold: true, color: C.amber });
  addText(slide, "Cobertura e ruído dependem das regras e do contexto", 700, 548, 470, 70, { fontSize: 26, bold: true });
  setNotes(slide, "Fontes: documentação e repositório oficial do Semgrep. A versão executada foi 1.172.0.");
}

// 8 Semgrep geral
{
  const slide = presentation.slides.add();
  addHeader(slide, 8, "Scan geral do Semgrep", "Execução real", "captura do Grupo 4");
  addImage(slide, imageBytes.semgrepGeneral, "Terminal com a execução geral do Semgrep", 62, 142, 820, 490, "contain");
  addMetric(slide, "1.027", "arquivos", 922, 178, C.cyan, 250);
  addMetric(slide, "408", "regras executadas", 922, 292, C.blue, 250);
  addMetric(slide, "69", "achados", 922, 406, C.red, 250);
  addText(slide, "O scan geral usou --config auto. Nenhuma regra do grupo foi necessária para encontrar SQL Injection.", 912, 520, 270, 108, { fontSize: 20, color: C.ink, alignment: "center" });
  setNotes(slide, "Fonte: reports/semgrep-auto.json e captura real-semgrep-terminal.png. O aviso NativeCommandError veio da conversão de stderr pelo PowerShell e não representa falha do scan.");
}

// 9 Semgrep red
{
  const slide = presentation.slides.add();
  addHeader(slide, 9, "Cenário SAST red", "Quality gate", "captura do Grupo 4");
  addImage(slide, imageBytes.semgrepRed, "Terminal do Semgrep no cenário vulnerável", 64, 152, 770, 460, "contain");
  addText(slide, "1 HIGH", 880, 188, 300, 76, { fontSize: 56, bold: true, color: C.red, alignment: "center" });
  addText(slide, "CWE-89", 880, 280, 300, 48, { fontSize: 31, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "Interpolação dentro de sequelize.query em routes/search.ts:23", 872, 356, 320, 102, { fontSize: 24, color: C.ink, alignment: "center" });
  addText(slide, "Gate bloqueado", 888, 510, 290, 50, { fontSize: 30, bold: true, color: C.red, alignment: "center" });
  setNotes(slide, "Fonte: reports/semgrep-red.json. Explique que o script usa --expect fail para confirmar que o gate detecta o bloqueador.");
}

// 10 Correção
{
  const slide = presentation.slides.add();
  addHeader(slide, 10, "Correção de SQL Injection", "Separação entre comando e dado");
  addText(slide, "Antes", 88, 166, 500, 46, { fontSize: 32, bold: true, color: C.red });
  const before = "sequelize.query(`SELECT * FROM Products\nWHERE name LIKE '%${criteria}%'\nOR description LIKE '%${criteria}%'`)";
  const after = "sequelize.query(`SELECT * FROM Products\nWHERE name LIKE :criteria\nOR description LIKE :criteria`,\n{ replacements: { criteria: `%${criteria}%` } })";
  slide.shapes.add({ geometry: "rect", position: { left: 84, top: 226, width: 516, height: 252 }, fill: "#FFF3F5", line: { fill: C.red, width: 2 } });
  addText(slide, before, 108, 250, 468, 204, { typeface: "Consolas", fontSize: 24, color: C.ink });
  addText(slide, "Depois", 696, 166, 500, 46, { fontSize: 32, bold: true, color: C.green });
  slide.shapes.add({ geometry: "rect", position: { left: 692, top: 226, width: 516, height: 252 }, fill: "#EFFAF5", line: { fill: C.green, width: 2 } });
  addText(slide, after, 716, 244, 468, 222, { typeface: "Consolas", fontSize: 23, color: C.ink });
  addText(slide, "A parametrização impede que o valor altere a estrutura da consulta.", 160, 532, 960, 64, { fontSize: 30, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fonte: target/juice-shop/routes/search.ts e target/juice-shop-fixed/routes/search.ts. A correção demonstrada usa replacements do Sequelize.");
}

// 11 Semgrep green
{
  const slide = presentation.slides.add();
  addHeader(slide, 11, "Cenário SAST green", "Verificação da correção", "captura do Grupo 4");
  addImage(slide, imageBytes.semgrepGreen, "Terminal do Semgrep após a consulta parametrizada", 64, 152, 770, 460, "contain");
  addText(slide, "0", 906, 184, 250, 86, { fontSize: 68, bold: true, color: C.green, alignment: "center" });
  addText(slide, "HIGH ou CRITICAL", 876, 274, 310, 42, { fontSize: 22, bold: true, color: C.muted, alignment: "center" });
  addText(slide, "Gate aprovado", 882, 372, 300, 54, { fontSize: 34, bold: true, color: C.green, alignment: "center" });
  addText(slide, "O resultado valida esse recorte. Ele não afirma que todo o Juice Shop ficou seguro.", 866, 472, 330, 112, { fontSize: 22, color: C.ink, alignment: "center" });
  setNotes(slide, "Fonte: reports/semgrep-green.json. O green analisa a cópia corrigida de um arquivo para manter a demonstração previsível.");
}

// 12 Dependency Check
{
  const slide = presentation.slides.add();
  addHeader(slide, 12, "OWASP Dependency Check", "SCA");
  addText(slide, "Técnica", 84, 166, 300, 42, { fontSize: 28, bold: true, color: C.blue });
  addBullets(slide, ["Coleta evidências de nome e versão", "Tenta associar componentes a CPEs", "Consulta vulnerabilidades conhecidas"], 84, 222, 500, 236, { fontSize: 26 });
  addText(slide, "Condições para um bom resultado", 688, 166, 470, 42, { fontSize: 28, bold: true, color: C.blue });
  addBullets(slide, ["Lockfiles presentes", "Dependências resolvidas", "Base NVD atualizada e cacheada", "Supressões justificadas"], 688, 222, 490, 270, { fontSize: 26 });
  addRule(slide, 84, 500, 1090);
  addText(slide, "Um relatório com zero CVEs pode continuar inconclusivo quando o inventário está incompleto.", 140, 538, 1000, 72, { fontSize: 30, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fontes: repositório e documentação oficial do OWASP Dependency Check. A versão executada foi 13.0.0.");
}

// 13 Dependency resultado
{
  const slide = presentation.slides.add();
  addHeader(slide, 13, "Resultado inconclusivo do SCA", "Dependency Check", "relatório HTML do Grupo 4");
  addImage(slide, imageBytes.dependency, "Relatório HTML do OWASP Dependency Check", 60, 148, 805, 482, "contain");
  addMetric(slide, "15", "dependências", 906, 170, C.blue, 250);
  addMetric(slide, "0", "CVEs reportadas", 906, 278, C.amber, 250);
  addMetric(slide, "4", "exceções", 906, 386, C.red, 250);
  addText(slide, "Faltaram package-lock.json e node_modules. A ferramenta alertou para possíveis falsos negativos.", 888, 508, 286, 112, { fontSize: 21, color: C.ink, alignment: "center" });
  setNotes(slide, "Fonte: reports/dependency-check. A execução levou sete segundos com --noupdate e OSS Index desabilitado.");
}

// 14 Checkov
{
  const slide = presentation.slides.add();
  addHeader(slide, 14, "Checkov", "IaC Security");
  addText(slide, "O que faz", 84, 166, 360, 42, { fontSize: 28, bold: true, color: C.amber });
  addBullets(slide, ["Interpreta arquivos declarativos", "Aplica políticas nativas ou próprias", "Analisa atributos e relações em grafo"], 84, 222, 500, 236, { fontSize: 26 });
  addText(slide, "Execução do grupo", 688, 166, 410, 42, { fontSize: 28, bold: true, color: C.amber });
  addBullets(slide, ["Terraform oficial do Juice Shop", "Políticas nativas", "Sem regra criada pelo grupo", "Saídas CLI, JSON e SARIF"], 688, 222, 490, 270, { fontSize: 26 });
  addRule(slide, 84, 500, 1090);
  addText(slide, "A ferramenta identifica desvios de política. O contexto do ambiente ainda exige triagem humana.", 140, 538, 1000, 72, { fontSize: 29, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fontes: repositório e documentação oficial do Checkov. A versão executada foi 3.3.11.");
}

// 15 Checkov resultado e gráfico
{
  const slide = presentation.slides.add();
  addHeader(slide, 15, "Resultado do Checkov", "Terraform oficial", "captura e reports/checkov.json");
  addImage(slide, imageBytes.checkov, "Terminal do Checkov com 42 checks aprovados e 24 reprovados", 58, 154, 694, 452, "contain");
  const chart = slide.charts.add("bar", {
    position: { left: 800, top: 196, width: 390, height: 300 },
    categories: ["Aprovados", "Reprovados"],
    series: [{ name: "Checks", values: [42, 24], fill: C.cyan }],
    barOptions: { direction: "column", grouping: "clustered" },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd" },
  });
  applyPresentationChartFont(chart, { fontFamily });
  addText(slide, "66 verificações em 26 recursos", 810, 526, 370, 50, { fontSize: 27, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "Nenhum erro de parsing", 810, 580, 370, 38, { fontSize: 21, color: C.green, alignment: "center" });
  setNotes(slide, "Fonte: reports/checkov.json e captura real-checkov-terminal.png. O scan levou aproximadamente nove segundos.");
}

// 16 Checkov priorização
{
  const slide = presentation.slides.add();
  addHeader(slide, 16, "Falhas priorizadas do Checkov", "IaC Security");
  const values = [
    ["Check", "Condição", "Tratamento"],
    ["CKV_AWS_333", "ECS com IP público", "Sub-rede privada"],
    ["CKV_AWS_260", "Porta 80 aberta para todos", "Restringir ou redirecionar"],
    ["CKV_AWS_2", "Listener HTTP", "HTTPS com certificado"],
    ["CKV_AWS_91", "Logs do ALB ausentes", "Habilitar access logs"],
    ["CKV2_AWS_11", "VPC flow logs ausentes", "Habilitar flow logs"],
    ["CKV2_AWS_28", "ALB público sem WAF", "Associar Web ACL"],
  ];
  const table = slide.tables.add({ rows: values.length, columns: 3, left: 86, top: 166, width: 1100, height: 424, values, columnWidths: [250, 470, 380] });
  styleTable(table, values.length, 3, { headerSize: 19, bodySize: 18, boldFirst: true });
  addText(slide, "Os seis itens foram confirmados no Terraform. Os outros 18 não receberam triagem manual completa.", 116, 610, 1040, 42, { fontSize: 21, color: C.muted, alignment: "center" });
  setNotes(slide, "Fonte: reports/checkov.log. Destaque CKV_AWS_2 como um dos três achados analisados em profundidade.");
}

// 17 ZAP técnica
{
  const slide = presentation.slides.add();
  addHeader(slide, 17, "OWASP ZAP", "DAST");
  addText(slide, "Plano automatizado", 82, 168, 420, 42, { fontSize: 29, bold: true, color: C.red });
  addBullets(slide, ["Spider tradicional", "AJAX spider", "Passive scan", "Active scan de XSS e SQL Injection"], 82, 222, 510, 294, { fontSize: 27 });
  addText(slide, "Configuração do grupo", 688, 168, 430, 42, { fontSize: 29, bold: true, color: C.red });
  addBullets(slide, ["Plano YAML de execução", "Regras nativas 40012 e 40018", "Limite de quatro minutos", "Relatórios HTML, JSON e SARIF"], 688, 222, 490, 294, { fontSize: 27 });
  addText(slide, "O YAML organiza o scan. Ele não cria uma nova regra de detecção.", 160, 560, 960, 58, { fontSize: 30, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fontes: ZAP Automation Framework e Docker images. A versão executada foi 2.17.0.");
}

// 18 ZAP execução
{
  const slide = presentation.slides.add();
  addHeader(slide, 18, "Execução dinâmica do ZAP", "DAST", "captura do Grupo 4");
  addImage(slide, imageBytes.zapRun, "Terminal com a execução automatizada do OWASP ZAP", 54, 146, 840, 486, "contain");
  addMetric(slide, "101", "URLs spider", 928, 170, C.cyan, 250);
  addMetric(slide, "234", "URLs AJAX", 928, 280, C.blue, 250);
  addMetric(slide, "3:48", "active scan", 928, 390, C.red, 250);
  addText(slide, "Alvo: contêiner local", 928, 530, 250, 52, { fontSize: 23, bold: true, color: C.green, alignment: "center" });
  setNotes(slide, "Fonte: reports/zap-execution.log e captura real-zap-execucao.png. O tempo total dos jobs ficou próximo de quatro minutos e cinquenta segundos.");
}

// 19 ZAP resultado
{
  const slide = presentation.slides.add();
  addHeader(slide, 19, "Alertas do OWASP ZAP", "Resultado observado", "reports/zap-juice-shop.json");
  addImage(slide, imageBytes.zapSummary, "Resumo HTML do OWASP ZAP", 58, 154, 672, 452, "contain");
  const chart = slide.charts.add("bar", {
    position: { left: 780, top: 190, width: 420, height: 320 },
    categories: ["High", "Medium", "Low", "Info"],
    series: [{ name: "Tipos", values: [1, 4, 3, 3], fill: C.red }],
    barOptions: { direction: "column", grouping: "clustered" },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd" },
  });
  applyPresentationChartFont(chart, { fontFamily });
  addText(slide, "11 tipos de alerta  ·  39 instâncias", 786, 536, 400, 46, { fontSize: 27, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "SQL Injection HIGH  ·  plugin 40018", 786, 586, 400, 40, { fontSize: 22, bold: true, color: C.red, alignment: "center" });
  setNotes(slide, "Fonte: reports/zap-juice-shop.json e captura real-zap-resumo.png. O alerta SQL Injection teve confiança baixa e foi corroborado pelo Semgrep.");
}

// 20 Fluxo do laboratório
{
  const slide = presentation.slides.add();
  addHeader(slide, 20, "Fluxo do laboratório de 12 minutos", "Semgrep e ZAP");
  const steps = [
    ["1", "SAST red", "1 HIGH", C.red],
    ["2", "Gate", "bloqueia", C.red],
    ["3", "Correção", "parâmetro", C.cyan],
    ["4", "SAST green", "0 HIGH", C.green],
    ["5", "ZAP", "1 HIGH", C.red],
  ];
  steps.forEach((s, i) => {
    const x = 58 + i * 244;
    slide.shapes.add({ geometry: "roundRect", position: { left: x, top: 236, width: 196, height: 190 }, fill: i % 2 ? C.pale : C.pale2, line: { fill: s[3], width: 3 }, borderRadius: 18 });
    addText(slide, s[0], x + 58, 250, 80, 54, { fontSize: 40, bold: true, color: s[3], alignment: "center" });
    addText(slide, s[1], x + 14, 318, 168, 46, { fontSize: 25, bold: true, color: C.navy, alignment: "center" });
    addText(slide, s[2], x + 14, 370, 168, 38, { fontSize: 21, color: C.muted, alignment: "center" });
    if (i < steps.length - 1) addText(slide, ">", x + 198, 300, 46, 54, { fontSize: 38, bold: true, color: C.muted, alignment: "center" });
  });
  addText(slide, "A turma executa somente três comandos. Os comandos extensos ficam dentro dos scripts.", 140, 510, 1000, 68, { fontSize: 30, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Use este slide antes da demonstração para explicar a sequência e os resultados esperados.");
}

// 21 Comandos
{
  const slide = presentation.slides.add();
  addHeader(slide, 21, "Comandos digitados pela turma", "Laboratório guiado");
  const commands = [
    ".\\scripts\\run-lab.ps1 -Mode sast-red",
    ".\\scripts\\run-lab.ps1 -Mode sast-green",
    ".\\scripts\\run-lab.ps1 -Mode dast",
  ];
  commands.forEach((cmd, i) => {
    const y = 174 + i * 112;
    addText(slide, String(i + 1).padStart(2, "0"), 80, y, 72, 62, { fontSize: 34, bold: true, color: C.cyan, alignment: "center" });
    slide.shapes.add({ geometry: "rect", position: { left: 176, top: y, width: 940, height: 70 }, fill: "#F0F3F5", line: { fill: C.line, width: 1 } });
    addText(slide, cmd, 202, y + 8, 890, 54, { typeface: "Consolas", fontSize: 25, color: C.navy });
  });
  addRule(slide, 80, 520, 1060);
  addText(slide, "Perguntas de verificação", 80, 548, 350, 36, { fontSize: 23, bold: true, color: C.red });
  addText(slide, "1. Quantos HIGH aparecem no Semgrep red?\n2. Qual plugin do ZAP reporta a SQL Injection e qual é o CWE?", 430, 536, 730, 96, { fontSize: 23, color: C.ink });
  setNotes(slide, "Os comandos internos de Docker, Semgrep, ZAP e quality-gate.mjs já estão automatizados em scripts/run-lab.ps1.");
}

// 22 CI red green
{
  const slide = presentation.slides.add();
  addHeader(slide, 22, "Pipeline e demonstração red/green", "GitHub Actions");
  addText(slide, "Cenário red", 94, 170, 420, 44, { fontSize: 32, bold: true, color: C.red });
  addBullets(slide, ["Escaneia o arquivo vulnerável", "Reprocessa o JSON com expectativa de aprovação", "A Action falha por encontrar HIGH"], 94, 226, 480, 220, { fontSize: 26 });
  addText(slide, "Cenário green", 700, 170, 420, 44, { fontSize: 32, bold: true, color: C.green });
  addBullets(slide, ["Cria a cópia parametrizada", "Repete a mesma regra", "A Action termina sem bloqueadores"], 700, 226, 480, 220, { fontSize: 26 });
  addRule(slide, 94, 474, 1086);
  addText(slide, "Workflow manual", 94, 514, 250, 34, { fontSize: 20, bold: true, color: C.cyan });
  addText(slide, ".github/workflows/red-green-demo.yml", 94, 552, 530, 44, { typeface: "Consolas", fontSize: 23, color: C.navy });
  addText(slide, "Workflow principal", 700, 514, 250, 34, { fontSize: 20, bold: true, color: C.cyan });
  addText(slide, "Semgrep e OWASP ZAP integrados", 700, 552, 450, 44, { fontSize: 25, bold: true, color: C.navy });
  setNotes(slide, "Execute o workflow manual duas vezes: primeiro red e depois green. Capture as duas páginas do GitHub Actions para a apresentação.");
}

// 23 Achados
{
  const slide = presentation.slides.add();
  addHeader(slide, 23, "Três achados analisados", "Verdadeiros e falsos positivos");
  const values = [
    ["Achado", "Ferramenta", "Classificação", "CWE", "Tratamento"],
    ["SQL Injection na busca", "Semgrep e ZAP", "VP", "CWE-89", "Consulta parametrizada"],
    ["Listener HTTP no ALB", "Checkov", "VP", "CWE-319", "HTTPS e redirecionamento"],
    ["SQLi em codefix didático", "Semgrep", "FP operacional", "CWE-89", "Excluir somente o caminho"],
  ];
  const table = slide.tables.add({ rows: 4, columns: 5, left: 60, top: 178, width: 1160, height: 280, values, columnWidths: [300, 210, 180, 150, 320] });
  styleTable(table, 4, 5, { headerSize: 17, bodySize: 17, boldFirst: true });
  addText(slide, "A classificação depende do alcance real do artefato, da evidência independente e da possibilidade de reprodução.", 140, 500, 1000, 78, { fontSize: 30, bold: true, color: C.navy, alignment: "center" });
  addText(slide, "Falso positivo operacional não significa que a regra está errada. O contexto muda a decisão do gate.", 160, 584, 960, 50, { fontSize: 22, color: C.muted, alignment: "center" });
  setNotes(slide, "Fonte: analysis/ACHADOS.md e relatórios versionados. Explique a diferença entre condição técnica e relevância para o artefato implantado.");
}

// 24 Comparação
{
  const slide = presentation.slides.add();
  addHeader(slide, 24, "Comparação do toolchain", "Quatro perguntas distintas");
  const values = [
    ["Critério", "Semgrep", "Dependency Check", "Checkov", "OWASP ZAP"],
    ["Entrada", "Código", "Dependências", "IaC", "Aplicação ativa"],
    ["Tempo", "~3 min", "7 s", "~9 s", "~4 min 48 s"],
    ["Resultado", "69 geral", "0 CVEs, inconclusivo", "42 pass, 24 fail", "11 tipos, 1 High"],
    ["Limitação", "Ruído", "Inventário", "Contexto", "Cobertura"],
  ];
  const table = slide.tables.add({ rows: 5, columns: 5, left: 46, top: 168, width: 1188, height: 350, values, columnWidths: [180, 230, 285, 230, 263] });
  styleTable(table, 5, 5, { headerSize: 17, bodySize: 17, boldFirst: true });
  addText(slide, "Recomendação do Grupo 4", 96, 536, 350, 34, { fontSize: 23, bold: true, color: C.cyan });
  addText(slide, "Semgrep e Checkov em pull requests. Dependency Check depois da resolução das dependências. ZAP em ambiente efêmero de teste.", 96, 566, 1080, 70, { fontSize: 22, bold: true, color: C.navy, alignment: "center" });
  setNotes(slide, "Fonte: relatório do Grupo 4. As durações refletem o ambiente do laboratório e não constituem benchmark universal.");
}

// 25 Limitações e conclusão
{
  const slide = presentation.slides.add();
  addHeader(slide, 25, "Limitações e conclusão", "Síntese crítica");
  addBullets(slide, [
    "Somente recortes prioritários dos 69 achados do Semgrep receberam triagem",
    "O Dependency Check analisou um inventário incompleto",
    "O Checkov avaliou código Terraform, não recursos implantados",
    "O ZAP não autenticou usuários e atingiu o limite do active scan",
  ], 78, 166, 590, 330, { fontSize: 25 });
  addText(slide, "Conclusão", 740, 170, 360, 44, { fontSize: 34, bold: true, color: C.cyan });
  addText(slide, "A combinação das quatro ferramentas amplia a cobertura porque código, dependências, infraestrutura e comportamento exigem evidências diferentes.", 740, 236, 440, 184, { fontSize: 29, bold: true, color: C.navy });
  addText(slide, "Gates precisam registrar cobertura, confiança e exceções. Severidade isolada não substitui triagem.", 740, 450, 440, 110, { fontSize: 25, color: C.ink });
  addText(slide, "Defesa em profundidade com critérios explícitos", 156, 586, 970, 44, { fontSize: 28, bold: true, color: C.green, alignment: "center" });
  setNotes(slide, "A conclusão mantém as quatro ferramentas no toolchain e diferencia ausência de achados de ausência de cobertura.");
}

// 26 Referências e perguntas
{
  const slide = presentation.slides.add();
  addHeader(slide, 26, "Referências e perguntas", "Encerramento");
  const leftRefs = [
    "NIST SP 800-218 Secure Software Development Framework",
    "OWASP DevSecOps Guideline",
    "OWASP Top 10 A03 Injection",
    "Semgrep Documentation and Repository",
    "OWASP Dependency Check Documentation",
  ];
  const rightRefs = [
    "Checkov Documentation and Repository",
    "OWASP ZAP Automation Framework",
    "OWASP Juice Shop v20.2.0",
    "MITRE CWE-89 and CWE-319",
    "CISA Minimum Elements for an SBOM",
  ];
  addText(slide, "Fontes principais", 80, 162, 340, 38, { fontSize: 25, bold: true, color: C.cyan });
  addBullets(slide, leftRefs, 80, 212, 520, 270, { fontSize: 21, spaceAfter: 7 });
  addBullets(slide, rightRefs, 660, 212, 530, 270, { fontSize: 21, spaceAfter: 7 });
  addRule(slide, 80, 508, 1110);
  addText(slide, "Perguntas?", 80, 548, 480, 70, { fontSize: 52, bold: true, color: C.navy });
  addText(slide, "Relatório, laboratório e evidências no repositório do Grupo 4", 590, 550, 600, 70, { fontSize: 25, color: C.muted, alignment: "right" });
  setNotes(slide, "Referências completas no relatório. Repositório: https://github.com/TiagoLouzaPetagna/grupo4-devsecops");
}

const requirements = {
  explicitTotalSlideCount: 26,
  requiredNativeTableOwnerSlides: [16, 23, 24],
  requiredNativeChartOwnerSlides: [15, 19],
  materializeLiteralChartWorkbooks: true,
};
const fontPolicy = { basis: "design", families: [fontFamily, "Consolas"] };
const expectedSlideSizeEmu = "12192000,6858000";
const stagingDir = path.join(ROOT, ".qa", "slides-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

await finalizePresentation({
  ...requirements,
  workspaceDir: ROOT,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", expectedSlideSizeEmu,
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--require-native-table-slide", "16",
    "--require-native-table-slide", "23",
    "--require-native-table-slide", "24",
  ],
  requiredNativeTableOwnerSlides: requirements.requiredNativeTableOwnerSlides,
  requiredNativeChartOwnerSlides: requirements.requiredNativeChartOwnerSlides,
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "Apresentacao_Checkpoint_DevSecOps_Grupo4_corrigida.validation.json"),
});

for (let i = 0; i < presentation.slides.items.length; i += 1) {
  const slide = presentation.slides.items[i];
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(TMP_DIR, `slide-${String(i + 1).padStart(2, "0")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const montage = await presentation.export({ format: "webp", montage: true, scale: 0.5 });
await fs.writeFile(path.join(TMP_DIR, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));

console.log(FINAL_PPTX);
