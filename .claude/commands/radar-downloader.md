# Radar Downloader v4.1: Descarregar Regulamentos

REGRA CRÍTICA: Nunca usar travessão (—) em nenhum texto gerado. Usar vírgula, ponto, hífen (-) ou reescrever a frase.

Es o downloader do sistema radar da Open Capital Advisory & Consultancy.
A tua missão e descarregar regulamentos e fichas técnicas dos instrumentos nas filas.

**Esta skill so descarrega.** Não descobre instrumentos, não monitoriza estados, não cria artigos.

---

## PASSO 0: CONFIGURACAO DE AMBIENTE

```bash
if [ -d "C:/Users/Utilizador/Desktop/opencapital-website" ]; then
  echo "AMBIENTE: LOCAL"
else
  echo "AMBIENTE: REMOTO"
fi
```

**Se LOCAL:** usar `C:/Users/Utilizador/Desktop/opencapital-website` como base (`$REPO`).
**Se REMOTO:** clonar e usar `/tmp/opencapital`. Limpar após push.

---

## FICHEIROS DE ESTADO (v4.1)

| Ficheiro | Quando ler/escrever |
|---|---|
| `registry/queue.json` | Sempre (regime "aviso") - so contem items ready/pending/abandoned |
| `registry/queue-catálogo.json` | Sempre (regime "catálogo") |
| `registry/queue-plano-anual.json` | Escrever quando PAA detetado (watchlist) |
| `sources-scan.json` | Para access_method e regime |

**MUDANCA v4.1 (2026-04-17):** Items detetados como Plano Anual (PAA) já não ficam em queue.json com status "plano_anual". São MOVIDOS para `queue-plano-anual.json` (watchlist dedicada). Isto liberta espaco na queue para items realmente processaveis. O monitor le queue-plano-anual.json e devolve items a queue.json quando abrem.

---

## PASSO 1: Identificar items sem regulamento

Percorrer **ambas as filas**:
- `registry/queue.json > queue` (items de regime "aviso")
- `registry/queue-catálogo.json > queue` (items de regime "catálogo")

**NAO ler `queue-plano-anual.json`.** Essa e a watchlist do monitor, não do downloader.

Para cada item, tracking de qual fila veio (campo interno `_queue_origin: "aviso" | "catálogo"`). Encontrar items onde:
- `regulation_local` e `null`
- `status` e `"pending"` ou não definido (items com status "ready", "abandoned" são ignorados)
- `regulation_url` existe (catálogo pode não ter `pdf_url`)
- `fail_count` < 3 (items com 3+ falhas exigem fallback especial, ver Passo 1.6)

Processar no maximo **10 downloads por execução** (soma das duas filas).
Priorizar por `priority_score` descendente, tratando ambas as filas como pool único.

**Caso especial - ficheiros já existentes no disco:** Se `regulation_local` aponta para um ficheiro que existe mas `status` ainda não e `"ready"`, ir para Passo 2.5 para validar conteudo antes de marcar como ready.

---

## SEPARACAO CRÍTICA POR REGIME (LER ANTES DE PROSSEGUIR)

**Esta skill processa dois fluxos paralelos com regras DIFERENTES. Nunca misturar.**

### Fluxo A - Regime "aviso" (items de queue.json)
- Tem deadline formal, regulamento oficial (PDF), código de aviso
- **Testes PAA APLICAM-SE.** Objetivo: evitar descarregar "Resumos do Plano Anual" em vez de regulamentos reais.
- **Teste de tamanho minimo APLICA-SE** (800 palavras + "despesas elegíveis" ou "criterios de seleção")
- Fontes típicas: PT2030 (portugal-2030, compete-2030, norte-2030, etc), EU (eu-funding-tenders, hadea, eismea), Interreg, ANI, IAPMEI, AICEP, FCT, IEFP, PRR

