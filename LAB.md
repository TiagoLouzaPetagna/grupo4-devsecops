# Laboratório reproduzível — Juice Shop + Semgrep + Dependency-Check + ZAP

**Grupo 4:** Tiago Louzã (RM562404, líder técnico), Luiz Fernando (RM562652),
Fabricio de Freitas Evangelista (RM564782),
Mateus Kalil (RM565098) e Erik Gunnar (RM565107, relator).

**Professor:** Fabio Pires  
**Repositório:** <https://github.com/TiagoLouzaPetagna/grupo4-devsecops>

## 1. Objetivo

Demonstrar como SAST, SCA, análise de infraestrutura como código e DAST examinam
um alvo conhecido e autorizado, e como políticas automatizadas reagem a achados
acima dos limites definidos.

O alvo é o **OWASP Juice Shop v20.2.0**, projeto deliberadamente vulnerável da OWASP. A imagem e o código-fonte usam a mesma versão. A aplicação é publicada somente em `127.0.0.1:3000` e o scanner se comunica com ela por uma rede interna do Docker Compose.

## 2. Escopo e autorização

- Alvo permitido: contêiner local `bkimminich/juice-shop:v20.2.0`.
- Código permitido: release oficial v20.2.0 baixado em `target/juice-shop`.
- Ferramentas: Semgrep 1.172.0, OWASP Dependency-Check 13.0.0 e OWASP ZAP 2.17.0.
- Dados: apenas dados sintéticos da própria aplicação de treinamento.
- Proibido: testar a demo pública do Juice Shop ou qualquer endereço de terceiro.

## 3. Preparação inicial

Windows PowerShell:

```powershell
git clone https://github.com/TiagoLouzaPetagna/grupo4-devsecops.git
Set-Location grupo4-devsecops
docker version
docker compose version
docker compose --profile tools pull
docker pull owasp/dependency-check:13.0.0
docker volume create grupo4-odc-data
Set-ExecutionPolicy -Scope Process Bypass
```

Linux com Bash:

```bash
git clone https://github.com/TiagoLouzaPetagna/grupo4-devsecops.git
cd grupo4-devsecops
docker version
docker compose version
docker compose --profile tools pull
docker pull owasp/dependency-check:13.0.0
docker volume create grupo4-odc-data
chmod +x scripts/*.sh
```

Atualize a base de CVEs antes do primeiro scan. Essa etapa pode demorar na
primeira execução:

```powershell
docker run --rm `
  -v grupo4-odc-data:/usr/share/dependency-check/data `
  owasp/dependency-check:13.0.0 `
  --updateonly `
  --nvdDatafeed "https://dependency-check.github.io/DependencyCheck_Builder/nvd_cache/nvdcve-{0}.json.gz"
```

No Linux, o mesmo comando usa barra invertida:

```bash
docker run --rm \
  -v grupo4-odc-data:/usr/share/dependency-check/data \
  owasp/dependency-check:13.0.0 \
  --updateonly \
  --nvdDatafeed "https://dependency-check.github.io/DependencyCheck_Builder/nvd_cache/nvdcve-{0}.json.gz"
```

Os scanners serão chamados diretamente por comandos Docker. O único script da
etapa de correção é `prepare-green.ps1`, que cria uma cópia segura sem alterar o
arquivo vulnerável original. `fetch-target.ps1` baixa o release oficial e
`quality-gate.mjs` interpreta os JSON, mas nenhum deles executa um scanner.
No Linux, use os equivalentes `fetch-target.sh` e `prepare-green.sh`; não é
necessário instalar PowerShell.

Execute cada análise, confirme os relatórios em `reports/` e registre os números
reais em `analysis/ACHADOS.md`.

## 4. SAST — build vermelho

Windows PowerShell:

```powershell
.\scripts\fetch-target.ps1
New-Item -ItemType Directory -Force .\reports | Out-Null
```

Linux com Bash:

```bash
./scripts/fetch-target.sh
mkdir -p reports
```

Execute o Semgrep no terminal correspondente. No PowerShell, use crase como
continuação de linha:

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

No Bash, use barra invertida:

```bash
docker compose --profile tools run --rm semgrep semgrep scan \
  --config auto \
  --json \
  --output /workspace/reports/semgrep-red.json \
  /workspace/target/juice-shop/routes/search.ts

docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs \
  --semgrep /workspace/reports/semgrep-red.json \
  --threshold HIGH \
  --expect fail
```

