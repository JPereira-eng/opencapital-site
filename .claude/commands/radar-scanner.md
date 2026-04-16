# Radar Scanner v4.0: Descoberta de Novos Instrumentos

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o scanner do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e navegar fontes de financiamento e descobrir novos instrumentos.

**Esta skill so descobre.** Nao descarrega regulamentos, nao monitoriza estados, nao cria artigos.

**REGRAS DE PROCESSAMENTO CRITICAS:**
1. **NUNCA criar ficheiros temporarios** (avisos_portugal2030.json, new_open_avisos.json, temp_*.json, ou qualquer outro ficheiro intermedio). Processar tudo em memoria na sessao. Criar ficheiros temporarios causa bloqueios de contexto e perde dados.
2. **Maximo 50 novos items por run.** Se uma fonte tiver mais de 50 avisos novos, adicionar apenas os 50 com maior priority_score (prazo mais urgente + dotacao maior). Os restantes serao descobertos em runs futuras quando o lookup os identificar como ausentes.
3. **Processar fonte a fonte**, adicionando imediatamente ao queue.json/overflow apos cada fonte. Nao acumular todos os avisos de todas as fontes antes de escrever.

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
**Se REMOTO:** clonar `https://github.com/JPereira-eng/opencapital-site.git` para `/tmp/opencapital` e usar como `$REPO`. Limpar apos push.

---

## FICHEIROS DE ESTADO (v4.0)

| Ficheiro | Conteudo | Quando ler |
|---|---|---|
| `registry/index.json` | contadores globais | Sempre |
| `registry/queue.json` | fila de instrumentos | Sempre |
| `registry/lookup.json` | dedup O(1) por id/codigo | Sempre |
| `sources-scan.json` | fontes com access_method, shard | Sempre |

**Leitura no inicio:**
```
Read $REPO/registry/index.json
Read $REPO/registry/queue.json
Read $REPO/registry/lookup.json
Read $REPO/sources-scan.json
```

---

## PASSO 1: Selecionar fontes a verificar

Verificar no maximo **5 fontes por execucao**: **4 slots para regime "aviso" + 1 slot para regime "catalogo"**.

**REGRA CRITICA: Nunca filtrar por tipo de beneficiario.** Todos os avisos abertos devem ser descobertos, independentemente de serem para entidades publicas, privadas, mistas, ou qualquer outro tipo. A decisao editorial e do writer, nao do scanner.

**REGRA CRITICA: Ignorar fontes com `access_status: "blocked-auth"`** (ex: balcao-2030, nato-diana). Estas requerem autenticacao externa. Nao gastar slots nelas.

---

### Regime "aviso" (4 slots) — fontes que produzem avisos com deadline formal

Sao as fontes PT2030, Interreg, EU, ANI, AICEP, FCT, IEFP, PRR, Horizonte Europa e equivalentes. Campo `regime: "aviso"` em sources-scan.json.

**Os 4 slots aviso sao divididos em dois grupos com regras independentes:**

#### Slots 1-3: HIGH priority

Selecionar por esta ordem:
1. Fontes "high" NUNCA verificadas (prioridade absoluta, ate 3)
2. Fontes "high" nao verificadas ha mais de 3 dias (ordenar por mais antiga primeiro)
3. Se menos de 3 candidatos: completar com fontes "high" mais antigas (mesmo dentro dos 3 dias)

**Ignorar completamente** fontes medium e low nestes 3 slots.

#### Slot 4: MEDIUM/LOW garantido

Este slot e exclusivo para fontes de prioridade medium ou low. Nunca e preenchido por uma fonte high. Isto garante que medium/low rodam mesmo quando ha muitas high atrasadas.

Selecionar por esta ordem:
1. Fontes medium ou low NUNCA verificadas (prioridade absoluta)
2. Fontes "medium" nao verificadas ha mais de 7 dias (ordenar por mais antiga primeiro)
3. Fontes "low" nao verificadas ha mais de 14 dias (ordenar por mais antiga primeiro)
4. Se nenhum candidato elegivel: deixar o slot vazio (nao substituir por high)

Consultar `registry/index.json > source_last_checked` para a data de ultima verificacao de cada fonte individual.

