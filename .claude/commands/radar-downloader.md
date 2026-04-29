# Radar Downloader v4.1: Descarregar Regulamentos

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o downloader do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e descarregar regulamentos e fichas tecnicas dos instrumentos nas filas.

**Esta skill so descarrega.** Nao descobre instrumentos, nao monitoriza estados, nao cria artigos.

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
**Se REMOTO:** clonar e usar `/tmp/opencapital`. Limpar apos push.

---

## FICHEIROS DE ESTADO (v4.1)

| Ficheiro | Quando ler/escrever |
|---|---|
| `registry/queue.json` | Sempre (regime "aviso") - so contem items ready/pending/abandoned |
| `registry/queue-catalogo.json` | Sempre (regime "catalogo") |
| `registry/queue-plano-anual.json` | Escrever quando PAA detetado (watchlist) |
| `sources-scan.json` | Para access_method e regime |

**MUDANCA v4.1 (2026-04-17):** Items detetados como Plano Anual (PAA) ja nao ficam em queue.json com status "plano_anual". Sao MOVIDOS para `queue-plano-anual.json` (watchlist dedicada). Isto liberta espaco na queue para items realmente processaveis. O monitor le queue-plano-anual.json e devolve items a queue.json quando abrem.

---

## PASSO 1: Identificar items sem regulamento

Percorrer **ambas as filas**:
- `registry/queue.json > queue` (items de regime "aviso")
- `registry/queue-catalogo.json > queue` (items de regime "catalogo")

**NAO ler `queue-plano-anual.json`.** Essa e a watchlist do monitor, nao do downloader.

Para cada item, tracking de qual fila veio (campo interno `_queue_origin: "aviso" | "catalogo"`). Encontrar items onde:
- `regulation_local` e `null`
- `status` e `"pending"` ou nao definido (items com status "ready", "abandoned" sao ignorados)
- `regulation_url` existe (catalogo pode nao ter `pdf_url`)
- `fail_count` < 3 (items com 3+ falhas exigem fallback especial, ver Passo 1.6)

Processar no maximo **10 downloads por execucao** (soma das duas filas).
Priorizar por `priority_score` descendente, tratando ambas as filas como pool unico.

**Caso especial - ficheiros ja existentes no disco:** Se `regulation_local` aponta para um ficheiro que existe mas `status` ainda nao e `"ready"`, ir para Passo 2.5 para validar conteudo antes de marcar como ready.

---

## SEPARACAO CRITICA POR REGIME (LER ANTES DE PROSSEGUIR)

**Esta skill processa dois fluxos paralelos com regras DIFERENTES. Nunca misturar.**

### Fluxo A - Regime "aviso" (items de queue.json)
- Tem deadline formal, regulamento oficial (PDF), codigo de aviso
- **Testes PAA APLICAM-SE.** Objetivo: evitar descarregar "Resumos do Plano Anual" em vez de regulamentos reais.
- **Teste de tamanho minimo APLICA-SE** (800 palavras + "despesas elegiveis" ou "criterios de selecao")
- Fontes tipicas: PT2030 (portugal-2030, compete-2030, norte-2030, etc), EU (eu-funding-tenders, hadea, eismea), Interreg, ANI, IAPMEI, AICEP, FCT, IEFP, PRR

### Fluxo B - Regime "catalogo" (items de queue-catalogo.json)
- Pode nao ter deadline, regulamento, nem codigo formal. Bancos/VC/premios vendem produtos/fundos continuamente.
- **Testes PAA NAO SE APLICAM.** A deteccao PAA esta desenhada para linguagem especifica do PT2030. Um produto bancario ou fundo VC nunca dispara esses marcadores, mas se por acaso um texto tivesse uma coincidencia linguistica, nao queremos bloquear.
- **Teste de tamanho minimo NAO se aplica** com o threshold de 800 palavras. Usar threshold de 200 palavras. Paginas de produtos bancarios e fichas de fundos VC tem tipicamente 300-800 palavras.
- **Aceitar conteudo de pagina web** (HTML) como regulamento valido. Nao exigir PDF.
- Fontes tipicas: banco-fomento, cgd-empresas, bpi-empresas, millennium-empresas, novobanco-empresas, santander-empresas, indico-capital, armilar-ventures, faber-ventures, shilling-vc, bynd-vc, portugal-ventures, edp-innovation, premio-bpi-lacaixa, premio-gulbenkian, bgi-accelerator, startup-lisboa, beta-i, f6s, eu-startups, startup-portugal, turismo-portugal

