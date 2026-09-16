# Relatórios

Esta pasta recebe os relatórios reais produzidos pelo Semgrep e pelo OWASP ZAP.

Arquivos esperados após `scripts/run-lab.ps1 -Mode all`:

- `semgrep-red.json`
- `semgrep-green.json`
- `zap-juice-shop.json`
- `zap-juice-shop.html`
- `zap-juice-shop.sarif.json`

Execução validada em 15 set. 2026:

- Semgrep red: 1 HIGH, gate bloqueado como esperado;
- Semgrep green: 0 HIGH/CRITICAL, gate aprovado;
- ZAP: 11 tipos de alerta (1 HIGH, 4 MEDIUM, 3 LOW e 3 INFO), gate bloqueado como esperado.

Resultados fictícios não são usados como substitutos de execução. A interpretação detalhada está em `../analysis/ACHADOS.md`.