**Fontes cobertas por superset:** `eu-funding-tenders` cobre HORIZON, CEF, DIGITAL, LIFE, ERASMUS+, CERV, JUST, COSME, EU4HEALTH, CREATIVE-EUROPE (ver `covers_programs` em sources-scan.json). Se `eu-funding-tenders` foi verificada ha menos de **2 dias**, as sub-fontes individuais (horizon-cluster1..6, horizon-msca, horizon-widera, horizon-missions, erasmus-*, cerv, justice-programme, creative-europe, single-market-programme) NAO devem ocupar slots. Os avisos ja foram descobertos via superset.

**Nota:** O limiar e 2 dias (nao 7) porque o catalogo EU tem milhares de topics ainda por descobrir. Fontes EU independentes (horizonte-europa via ANI, hadea, eismea, interreg-*) nunca sao bloqueadas pelo superset — sao fontes distintas com conteudo proprio.

**NOTA:** Programas regionais PT2030 (norte-2030, centro-2030, etc.) sao fontes independentes. Verificar a API central do PT2030 NAO cobre automaticamente os portais regionais. Cada um deve ser verificado individualmente.

---

### Regime "catalogo" (1 slot) — fontes de referencia, candidatura continua ou periodicidade irregular

Sao as fontes de bancos, VC, premios, aceleradores e startups. Campo `regime: "catalogo"` em sources-scan.json.

**Prioridade de selecao:**

1. Fontes catalogo NUNCA verificadas: prioridade absoluta (1 por run)
2. Fontes catalogo verificadas ha mais de 90 dias (1 por run, a mais antiga primeiro)
3. **Se nenhuma fonte catalogo for elegivel:** usar o slot para uma fonte aviso de prioridade medium ou low (a mais antiga por antiguidade, mesma logica do slot 4). Nao desperdicar o slot.

**Nota:** com 22 fontes catalogo e 1 slot/run, nos primeiros ~22 dias o slot fica preenchido pelas nunca-verificadas. Depois disso, a maioria dos dias nao ha candidatos catalogo elegíveis (90 dias ainda nao passaram) e o slot cai automaticamente para aviso medium/low.

**Regras especificas para regime "catalogo":**
- **Nao exigir deadline formal.** Estas fontes operam com candidatura continua, produtos permanentes ou premios anuais sem data fixa. Registar o instrumento mesmo sem prazo (`deadline: null`).
- **Nao adicionar a queue.json.** Instrumentos de regime "catalogo" sao adicionados diretamente ao `registry/queue-catalogo.json` (estrutura identica a queue.json). O writer le este ficheiro separadamente.
- **VC e fundos de investimento privado:** Verificar uma vez por trimestre. Se nao houver call formal aberta, registar o fundo como instrumento de referencia (ex: "Fundo Indico Capital - candidatura permanente") com `status: "cont"` (candidatura continua). Util para o catalogo mesmo sem aviso ativo.
- **Bancos (CGD, BPI, Millennium, NovoBanco, Santander):** Verificar uma vez por trimestre. Registar linhas de credito e produtos para empresas como instrumentos de tipo "div" (divida). Sem deadline.
- **Premios e aceleradores:** Verificar uma vez por trimestre. Se existir candidatura aberta com prazo, registar normalmente. Se nao: registar como referencia anual.

---

## PASSO 2: Aceder a cada fonte

Consultar `access_method` no `sources-scan.json`:

### Se `access_method: "api"` (portais WordPress PT2030):

**Aplica-se a:** portugal-2030, centro-2030, lisboa-2030, pessoas-2030, alentejo-2030, algarve-2030, madeira-2030, acores-2030, pat-2030, sustentavel-2030.

Usar o `api_url` definido em `sources-scan.json` para cada fonte. Exemplo:
```
WebFetch: https://centro2030.pt/wp-json/wp/v2/aviso-2024?page=1
WebFetch: https://centro2030.pt/wp-json/wp/v2/aviso-2024?page=2
... (continuar ate resposta vazia ou erro 400)
```

**REGRA CRITICA DE PAGINACAO — NUNCA PARAR ANTES DO FIM:**
- Cada pagina devolve 10 resultados
- OBRIGATORIO percorrer TODAS as paginas ate receber resposta vazia ou erro HTTP 400
- Nunca parar na pagina 3 ou 5 "para poupar tokens" — a paginacao incompleta causa perda de instrumentos
- Se uma fonte tem 22 paginas, percorrer as 22. Se tem 4, percorrer as 4
- O custo de tokens da paginacao e muito inferior ao custo de perder instrumentos