**Determinacao do regime para um item:**
- Se `_queue_origin == "catalogo"`: regime = "catalogo"
- Se `_queue_origin == "aviso"`: regime = "aviso"
- Nunca derivar por outras vias. A fila de origem e autoritativa.

---

## PASSO 1.5: Verificar se e Plano Anual (APENAS Fluxo A - regime "aviso", APENAS PT2030)

**Este passo NAO se aplica a items de regime "catalogo". Saltar diretamente para Passo 2 se `_queue_origin == "catalogo"`.**

Para items de regime "aviso" com `source_id` que contenha "2030" ou "pessoas" E que tenham `regulation_url`:

Fazer WebFetch ao `regulation_url` ANTES de tentar descarregar qualquer PDF.

Verificar se a pagina contem QUALQUER um destes textos (case-insensitive):
- "previsao aproximada" / "previsão aproximada"
- "ficha que aqui pode consultar e apenas uma previsao"
- "aviso que ira ser lancado" / "aviso que irá ser lançado"
- "plano anual de avisos"

**Se qualquer um destes textos for encontrado:** MOVER item para `queue-plano-anual.json` (ver PASSO 3.5). Nao descarregar. Nao contar como falha nem como sucesso.

**Se nenhum destes textos for encontrado:** continuar para Passo 2.

---

## PASSO 1.6: Fallback via WebSearch para items com 3+ falhas

Items com `fail_count >= 3` ja falharam cascata normal. Antes de os marcar como `abandoned`, tentar **recuperacao de slug/URL via WebSearch**.

Muitos 404s sao causados por mudancas no slug da URL (ex: "adaptacao-as-alteracoes-climaticas-2-aviso" -> "adaptacao-as-alteracoes-climaticas-2o-aviso"). Este passo recupera esses casos.

**Logica:**

1. Query: `"[aviso_codigo]" "[nome do item]" site:[dominio da fonte]`
2. Se encontrar URL valido diferente do `regulation_url` atual:
   - Atualizar `regulation_url` no item
   - Resetar `fail_count` para 0
   - Tentar novamente a cascata normal (Passo 2)
3. Se nao encontrar nada de novo:
   - Marcar `status: "abandoned"`, `download_error: "URL inacessivel apos 3+ tentativas e WebSearch fallback"`
   - **Manter o item no queue.json** (nao apagar). O monitor podera re-verificar trimestralmente.

**Items "abandoned" sao ignorados pelo downloader em runs futuras** (filtro no Passo 1). Isto evita loops infinitos em items mortos.

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

Prompt para WebFetch: "Extrai toda a informacao sobre este aviso/instrumento de financiamento: nome, codigo, dotacao, taxa de cofinanciamento, elegibilidade, despesas elegiveis, prazos, criterios de selecao, programa, fundo."

Guardar resultado em `regulamentos/[source_id]/[id].txt`.

**Nota para items PT2030:** Portais regionais sao server-rendered (WebFetch funciona). Central (portugal2030.pt) e JS-rendered (WebFetch so retorna CSS/JS).

**Se WebFetch retornar < 300 palavras de conteudo real:** tratar como falha e continuar para 2b-pdf.

#### 2b-pdf: PDF via WordPress media API (para portais PT2030)

Se o item tem `wordpress_id` E regulamento ainda nao obtido:

1. `GET https://[portal-base]/wp-json/wp/v2/aviso-2024/[wordpress_id]` e extrair `acf.pdf`
2. Se `acf.pdf` for null/0: sem PDF. Continuar para 2c.
3. Se ID numerico valido: `GET https://[portal-base]/wp-json/wp/v2/media/[acf.pdf]`, extrair `source_url`
4. Descarregar e extrair:
   ```bash
   curl -sL "[source_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
   pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
   ```

