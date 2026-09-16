# Laboratório reproduzível — OWASP Juice Shop + Semgrep + ZAP

**Grupo 4:** Tiago Louzã (líder técnico), Leando de Souza Silva (RM566485),
Luiz Fernando (RM562652), Fabricio de Freitas Evangelista (RM564782) e
Erik Gunnar (RM565107, relator).

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

Os participantes não precisam digitar diretamente os comandos extensos de
Semgrep, ZAP ou do quality gate. Eles estão dentro de `scripts/run-lab.ps1`.
Durante o laboratório serão usados somente os três comandos das seções 5, 6 e 7.

O grupo deve executar `-Mode all` antes da aula, confirmar os relatórios em
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
.\scripts\run-lab.ps1 -Mode sast-red
```

Esse comando executa automaticamente o Semgrep e o quality gate. O participante
não precisa copiar os comandos internos de Docker.

O Semgrep procura interpolação dentro de `sequelize.query`. No release fixado, `routes/search.ts` concatena `req.query.q` em uma instrução SQL. O relatório `semgrep-red.json` deve conter `juice-shop.typescript.sql-injection` com severidade normalizada HIGH. O gate passa como teste apenas quando comprova que o build vulnerável seria bloqueado.

## 6. SAST — correção e build verde

```powershell
.\scripts\run-lab.ps1 -Mode sast-green
```

Esse comando cria a cópia corrigida, repete o Semgrep e valida o resultado no gate.

`prepare-green.ps1` preserva o original e cria `target/juice-shop-fixed/routes/search.ts`. A cópia troca a interpolação no SQL por um marcador `:criteria` e envia o valor por `replacements`. O Semgrep escaneia a cópia e o gate exige zero HIGH/CRITICAL nesse recorte.

Essa etapa demonstra a correção de um achado, não afirma que todo o Juice Shop ficou seguro. O alvo continua propositalmente vulnerável.

## 7. DAST com OWASP ZAP

```powershell
.\scripts\run-lab.ps1 -Mode dast
```

Esse comando sobe o Juice Shop, executa o plano do ZAP, processa o relatório no
gate e encerra os contêineres ao final.

O plano automatizado executa spider tradicional, AJAX spider, varredura passiva e active scan limitado às regras de XSS refletido e SQL Injection. O tempo do active scan é limitado a quatro minutos. São gerados:

- `zap-juice-shop.html`
- `zap-juice-shop.json`
- `zap-juice-shop.sarif.json`

Na execução validada em 15 set. 2026, o spider tradicional encontrou 101 URLs, o AJAX spider encontrou 233 e o relatório apresentou 11 tipos de alerta. A regra 40018 sinalizou uma SQL Injection HIGH em `/rest/products/search?q=...`; o gate bloqueou o cenário. O resultado de uma nova execução pode variar conforme cobertura e versão, portanto sempre confira o JSON em vez de repetir números por pressuposição.

## 8. Política do gate

| Fonte | Regra | Normalização |
|---|---|---|
| Semgrep | `ERROR` ou `devsecops_severity: HIGH` | HIGH |
| ZAP | `riskcode: 3` | HIGH |
| ZAP | `riskcode: 4` | CRITICAL |

O laboratório bloqueia HIGH/CRITICAL. Em produção, a política também precisaria de contexto de exposição, explorabilidade, proprietário, prazo e exceção formalmente aprovada.

## 9. Três achados para análise

1. **SQL Injection na busca — Semgrep + ZAP:** CWE-89, verdadeiro positivo corroborado, correção por parâmetros.
2. **Content Security Policy ausente — ZAP:** CWE-693, verdadeiro positivo de configuração; impacto depende das demais defesas.
3. **CORS com origem curinga — ZAP:** configuração permissiva real, mas impacto contextual nas rotas públicas observadas.

Acrescente os alertas reais do ZAP após a execução, sempre vinculados ao relatório.

## 10. Plano B

Se Docker ou rede falhar durante a apresentação:

1. mostrar os relatórios previamente gerados;
2. comparar `target/juice-shop/routes/search.ts` com a cópia corrigida;
3. executar apenas o gate nos JSON, se a imagem `node:22-alpine` estiver em cache;
4. explicar que código, regras, versões e política continuam rastreáveis.

## 11. Limpeza

```powershell
docker compose --profile tools down --remove-orphans
```

Esse comando remove somente os contêineres e a rede do laboratório. As imagens permanecem em cache para evitar novo download durante a aula.