**NOTA sobre Sustentavel 2030:** O endpoint e `/wp-json/wp/v2/aviso` (sem "-2024"). Verificar sempre o campo `api_url` em sources-scan.json.

De cada aviso JSON, extrair:
- `link` - URL canonica da pagina do aviso (OBRIGATORIO como regulation_url)
- `acf.codigo` (ex: "FA0212/2025") - chave de deduplicacao
- `title.rendered` - nome do aviso
- `acf.data_inicio` / `acf.data_fim` - datas (formato YYYYMMDD)
- `acf.df` - dotacao financeira
- `acf.programa[]` - programas
- `acf.fundo[]` - fundo EU
- `acf.beneficiario[]` - elegibilidade (registar mas NAO filtrar)
- `acf.natureza` - Concurso/Convite
- `acf.pdf` - ID do media WordPress

**REGRA CRITICA - FILTRO acf.pdf (APENAS fontes PT2030 com access_method: "api"):**

Para cada aviso obtido da API, verificar o campo `acf.pdf`:
- Se `acf.pdf` e null, 0, false ou string vazia: **SKIP TOTAL** - nao adicionar a queue, nao adicionar ao lookup.json. Estes items sao quase sempre plano anual ou resumos sem regulamento. Serao reavaliados em futuras runs quando o PDF for publicado.
- Se `acf.pdf` e um ID numerico valido (ex: 252679): continuar normalmente.

Esta regra aplica-se APENAS a fontes com `access_method: "api"`. Para fontes webfetch/chrome/websearch nao existe campo `acf.pdf`, ignorar esta regra.

Registar no relatorio: "N items sem PDF ignorados (possivel plano anual)".

**REGRA CRITICA - URL DO AVISO:**
O campo `regulation_url` de cada item DEVE ser o campo `link` do JSON da API (ex: `https://portugal2030.pt/aviso-2024/nome-do-aviso/`). NUNCA usar URLs genericos como `https://portugal2030.pt/avisos/` ou `https://pessoas2030.gov.pt/avisos/`. Se `link` nao estiver disponivel, construir a partir do slug do aviso.

**REGRA CRITICA - ESTADO DO AVISO:**
Determinar o estado com base na data de hoje:
- Se `data_inicio > hoje`: estado = `"previsto"` (aviso publicado mas candidaturas ainda nao abriram)
- Se `data_inicio <= hoje` E `data_fim > hoje`: estado = `"aberto"` (candidaturas abertas)
- Se `data_fim <= hoje`: SKIP - nao adicionar a queue (encerrado)

**Registar sempre o campo `acf.natureza` nas notes** (Concurso/Convite/Pre-Qualificacao). O writer usa esta informacao para contextualizar o artigo.

Filtrar por data: `data_fim > hoje`. NAO filtrar por beneficiario nem por natureza.

**Dedup entre APIs regionais e API central:**
Muitos avisos aparecem tanto na API central (portugal2030.pt) como nas APIs regionais (centro2030.pt, etc.). A deduplicacao por `acf.codigo` (via lookup.json) evita duplicados automaticamente. Nao e necessario tratamento especial.

### Se `access_method: "api"` (eu-funding-tenders):

**Logica de paginacao progressiva — o lookup.json e o marcador de progresso:**

A SEDIA API tem centenas ou milhares de topics abertos. Nao e possivel processar todos numa run. A logica correcta e:

1. Percorrer as paginas da API **em ordem**, uma a uma (pageSize=200):
   ```
   pageNumber=1 → pageNumber=2 → pageNumber=3 → ...
   ```
2. Para cada topic de cada pagina: verificar o lookup.
   - Se ja esta em `lookup.by_aviso_codigo` ou `lookup.by_id`: **skip** (ja foi descoberto numa run anterior)
   - Se e novo: buscar detalhes e adicionar a queue
3. Continuar a paginar ate atingir **50 topics novos** (com detalhes buscados) OU ate a API nao retornar mais resultados.
4. Parar. Os topics seguintes ficam para a proxima run.

**Na proxima run:** o lookup ja tem os 50 do ciclo anterior. O scanner percorre as primeiras paginas rapidamente (todos skip), avanca ate encontrar os proximos novos, e recolhe mais 50. E assim sucessivamente ate cobrir todos os topics.