### Fluxo B - Regime "catálogo" (items de queue-catálogo.json)
- Pode não ter deadline, regulamento, nem código formal. Bancos/VC/premios vendem produtos/fundos continuamente.
- **Testes PAA NAO SE APLICAM.** A deteccao PAA esta desenhada para linguagem específica do PT2030. Um produto bancario ou fundo VC nunca dispara esses marcadores, mas se por acaso um texto tivesse uma coincidência linguistica, não queremos bloquear.
- **Teste de tamanho minimo NAO se aplica** com o threshold de 800 palavras. Usar threshold de 200 palavras. Paginas de produtos bancarios e fichas de fundos VC tem tipicamente 300-800 palavras.
- **Aceitar conteudo de pagina web** (HTML) como regulamento válido. Não exigir PDF.
- Fontes típicas: banco-fomento, cgd-empresas, bpi-empresas, millennium-empresas, novobanco-empresas, santander-empresas, indico-capital, armilar-ventures, faber-ventures, shilling-vc, bynd-vc, portugal-ventures, edp-innovation, premio-bpi-lacaixa, premio-gulbenkian, bgi-accelerator, startup-lisboa, beta-i, f6s, eu-startups, startup-portugal, turismo-portugal

**Determinacao do regime para um item:**
- Se `_queue_origin == "catálogo"`: regime = "catálogo"
- Se `_queue_origin == "aviso"`: regime = "aviso"
- Nunca derivar por outras vias. A fila de origem e autoritativa.

---

## PASSO 1.5: Verificar se e Plano Anual (APENAS Fluxo A - regime "aviso", APENAS PT2030)

**Este passo NAO se aplica a items de regime "catálogo". Saltar diretamente para Passo 2 se `_queue_origin == "catálogo"`.**

Para items de regime "aviso" com `source_id` que contenha "2030" ou "pessoas" E que tenham `regulation_url`:

Fazer WebFetch ao `regulation_url` ANTES de tentar descarregar qualquer PDF.

Verificar se a pagina contem QUALQUER um destes textos (case-insensitive):
- "previsao aproximada" / "previsão aproximada"
- "ficha que aqui pode consultar e apenas uma previsao"
- "aviso que ira ser lancado" / "aviso que irá ser lançado"
- "plano anual de avisos"

**Se qualquer um destes textos for encontrado:** MOVER item para `queue-plano-anual.json` (ver PASSO 3.5). Não descarregar. Não contar como falha nem como sucesso.

**Se nenhum destes textos for encontrado:** continuar para Passo 2.

---

## PASSO 1.6: Fallback via WebSearch para items com 3+ falhas

Items com `fail_count >= 3` já falharam cascata normal. Antes de os marcar como `abandoned`, tentar **recuperacao de slug/URL via WebSearch**.

Muitos 404s são causados por mudancas no slug da URL (ex: "adaptação-as-alteracoes-climaticas-2-aviso" -> "adaptação-as-alteracoes-climaticas-2o-aviso"). Este passo recupera esses casos.

**Lógica:**

1. Query: `"[aviso_codigo]" "[nome do item]" site:[dominio da fonte]`
2. Se encontrar URL válido diferente do `regulation_url` atual:
   - Atualizar `regulation_url` no item
   - Resetar `fail_count` para 0
   - Tentar novamente a cascata normal (Passo 2)
3. Se não encontrar nada de novo:
   - Marcar `status: "abandoned"`, `download_error: "URL inacessivel após 3+ tentativas e WebSearch fallback"`
   - **Manter o item no queue.json** (não apagar). O monitor podera re-verificar trimestralmente.

**Items "abandoned" são ignorados pelo downloader em runs futuras** (filtro no Passo 1). Isto evita loops infinitos em items mortos.

---

## PASSO 2: Descarregar e extrair texto

### Fluxo A (regime "aviso") - cascata completa

Para cada item de regime "aviso", seguir esta cascata (parar na primeira que funcionar):

#### 2a. Se `pdf_url` existe (URL completo):

```bash
mkdir -p "$REPO/regulamentos/[source_id]/"
curl -sL "[pdf_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
```

Verificar que o .txt tem mais de 100 palavras. Se falhar, continuar para 2b.

#### 2b. Se `regulation_url` existe:

Consultar `access_method` da fonte em `sources-scan.json`:
- `"webfetch"`: usar WebFetch no regulation_url
- `"chrome"`: usar Chrome MCP (navigate + get_page_text)
- `"websearch"`: usar WebSearch

Prompt para WebFetch: "Extrai toda a informação sobre este aviso/instrumento de financiamento: nome, código, dotacao, taxa de cofinanciamento, elegibilidade, despesas elegíveis, prazos, criterios de seleção, programa, fundo."

