# Radar Scanner — Camada de Descoberta e Download

Es o scanner do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e navegar fontes de financiamento, descobrir novos instrumentos, descarregar regulamentos, e monitorizar alteracoes de estado.

**Esta skill NAO cria artigos.** Apenas descobre, descarrega e organiza. A criacao de artigos e feita pela skill `/radar-instrumentos`.

---

## FICHEIROS DE ESTADO

- **`sources.json`** — lista de 88 fontes com URLs, metodo de acesso e prioridade
- **`registry.json`** — estado do agente: fila, publicados, ultima verificacao
- **`regulamentos/`** — pasta onde os textos extraidos sao guardados

Le `sources.json` e `registry.json` no inicio de cada execucao.

---

## ARQUITECTURA — 3 CAMADAS

Este scanner executa 3 camadas por ordem. Cada execucao pode executar todas ou apenas algumas, conforme o budget de tokens disponivel.

### Camada 1: SCAN — Descobrir novos instrumentos
### Camada 2: DOWNLOAD — Descarregar regulamentos
### Camada 3: MONITOR — Verificar alteracoes de estado

---

## CAMADA 1 — SCAN (descoberta de novos instrumentos)

### 1.1 Selecionar fontes a verificar

Verificar no maximo **5 fontes por execucao**.

**Prioridade de selecao:**
1. Fontes com `priority: "high"` nao verificadas ha mais de 7 dias
2. Fontes com `priority: "medium"` nao verificadas ha mais de 14 dias
3. Fontes com `priority: "low"` nao verificadas ha mais de 30 dias
4. Se nenhuma fonte precisa de verificacao: saltar para Camada 2

Consultar `registry.json > source_last_checked` para datas.

### 1.2 Aceder a cada fonte

Consultar o campo `access_method` no `sources.json`:

**Se `access_method: "webfetch"`:**
- Usar WebFetch no `url_avisos` da fonte
- Extrair: nome do aviso, codigo, estado, prazo, dotacao, URL regulamento, URL PDF

**Se `access_method: "chrome"`:**
- Usar Chrome MCP tools para navegar ao `url_avisos`
- Sequencia: `navigate` → aguardar render → `get_page_text` ou `read_page`
- Se a pagina tem tabs/filtros (ex: "Abertos"): clicar no filtro via `computer` tool
- Extrair os mesmos campos

**Se `access_method: "websearch"`:**
- Usar WebSearch com query: `site:[url] avisos abertos 2026` ou `[nome_fonte] concursos abertos financiamento 2026`
- Combinar resultados de multiplas pesquisas se necessario

### 1.3 Comparar com registry

Para cada instrumento detectado na pagina:

1. Gerar `id` slug (kebab-case do nome)
2. Verificar se ja existe em `registry.json > published` ou `queue`
3. Se ja existe: anotar para Camada 3 (monitor)
4. Se e novo: adicionar a `queue`

### 1.4 Adicionar novos a fila

Para cada instrumento novo, adicionar ao array `queue` do `registry.json`:

```json
{
  "id": "slug-do-instrumento",
  "name": "Nome completo do aviso",
  "source_id": "compete-2030",
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

## CAMADA 2 — DOWNLOAD (descarregar regulamentos)

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

## CAMADA 3 — MONITOR (verificar alteracoes de estado)

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
   - Ha notas ou alteracoes?

### 3.3 Registar alteracoes

**Se estado mudou (aberto → fechado/previsto):**
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

**Se nada mudou:**
```json
{
  "last_state_check": "2026-04-10"
}
```

As alteracoes de estado NAO sao aplicadas aos artigos HTML nesta skill. A skill `/radar-instrumentos` e que aplica as alteracoes editoriais quando executar o Passo 3B.

---

## CAMADA EXTRA — DISCOVERY (descoberta exploratoria)

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

## PASSO FINAL — Deploy

**Usar sempre `git -C "C:/Users/Utilizador/Desktop/opencapital-website"` para todos os comandos git.**

```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" add registry.json regulamentos/
git -C "C:/Users/Utilizador/Desktop/opencapital-website" commit -m "scanner: [resumo das acoes]"
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

Exemplos de mensagens de commit:
- `scanner: scan compete-2030 + norte-2030, 3 novos na fila`
- `scanner: download 2 regulamentos (step-energia, siac-digital)`
- `scanner: monitor 3 instrumentos, siac-digital fechado`
- `scanner: scan 5 fontes + download 2 + monitor 1`

Se o push falhar:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" pull --rebase origin main
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca duplicar items na fila.** Verificar sempre `queue` e `published` antes de adicionar.
2. **Nunca exceder 5 scans + 3 downloads + 3 monitors por execucao.** Respeitar os limites para caber no budget de tokens.
3. **Nunca modificar artigos HTML.** Esta skill so modifica `registry.json` e ficheiros em `regulamentos/`.
4. **Nunca modificar `sources.json`.** Se encontrar fontes novas, apenas reportar.
5. **Se WebFetch/Chrome falhar:** registar o erro e continuar para o proximo item. Nunca parar a execucao.
6. **Se curl falhar:** tentar WebFetch como alternativa. Se tambem falhar, marcar `download_error` e continuar.
7. **Sempre guardar ficheiros de regulamento em UTF-8.** Usar `-enc UTF-8` no pdftotext.

---

## RESUMO DE UMA EXECUCAO TIPICA

```
1. Ler registry.json + sources.json
2. SCAN: verificar ate 5 fontes → detectar novos → adicionar a fila
3. DOWNLOAD: descarregar ate 3 regulamentos → guardar em regulamentos/[fonte]/[id].txt
4. MONITOR: verificar ate 3 instrumentos publicados → registar alteracoes
5. [Opcional] DISCOVERY: 2 WebSearch queries exploratorias
6. Atualizar registry.json
7. git commit + push
8. Reportar: "Scan: [N fontes]. Novos: [N]. Downloads: [N]. Monitor: [N updates]. Fila total: [N]."
```