**Implementacao:**
```
pageNumber = 1
novos_encontrados = 0

enquanto novos_encontrados < 50:
  GET https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA&text=2026&pageSize=200&pageNumber=[pageNumber]
  se resposta vazia: parar (fim do catalogo)
  
  para cada topic na pagina:
    se topic em lookup: skip
    senao:
      WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{slug}.json
      adicionar a queue + lookup
      novos_encontrados += 1
      se novos_encontrados == 50: parar

  pageNumber += 1
```

**Registar no relatorio granular:** paginas percorridas, topics vistos, topics skip (dedup), topics novos com detalhes.

**Nota importante:** Filtrar por status Open. Topics com status FORTHCOMING, CLOSED ou AWARDED: skip sem buscar detalhes.

### Se `access_method: "webfetch"`:

Usar WebFetch no `url_avisos` da fonte. Se a fonte tem paginacao, percorrer paginas.

Prompt: "Lista todos os avisos/instrumentos de financiamento visiveis. Para cada um: nome, codigo, estado, prazo, dotacao, URL regulamento, URL PDF."

**REGRA CRITICA - MULTIPLOS URLs ANTES DE DECLARAR "0 NOVOS":**

Muitos portais organizam conteudo em multiplas paginas/seccoes. Antes de concluir que uma fonte webfetch nao tem nada novo, **verificar pelo menos 3 URLs** do dominio, nesta ordem:

1. **URL principal** (`url_avisos` de sources-scan.json)
2. **URLs alternativos tipicos** (tentar ate encontrar 200 OK):
   - `[dominio]/convocatorias/`
   - `[dominio]/calls/`
   - `[dominio]/oportunidades/`
   - `[dominio]/avisos/`
   - `[dominio]/concursos/`
   - `[dominio]/open-calls/` ou `[dominio]/open-call/`
   - `[dominio]/programas/`
   - `[dominio]/en/calls/` (versao inglesa)
3. **WebSearch de fallback** se nenhum dos anteriores retornou conteudo util:
   ```
   site:[dominio] (calls OR concursos OR convocatorias OR avisos) 2026
   ```

**Minimo 3 tentativas antes de declarar "0 novos".** Registar no relatorio granular (ver Passo 5) quais URLs foram verificados e o que cada um retornou.

**Excecao:** se o URL principal ja lista claramente "todas as oportunidades" num indice (ex: ec.europa.eu/info/funding-tenders), uma so verificacao basta. Documentar esta decisao no relatorio.

### Se `access_method: "chrome"`:

Usar Chrome MCP: `navigate` -> `get_page_text` ou `read_page`.
Se pagina tem tabs/filtros "Abertos": clicar no filtro.
Se pagina tem "Ver mais": clicar ate carregar todos.

**NOTA:** Chrome MCP so funciona em execucao local (nao em agentes remotos). Se Chrome nao estiver disponivel, tentar WebFetch como fallback. Se tambem falhar, registar a fonte como "skipped: chrome unavailable" e continuar.

### Se `access_method: "websearch"`:

Usar WebSearch: `site:[url] avisos abertos 2026` ou `[nome_fonte] concursos abertos financiamento 2026`

### Campos a extrair de fontes nao-API (webfetch, chrome, websearch)

Para fontes que nao tem API estruturada, extrair o maximo possivel:
- **Nome** do instrumento/programa (OBRIGATORIO)
- **URL** da pagina do instrumento (OBRIGATORIO como regulation_url)
- **Prazo/deadline** (se existir na pagina - muitas fontes nao tem deadline formal)
- **Dotacao/budget** (se disponivel)
- **Elegibilidade** (tipo de entidades elegiveis)
- **Estado** (aberto, encerrado, permanente, candidatura continua)

**Se a fonte nao tem prazos formais** (ex: IEFP, bancos, aceleradores, premios permanentes): usar `deadline: null`. Nao inventar prazos. Nao excluir o item por falta de prazo. Estas fontes operam com candidatura continua ou "ate esgotar dotacao".

**ATENCAO - Fontes PT2030 continuam com regras estritas:** A flexibilidade de deadline nulo aplica-se APENAS a fontes nao-PT2030 e nao-EU. Para fontes PT2030 com access_method "webfetch" (ex: compete-2030, norte-2030), os avisos devem ter prazo. Se nao tiverem prazo visivel, registar mas com nota "prazo nao visivel na pagina".