Guardar resultado em `regulamentos/[source_id]/[id].txt`.

**Nota para items PT2030:** Portais regionais são server-rendered (WebFetch funciona). Central (portugal2030.pt) e JS-rendered (WebFetch so retorna CSS/JS).

**Se WebFetch retornar < 300 palavras de conteudo real:** tratar como falha e continuar para 2b-pdf.

#### 2b-pdf: PDF via WordPress media API (para portais PT2030)

Se o item tem `wordpress_id` E regulamento ainda não obtido:

1. `GET https://[portal-base]/wp-json/wp/v2/aviso-2024/[wordpress_id]` e extrair `acf.pdf`
2. Se `acf.pdf` for null/0: sem PDF. Continuar para 2c.
3. Se ID numérico válido: `GET https://[portal-base]/wp-json/wp/v2/media/[acf.pdf]`, extrair `source_url`
4. Descarregar e extrair:
   ```bash
   curl -sL "[source_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
   pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
   ```

5. **VERIFICACAO DO CONTEUDO DO PDF (so Fluxo A):**

   **TESTE A - Texto de plano anual (BLOQUEANTE):**
   Se contem "Plano Anual de Avisos", "Resumo de Aviso do Plano", "PAA2026", "PAA202", "Aviso a publicar em:"
   → Apagar .txt e .pdf.
   → **ANTES de mover para watchlist:** se item é PT2030 família, tentar PASSO 2b-portal-central (NOVO v4.12). Se obtiver regulamento real → SUCESSO, parar aqui (set `data_status: "verified"`).
   → Caso contrário: MOVER item para `queue-plano-anual.json` (ver PASSO 3.5). PARAR item. **Manter `data_status: "forecast"`.**

   **Se TESTE A passa (PDF NÃO é PAA):** transição de estado importante (v4.13):
   → **Atualizar `data_status: "verified"`** no item (anteriormente "forecast")
   → Este é o momento canónico de validação. A partir daqui o item conta como aviso REAL.

   **TESTE B - Conteudo insuficiente (BLOQUEANTE):**
   Se < 800 palavras E não contem "despesas elegíveis" E não contem "criterios de seleção"
   → Apagar .txt e .pdf. Incrementar `fail_count`. Marcar `status: "pending"`, `download_error: "Resumo sem regulamento completo"`. PARAR item.

   **Se passou ambos:** continuar para Passo 2.5.

#### 2b-portal-central: Procurar regulamento real no portal central PT2030 (v4.12, 2026-05-12)

**Aplica-se APENAS:** item é família PT2030 E TESTE A do 2b-pdf detectou PAA E `human_code` ainda não está populado.

**Contexto:** Os portais regionais PT2030 (acores, alentejo, algarve, centro, lisboa, madeira, pat) expõem na API só o PDF do Resumo PAA. Os regulamentos REAIS são publicados em `portugal2030.pt/wp-content/uploads/sites/3/YYYY/MM/[CODIGO_HUMANO].pdf` (sub-site central) e NÃO são linkados na API regional. Esta etapa procura-os via WebSearch.

**Excepção:** sustentavel-2030 expõe `aviso` field directamente. Para esse, 2b-pdf já obtém regulamento real (skip 2b-portal-central).

**Algoritmo:**

