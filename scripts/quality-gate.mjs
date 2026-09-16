import fs from "node:fs";
import path from "node:path";

const severityRank = { LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };

function usage() {
  console.log("Uso: node quality-gate.mjs [--semgrep <json>] [--zap <json>] [--threshold HIGH] [--expect pass|fail]");
}

function parseArgs(values) {
  const result = { threshold: "HIGH", expect: "pass" };
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index]?.replace(/^--/, "");
    const value = values[index + 1];
    if (!key || value === undefined) throw new Error("Argumentos incompletos.");
    result[key] = value;
  }
  return result;
}

function readJson(filePath) {
  if (!filePath) return null;
  const absolutePath = path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Relatório não encontrado: ${absolutePath}`);
  return JSON.parse(fs.readFileSync(absolutePath, "utf8"));
}

function normalizeSemgrep(report) {
  if (!report) return [];
  return (report.results || []).map((finding) => {
    const semgrepSeverity = String(finding.extra?.severity || "INFO").toUpperCase();
    const mapped = { INFO: "LOW", WARNING: "MEDIUM", ERROR: "HIGH" }[semgrepSeverity] || "LOW";
    return {
      source: "Semgrep",
      id: finding.check_id || "semgrep-unknown",
      severity: mapped,
      location: `${finding.path || "?"}:${finding.start?.line || "?"}`,
      message: finding.extra?.message || "Sem mensagem",
    };
  });
}

function normalizeZap(report) {
  if (!report) return [];
  const sites = report.site || report.sites || [];
  const findings = [];
  for (const site of sites) {
    for (const alert of site.alerts || []) {
      const riskCode = Number(alert.riskcode ?? alert.riskCode ?? -1);
      const fromCode = { 0: "LOW", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL" }[riskCode];
      const riskText = String(alert.riskdesc || alert.risk || "LOW").split(/[\s(]/)[0].toUpperCase();
      const severity = fromCode || (severityRank[riskText] ? riskText : "LOW");
      findings.push({
        source: "OWASP ZAP",
        id: String(alert.pluginid || alert.alertRef || alert.name || "zap-unknown"),
        severity,
        location: site["@name"] || site.name || "target",
        message: alert.alert || alert.name || "Alerta sem nome",
      });
    }
  }
  return findings;
}

try {
  const args = parseArgs(process.argv.slice(2));
  const threshold = String(args.threshold).toUpperCase();
  const expect = String(args.expect).toLowerCase();
  if (!severityRank[threshold] || !["pass", "fail"].includes(expect)) {
    usage();
    process.exit(2);
  }

  const findings = [
    ...normalizeSemgrep(readJson(args.semgrep)),
    ...normalizeZap(readJson(args.zap)),
  ];
  const blocking = findings.filter((finding) => severityRank[finding.severity] >= severityRank[threshold]);

  console.log(`\nGate DevSecOps — limiar ${threshold}`);
  console.log(`Achados totais: ${findings.length} | Bloqueadores: ${blocking.length}`);
  for (const finding of blocking) {
    console.log(`- [${finding.severity}] ${finding.source} ${finding.id} — ${finding.message} (${finding.location})`);
  }

  if (expect === "fail") {
    if (blocking.length === 0) {
      console.error("FALHA DO TESTE: o cenário vulnerável não foi bloqueado.");
      process.exit(2);
    }
    console.log("SUCESSO DO TESTE: o gate bloqueou o cenário vulnerável como esperado.");
    process.exit(0);
  }

  if (blocking.length > 0) {
    console.error("GATE BLOQUEADO: corrija ou trate formalmente os achados HIGH/CRITICAL.");
    process.exit(1);
  }
  console.log("GATE APROVADO: nenhum HIGH/CRITICAL nos relatórios informados.");
} catch (error) {
  console.error(`Erro no gate: ${error.message}`);
  usage();
  process.exit(2);
}
