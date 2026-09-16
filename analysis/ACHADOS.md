# Análise dos achados — execução de 15 set. 2026

Os dados abaixo foram extraídos dos relatórios versionados em `reports/`. As contagens do ZAP representam tipos de alerta; um mesmo alerta pode ter várias instâncias.

## Resumo executivo

| Ferramenta | Cenário | Resultado | Gate |
|---|---|---:|---|
| Semgrep 1.172.0 | Código vulnerável (`routes/search.ts`) | 1 HIGH | Bloqueado, como esperado |
| Semgrep 1.172.0 | Cópia corrigida com query parametrizada | 0 HIGH/CRITICAL | Aprovado |
| OWASP ZAP 2.17.0 | Juice Shop v20.2.0 local | 11 alertas: 1 HIGH, 4 MEDIUM, 3 LOW e 3 INFO | Bloqueado, como esperado |

## Matriz de classificação

| # | Origem | Achado | Risco | CWE | Classificação |
|---|---|---|---|---|---|
| 1 | Semgrep + ZAP | SQL Injection na busca de produtos | HIGH | CWE-89 | Verdadeiro positivo corroborado |
| 2 | ZAP | Content Security Policy ausente | MEDIUM | CWE-693 | Verdadeiro positivo de configuração |
| 3 | ZAP | CORS com `Access-Control-Allow-Origin: *` | MEDIUM | CWE-264 no relatório | Verdadeiro positivo; impacto contextual |

## 1. SQL Injection na busca de produtos

- **SAST:** a regra comunitária `javascript.sequelize.security.audit.sequelize-injection-express.express-sequelize-injection`, carregada por `--config auto`, identificou que `target/juice-shop/routes/search.ts:23` leva entrada de `req.query.q` até `models.sequelize.query(...)`.
- **DAST:** regra ZAP 40018 em `GET /rest/products/search`, parâmetro `q`, payload registrado como `'(` e resposta `HTTP/1.1 500 Internal Server Error`.
- **Confiança:** o ZAP marcou `High (Low)`, pois uma resposta 500 isolada não prova exploração. A confirmação independente do fluxo source-to-sink pelo Semgrep reduz a incerteza e sustenta a classificação como verdadeiro positivo no alvo de treinamento.
- **Impacto:** manipulação da consulta, leitura indevida e possível alteração de dados, conforme privilégios do banco.
- **Tratamento demonstrado:** substituir a interpolação pelo marcador `:criteria` e fornecer o valor em `replacements` do Sequelize.
- **Validação:** o cenário red contém 1 HIGH; a cópia green contém 0 achados. O DAST continua bloqueando porque executa a imagem vulnerável oficial, e não a cópia corrigida usada apenas na demonstração SAST.

## 2. Content Security Policy ausente

- **DAST:** regra ZAP 10038-1, `Medium (High)`, em cinco instâncias, incluindo `GET /`, `/sitemap.xml` e arquivos expostos em `/ftp`.
- **Evidência:** respostas sem o cabeçalho `Content-Security-Policy`.
- **Impacto:** não cria XSS sozinho, mas remove uma camada de defesa contra execução de conteúdo não autorizado e reduz contenção caso outra injeção exista.
- **Tratamento:** definir uma política restritiva, começar em `Content-Security-Policy-Report-Only`, observar violações e então aplicar `default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `object-src 'none'` e `frame-ancestors` conforme as dependências reais.
- **Classificação:** verdadeiro positivo de configuração. A severidade final deve considerar se a aplicação já possui injeções exploráveis e quais origens externas são necessárias.

## 3. CORS excessivamente permissivo

- **DAST:** regra ZAP 10098, `Medium (Medium)`, em cinco instâncias.
- **Evidência:** `Access-Control-Allow-Origin: *` em respostas como `/`, `/robots.txt`, `/styles.css` e `/sitemap.xml`.
- **Impacto:** permite leitura cross-origin de recursos não autenticados. O risco cresce se endpoints com dados sensíveis ou mecanismos de autenticação compatíveis responderem com a mesma política.
- **Tratamento:** manter uma allowlist explícita de origens necessárias, variar a resposta por `Origin`, evitar reflexão indiscriminada e testar separadamente endpoints públicos e autenticados.
- **Classificação:** o cabeçalho permissivo é um verdadeiro positivo; o impacto é contextual. Nas instâncias observadas, várias rotas são públicas, então o achado não equivale automaticamente a vazamento de dados sensíveis.

## Achados adicionais do ZAP

| Risco | Alerta | Instâncias | Observação |
|---|---|---:|---|
| MEDIUM | Missing Anti-clickjacking Header | 2 | Respostas do Socket.IO sem `X-Frame-Options`/`frame-ancestors` |
| MEDIUM | Session ID in URL Rewrite | 5 | `sid` do Socket.IO aparece na URL; revisar sem assumir equivalência com sessão de usuário |
| LOW | Private IP Disclosure | 1 | `192.168.99.100` em configuração retornada |
| LOW | Timestamp Disclosure - Unix | 5 | Datas embutidas em conteúdo estático |
| LOW | X-Content-Type-Options Header Missing | 4 | Respostas sem `nosniff` |
| INFO | Modern Web Application | 5 | Justifica o uso do AJAX spider |
| INFO | Session Management Response Identified | 1 | Detecção automática de `continueCode` |
| INFO | User Agent Fuzzer | 3 | Diferenças de resposta sob variação do cabeçalho |

## Métricas registradas

| Métrica | Valor observado |
|---|---:|
| Regras comunitárias executadas no Semgrep red | 210 |
| Tempo total interno do Semgrep red | 4,242 s |
| HIGH/CRITICAL no Semgrep red | 1 / 0 |
| Regras comunitárias executadas no Semgrep green | 210 |
| Tempo total interno do Semgrep green | 3,542 s |
| HIGH/CRITICAL no Semgrep green | 0 / 0 |
| Spider tradicional | 18 s; 101 URLs |
| AJAX spider | 34 s; 233 URLs |
| Active scan | 4 min (limite atingido) |
| Tempo dos jobs do ZAP | aproximadamente 4 min 54 s |
| Tipos de alerta do ZAP | 11 |
| HIGH/CRITICAL no ZAP | 1 / 0 |

## Limitações

- O Semgrep red/green usa regras comunitárias gerais com `--config auto`. O alvo foi intencionalmente restrito ao arquivo da busca para uma demonstração determinística; esse recorte não representa cobertura completa do repositório.
- O active scan atingiu o limite de quatro minutos e foi limitado às regras de SQL Injection e XSS refletido.
- O DAST não autenticou usuários nem percorreu todos os estados da aplicação.
- Alertas automáticos não substituem reprodução manual, análise de fluxo e priorização pelo contexto de negócio.
- O Juice Shop é deliberadamente vulnerável; os números não devem ser usados como benchmark de uma aplicação comum.
