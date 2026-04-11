# Radar Scanner: Camada de Descoberta e Download

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o scanner do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e navegar fontes de financiamento, descobrir novos instrumentos, descarregar regulamentos, e monitorizar alteracoes de estado.

**Esta skill NAO cria artigos.** Apenas descobre, descarrega e organiza. A criacao de artigos e feita pela skill `/radar-instrumentos`.

---

## PASSO 0: CONFIGURACAO DE AMBIENTE

**Executar antes de qualquer outra operacao.**

```bash
if [ -d "C:/Users/Utilizador/Desktop/opencapital-website" ]; then
  echo "AMBIENTE: LOCAL"
else
  echo "AMBIENTE: REMOTO"
fi
```

**Se LOCAL:** usar `C:/Users/Utilizador/Desktop/opencapital-website` como base (`$REPO`) em todos os caminhos e comandos git desta execucao.

**Se REMOTO:**
1. Clonar o repositorio:
```bash
git clone https://github.com/JPereira-eng/opencapital-site.git /tmp/opencapital
```
2. Usar `/tmp/opencapital` como `$REPO` em todos os caminhos e comandos git desta execucao.
3. No final, apos o push com sucesso, limpar: `rm -rf /tmp/opencapital`

Todos os caminhos de ficheiros e comandos `git -C` nas instrucoes seguintes referem-se a `$REPO`.

---

## FICHEIROS DE ESTADO

- **`$REPO/sources.json`**: lista de fontes com URLs, metodo de acesso, prioridade, e campos API (v3.0: 2 super-fontes API + 25 fontes cobertas + ~61 independentes)
- **`$REPO/registry.json`**: estado do agente - fila, publicados, ultima verificacao
- **`$REPO/regulamentos/`**: pasta onde os textos extraidos sao guardados

Le `sources.json` e `registry.json` no inicio de cada execucao.

---

## ARQUITECTURA: 3 CAMADAS

Este scanner executa 3 camadas por ordem. Cada execucao pode executar todas ou apenas algumas, conforme o budget de tokens disponivel.

### Camada 1: SCAN - Descobrir novos instrumentos
### Camada 2: DOWNLOAD - Descarregar regulamentos
### Camada 3: MONITOR - Verificar alteracoes de estado

---

## CAMADA 1: SCAN (descoberta de novos instrumentos)

### 1.1 Selecionar fontes a verificar

Verificar no maximo **8 fontes por execucao** (APIs contam como 1 fonte mas cobrem muitos avisos).

**Regra de super-fontes:** Fontes com `is_superset: true` (portugal-2030, eu-funding-tenders) devem ser priorizadas. Quando uma super-fonte e verificada, todas as fontes com `covered_by` correspondente ficam implicitamente cobertas.

**Fontes com `covered_by` definido:** so sao verificadas individualmente se a super-fonte correspondente nao foi verificada nos ultimos 14 dias (fallback).

**Prioridade de selecao:**
1. Super-fontes (`is_superset: true`) nao verificadas ha mais de 3 dias
2. Fontes independentes com `priority: "high"` nao verificadas ha mais de 7 dias
3. Fontes independentes com `priority: "medium"` nao verificadas ha mais de 14 dias
4. Fontes independentes com `priority: "low"` nao verificadas ha mais de 30 dias
5. Fontes com `covered_by` como fallback (so se super-fonte ha mais de 14 dias)
6. Se nenhuma fonte precisa de verificacao: saltar para Camada 2

Consultar `registry.json > source_last_checked` para datas.

### 1.2 Aceder a cada fonte

Consultar o campo `access_method` no `sources.json`:

**Se `access_method: "api"` (super-fontes):**

Usar a estrategia especifica da fonte:

**Portugal 2030 (id: portugal-2030):**
1. Buscar todos os avisos via REST API com paginacao:
   ```
   WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?per_page=100&offset=0
   WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?per_page=100&offset=100
   WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?per_page=100&offset=200
   ```
2. De cada aviso JSON, extrair:
   - `acf.codigo` (ex: "FA0212/2025") - chave de deduplicacao
   - `title.rendered` - nome do aviso
   - `acf.data_inicio` / `acf.data_fim` - datas (formato YYYYMMDD)
   - `acf.df` - dotacao financeira
   - `acf.programa[]` - programas (COMPETE2030, NORTE2030, etc.)
   - `acf.fundo[]` - fundo EU (FEDER, FSE+, etc.)
   - `acf.beneficiario[]` - elegibilidade
   - `acf.natureza` - Concurso/Convite
   - `acf.pdf` - ID do media WordPress (PDF do regulamento)