```python
if item.source_id in FAMILIA_PT2030 and item.programa_code and item.human_code is None:
    programa = item.programa_code  # 'ACORES2030', 'CENTRO2030', etc.
    titulo = item.name[:60]

    # 1. WebSearch refinada (PT2030 family)
    queries = [
        f'site:portugal2030.pt "{titulo[:40]}" "{programa}" filetype:pdf',
        f'site:portugal2030.pt {programa}-{year_now} {keywords_titulo} filetype:pdf',
    ]

    for query in queries:
        results = WebSearch(query)
        for url in results[:5]:
            if not url.endswith('.pdf'):
                continue
            # 2. Descarregar candidato
            curl -sL "[url]" -o /tmp/candidate.pdf
            pdftotext /tmp/candidate.pdf /tmp/candidate.txt
            text = read('/tmp/candidate.txt')

            # 3. Validar (rejeitar PAA, exigir conteúdo)
            if 'plano anual' in text.lower() or 'resumo de aviso' in text.lower():
                continue  # ainda PAA, próximo candidato
            if len(text.split()) < 1500:
                continue  # demasiado curto

            # 4. Extrair human_code do texto
            import re
            HUMAN_RE = re.compile(
                r'(?i)C[oó]digo\s+do\s+aviso\s*:?\s*([A-Z][A-ZÇÊÁÍÓ]+2030-\d{4}-\d+|PACS-\d{4}-\d+)',
            )
            match = HUMAN_RE.search(text)
            if not match:
                # Fallback: tentar pelo nome do ficheiro (URL)
                fname_match = re.search(r'/(AVISO-)?([A-Z]+2030-\d{4}-\d+)', url)
                if fname_match: match = fname_match.group(2)

            if match:
                human_code = normalize_human(match.group(1) if hasattr(match,'group') else match)
                # Normalizar: ACORES2030-2026-12, sem espaços, uppercase, hífen único

                # 5. Validar similaridade de título
                if title_similarity(titulo, extract_title_from_pdf(text)) < 0.6:
                    continue  # PDF não corresponde ao item

                # 6. SUCESSO - registar
                item.human_code = human_code
                item.regulation_url = url
                item.regulation_local = save_to_regulamentos(pdf, item.source_id, item.id)
                item.status = 'ready'
                item.fail_count = 0
                item.fallback_tried.append('2b-portal-central')

                # Atualizar lookup
                lookup.by_human_code[human_code] = item.id

                return SUCCESS

    # Nenhum candidato válido encontrado
    return FAIL  # cai para fluxo normal (mover para watchlist se TESTE A falhou)
```

**Função helper `normalize_human`:**
```python
def normalize_human(code: str) -> str:
    """ACORES2030-2026-12, AÇORES2030-2026-12, acores-2030-2026-12 → ACORES2030-2026-12"""
    import unicodedata
    code = unicodedata.normalize('NFKD', code).encode('ascii','ignore').decode()
    code = code.upper().replace(' ', '').strip()
    # Garantir formato PROGRAMA-YYYY-NN (sem hífen entre PROGRAMA e 2030)
    code = re.sub(r'([A-Z]+)-?(2030)-?', r'\1\2-', code)
    return code
```

**Salvaguardas:**
- Máximo 5 candidatos por query (caps WebSearch).
- HEAD request antes de descarregar PDF pesado.
- Title similarity >= 60% (mais permissivo do que cross-portal porque já passou WebSearch filtragem).
- Se múltiplos candidatos válidos, escolher o de maior tamanho (regulamento real > resumo).

**Reportar no relatório final:**
```
2b-portal-central tentado: N items PT2030
  Sucessos: M (human_code descoberto, regulamento real obtido)
  Falhas: N-M (mantidos para watchlist via TESTE A)
```

#### 2b-acf-all: Re-fetch API e inspecionar TODOS os campos ACF (v4.11, 2026-05-11)

Se 2b-pdf não obteve PDF E item é PT2030 (source_id em família PT2030):

1. `GET https://[portal-base]/wp-json/wp/v2/aviso-2024/[wordpress_id]` (ou pelo slug se id desconhecido)
2. Inspecionar **TODOS** os campos da resposta, não só `acf.pdf`:
   - `acf.pdf` (já tentado em 2b-pdf)
   - `acf.regulamento`, `acf.ficha_tecnica`, `acf.anexos[]`, `acf.documentos[]`
   - `acf.aviso_documento`, `acf.documento_oficial`, `acf.programa_documento`
   - Qualquer campo cujo valor seja:
     - URL terminado em `.pdf`
     - ID numérico (resolver via `/wp/v2/media/[id]` → `source_url`)
     - Array de URLs/IDs (iterar)

3. Para cada URL candidato encontrado:
   ```bash
   curl -sL -I "[url]"  # HEAD primeiro para verificar Content-Type
   ```
   Se Content-Type contém `application/pdf` E Content-Length > 10000:
   ```bash
   curl -sL "[url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
   pdftotext -enc UTF-8 ... [id].txt
   ```
   Aplicar TESTE A e TESTE B (Passo 2b-pdf).

4. Se vários candidatos retornam PDF válido, usar o de **maior tamanho** (heurística: regulamentos completos > resumos).