O Semgrep usa `--config auto`, que consulta o catálogo comunitário e seleciona
regras gerais compatíveis com TypeScript. Não existe regra Semgrep criada pelo
grupo. No release fixado, a regra comunitária
`javascript.sequelize.security.audit.sequelize-injection-express.express-sequelize-injection`
identifica o fluxo de entrada do Express até `sequelize.query` na linha 23. A
severidade `ERROR` é normalizada como HIGH. `--expect fail` faz o teste terminar
com sucesso somente quando comprova que o gate bloquearia o código vulnerável.

## 5. SAST — correção e build verde

Windows PowerShell:

```powershell
.\scripts\prepare-green.ps1
```

Linux com Bash:

```bash
./scripts/prepare-green.sh
```

Continuação no PowerShell:

```powershell

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

Continuação no Bash:

```bash
docker compose --profile tools run --rm semgrep semgrep scan \
  --config auto \
  --json \
  --output /workspace/reports/semgrep-green.json \
  /workspace/target/juice-shop-fixed/routes/search.ts

docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs \
  --semgrep /workspace/reports/semgrep-green.json \
  --threshold HIGH \
  --expect pass
```

`prepare-green.ps1` preserva o original e cria `target/juice-shop-fixed/routes/search.ts`. A cópia troca a interpolação no SQL por um marcador `:criteria` e envia o valor por `replacements`. O Semgrep escaneia a cópia e o gate exige zero HIGH/CRITICAL nesse recorte.

O green usa o mesmo `--config auto` e muda somente o arquivo analisado. Isso evita
que uma regra feita especificamente para a correção produza um resultado
artificial. O recorte de um arquivo permite demonstrar a mudança red/green sem
misturar essa validação com os demais achados deliberados do Juice Shop.

Essa etapa demonstra a correção de um achado, não afirma que todo o Juice Shop ficou seguro. O alvo continua propositalmente vulnerável.

## 6. SCA com OWASP Dependency-Check

O alvo continua sendo exclusivamente o código oficial do Juice Shop. O grupo não
adiciona dependências vulneráveis nem usa uma aplicação separada para produzir
achados. O gate nativo falha somente se o relatório contiver CVSS 7 ou superior.

```powershell
$ProjectDir = (Get-Location).Path
New-Item -ItemType Directory -Force .\reports\dependency-check | Out-Null
$OdcReports = @(
  '.\reports\dependency-check\dependency-check-report.html',
  '.\reports\dependency-check\dependency-check-report.json',
  '.\reports\dependency-check\dependency-check-report.sarif'
)
Remove-Item -Force $OdcReports -ErrorAction SilentlyContinue

docker run --rm `
  -v "${ProjectDir}\target\juice-shop:/src/target/juice-shop:ro" `
  -v "${ProjectDir}\reports\dependency-check:/report" `
  -v grupo4-odc-data:/usr/share/dependency-check/data `
  owasp/dependency-check:13.0.0 `
  --scan /src/target/juice-shop `
  --exclude '**/test/files/**' `
  --out /report `
  --format HTML `
  --format JSON `
  --format SARIF `
  --project "OWASP Juice Shop v20.2.0 - Grupo 4" `
  --noupdate `
  --disableOssIndex `
  --enableExperimental `
  --failOnCVSS 7
```

A ausência de lockfile e `node_modules` no release limita o inventário. Por isso,
zero CVEs significa apenas que nenhuma CVE foi confirmada nas dependências que a
ferramenta conseguiu observar. Essa limitação deve permanecer documentada na
interpretação do resultado.

Na execução validada em 16 set. 2026, a base atualizada observou 11 dependências,
0 CVEs e 0 exceções. O gate terminou com aprovação porque nenhuma pontuação CVSS
atingiu o limite 7.

No Linux, substitua o bloco PowerShell anterior por:

```bash
project_dir="$(pwd)"
mkdir -p reports/dependency-check
rm -f reports/dependency-check/dependency-check-report.html
rm -f reports/dependency-check/dependency-check-report.json
rm -f reports/dependency-check/dependency-check-report.sarif

docker run --rm \
  -v "$project_dir/target/juice-shop:/src/target/juice-shop:ro" \
  -v "$project_dir/reports/dependency-check:/report" \
  -v grupo4-odc-data:/usr/share/dependency-check/data \
  owasp/dependency-check:13.0.0 \
  --scan /src/target/juice-shop \
  --exclude '**/test/files/**' \
  --out /report \
  --format HTML \
  --format JSON \
  --format SARIF \
  --project "OWASP Juice Shop v20.2.0 - Grupo 4" \
  --noupdate \
  --disableOssIndex \
  --enableExperimental \
  --failOnCVSS 7
```

## 7. DAST com OWASP ZAP

```powershell
docker compose up -d juice-shop
docker compose --profile tools run --rm zap
docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
  --zap /workspace/reports/zap-juice-shop.json `
  --threshold HIGH `
  --expect fail
```

No Linux, os comandos são os mesmos, trocando apenas a continuação do gate:

```bash
docker compose up -d juice-shop
docker compose --profile tools run --rm zap
docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs \
  --zap /workspace/reports/zap-juice-shop.json \
  --threshold HIGH \
  --expect fail
```

O arquivo `security/zap-juice-shop.yaml` é um plano de automação, não uma regra de
detecção criada pelo grupo. As regras de SQL Injection e XSS executadas pelo ZAP
pertencem aos add-ons oficiais. O plano define alvo local, spiders, limite de tempo
e formatos dos relatórios.

O plano automatizado executa spider tradicional, AJAX spider, varredura passiva e active scan limitado às regras de XSS refletido e SQL Injection. O tempo do active scan é limitado a quatro minutos. São gerados:

- `zap-juice-shop.html`
- `zap-juice-shop.json`
- `zap-juice-shop.sarif.json`

Na execução validada em 15 set. 2026, o spider tradicional encontrou 101 URLs, o AJAX spider encontrou 233 e o relatório apresentou 11 tipos de alerta. A regra 40018 sinalizou uma SQL Injection HIGH em `/rest/products/search?q=...`; o gate bloqueou o cenário. O resultado de uma nova execução pode variar conforme cobertura e versão, portanto sempre confira o JSON em vez de repetir números por pressuposição.

## 8. Checkov por comando

Defina o caminho absoluto do projeto uma vez:

```powershell
$ProjectDir = (Get-Location).Path
```

```powershell
docker run --rm `
  -v "${ProjectDir}\target\juice-shop\terraform:/tf:ro" `
  ghcr.io/bridgecrewio/checkov:3.3.11 `
  -d /tf `
  --framework terraform `
  --quiet `
  --compact `
  --soft-fail
```

O Checkov usa somente as políticas nativas, sem regra criada pelo grupo.

No Linux:

```bash
project_dir="$(pwd)"
docker run --rm \
  -v "$project_dir/target/juice-shop/terraform:/tf:ro" \
  ghcr.io/bridgecrewio/checkov:3.3.11 \
  -d /tf \
  --framework terraform \
  --quiet \
  --compact \
  --soft-fail
```

## 9. Política do gate

| Fonte | Regra | Normalização |
|---|---|---|
| Semgrep | `ERROR` | HIGH |
| Dependency-Check | `CVSS >= 7` | HIGH/CRITICAL conforme o CVSS |
| ZAP | `riskcode: 3` | HIGH |
| ZAP | `riskcode: 4` | CRITICAL |

O laboratório bloqueia HIGH/CRITICAL. Em produção, a política também precisaria de contexto de exposição, explorabilidade, proprietário, prazo e exceção formalmente aprovada.

## 10. Três achados para análise

1. **SQL Injection na busca — Semgrep + ZAP:** CWE-89, verdadeiro positivo corroborado, correção por parâmetros.
2. **Content Security Policy ausente — ZAP:** CWE-693, verdadeiro positivo de configuração; impacto depende das demais defesas.
3. **CORS com origem curinga — ZAP:** configuração permissiva real, mas impacto contextual nas rotas públicas observadas.

Acrescente os alertas reais do ZAP após a execução, sempre vinculados ao relatório.

## 11. Limpeza

```powershell
docker compose --profile tools down --remove-orphans
```

Esse comando remove somente os contêineres e a rede do laboratório. As imagens
permanecem em cache para evitar novo download em execuções futuras.
