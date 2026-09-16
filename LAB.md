# Laboratório reproduzível — OWASP Juice Shop + Semgrep + ZAP

**Grupo 4:** Tiago Louzã (RM562404, líder técnico), Leandro de Souza da Silva (RM566485),
Luiz Fernando (RM562652), Fabricio de Freitas Evangelista (RM564782),
Mateus Kalil (RM565098) e Erik Gunnar (RM565107, relator).

**Professor:** Fabio Pires  
**Repositório:** <https://github.com/TiagoLouzaPetagna/grupo4-devsecops>

## 1. Objetivo

Demonstrar, em até 12 minutos, como SAST e DAST identificam vulnerabilidades em um alvo conhecido e autorizado, e como uma política automatizada impede a promoção de código com severidade alta.

O alvo é o **OWASP Juice Shop v20.2.0**, projeto deliberadamente vulnerável da OWASP. A imagem e o código-fonte usam a mesma versão. A aplicação é publicada somente em `127.0.0.1:3000` e o scanner se comunica com ela por uma rede interna do Docker Compose.

## 2. Escopo e autorização

- Alvo permitido: contêiner local `bkimminich/juice-shop:v20.2.0`.
- Código permitido: release oficial v20.2.0 baixado em `target/juice-shop`.
- Ferramentas: Semgrep 1.172.0 e OWASP ZAP 2.17.0.
- Dados: apenas dados sintéticos da própria aplicação de treinamento.
- Proibido: testar a demo pública do Juice Shop ou qualquer endereço de terceiro.

## 3. Preparação antes da aula

```powershell
git clone https://github.com/TiagoLouzaPetagna/grupo4-devsecops.git
Set-Location grupo4-devsecops
docker version
docker compose version
docker compose --profile tools pull
Set-ExecutionPolicy -Scope Process Bypass
```

Os scanners serão chamados diretamente por comandos Docker. O único script da
etapa de correção é `prepare-green.ps1`, que cria uma cópia segura sem alterar o
arquivo vulnerável original. `fetch-target.ps1` baixa o release oficial e
`quality-gate.mjs` interpreta os JSON, mas nenhum deles executa um scanner.

Antes da aula, o grupo deve percorrer as seções 5 a 9, confirmar os relatórios em
`reports/` e registrar os números reais em `analysis/ACHADOS.md`.

## 4. Roteiro de 12 minutos

| Tempo | Parte | Ação | Evidência |
|---|---|---|---|
| 0:00–1:00 | Escopo | Apresentar Juice Shop, versão fixada e isolamento | Compose e aviso ético |
| 1:00–3:00 | SAST red | Mostrar `routes/search.ts` e executar Semgrep | SQL interpolado, CWE-89 |
| 3:00–4:30 | Gate red | Processar o JSON com limiar HIGH | Bloqueio esperado |
| 4:30–6:00 | Correção | Mostrar query parametrizada na cópia de trabalho | `replacements` do Sequelize |
| 6:00–7:00 | Gate green | Reexecutar Semgrep | Ausência do HIGH específico |
| 7:00–10:30 | DAST | Executar ZAP no contêiner local | JSON, HTML e SARIF |
| 10:30–12:00 | Análise | Discutir três achados, VP/FP e limitações | Matriz de achados |

Distribua as partes entre os integrantes reais do grupo.

## 5. SAST — build vermelho

```powershell
.\scripts\fetch-target.ps1
New-Item -ItemType Directory -Force .\reports | Out-Null

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

O Semgrep usa `--config auto`, que consulta o catálogo comunitário e seleciona
regras gerais compatíveis com TypeScript. Não existe regra Semgrep criada pelo
grupo. No release fixado, a regra comunitária
`javascript.sequelize.security.audit.sequelize-injection-express.express-sequelize-injection`
identifica o fluxo de entrada do Express até `sequelize.query` na linha 23. A
severidade `ERROR` é normalizada como HIGH. `--expect fail` faz o teste terminar
com sucesso somente quando comprova que o gate bloquearia o código vulnerável.

## 6. SAST — correção e build verde

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

`prepare-green.ps1` preserva o original e cria `target/juice-shop-fixed/routes/search.ts`. A cópia troca a interpolação no SQL por um marcador `:criteria` e envia o valor por `replacements`. O Semgrep escaneia a cópia e o gate exige zero HIGH/CRITICAL nesse recorte.

O green usa o mesmo `--config auto` e muda somente o arquivo analisado. Isso evita
que uma regra feita especificamente para a correção produza um resultado
artificial. O recorte de um arquivo permite demonstrar a mudança red/green sem
confundir a turma com os demais achados deliberados do Juice Shop.

Essa etapa demonstra a correção de um achado, não afirma que todo o Juice Shop ficou seguro. O alvo continua propositalmente vulnerável.

## 7. DAST com OWASP ZAP

```powershell
docker compose up -d juice-shop
docker compose --profile tools run --rm zap
docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
  --zap /workspace/reports/zap-juice-shop.json `
  --threshold HIGH `
  --expect fail
docker compose --profile tools down --remove-orphans
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

## 8. Dependency-Check e Checkov por comandos

As duas ferramentas complementares também são executadas diretamente. Defina o
caminho absoluto do projeto uma vez:

```powershell
$ProjectDir = (Get-Location).Path
```

Dependency-Check:

```powershell
New-Item -ItemType Directory -Force .\reports\dependency-check | Out-Null
docker run --rm `
  -v "${ProjectDir}\target\juice-shop:/src/target/juice-shop:ro" `
  -v "${ProjectDir}\reports\dependency-check:/report" `
  owasp/dependency-check:13.0.0 `
  --scan /src/target/juice-shop `
  --out /report `
  --format ALL `
  --project "Checkpoint DevSecOps Grupo 4" `
  --noupdate `
  --disableOssIndex `
  --enableExperimental
```

Checkov:

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

O resultado limitado do Dependency-Check continua registrado como inconclusivo,
pois o release baixado não contém lockfiles nem `node_modules`. O Checkov usa
somente as políticas nativas, sem regra criada pelo grupo.

## 9. Política do gate

| Fonte | Regra | Normalização |
|---|---|---|
| Semgrep | `ERROR` | HIGH |
| ZAP | `riskcode: 3` | HIGH |
| ZAP | `riskcode: 4` | CRITICAL |

O laboratório bloqueia HIGH/CRITICAL. Em produção, a política também precisaria de contexto de exposição, explorabilidade, proprietário, prazo e exceção formalmente aprovada.

## 10. Três achados para análise

1. **SQL Injection na busca — Semgrep + ZAP:** CWE-89, verdadeiro positivo corroborado, correção por parâmetros.
2. **Content Security Policy ausente — ZAP:** CWE-693, verdadeiro positivo de configuração; impacto depende das demais defesas.
3. **CORS com origem curinga — ZAP:** configuração permissiva real, mas impacto contextual nas rotas públicas observadas.

Acrescente os alertas reais do ZAP após a execução, sempre vinculados ao relatório.

## 11. Plano B

Se Docker ou rede falhar durante a apresentação:

1. mostrar os relatórios previamente gerados;
2. comparar `target/juice-shop/routes/search.ts` com a cópia corrigida;
3. executar apenas o gate nos JSON, se a imagem `node:22-alpine` estiver em cache;
4. explicar que código, regras, versões e política continuam rastreáveis.

## 12. Limpeza

```powershell
docker compose --profile tools down --remove-orphans
```

Esse comando remove somente os contêineres e a rede do laboratório. As imagens permanecem em cache para evitar novo download durante a aula.