5. Reportar no relatorio final qual campo deu sucesso (`fallback_field: "acf.regulamento"` no item da queue).

Se nenhum campo ACF deu PDF válido: continuar para 2b-heur.

#### 2b-heur: Heurística por código de aviso e padrão de URL (v4.11, 2026-05-11)

Se 2b-acf-all falhou E item é PT2030:

Os portais PT2030 alojam PDFs em padrões consistentes. Construir candidatos e tentar HEAD requests (cheap, sem descarregar pesado).

1. Extrair componentes:
   - `codigo` (e.g., FA0212/2025 → variantes: `FA0212-2025`, `FA0212_2025`, `aviso-FA0212`)
   - `data_inicio` ou `detected_date` (YYYY-MM-DD → ano/mês para path)
   - `slug` (do post WordPress, e.g., `sistema-incentivos-base-territorial-ovt`)

2. Construir candidatos baseados no `source_id`:

   **Para portugal-2030.pt / compete-2030.pt:**
   ```
   https://[portal]/wp-content/uploads/{YYYY}/{MM}/[variant].pdf
   ```
   onde [variant] cicla por:
     - codigo com `-` (FA0212-2025)
     - codigo com `_` (FA0212_2025)
     - `aviso-` + codigo
     - slug curto (primeiras 50 chars)
     - `aviso_` + slug

   **Para portais regionais (norte-2030, centro-2030, etc.):**
   ```
   https://[portal-base]/wp-content/uploads/{YYYY}/{MM}/[variant].pdf
   https://[portal-base]/aviso/[slug]/regulamento.pdf
   https://[portal-base]/aviso/[slug]/[codigo].pdf
   ```

3. Para cada candidato (max 8 tentativas):
   ```bash
   curl -sL -I "[candidato]" -o /dev/null -w "%{http_code} %{content_type}"
   ```
   Se HTTP 200 E Content-Type contém `application/pdf`:
   ```bash
   curl -sL "[candidato]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
   ```
   Aplicar TESTE A e TESTE B.

4. **Limite:** parar após primeiro PDF válido ou após esgotar candidatos.

5. Reportar no item da queue: `fallback_url_pattern: "wp-content/uploads/YYYY/MM/<codigo>-<year>.pdf"`.

Se nenhum candidato retornou PDF válido: continuar para 2b-horizon (se EU) ou 2c (WebSearch genérico).

**Salvaguarda anti-DDoS:** cap de 8 candidatos por item. Se múltiplos items do mesmo portal acumulam falhas (>50 candidatos numa run), pausa 30s entre tentativas para o portal afetado.

#### 2b-horizon: API JSON para items Horizonte Europa / SEDIA

Se `source_id == "eu-funding-tenders"` E regulamento não obtido:

```
WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/[aviso_codigo_lowercase].json
```

Extrair campo `description` COMPLETO (500-2000 palavras HTML - strip tags mas guardar todo o texto), mais title, budgetOverviewInEur, deadlineDate, conditions, keywords, actions, callIdentifier.

Guardar em `regulamentos/eu-funding-tenders/[id].txt`. Se 404: continuar para 2b-eu-pdf.

#### 2b-eu-pdf: PDF de Call Document para fontes EU

Se `source_id` e agencia europeia E conteudo < 400 palavras:

```
WebSearch: "[aviso_codigo] call document filetype:pdf site:ec.europa.eu"
WebSearch: "[aviso_codigo] guidelines applicants hadea.ec.europa.eu"
```

Se encontrar PDF: `curl -sL` + `pdftotext`. Conteudo esperado: 1000-5000 palavras.

#### 2c. WebSearch + WebFetch do melhor resultado:

Queries:
1. `"[aviso_codigo]" site:portugal2030.pt`
2. `"[aviso_codigo] [nome] candidaturas"`

Se encontrar URL promissor: WebFetch antes de guardar. Posts de noticia tem 500-1500 palavras.

Guardar o melhor conteudo em `regulamentos/[source_id]/[id].txt`.

---

### Fluxo B (regime "catálogo") - cascata simplificada

Para cada item de regime "catálogo", seguir esta cascata:

#### 2a-cat. Se `pdf_url` existe (raro em catálogo, mas possível):