5. **VERIFICACAO DO CONTEUDO DO PDF (so Fluxo A):**

   **TESTE A - Texto de plano anual (BLOQUEANTE):**
   Se contem "Plano Anual de Avisos", "Resumo de Aviso do Plano", "PAA2026", "PAA202", "Aviso a publicar em:"
   → Apagar .txt e .pdf. MOVER item para `queue-plano-anual.json` (ver PASSO 3.5). PARAR item.

   **TESTE B - Conteudo insuficiente (BLOQUEANTE):**
   Se < 800 palavras E nao contem "despesas elegiveis" E nao contem "criterios de selecao"
   → Apagar .txt e .pdf. Incrementar `fail_count`. Marcar `status: "pending"`, `download_error: "Resumo sem regulamento completo"`. PARAR item.

   **Se passou ambos:** continuar para Passo 2.5.

#### 2b-horizon: API JSON para items Horizonte Europa / SEDIA

Se `source_id == "eu-funding-tenders"` E regulamento nao obtido:

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

### Fluxo B (regime "catalogo") - cascata simplificada

Para cada item de regime "catalogo", seguir esta cascata:

#### 2a-cat. Se `pdf_url` existe (raro em catalogo, mas possivel):

```bash
mkdir -p "$REPO/regulamentos/[source_id]/"
curl -sL "[pdf_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
```

#### 2b-cat. Se `regulation_url` existe (caso normal para catalogo):

Usar `access_method` da fonte:
- `"webfetch"`: WebFetch no regulation_url
- `"chrome"`: Chrome MCP (navigate + get_page_text)
- `"websearch"`: WebSearch

Prompt para WebFetch (adaptado a catalogo): "Extrai toda a informacao sobre este produto de financiamento, fundo de investimento, premio ou programa: nome oficial, descricao, montantes/ticket, prazos de candidatura (se existirem), elegibilidade/perfil de empresas-alvo, setores, fases/estagios, contactos. Se nao existir deadline ou dotacao, registar que e candidatura continua ou produto permanente."

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

**Obrigatoria para TODOS os items de regime "aviso", independentemente do metodo de download. Nunca saltar.**

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

Este teste captura casos em que o downloader descarregou um "Resumo de Aviso do Plano Anual" em vez de aviso publicado. Sao documentos de previsao, nao regulamentos validos.

**Se passou Teste A:** continuar para Passo 3.

### 2.5.B - Fluxo B (regime "catalogo") - VALIDACAO LAX

**Os testes PAA do 2.5.A NAO SE APLICAM aqui. A linguagem PAA e especifica do PT2030 e nao aparece em produtos bancarios, fundos VC ou premios. Nunca correr Teste A em catalogo.**

Ler `.txt` obtido.

**TESTE C - Conteudo minimo para catalogo (NAO BLOQUEANTE, apenas warn):**
- Se tem >= 200 palavras: valido, marcar `status: "ready"`, prosseguir para Passo 3.
- Se tem < 200 palavras mas > 50: marcar `status: "ready"` com `download_note: "Conteudo breve - o writer deve complementar com WebSearch"`. Continuar para Passo 3.
- Se tem < 50 palavras ou ficheiro vazio: marcar `status: "pending"`, `download_error: "Conteudo insuficiente"`, tentar de novo em execucao futura.

**TESTE D - Link rot (NAO BLOQUEANTE):**
Se o curl ou WebFetch devolveu 404/403/500: marcar `status: "pending"`, `download_error: "HTTP [codigo] - URL pode ter mudado"`. O monitor marcara como needs_review.

**Nao e falha do downloader se um produto bancario tem pouco texto.** Muitos produtos bancarios sao descritos em 300-500 palavras. Isto e aceitavel em catalogo.

---

## PASSO 3: Atualizar queue (fila correcta)

Apos validacao bem-sucedida, atualizar o item:

```json
{
  "regulation_local": "regulamentos/[source_id]/[id].txt",
  "status": "ready",
  "fail_count": 0
}
```