---

## PASSO 3: Deduplicacao (usando lookup.json)

Para cada instrumento detectado:

1. **Filtro temporal (depende do regime da fonte):**
   - **Regime "aviso" PT2030** (access_method: "api", portais WordPress): `data_fim > hoje` obrigatorio. Se encerrado ou sem data_fim: skip.
   - **Regime "aviso" EU** (eu-funding-tenders, Horizon, Interreg): deadline obrigatorio. Se expirado: skip.
   - **Regime "aviso" outras** (IEFP, ANI, IAPMEI, agencias nacionais): deadline pode ser null. Se deadline existe e ja passou: skip. Se nao existe deadline: incluir com `deadline: null`.
   - **Regime "catalogo"** (bancos, VC, premios, aceleradores, startups): deadline NUNCA obrigatorio. Incluir sempre com `deadline: null` se nao existir prazo formal.
2. Gerar `id` slug (kebab-case do nome)
3. **Lookup por ID:** `lookup.json.by_id[id]` existe? Se sim: skip
4. **Lookup por codigo:** `lookup.json.by_aviso_codigo[codigo]` existe? Se sim: skip
5. **Verificacao por titulo:** Se >= 80% similar a um item existente (mesma fonte): skip
6. Se novo e nao filtrado: adicionar a queue (ver Passo 4 para destino correto por regime)

---

## PASSO 4: Adicionar novos a fila

### Destino por regime

**Regime "aviso":** adicionar a `registry/queue.json` (ou overflow se cheio). O writer le esta fila em cada run.

**Regime "catalogo":** adicionar a `registry/queue-catalogo.json`. O writer le esta fila separadamente, com menor frequencia. Estrutura identica a queue.json.

---

### Regime "aviso" - Limite de queue com swap por prioridade

Antes de adicionar novos items, verificar o tamanho atual da queue:

**Se `queue.length < 100`:** adicionar normalmente a `queue.json`.

**Se `queue.length >= 100`:** nao ir directamente para overflow. Fazer swap por prioridade:

1. Calcular `min_score = min(queue[].priority_score)`
2. Se `novo_item.priority_score > min_score`:
   - Remover da queue todos os items com `priority_score == min_score` ate ter espaco (max 1 item removido por novo item inserido)
   - Mover o item removido para `registry/queue-overflow.json`
   - Adicionar o novo item a `queue.json`
3. Se `novo_item.priority_score <= min_score`:
   - Adicionar directamente a `registry/queue-overflow.json`

**Regra de migracao do overflow:** Quando o scanner deteta `queue.length < 80`, migrar os items de maior priority_score do overflow para a queue ate perfazer 100 items.

O overflow tem a mesma estrutura que queue.json mas com `"_meta": "Overflow. Items migram para queue.json quando esta desce abaixo de 80."`. **O writer nao le o overflow.**

Para cada instrumento de regime "aviso", adicionar a `registry/queue.json > queue` (ou `queue-overflow.json` se limite atingido):

```json
{
  "id": "slug-do-instrumento",
  "name": "Nome completo do aviso",
  "source_id": "fonte-id",
  "shard": "shard-da-fonte (ver sources-scan.json)",
  "aviso_codigo": "FA####/YYYY ou HORIZON-xxx (se disponivel)",
  "detected_date": "2026-04-12",
  "deadline": "2026-09-30",
  "budget": "2.000.000 EUR",
  "regulation_url": "https://...",
  "pdf_url": "https://...pdf (se disponivel)",
  "regulation_local": null,
  "priority_score": 0,
  "status": "pending",
  "notes": "Dados basicos: codigo, programa, dotacao, beneficiario, prazo. SEM_PDF se acf.pdf=null (possivel plano anual - downloader verificara)"
}
```

**Routing de shard para items de APIs WordPress PT2030:**

Items de APIs regionais (centro-2030, lisboa-2030, pessoas-2030, alentejo-2030, algarve-2030, madeira-2030, acores-2030, pat-2030, sustentavel-2030): usar o `shard` definido em `sources-scan.json` para a fonte. O shard ja esta pre-definido.