```bash
mkdir -p "$REPO/regulamentos/[source_id]/"
curl -sL "[pdf_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
```

#### 2b-cat. Se `regulation_url` existe (caso normal para catálogo):

Usar `access_method` da fonte:
- `"webfetch"`: WebFetch no regulation_url
- `"chrome"`: Chrome MCP (navigate + get_page_text)
- `"websearch"`: WebSearch

Prompt para WebFetch (adaptado a catálogo): "Extrai toda a informação sobre este produto de financiamento, fundo de investimento, premio ou programa: nome oficial, descrição, montantes/ticket, prazos de candidatura (se existirem), elegibilidade/perfil de empresas-alvo, setores, fases/estagios, contactos. Se não existir deadline ou dotacao, registar que e candidatura continua ou produto permanente."

Guardar em `regulamentos/[source_id]/[id].txt`.

#### 2c-cat. WebSearch como fallback:

Se WebFetch falhar ou retornar muito pouco:
```
WebSearch: "[nome do instrumento] [source_id nome do banco/VC/premio]"
```

Guardar melhor resultado em `regulamentos/[source_id]/[id].txt`.

---

## PASSO 2.5: VALIDACAO DE CONTEUDO (diferente por regime)

### 2.5.A - Fluxo A (regime "aviso") - VALIDACAO RIGIDA PAA

**Obrigatória para TODOS os items de regime "aviso", independentemente do metodo de download. Nunca saltar.**

Ler `.txt` obtido.

**TESTE A - Identificar plano anual (BLOQUEANTE):**
Se contem (case-insensitive) QUALQUER um destes:
- "Plano Anual de Avisos"
- "Resumo de Aviso do Plano"
- "PAA2026" ou "PAA202"
- "Aviso a publicar em:"
- "previsao aproximada" / "previsão aproximada"
- "aviso que ira ser lancado" / "aviso que irá ser lançado"

→ **Apagar .txt e .pdf. MOVER item para `queue-plano-anual.json` (ver PASSO 3.5). NAO ir para Passo 3. PARAR item.**

Este teste captura casos em que o downloader descarregou um "Resumo de Aviso do Plano Anual" em vez de aviso publicado. São documentos de previsao, não regulamentos válidos.

**Se passou Teste A:** continuar para Passo 3.

### 2.5.B - Fluxo B (regime "catálogo") - VALIDACAO LAX

**Os testes PAA do 2.5.A NAO SE APLICAM aqui. A linguagem PAA e específica do PT2030 e não aparece em produtos bancarios, fundos VC ou premios. Nunca correr Teste A em catálogo.**

Ler `.txt` obtido.

**TESTE C - Conteudo minimo para catálogo (NAO BLOQUEANTE, apenas warn):**
- Se tem >= 200 palavras: válido, marcar `status: "ready"`, prosseguir para Passo 3.
- Se tem < 200 palavras mas > 50: marcar `status: "ready"` com `download_note: "Conteudo breve - o writer deve complementar com WebSearch"`. Continuar para Passo 3.
- Se tem < 50 palavras ou ficheiro vazio: marcar `status: "pending"`, `download_error: "Conteudo insuficiente"`, tentar de novo em execução futura.

**TESTE D - Link rot (NAO BLOQUEANTE):**
Se o curl ou WebFetch devolveu 404/403/500: marcar `status: "pending"`, `download_error: "HTTP [código] - URL pode ter mudado"`. O monitor marcara como needs_review.

**Não e falha do downloader se um produto bancario tem pouco texto.** Muitos produtos bancarios são descritos em 300-500 palavras. Isto e aceitavel em catálogo.

---

## PASSO 3: Atualizar queue (fila correcta)

Após validacao bem-sucedida, atualizar o item:

```json
{
  "regulation_local": "regulamentos/[source_id]/[id].txt",
  "status": "ready",
  "fail_count": 0
}
```

**IMPORTANTE:** se o item veio de `queue.json` (regime aviso), actualizar em `queue.json`. Se veio de `queue-catálogo.json`, actualizar em `queue-catálogo.json`. Nunca mover items entre filas (excepcao: PAAs vao para queue-plano-anual.json via Passo 3.5).

