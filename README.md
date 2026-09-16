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
- `security/zap-juice-shop.yaml`: spider, AJAX spider, active scan e relatórios.
- `scripts/fetch-target.ps1`: baixa o código oficial fixado em v20.2.0.
- `scripts/prepare-green.ps1`: cria uma cópia com correção parametrizada da busca SQL.
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

## Execução do laboratório

Os scanners são executados diretamente por comandos Docker. Nenhum script inicia
Semgrep, ZAP, Dependency-Check ou Checkov. Os scripts restantes apenas baixam o
código, preparam a cópia corrigida e interpretam os relatórios no quality gate.

Na raiz do projeto, prepare o alvo e a pasta de relatórios:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\fetch-target.ps1
New-Item -ItemType Directory -Force .\reports | Out-Null
```

### Semgrep red com regras gerais

`--config auto` seleciona regras comunitárias adequadas à linguagem. O grupo não
mantém arquivo de regras próprio. O caminho ao final limita somente o alvo do
red/green a um arquivo, para que a correção desse arquivo possa ser verificada.

```powershell
docker compose --profile tools run --rm semgrep semgrep scan `
  --config auto `
  --json `
  --output /workspace/reports/semgrep-red.json `
  /workspace/target/juice-shop/routes/search.ts

docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
  --semgrep /workspace/reports/semgrep-red.json `
  --threshold HIGH `
  --expect fail
```

### Correção e Semgrep green

```powershell
.\scripts\prepare-green.ps1

docker compose --profile tools run --rm semgrep semgrep scan `
  --config auto `
  --json `
  --output /workspace/reports/semgrep-green.json `
  /workspace/target/juice-shop-fixed/routes/search.ts

docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
  --semgrep /workspace/reports/semgrep-green.json `
  --threshold HIGH `
  --expect pass
```

### OWASP ZAP

```powershell
docker compose up -d juice-shop
docker compose --profile tools run --rm zap
docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
  --zap /workspace/reports/zap-juice-shop.json `
  --threshold HIGH `
  --expect fail
docker compose --profile tools down --remove-orphans
```

Os comandos diretos de Dependency-Check e Checkov estão no `LAB.md`.

Para demonstrar uma execução realmente vermelha e outra verde no GitHub Actions,
abra a action **Grupo 4 — demonstração red/green**, escolha **Run workflow** e
execute primeiro o cenário `red` e depois o cenário `green`.

Resultados validados em 15 set. 2026:

- **SAST red:** a regra comunitária de injeção via Sequelize encontrou 1 ERROR,
  normalizado como HIGH; gate bloqueado.
- **SAST green:** 0 HIGH/CRITICAL após parametrização com `replacements`; gate aprovado.
- **DAST:** 11 tipos de alerta, incluindo 1 HIGH de SQL Injection; gate bloqueado. O ZAP gerou JSON, HTML e SARIF.

Os relatórios ficam em `reports/`. A pasta `target/` é gerada e não deve ser enviada como autoria do grupo.

## Ética e segurança

Não use o plano do ZAP contra a instância pública de demonstração nem contra qualquer terceiro. O repositório oficial deixa claro que a demonstração pública não é alvo para testes. Esta atividade limita a varredura à cópia local deliberadamente vulnerável.

## Plano B

Antes da aula, gere e versione os relatórios finais. Se o Docker ou a rede falhar durante a apresentação, mostre essas evidências e execute o gate sobre os JSON já gerados. Não improvise testes contra um serviço externo.
