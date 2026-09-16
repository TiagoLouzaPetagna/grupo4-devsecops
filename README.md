# Check Point 01 — DevSecOps — Grupo 4

Repositório oficial: <https://github.com/TiagoLouzaPetagna/grupo4-devsecops>

## Equipe

| Integrante | RM | Responsabilidade |
|---|---:|---|
| Tiago Louzã | — | Líder técnico e responsável pelo repositório |
| Leando de Souza Silva | 566485 | Integrante |
| Luiz Fernando | 562652 | Integrante |
| Fabricio de Freitas Evangelista | 564782 | Integrante |
| Erik Gunnar | 565107 | Relator |

Professor: **Fabio Pires**.

Pacote de apoio para o estudo e o laboratório das ferramentas definidas para o Grupo 4:

| Categoria | Ferramenta | Papel na entrega |
|---|---|---|
| SAST | Semgrep | Análise estática e gate red/green |
| SCA | OWASP Dependency-Check | Estudo comparativo e exemplo Maven |
| IaC | Checkov | Estudo comparativo e exemplo Terraform |
| DAST | OWASP ZAP | Varredura dinâmica automatizada |

O alvo do laboratório é o **OWASP Juice Shop v20.2.0**, aplicação deliberadamente insegura mantida pela OWASP. A imagem oficial roda somente em `127.0.0.1:3000`, dentro de uma rede Docker isolada. O Semgrep analisa o código-fonte oficial do mesmo release.

## Estrutura

- `LAB.md`: roteiro reproduzível e divisão dos 12 minutos.
- `docker-compose.yml`: Juice Shop, Semgrep, ZAP e executor do gate.
- `security/semgrep.yml`: regras para SQL Injection, `eval()` e bypass de sanitização Angular.
- `security/zap-juice-shop.yaml`: spider, AJAX spider, active scan e relatórios.
- `scripts/fetch-target.ps1`: baixa o código oficial fixado em v20.2.0.
- `scripts/prepare-green.ps1`: cria uma cópia com correção parametrizada da busca SQL.
- `scripts/run-lab.ps1`: executa SAST vermelho, SAST verde e DAST.
- `scripts/quality-gate.mjs`: bloqueia achados HIGH/CRITICAL.
- `analysis/ACHADOS.md`: classificação e tratamento de três achados reais.
- `examples`: demonstrações opcionais de Dependency-Check e Checkov.
- `USO-DE-IA.md`: declaração transparente de apoio por IA.

## Pré-requisitos

- Docker Desktop usando contêineres Linux.
- Docker Compose.
- PowerShell 7 ou Windows PowerShell 5.1.
- Internet na primeira execução para baixar imagens e o código-fonte oficial.

Validação do ambiente:

```powershell
docker version
docker compose version
docker info
```

Preparação recomendada antes da aula:

```powershell
git clone https://github.com/TiagoLouzaPetagna/grupo4-devsecops.git
Set-Location grupo4-devsecops
docker compose --profile tools pull
docker pull ghcr.io/bridgecrewio/checkov:3.3.11
docker pull owasp/dependency-check:13.0.0
```

O `docker compose --profile tools pull` baixa as imagens do Juice Shop, Semgrep,
OWASP ZAP e do executor Node usado pelo quality gate. Os dois comandos seguintes
baixam Checkov e OWASP Dependency-Check, usados nas execuções complementares.

## Execução rápida

Na raiz deste projeto, o participante digita somente:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-lab.ps1 -Mode all
```

Esse script verifica o Docker, baixa o código oficial do Juice Shop quando
necessário, executa Semgrep ou ZAP, grava os relatórios e chama o quality gate.
Os comandos internos de `docker compose`, `semgrep scan`, `zap.sh` e
`quality-gate.mjs` já estão automatizados em `scripts/run-lab.ps1`.

Execuções separadas:

```powershell
.\scripts\run-lab.ps1 -Mode sast-red
.\scripts\run-lab.ps1 -Mode sast-green
.\scripts\run-lab.ps1 -Mode dast
```

Para demonstrar uma execução realmente vermelha e outra verde no GitHub Actions,
abra a action **Grupo 4 — demonstração red/green**, escolha **Run workflow** e
execute primeiro o cenário `red` e depois o cenário `green`.

Resultados validados em 15 set. 2026:

- **SAST red:** 1 HIGH na interpolação SQL em `routes/search.ts`; gate bloqueado.
- **SAST green:** 0 HIGH/CRITICAL após parametrização com `replacements`; gate aprovado.
- **DAST:** 11 tipos de alerta, incluindo 1 HIGH de SQL Injection; gate bloqueado. O ZAP gerou JSON, HTML e SARIF.

Os relatórios ficam em `reports/`. A pasta `target/` é gerada e não deve ser enviada como autoria do grupo.

## Ética e segurança

Não use o plano do ZAP contra a instância pública de demonstração nem contra qualquer terceiro. O repositório oficial deixa claro que a demonstração pública não é alvo para testes. Esta atividade limita a varredura à cópia local deliberadamente vulnerável.

## Plano B

Antes da aula, gere e versione os relatórios finais. Se o Docker ou a rede falhar durante a apresentação, mostre essas evidências e execute o gate sobre os JSON já gerados. Não improvise testes contra um serviço externo.