Items detetados via API central (`source_id: "portugal-2030"`) devem ser encaminhados para o shard correto com base no campo `acf.programa[]`:
- Se programa contem apenas "COMPETE" ou "COMPETE2030": `shard: "pt2030-compete"`
- Se programa contem apenas "PESSOAS" ou "PESSOAS2030": `shard: "pt2030-pessoas"`
- Se programa contem apenas "NORTE" ou "NORTE2030": `shard: "pt2030-norte"`
- Se programa contem apenas "CENTRO" ou "CENTRO2030": `shard: "pt2030-centro"`
- Se programa contem apenas "LISBOA" ou "LISBOA2030": `shard: "pt2030-lisboa"`
- Se programa contem apenas "ALENTEJO", "ALGARVE", "ACORES", "MADEIRA", "MAR", "SUSTENTAVEL", ou "PAT": `shard: "pt2030-other"`
- Se programa contem multiplos programas (ex: "COMPETE + ALENTEJO + ALGARVE"): `shard: "pt2030-central"`
- Se programa nao identificavel: `shard: "pt2030-central"`

Para fontes nao-PT2030 (EU, Interreg, etc.), usar o `shard` definido em `sources-scan.json`.

**Calculo do priority_score:**
- Prazo < 30 dias: +100
- Prazo 30-60 dias: +50
- Prazo 60-90 dias: +20
- Prazo null (candidatura continua/permanente): +10
- Dotacao > 10M EUR: +30
- Dotacao > 1M EUR: +10
- Fonte priority "high": +15
- Fonte priority "medium": +5

**Tambem adicionar ao lookup.json:**
```json
"by_id": { "novo-slug": true },
"by_aviso_codigo": { "FA####/YYYY": "novo-slug" }
```

---

## PASSO 5: Atualizar estado e produzir relatorio granular

### 5a. Atualizar registry/index.json

1. `totals.in_queue`: novo tamanho da queue.json (NAO somar queue-catalogo)
2. `last_scanner_run`: data de hoje
3. `source_last_checked` para cada fonte verificada nesta run:
   ```json
   "source_last_checked": {
     "compete-2030": "2026-04-12",
     "norte-2030": "2026-04-12"
   }
   ```
   Manter as datas das fontes nao verificadas inalteradas.

### 5b. RELATORIO GRANULAR OBRIGATORIO

**No final da execucao, produzir relatorio estruturado com TODAS as metricas por fonte.** Este relatorio torna o comportamento do scanner transparente e auditavel. Sem este detalhe, e impossivel detectar regressoes (falhas silenciosas, paginacao incompleta, filtros excessivos, dedup incorrecto).

**Template obrigatorio por fonte:**

```
[source-id] (regime: aviso|catalogo, access_method: X)
  Paginas/URLs verificados:
    - [url_1]: [N items retornados | vazio | HTTP xxx | timeout]
    - [url_2]: [...]
  Items retornados pela fonte (total): N
  Filtros aplicados:
    - Sem acf.pdf (PT2030 apenas): N ignorados
    - data_fim no passado: N ignorados
    - data_inicio no passado mas data_fim no futuro: N mantidos (abertos)
    - data_inicio no futuro: N mantidos (previstos)
  Deduplicacao:
    - Ja em lookup.by_aviso_codigo: N ignorados
    - Ja em lookup.by_id: N ignorados
    - Titulo >= 80% similar: N ignorados
  NOVOS adicionados a queue.json (aviso): N
  NOVOS adicionados a queue-catalogo.json (catalogo): N
```

**Template final do run:**

```
Scanner run: 2026-04-16
Fontes verificadas: 5 de 5 slots
  - Regime aviso: 4 (listar)
  - Regime catalogo: 1 (listar)

[bloco granular por fonte, conforme template acima]

Totais da run:
  - Total items retornados pelas fontes: N
  - Total ignorados por acf.pdf: N
  - Total ignorados por deadline: N
  - Total ignorados por dedup: N
  - Total NOVOS aviso: N
  - Total NOVOS catalogo: N

Estado da queue:
  - queue.json antes: N
  - queue.json depois: N (delta = novos_aviso - migrados_para_overflow + migrados_do_overflow)
  - queue-catalogo.json antes: N
  - queue-catalogo.json depois: N (delta = novos_catalogo)
  - queue-overflow.json antes: N
  - queue-overflow.json depois: N

Operacoes de overflow (se houver):
  - Items movidos queue -> overflow: N (priority_score min: X)
  - Items movidos overflow -> queue: N
```