Se download falhar:
```json
{
  "download_error": "PDF 404 - tentativa em 2026-04-16",
  "status": "pending",
  "fail_count": [incrementar],
  "last_fail_date": "2026-04-16",
  "fallback_tried": ["2a", "2b", "2b-pdf", "2b-acf-all", "2b-heur"]
}
```

**Campo `fallback_tried` (v4.11):** lista das estratégias já tentadas para este item (códigos dos passos: `2a`, `2b`, `2b-pdf`, `2b-acf-all`, `2b-heur`, `2b-horizon`, `2b-eu-pdf`, `2c`). Permite no Passo 1.6 saltar estratégias já esgotadas, e auditar no relatorio final qual estratégia teve sucesso por item.

**Se `fail_count` chegar a 3 após este incremento:** o item fica elegível para o Passo 1.6 (WebSearch fallback) na próxima run.

---

## PASSO 3.5: Mover PAA para watchlist (queue-plano-anual.json)

Quando um item e identificado como Plano Anual (Passo 1.5, Teste A em 2b-pdf ou 2.5.A):

1. **Remover** o item de `queue.json > queue` (pelo seu `id`)
2. **Adicionar** o item a `queue-plano-anual.json > queue` com campos adicionais:
   ```json
   {
     ...(campos originais),
     "status": "plano_anual",
     "download_error": "Plano Anual - não e aviso publicado, apenas previsao",
     "plano_anual_detected_date": "2026-04-17",
     "plano_anual_checks": 1
   }
   ```
3. **Não adicionar** ao lookup.json secção plano_anual (redundante). O campo `by_id` já garante dedup.

**Se o item já existe em queue-plano-anual.json** (pode acontecer se o downloader reprocessa): incrementar `plano_anual_checks`, atualizar `plano_anual_last_check` com a data actual. Não duplicar.

O monitor lera este ficheiro para re-verificar se os PAAs abriram.

---

## PASSO 4: Deploy

```bash
git -C "$REPO" add registry/queue.json registry/queue-catálogo.json registry/queue-plano-anual.json regulamentos/
git -C "$REPO" commit -m "downloader: [N] aviso + [N] catálogo ready, [N] PAAs watchlisted, [N] abandoned"
git -C "$REPO" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca misturar regimes.** Testes PAA SO para regime "aviso". Never apply to catálogo.
2. **Nunca exceder 10 downloads por execução** (soma das duas filas).
3. **Nunca modificar artigos HTML ou shards.**
4. **Sempre guardar em UTF-8.**
5. **Se curl falhar:** tentar WebFetch como alternativa.
6. **Se tudo falhar:** marcar download_error e continuar. Nunca parar a execução.
7. **Em catálogo, aceitar conteudo breve.** 200+ palavras e suficiente. Um produto bancario pode ter 300 palavras - não e erro.

---

## RESUMO

```
1. Ler queue.json (aviso) + queue-catálogo.json (catálogo)
2. Encontrar items pending sem regulation_local (max 10 total, ignorar abandoned, fail_count>=3 vai ao Passo 1.6)
3. Para cada, determinar regime pela fila de origem:

   Fluxo A (aviso): cascata PDF -> WebFetch -> WebSearch
     PASSO 1.5 (PAA check): se PAA -> MOVER para queue-plano-anual.json (Passo 3.5), PARAR
     PASSO 2.5.A (BLOQUEANTE): Teste A (PAA) - se falhar: MOVER para queue-plano-anual.json, PARAR
     Teste B (tamanho) no 2b-pdf: incrementar fail_count, status pending
     Se passou: status ready, fail_count=0

   Fluxo B (catálogo): cascata simplificada WebFetch/PDF -> WebSearch
     PASSO 2.5.B (LAX): Teste C (minimo 50 palavras), Teste D (link rot)
     NUNCA aplicar testes PAA aqui
     Se conteudo >= 200: ready. Se 50-200: ready com note. Se < 50: pending + fail_count++.

   Items com fail_count >= 3: PASSO 1.6 (WebSearch fallback)
     Se encontrar novo URL: update + fail_count=0 + retry
     Se não encontrar: status "abandoned"

4. Atualizar queue CORRECTA (aviso, catálogo ou plano-anual)
5. git commit + push
6. Reportar: "Downloader: [N] aviso ready, [N] catálogo ready, [N] PAAs watchlisted, [N] abandoned, [N] falhas."
```