3. Filtrar apenas avisos com status "Aberto" (verificar `acf.data_fim` > hoje)
4. Atualizar `source_last_checked` para portugal-2030 E para todas as fontes em `covers_programs`

**EU Funding & Tenders (id: eu-funding-tenders):**
1. Usar SEDIA Search API para descobrir topics abertos:
   ```
   POST https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA&text=2026&pageSize=200&pageNumber=1
   ```
2. Filtrar resultados client-side: manter apenas onde `metadata.status[0] === "31094502"` (Open)
3. Para cada topic aberto, buscar detalhes completos:
   ```
   WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{slug-lowercase}.json
   ```
4. De cada topicDetails JSON, extrair:
   - `identifier` (ex: "HORIZON-CL4-2026-DATA-AI-01-02") - chave de deduplicacao
   - `title` - nome do topic
   - `actions[0].status.abbreviation` - "Open"/"Closed"/"Forthcoming"
   - `actions[0].deadlineDates[]` - prazos (Unix timestamp ms)
   - `budgetOverviewJSONItem` - orcamento
   - `frameworkProgramme.abbreviation` - programa (HORIZON, CEF, etc.)
   - `description` - descricao completa (HTML)
5. Limitar a 20 topics detalhados por execucao (para controlar tokens)
6. Atualizar `source_last_checked` para eu-funding-tenders E para todas as fontes em `covers_programs`

**Se `access_method: "webfetch"`:**
- Usar WebFetch no `url_avisos` da fonte
- **Se a fonte tem `pagination`:** percorrer todas as paginas (ex: `?page=1` ate `?page=N` para COMPETE 2030, ou `?paged=N` para FCT)
- Extrair: nome do aviso, codigo, estado, prazo, dotacao, URL regulamento, URL PDF

**Se `access_method: "chrome"`:**
- Usar Chrome MCP tools para navegar ao `url_avisos`
- Sequencia: `navigate` -> aguardar render -> `get_page_text` ou `read_page`
- Se a pagina tem tabs/filtros (ex: "Abertos"): clicar no filtro via `computer` tool
- Se a pagina tem "Ver mais" (ex: Norte 2030): clicar repetidamente ate carregar todos
- Extrair os mesmos campos

**Se `access_method: "websearch"`:**
- Usar WebSearch com query: `site:[url] avisos abertos 2026` ou `[nome_fonte] concursos abertos financiamento 2026`
- Combinar resultados de multiplas pesquisas se necessario

### 1.3 Comparar com registry (deduplicacao)

Para cada instrumento detectado:

1. Gerar `id` slug (kebab-case do nome)
2. **Verificacao por ID:** existe em `registry.json > published` ou `queue` com o mesmo id? Se sim: skip
3. **Verificacao por codigo:** se o instrumento tem codigo (FA####/YYYY ou HORIZON-xxx), verificar se algum item existente tem o mesmo codigo no campo `aviso_codigo`. Se sim: skip
4. **Verificacao por titulo:** se o titulo e >= 80% similar a um item existente (mesma fonte ou fonte coberta pela mesma super-fonte): skip e registar "possivel duplicado: [id-existente]"
5. Se e novo: adicionar a `queue`

### 1.4 Adicionar novos a fila

Para cada instrumento novo, adicionar ao array `queue` do `registry.json`:

```json
{
  "id": "slug-do-instrumento",
  "name": "Nome completo do aviso",
  "source_id": "portugal-2030",
  "aviso_codigo": "FA0212/2025 ou HORIZON-CL4-2026-xxx (se disponivel, null se nao)",
  "detected_date": "2026-04-10",
  "deadline": "2026-09-30",
  "budget": "2.000.000 EUR",
  "regulation_url": "https://...",
  "pdf_url": "https://...pdf",
  "regulation_local": null,
  "priority_score": 0,
  "status": "pending"
}
```

**Calculo do priority_score (maior = mais urgente):**
- Prazo < 30 dias: +100
- Prazo 30-60 dias: +50
- Prazo 60-90 dias: +20
- Dotacao > 10M EUR: +30
- Dotacao > 1M EUR: +10
- Fonte priority "high": +15
- Fonte priority "medium": +5

### 1.5 Atualizar source_last_checked

Para cada fonte verificada, atualizar a data em `registry.json > source_last_checked`.

---

## CAMADA 2: DOWNLOAD (descarregar regulamentos)

### 2.1 Identificar items sem regulamento local

Percorrer `registry.json > queue` e encontrar items onde `regulation_local` e `null` mas `pdf_url` ou `regulation_url` existem.

Processar no maximo **3 downloads por execucao**.

Priorizar por `priority_score` descendente.

### 2.2 Descarregar e extrair texto

Para cada item:

**Se `pdf_url` existe:**

1. Criar pasta `regulamentos/[source_id]/` se nao existir
2. Descarregar o PDF:
   ```bash
   curl -sL "[pdf_url]" -o "regulamentos/[source_id]/[id].pdf"
   ```
3. Extrair texto:
   ```bash
   pdftotext -enc UTF-8 "regulamentos/[source_id]/[id].pdf" "regulamentos/[source_id]/[id].txt"
   ```
4. Verificar que o `.txt` tem conteudo (mais de 100 palavras)
5. Se pdftotext falhar ou texto vazio: tentar alternativa com WebFetch no `regulation_url`

**Se so `regulation_url` existe (sem PDF):**

1. Consultar `access_method` da fonte:
   - Se `"webfetch"`: usar WebFetch no `regulation_url`
   - Se `"chrome"`: usar Chrome MCP para navegar e extrair `get_page_text`
   - Se `"websearch"`: usar WebSearch para encontrar informacao
2. Guardar o texto extraido em `regulamentos/[source_id]/[id].txt`

**Se Chrome MCP tools:**

1. Usar `navigate` para abrir a pagina do regulamento
2. Usar `get_page_text` para extrair o conteudo completo
3. Se a pagina tem PDF embutido: identificar o link do PDF e descarregar com `curl`
4. Guardar em `regulamentos/[source_id]/[id].txt`

### 2.3 Atualizar registry

Apos download bem-sucedido, atualizar o item na `queue`:
```json
"regulation_local": "regulamentos/compete-2030/step-inovacao-produtiva.txt"
```

Se o download falhar, manter `regulation_local: null` e adicionar nota:
```json
"download_error": "PDF 404 - tentativa em 2026-04-10"
```

---

## CAMADA 3: MONITOR (verificar alteracoes de estado)

### 3.1 Identificar instrumentos a monitorizar

Percorrer `registry.json > published` e encontrar items onde:
- `current_state` e `"aberto"` E
- `last_state_check` e anterior a 7 dias

Verificar no maximo **3 instrumentos por execucao**.

Priorizar instrumentos com prazo proximo (se conhecido).

### 3.2 Verificar estado atual

Para cada instrumento:

1. Identificar a fonte (`source`) e consultar `access_method` em `sources.json`
2. Navegar a pagina da fonte (WebFetch, Chrome ou WebSearch)
3. Procurar o instrumento pelo nome ou codigo
4. Verificar:
   - O instrumento ainda esta listado como aberto?
   - O prazo mudou?
   - A dotacao mudou?
   - Ha notas ou alertas de alteracao?
   - Apareceu um novo PDF de regulamento ou adenda? (comparar com `regulation_local` atual)

### 3.3 Registar alteracoes

**Se estado mudou (aberto -> fechado/previsto):**
```json
{
  "current_state": "fechado",
  "last_state_check": "2026-04-10",
  "state_change_detected": "2026-04-10",
  "state_change_note": "candidaturas encerradas"
}
```

**Se prazo mudou:**
```json
{
  "last_state_check": "2026-04-10",
  "deadline_change": { "old": "2026-09-30", "new": "2026-12-31", "detected": "2026-04-10" }
}
```

**Se apareceu novo PDF de regulamento (adenda, retificacao, novo aviso):**

1. Descarregar o novo PDF para `regulamentos/[source_id]/[id]-v2.pdf` (ou `-adenda`, `-retificacao`)
2. Extrair texto: `pdftotext -enc UTF-8 [novo.pdf] [novo.txt]`
3. Atualizar `regulation_local` para o novo ficheiro
4. Registar no item de `published`:
```json
{
  "last_state_check": "2026-04-10",
  "regulation_local": "regulamentos/compete-2030/step-energia-v2.txt",
  "regulation_update": { "previous": "regulamentos/compete-2030/step-energia.txt", "new": "regulamentos/compete-2030/step-energia-v2.txt", "detected": "2026-04-10", "note": "adenda publicada" }
}
```
5. A skill `/radar-instrumentos` no Passo 3B sera responsavel por atualizar o conteudo editorial do artigo se necessario.

**Se nada mudou:**
```json
{
  "last_state_check": "2026-04-10"
}
```

As alteracoes de estado e conteudo NAO sao aplicadas aos artigos HTML nesta skill. A skill `/radar-instrumentos` e que aplica as alteracoes editoriais quando executar o Passo 3B.

---

## CAMADA EXTRA: DISCOVERY (descoberta exploratoria)

Executar apenas quando TODAS as fontes de alta prioridade foram verificadas nos ultimos 7 dias.

### D.1 WebSearch com queries rotativas

Consultar `sources.json > discovery_queries` e selecionar **2 queries** que nao foram usadas recentemente.

Usar WebSearch para cada query. Analisar os resultados:
- Identificar instrumentos que nao estao em nenhuma fonte conhecida
- Identificar novas fontes (universidades, institutos, bancos, fundacoes)

### D.2 Registar descobertas

Se encontrar um novo instrumento:
1. Adicionar a `queue` com `source_id: "discovery"`
2. Incluir o URL da fonte original

Se encontrar uma nova fonte potencial:
1. NAO adicionar automaticamente ao `sources.json`
2. Reportar no resumo final: "Nova fonte potencial detectada: [nome] ([url])"

---

## PASSO FINAL: Deploy

**Usar sempre `git -C "$REPO"` para todos os comandos git (ver Passo 0 para o valor de $REPO).**

```bash
git -C "$REPO" add registry.json regulamentos/
git -C "$REPO" commit -m "scanner: [resumo das acoes]"
git -C "$REPO" push origin main
```

Exemplos de mensagens de commit:
- `scanner: scan compete-2030 + norte-2030, 3 novos na fila`
- `scanner: download 2 regulamentos (step-energia, siac-digital)`
- `scanner: monitor 3 instrumentos, siac-digital fechado`
- `scanner: scan 8 fontes + download 3 + monitor 2`

Se o push falhar:
```bash
git -C "$REPO" pull --rebase origin main
git -C "$REPO" push origin main
```

Se ambiente REMOTO, apos push com sucesso:
```bash
rm -rf /tmp/opencapital
```

---

## REGRAS DE SEGURANCA

1. **Nunca duplicar items na fila.** Verificar sempre `queue` e `published` antes de adicionar.
2. **Nunca exceder 8 scans + 5 downloads + 3 monitors por execucao. APIs contam como 1 scan mas podem retornar centenas de avisos.** Respeitar os limites para caber no budget de tokens.
3. **Nunca modificar artigos HTML.** Esta skill so modifica `registry.json` e ficheiros em `regulamentos/`.
4. **Nunca modificar `sources.json`.** Se encontrar fontes novas, apenas reportar.
5. **Se WebFetch/Chrome falhar:** registar o erro e continuar para o proximo item. Nunca parar a execucao.
6. **Se curl falhar:** tentar WebFetch como alternativa. Se tambem falhar, marcar `download_error` e continuar.
7. **Sempre guardar ficheiros de regulamento em UTF-8.** Usar `-enc UTF-8` no pdftotext.

---

## RESUMO DE UMA EXECUCAO TIPICA

```
1. Ler registry.json + sources.json
2. SCAN: verificar ate 8 fontes (APIs primeiro) -> detectar novos -> deduplicar -> adicionar a fila
3. DOWNLOAD: descarregar ate 5 regulamentos -> guardar em regulamentos/[fonte]/[id].txt
4. MONITOR: verificar ate 3 instrumentos publicados -> registar alteracoes
5. [Opcional] DISCOVERY: 2 WebSearch queries exploratorias
6. Atualizar registry.json
7. git commit + push
8. Reportar: "Scan: [N fontes] ([N via API]). Novos: [N]. Dedup: [N ignorados]. Downloads: [N]. Monitor: [N updates]. Fila total: [N]."
```