**Nunca suprimir campos por brevidade.** Mesmo que zero, reportar `Sem acf.pdf: 0 ignorados`. Ausencia de campo e ambiguidade.

---

## PASSO 6: Sanity check + Deploy

### 6a. SANITY CHECK DE CONTAGEM (OBRIGATORIO antes do commit)

Antes de qualquer `git add`, validar que as contagens batem certo. Uma discrepancia indica bug interno (items adicionados silenciosamente, migracao inesperada do overflow, dedup falhado).

**Calcular as esperancas:**
```
expected_queue_delta = novos_aviso - movidos_para_overflow + movidos_do_overflow
expected_queue_catalogo_delta = novos_catalogo
expected_overflow_delta = movidos_para_overflow - movidos_do_overflow
expected_in_queue = queue_antes + expected_queue_delta
```

**Verificar os valores reais:**
```
actual_queue_depois = queue.json.queue.length
actual_queue_catalogo_depois = queue-catalogo.json.queue.length
actual_overflow_depois = queue-overflow.json.queue.length
actual_in_queue = index.json.totals.in_queue
```

**Comparar:**
- `actual_queue_depois == queue_antes + expected_queue_delta` ?
- `actual_queue_catalogo_depois == queue_catalogo_antes + expected_queue_catalogo_delta` ?
- `actual_overflow_depois == overflow_antes + expected_overflow_delta` ?
- `actual_in_queue == actual_queue_depois` (index.json deve reflectir queue.json) ?

**Se QUALQUER uma falhar:**
1. **NAO fazer commit.**
2. Imprimir discrepancia completa:
   ```
   SANITY CHECK FAIL:
     queue.json esperado: [X], actual: [Y], diff: [Y-X]
     index.in_queue esperado: [X], actual: [Y], diff: [Y-X]
   ```
3. Investigar qual foi o item/operacao extra ou em falta.
4. Corrigir antes de commit, ou reverter mudancas e abortar a run.

**Se todas passarem:** prosseguir para 6b.

Este sanity check existe porque em runs anteriores foram reportados "3 novos" quando `in_queue` subiu 7 - indicando que 4 items entraram sem ser explicitamente contabilizados. Este teste deteta isso antes do push.

### 6b. Commit e push

```bash
git -C "$REPO" add registry/index.json registry/queue.json registry/queue-catalogo.json registry/queue-overflow.json registry/lookup.json sources-scan.json
git -C "$REPO" commit -m "scanner: [N fontes], [N novos aviso], [N novos catalogo]"
git -C "$REPO" push origin main
```

Se push falhar: `git -C "$REPO" pull --rebase origin main && git -C "$REPO" push origin main`

---

## REGRAS DE SEGURANCA

1. **Nunca duplicar items.** Usar lookup.json para dedup O(1).
2. **Nunca filtrar por beneficiario.** Todos os tipos de organizacoes sao incluidos.
3. **Nunca exceder 5 fontes por execucao.**
4. **Nunca modificar artigos HTML ou shards de publicados.** So modifica queue e lookup.
5. **Se WebFetch/Chrome falhar:** registar o erro e continuar para a proxima fonte.

---

## RESUMO

```
1. Ler index.json + queue.json + queue-catalogo.json + lookup.json + sources-scan.json
2. Selecionar ate 5 fontes:
   - Slots 1-3: high nunca-verificadas > high >3d > high mais antigas (so high)
   - Slot 4: medium/low nunca-verificadas > medium >7d > low >14d (nunca high, pode ficar vazio)
   - Slot 5: catalogo nunca-verificadas > catalogo >90d > se vazio: medium/low aviso mais antiga
3. Para cada fonte:
   - Aceder (se webfetch: tentar 3 URLs antes de declarar "0 novos")
   - Extrair items, aplicar filtros, deduplicar
   - Adicionar novos a queue correcta (aviso -> queue.json, catalogo -> queue-catalogo.json)
4. Manter contadores internos: novos_aviso, novos_catalogo, movidos_overflow
5. Atualizar index.json e source_last_checked
5b. Produzir RELATORIO GRANULAR: por fonte detalhar URLs verificados, items retornados, filtros, dedup, novos
6a. SANITY CHECK: queue_depois == queue_antes + delta esperado. Se falhar: ABORT sem commit.
6b. git commit + push
7. Reportar relatorio granular completo
```
