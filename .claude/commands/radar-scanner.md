# Radar Scanner v4.0: Descoberta de Novos Instrumentos

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o scanner do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e navegar fontes de financiamento e descobrir novos instrumentos.

**Esta skill so descobre.** Nao descarrega regulamentos, nao monitoriza estados, nao cria artigos.

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

Verificar no maximo **5 fontes por execucao**.

**REGRA CRITICA: Nunca filtrar por tipo de beneficiario.** Todos os avisos abertos devem ser descobertos, independentemente de serem para entidades publicas, privadas, mistas, ou qualquer outro tipo. A decisao editorial e do writer, nao do scanner.

**Prioridade de selecao:**
1. Fontes com `priority: "high"` nao verificadas ha mais de 3 dias
2. Fontes com `priority: "medium"` nao verificadas ha mais de 7 dias
3. Fontes com `priority: "low"` nao verificadas ha mais de 14 dias

Consultar `registry/index.json > source_last_checked` para a data de ultima verificacao de cada fonte individual. Este mapa contem a data exata de cada fonte (nao apenas a data global do ultimo scan).

**NOTA:** Programas regionais PT2030 (norte-2030, centro-2030, etc.) sao fontes independentes. Verificar a API central do PT2030 NAO cobre automaticamente os portais regionais. Cada um deve ser verificado individualmente.

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
- `acf.codigo` (ex: "FA0212/2025") - chave de deduplicacao
- `title.rendered` - nome do aviso
- `acf.data_inicio` / `acf.data_fim` - datas (formato YYYYMMDD)
- `acf.df` - dotacao financeira
- `acf.programa[]` - programas
- `acf.fundo[]` - fundo EU
- `acf.beneficiario[]` - elegibilidade (registar mas NAO filtrar)
- `acf.natureza` - Concurso/Convite
- `acf.pdf` - ID do media WordPress

Filtrar apenas por data: `data_fim > hoje` (abertos). NAO filtrar por beneficiario.

**Dedup entre APIs regionais e API central:**
Muitos avisos aparecem tanto na API central (portugal2030.pt) como nas APIs regionais (centro2030.pt, etc.). A deduplicacao por `acf.codigo` (via lookup.json) evita duplicados automaticamente. Nao e necessario tratamento especial.

### Se `access_method: "api"` (eu-funding-tenders):

Usar SEDIA Search API:
```
POST https://api.tech.ec.europa.eu/search-api/prod/rest/search?apiKey=SEDIA&text=2026&pageSize=200&pageNumber=1
```

Filtrar por status Open. Para cada topic aberto, buscar detalhes:
```
WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{slug}.json
```

Limitar a 20 topics detalhados por execucao.

### Se `access_method: "webfetch"`:

Usar WebFetch no `url_avisos` da fonte. Se a fonte tem paginacao, percorrer paginas.

Prompt: "Lista todos os avisos/instrumentos de financiamento visiveis. Para cada um: nome, codigo, estado, prazo, dotacao, URL regulamento, URL PDF."

### Se `access_method: "chrome"`:

Usar Chrome MCP: `navigate` -> `get_page_text` ou `read_page`.
Se pagina tem tabs/filtros "Abertos": clicar no filtro.
Se pagina tem "Ver mais": clicar ate carregar todos.

**NOTA:** Chrome MCP so funciona em execucao local (nao em agentes remotos). Se Chrome nao estiver disponivel, tentar WebFetch como fallback. Se tambem falhar, registar a fonte como "skipped: chrome unavailable" e continuar.

### Se `access_method: "websearch"`:

Usar WebSearch: `site:[url] avisos abertos 2026` ou `[nome_fonte] concursos abertos financiamento 2026`

---

## PASSO 3: Deduplicacao (usando lookup.json)

Para cada instrumento detectado:

1. Verificar se aberto: `data_fim > hoje`. Se encerrado: skip
2. Gerar `id` slug (kebab-case do nome)
3. **Lookup por ID:** `lookup.json.by_id[id]` existe? Se sim: skip
4. **Lookup por codigo:** `lookup.json.by_aviso_codigo[codigo]` existe? Se sim: skip
5. **Verificacao por titulo:** Se >= 80% similar a um item existente (mesma fonte): skip
6. Se novo e aberto: adicionar a queue

---

## PASSO 4: Adicionar novos a fila

### Limite de queue com swap por prioridade

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

Para cada instrumento novo, adicionar a `registry/queue.json > queue` (ou `queue-overflow.json` se limite atingido):

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
  "notes": "Dados basicos: codigo, programa, dotacao, beneficiario, prazo"
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

## PASSO 5: Atualizar estado

1. Atualizar `registry/index.json`:
   - `totals.in_queue`: novo tamanho da queue
   - `last_scanner_run`: data de hoje
2. Atualizar `source_last_checked` em `registry/index.json` para cada fonte verificada nesta run:
   ```json
   "source_last_checked": {
     "compete-2030": "2026-04-12",
     "norte-2030": "2026-04-12"
   }
   ```
   Manter as datas das fontes nao verificadas inalteradas.

---

## PASSO 6: Deploy

```bash
git -C "$REPO" add registry/index.json registry/queue.json registry/lookup.json sources-scan.json
git -C "$REPO" commit -m "scanner: [N fontes], [N novos] na fila"
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
1. Ler index.json + queue.json + lookup.json + sources-scan.json
2. Selecionar ate 5 fontes por prioridade/data
3. Para cada fonte: aceder, extrair avisos, deduplicar
4. Adicionar novos a queue + lookup
5. Atualizar index.json
6. git commit + push
7. Reportar: "Scanner: [N fontes]. Novos: [N]. Fila total: [N]."
```