**IMPORTANTE:** se o item veio de `queue.json` (regime aviso), actualizar em `queue.json`. Se veio de `queue-catalogo.json`, actualizar em `queue-catalogo.json`. Nunca mover items entre filas (excepcao: PAAs vao para queue-plano-anual.json via Passo 3.5).

Se download falhar:
```json
{
  "download_error": "PDF 404 - tentativa em 2026-04-16",
  "status": "pending",
  "fail_count": [incrementar],
  "last_fail_date": "2026-04-16"
}
```

**Se `fail_count` chegar a 3 apos este incremento:** o item fica elegivel para o Passo 1.6 (WebSearch fallback) na proxima run.

---

## PASSO 3.5: Mover PAA para watchlist (queue-plano-anual.json)

Quando um item e identificado como Plano Anual (Passo 1.5, Teste A em 2b-pdf ou 2.5.A):

1. **Remover** o item de `queue.json > queue` (pelo seu `id`)
2. **Adicionar** o item a `queue-plano-anual.json > queue` com campos adicionais:
   ```json
   {
     ...(campos originais),
     "status": "plano_anual",
     "download_error": "Plano Anual - nao e aviso publicado, apenas previsao",
     "plano_anual_detected_date": "2026-04-17",
     "plano_anual_checks": 1
   }
   ```
3. **Nao adicionar** ao lookup.json seccao plano_anual (redundante). O campo `by_id` ja garante dedup.

**Se o item ja existe em queue-plano-anual.json** (pode acontecer se o downloader reprocessa): incrementar `plano_anual_checks`, atualizar `plano_anual_last_check` com a data actual. Nao duplicar.

O monitor lera este ficheiro para re-verificar se os PAAs abriram.

---

## PASSO 4: Deploy

```bash
git -C "$REPO" add registry/queue.json registry/queue-catalogo.json registry/queue-plano-anual.json regulamentos/
git -C "$REPO" commit -m "downloader: [N] aviso + [N] catalogo ready, [N] PAAs watchlisted, [N] abandoned"
git -C "$REPO" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca misturar regimes.** Testes PAA SO para regime "aviso". Never apply to catalogo.
2. **Nunca exceder 10 downloads por execucao** (soma das duas filas).
3. **Nunca modificar artigos HTML ou shards.**
4. **Sempre guardar em UTF-8.**
5. **Se curl falhar:** tentar WebFetch como alternativa.
6. **Se tudo falhar:** marcar download_error e continuar. Nunca parar a execucao.
7. **Em catalogo, aceitar conteudo breve.** 200+ palavras e suficiente. Um produto bancario pode ter 300 palavras - nao e erro.

---

## RESUMO

```
1. Ler queue.json (aviso) + queue-catalogo.json (catalogo)
2. Encontrar items pending sem regulation_local (max 10 total, ignorar abandoned, fail_count>=3 vai ao Passo 1.6)
3. Para cada, determinar regime pela fila de origem:

   Fluxo A (aviso): cascata PDF -> WebFetch -> WebSearch
     PASSO 1.5 (PAA check): se PAA -> MOVER para queue-plano-anual.json (Passo 3.5), PARAR
     PASSO 2.5.A (BLOQUEANTE): Teste A (PAA) - se falhar: MOVER para queue-plano-anual.json, PARAR
     Teste B (tamanho) no 2b-pdf: incrementar fail_count, status pending
     Se passou: status ready, fail_count=0

   Fluxo B (catalogo): cascata simplificada WebFetch/PDF -> WebSearch
     PASSO 2.5.B (LAX): Teste C (minimo 50 palavras), Teste D (link rot)
     NUNCA aplicar testes PAA aqui
     Se conteudo >= 200: ready. Se 50-200: ready com note. Se < 50: pending + fail_count++.

   Items com fail_count >= 3: PASSO 1.6 (WebSearch fallback)
     Se encontrar novo URL: update + fail_count=0 + retry
     Se nao encontrar: status "abandoned"

4. Atualizar queue CORRECTA (aviso, catalogo ou plano-anual)
5. git commit + push
6. Reportar: "Downloader: [N] aviso ready, [N] catalogo ready, [N] PAAs watchlisted, [N] abandoned, [N] falhas."
```
