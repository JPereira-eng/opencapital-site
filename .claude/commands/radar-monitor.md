---
name: radar-monitor
model: claude-sonnet-4-7
---

# Radar Monitor v4.2: Verificacao de Estados e Integridade

REGRA CRÍTICA: Nunca usar travessão (—) em nenhum texto gerado. Usar vírgula, ponto, hífen (-) ou reescrever a frase.

Es o monitor do sistema radar da Open Capital Advisory & Consultancy.
A tua missão e verificar se instrumentos publicados mudaram de estado, prazo, dotacao ou conteudo do regulamento.

**Esta skill so monitoriza.** Não descobre instrumentos, não descarrega regulamentos, não cria artigos.

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
| `registry/index.json` | Sempre (para decidir que shard verificar) |
| `registry/shards/[shard].json` | 1-2 shards por run |
| `registry/integrity.json` | Sempre (hashes de PDFs dos regulamentos) |
| `registry/queue-plano-anual.json` | Sempre (watchlist de PAAs - Passo 2.6) |
| `registry/queue.json` | Ler para promoção de PAAs que abriram |
| `sources-scan.json` | Para access_method e regime das fontes |

**NAO ler todos os shards.** Ler apenas o(s) shard(s) a verificar nesta run.

**MUDANCA v4.1 (2026-04-17):** A watchlist de PAAs migrou de `lookup.json > plano_anual` para ficheiro dedicado `queue-plano-anual.json`. Capacidade duplicada (10 items/run vs 5).

---

## SEPARACAO CRÍTICA POR REGIME

O monitor atua de forma DIFERENTE consoante o regime da fonte do item:

### Regime "aviso" (shards: pt2030-*, eu-*, eic, interreg, pt-other)
- Verifica **estado** (aberto/fechado/previsto)
- Verifica **prazo** (data_fim)
- Verifica **dotacao** (budget)
- Verifica **integridade do regulamento** (SHA1 hash do PDF - detecta adendas)

### Regime "catálogo" (shards: catálogo-bancos, catálogo-vc, catálogo-premios, catálogo-aceleradores)
- **NAO verifica estado.** Produtos bancarios, fundos VC e aceleradores operam em candidatura continua. Assumir sempre "aberto" (status "cont").
- **NAO verifica prazo** (não existe deadline formal).
- Verifica **link rot** apenas: URL continua a responder 200?
- Se pagina foi removida ou redireccionada: marcar `needs_review: true` no shard.

---

## PASSO 0.5: Auto-fecho por data expirada (fail-safe) — v4.13 diferenciado

**Antes** de qualquer verificação de fonte externa, executar passagem local de fail-safe sobre TODOS os shards de regime "aviso".

⚠️ **MUDANÇA v4.13 (2026-05-12):** comportamento DIFERENTE consoante `data_status` do item:

### Para items com `data_status: "verified"` (regulamento real confirmado)

Para cada item com `estado: "aberto"` e `data_fim` definida:
- Se `data_fim < hoje`: marcar como `estado: "fechado"`, atualizar `status_text` para "Fechado", `status_class` para "status-closed", `auto_closed: true`, e propagar ao `instruments-catalog.json`.
- Comportamento normal (regulamento real teve abertura → agora fechado).

### Para items com `data_status: "forecast"` (apenas PAA forecast, nunca verificado)

⚠️ **NÃO usar a label "fechado".** Estes items nunca abriram como aviso real — as datas vieram do PAA forecast da API central PT2030. Marcar como fechado seria mentira semântica (não houve nada para fechar).

- Se `data_fim < hoje`: marcar como `estado: "expired_unrealized"`, `status_text: "PAA expirado sem publicação"`, `status_class: "status-unrealized"`.
- Mover para `registry/queue-plano-anual-archived.json` (sai do circuito ativo, fica para auditoria).
- Não retentar via PASSO 2.6, 2.7 (ineficaz: AG não publicou no calendário previsto).

### Para items com `data_status: "n/a"` (famílias não-PT2030)

Comportamento idêntico ao v4.12 anterior (estes itens não usam o conceito forecast/verified).

**Justificação:** o monitor depende da fonte para confirmar fechos. Mas para items PT2030 forecast, "fechar" sem ter aberto é incoerente. `expired_unrealized` reflete a realidade: PAA previu calendário, AG não cumpriu, aviso real nunca apareceu.

Esta passagem é rápida (leitura local, sem WebFetch) e não conta para o limite de 1-2 shards por run.

---

## PASSO 1: Selecionar shard a verificar

Ler `registry/index.json`. Selecionar **1-2 shards** por run, priorizando:

1. Shards com mais items "aberto" ou "previsto" (regime aviso)
2. Shards cujas fontes não foram verificadas ha mais tempo
3. Shards com deadlines próximos (< 30 dias) - so regime aviso
4. Shards catálogo verificados ha > 90 dias (rotacao trimestral)

**Smart scheduling por risco (regime aviso):**
- Items com deadline < 30 dias: verificar sempre
- Items com deadline < 90 dias: verificar a cada 3 runs
- Items com deadline > 90 dias: verificar a cada 10 runs
- Items "fechado": verificar 1 por cada 5 abertos (para confirmar se reabriram)

**Smart scheduling regime catálogo:**
- Items catálogo: verificar 1 vez por trimestre (link rot apenas)

---

## PASSO 2: Verificar por lotes via super-fonte

### 2.A - Shards de regime "aviso" - verificação completa

Verificar **fonte a fonte** em vez de instrumento a instrumento:

#### Para shards PT2030:

```
WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?page=1
(percorrer todas as paginas)
```

Um único ciclo de WebFetch retorna todos os avisos da API central. Comparar com os items no shard:
- Para cada item do shard, procurar o aviso correspondente na API (por aviso_codigo ou titulo)
- Verificar: estado mudou? prazo mudou? dotacao mudou?

#### Para portais regionais PT2030 (centro-2030, lisboa-2030, alentejo-2030, etc.):

Portais com WordPress API (ver `api_url` em sources-scan.json): usar a API diretamente.
```
WebFetch: https://centro2030.pt/wp-json/wp/v2/aviso-2024?page=1
```
Comparar `acf.data_fim`, `acf.df`, e estado com os dados do shard.

Portais sem API (norte-2030, compete-2030): WebFetch na pagina de concursos.

#### Para shards EU:

```
WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{topic-id}.json
```

Verificar `actions[0].status.abbreviation` para cada item.

#### Para pt-other:

Verificar cada item individualmente na sua fonte. Max 10 verificacoes individuais por run.

### 2.B - Shards catálogo - link rot apenas

Para cada item no shard catálogo, fazer HEAD request ao `regulation_url` (ou GET leve via WebFetch):

```bash
curl -sI "[regulation_url]" -o /dev/null -w "%{http_code}"
```

- Se retorna 200: OK, actualizar `last_check` no shard
- Se retorna 404/410 (removido): marcar `needs_review: true` no shard, `review_reason: "URL removida (HTTP [código])"`
- Se retorna 301/302 (redirect): seguir redirect, se destino final OK, actualizar `regulation_url` no shard. Se destino também 404: marcar needs_review
- Se retorna 403/500/timeout: não alterar (pode ser erro transitorio), tentar na próxima run

**Nunca reescrever artigos de catálogo automaticamente.** So marcar needs_review.

---

## PASSO 2.5: Verificacao de integridade do regulamento (APENAS regime aviso)

**Objetivo:** detetar adendas, alteracoes ou novas versões de regulamentos que normalmente são publicadas sob o mesmo aviso_codigo mas com conteudo diferente. Um regulamento alterado pode mudar dotacao, beneficiarios, criterios - afetando o artigo.

**Este passo NAO se aplica a regime catálogo.** Saltar.

Para cada item do shard com `regulation_local` apontando para PDF existente:

1. Calcular SHA1 hash do PDF actual no disco:
   ```bash
   sha1sum "$REPO/regulamentos/[source_id]/[id].pdf"
   ```

2. Ler hash anterior em `registry/integrity.json`:
   ```json
   { "[slug]": { "sha1": "abc123...", "checked": "2026-03-01", "size": 234567 } }
   ```

3. Re-descarregar o PDF da URL original para ficheiro temporario:
   ```bash
   curl -sL "[pdf_url]" -o "/tmp/[id]-check.pdf"
   sha1sum "/tmp/[id]-check.pdf"
   ```

4. Comparar hashes:
   - **Iguais:** regulamento inalterado. Actualizar `checked` em integrity.json. Continuar.
   - **Diferentes:** regulamento foi alterado (adenda, revisão, nova versão).
     - Marcar item no shard com `needs_review: true`, `review_reason: "Hash do PDF mudou desde [data anterior]. Possível adenda/revisão do regulamento."`
     - Guardar nova versão do PDF: `[id]-v[data].pdf` (manter histórico)
     - Actualizar `registry/integrity.json` com novo hash
     - **NAO reescrever o artigo automaticamente.** Writer revisa manualmente na próxima batch.

5. Se URL do PDF não responde:
   - Marcar `needs_review: true`, `review_reason: "PDF original inacessivel"`
   - Não apagar PDF local (manter conteudo editorial)

**Limite:** max 10 verificacoes de integridade por run (são pesadas - curl + sha1sum). Rodar entre os items do shard seleccionado.

---

## PASSO 2.6: Re-verificar watchlist (queue-plano-anual.json)

**MUDANCA v4.1:** Ler `registry/queue-plano-anual.json` (não `lookup.json`). Contem items detectados como Plano Anual pelo downloader que podem ter aberto entretanto.

**MUDANCA v4.2 (2026-05-05):** Items com `paa_status: "published_externamente"` (sinalizados pelo scanner v4.8 PASSO 3.6 via news post) são DESCONSIDERADOS pelo monitor. Razão: já sabemos que o aviso real foi publicado externamente, mas o portal do PAA continua stuck no placeholder. Re-verificar via TESTE A no PDF do PAA seria desperdício (vai sempre falhar). Estes items ficam na watchlist como sinalizados para revisão manual; o monitor não tenta promovê-los.

**Max 10 items por run** (duplicou vs v4.0, dado que agora existe ficheiro dedicado).

### POLITICA DE COBERTURA MINIMA (v4.3, 2026-05-09)

**Problema detectado:** auditoria a 2026-05-09 revelou que 65% dos items da watchlist (85 de 131) tinham `plano_anual_checks: 0`, ou seja nunca tinham sido revisitados. Items entram e ficam parados.

**Regra de cobertura:**

1. **Floor obrigatorio:** o monitor DEVE verificar pelo menos **5 items por run** com `plano_anual_checks: 0` (nunca verificados antes), se existirem. Estes contam dentro do limite de 10.
2. **Ordem dentro deste floor:** `priority_score` descendente, depois `detected_date` ascendente (mais antigos primeiro).
3. **Slots restantes (max 5):** seguir a ordem de seleção normal abaixo.
4. **Cobertura completa garantida:** com este floor, uma watchlist de 131 items e revisitada por inteiro em ~26 runs (2-3 semanas a um run/dia). Antes desta regra, eram precisos ~6 meses ou mais.
5. **Auto-archive (proteccao contra acumulacao):** items com `plano_anual_checks >= 8` E sem mudanca em nenhuma das verificacoes E `detected_date` ha mais de 180 dias devem ser movidos para `registry/queue-plano-anual-archive.json`. Saem da watchlist activa. Continuam acessiveis para auditoria mas não consomem slots.

**Ordem de seleção (ordem normal, aplicada DEPOIS do floor):**
1. **Filtrar primeiro:** items com `paa_status == "published_externamente"` são EXCLUÍDOS desta seleção (desconsiderados pelo monitor)
2. Items com `plano_anual_last_check` mais antigo (ou sem check ainda)
3. Em caso de empate: items com `priority_score` mais alto
4. Ignorar items já verificados ha menos de 7 dias

Para cada item na watchlist (apenas items `paa_status == "planejado"` ou ausente):
1. Verificar na API da fonte se o aviso já tem regulamento publicado
2. Para fontes PT2030 com API WordPress: `GET https://[portal]/wp-json/wp/v2/aviso-2024?slug=[id]` e verificar se `acf.pdf` agora aponta para regulamento real. Descarregar PDF rapidamente (1-2 paginas) e correr TESTE A (PAA detection).
3. Para outras fontes: WebFetch na URL e verificar se ha PDF de regulamento

### Se o aviso abriu (PDF existe E passa TESTE A - não e PAA):
1. **Verificar primeiro** se o `id` já existe em `queue.json`:
   ```python
   existing_ids = [q['id'] for q in queue_json['queue']]
   if item_id in existing_ids:
       # Já esta em queue - apenas remover de plano_anual, não duplicar
       # Reportar: "Watchlist: [id] já existia em queue.json - removido da watchlist (sem duplicar)"
       pass
   else:
       # Adicionar a queue.json normalmente
   ```
2. **Remover** item de `queue-plano-anual.json` (independentemente do resultado acima)
3. **So se não existia em queue.json:** adicionar com `"status": "pending"`, `"fail_count": 0`, limpar `download_error`
4. O downloader ira processa-lo na próxima run normalmente
5. Reportar: "Watchlist: [id] abriu - movido para queue.json como pending" (ou "já existia em queue.json - watchlist limpa")

### Se continua como plano anual:
1. Atualizar apenas `plano_anual_last_check: "[data]"` e incrementar `plano_anual_checks` no item
2. Não fazer mais nada

### Se o aviso foi removido/cancelado (URL 404 + não encontrado via WebSearch):
1. Atualizar item com `plano_anual_last_check: "[data]"`, `plano_anual_status: "url_removed"`, incrementar `plano_anual_checks`
2. **Após 10 checks sem sucesso** (cerca de 10 semanas de verificacoes): mover item para `queue-plano-anual-archived.json` (criar se não existir). Não eliminar - preservar para auditoria.

**Nota importante:** Nunca remover o item de `lookup.json` (secções `by_id` e `by_aviso_codigo`) mesmo se for arquivado. Isto garante que o scanner não o re-detete.

---

## PASSO 2.7: Cross-portal matching para PAAs com data_inicio passada (v4.11, 2026-05-11)

**Contexto:** o portal central `portugal-2030` publica entries previsionais (PAA summaries). Quando o aviso real abre, é frequentemente publicado nos portais REGIONAIS sob código diferente (e.g., FA0263 central = PACS-2026-07 sustentavel). O PASSO 2.6 verifica se o central atualizou o PAA para regulamento real, mas isto frequentemente NUNCA acontece. Este passo procura o aviso real nos portais regionais.

**Aplicável a:** items em `queue-plano-anual.json` onde:
- `source_id` está na **FAMILIA_PT2030** (qualquer dos 11 portais: portugal-2030, compete-2030, norte-2030, centro-2030, lisboa-2030, alentejo-2030, algarve-2030, pessoas-2030, sustentavel-2030, madeira-2030, acores-2030)
- `data_inicio < hoje` (aviso teoricamente já abriu segundo PAA forecast)
- `plano_anual_checks >= 1` (PASSO 2.6 já tentou via fonte original pelo menos 1 vez sem sucesso)
- `data_status != "expired_unrealized"` (não retentar items já dados como falhados)

### Priorização inteligente (v4.13, 2026-05-12)

Ordenar elegíveis para maximizar probabilidade de sucesso (cap=15/run):

**Tier 1 (alta probabilidade):** items onde há SINAL real de publicação
- Existe news post no portal regional mencionando o aviso (campo `news_post_url` populado)
- Items previamente `verified` cujo regulamento se perdeu
- Items com `last_websearch_attempt` mais antigo (>=7 dias) E poucos `websearch_attempts` (<3)

**Tier 2 (média probabilidade):** items "típicos"
- Items sem sinais especiais, com cooldown respeitado

**Tier 3 (baixa probabilidade — não priorizar mas não excluir):**
- Items com 3+ `websearch_attempts` sem sucesso (provável que regulamento real não exista)
- Items com `data_fim` próxima de expirar (vão entrar em `expired_unrealized` em breve)

**Exclusões obrigatórias:**
- Items com `data_status: "expired_unrealized"` → não retentar
- Items com `chrome_fail_count >= 3` (se aplicável)
- Items em `registry/depublished.json` (regra 0 v4.12.1)
- Items com cooldown ativo (`last_websearch_attempt` < 7 dias)

### Estratégia de matching (v4.12.1, 2026-05-12 — REFORÇADO)

⚠️ **REGRAS BLOQUEANTES (aplicar SEMPRE):**

0. **Verificar `registry/depublished.json`:** se `item.codigo_api` ou `item.id` está na lista de depublicados, **REMOVER da watchlist sem promoção**. Item foi despublicado editorialmente; não voltar a processar.

1. **`human_code` tem formato canónico:** apenas valores que correspondam a regex `^([A-Z]+2030-\d{4}-\d+|PACS-\d{4}-\d+)$`. **NUNCA aceitar FA codes (`FAxxxx/YYYY`) como human_code** — são `codigo_api`, não humano.

2. **Promoção EXIGE regulation_url válida:** se não houver URL HTTP descarregável NEM acesso a campo `aviso` da API regional Tipo A, **NÃO PROMOVER**. Item fica em watchlist.

3. **`matched_portal` NUNCA pode ser `portugal-2030`:** o portal central é Tipo B (só serve PAAs). Match no central é redundante (mesmo PAA do qual o item veio). **Excluir explicitamente portugal-2030 dos candidatos a match.**

4. **`matched_portal` NUNCA pode ser igual a `original_portal`:** procurar o aviso onde já falhou não traz informação nova.

**Ordem de tentativa (parar no primeiro sucesso que respeite as regras acima):**

1. **Match por `human_code` (preferencial):**
   - Se item tem `human_code` populado e válido (formato canónico)
   - Procurar APENAS nos portais REGIONAIS (excluir portugal-2030 central)
   - Procurar items cujo `acf.codigo` corresponda ao human_code OU cujo título contenha o human_code
   - Match exato no human_code = alta confiança editorial

2. **Match por `aviso` field em sustentavel-2030 (Tipo A):**
   - sustentavel-2030 expõe campo `aviso` com URL direta para regulamento real
   - Procurar items em sustentavel-2030 com title similarity >= 85% ao item da watchlist
   - Se hit: confirmar que `aviso` field está preenchido + descarregar para validar não-PAA

3. **Match por title similarity nos REGIONAIS (FALLBACK):**
   - >= 85% similarity via SequenceMatcher
   - APENAS nos portais regionais Tipo B com PDF que passe TESTE A (não-PAA)
   - Validar antes de promover: HEAD request no PDF, GET, pdftotext, TESTE A

⚠️ **VALIDAÇÃO PRÉ-PROMOÇÃO (obrigatória antes de mover para queue):**
- Item promovido DEVE ter `regulation_url` HTTP válida (não `'-'`, não ID numérico, não vazio)
- Item promovido DEVE ter texto-fonte que **não dispare TESTE A** (não-PAA)
- Item promovido DEVE ter `cross_portal_match.matched_portal != "portugal-2030"`
- Se qualquer falha: **não promover**, deixar em watchlist com `plano_anual_last_check` atualizado

**Razão das regras estritas (v4.12.1):**
Em 2026-05-12, primeira execução do v4.12 PASSO 2.7 promoveu 12 items para a queue com:
- human_code populado erradamente com FA codes
- matched_portal = portugal-2030 (central, mesmo PAA do qual vieram)
- regulation_url vazio
Resultado: items voltariam ao ciclo no próximo downloader e seriam redirecionados para watchlist. Loop. As regras acima fecham essa brecha.

---

### Estratégia 4: WebSearch no portal central (v4.12.2, 2026-05-12)

Após esgotar matching nos portais regionais (estratégias 1-3), aplicar a estratégia que o downloader usa em `PASSO 2b-portal-central`: procurar o regulamento real publicado em `portugal2030.pt/wp-content/uploads/sites/3/YYYY/MM/[CODIGO_HUMANO].pdf` via WebSearch.

**Por que faz sentido no monitor (não duplica downloader):**

- Items em watchlist NÃO são tocados pelo downloader (só itens em queue.json)
- Items em watchlist são exatamente aqueles onde a tentativa anterior falhou
- Mas o tempo passa: AGs podem ter publicado o regulamento entretanto
- Esta estratégia dá uma re-tentativa periódica

**Cooldown obrigatório (cap de custo):**

Cada item tem campo `last_websearch_attempt: YYYY-MM-DD`. WebSearch para um item só corre se:
- Campo está vazio (nunca tentado), OU
- Passaram **>= 7 dias** desde `last_websearch_attempt`

Isto evita repetir WebSearch para o mesmo item todos os dias.

**Seleção dos 15 items/run:**

Ordem de prioridade (parar quando 15 selecionados):
1. Items sem `last_websearch_attempt` (nunca tentaram)
2. Items com `last_websearch_attempt` mais antigo (>= 7 dias)
3. Skip items com tentativa < 7 dias

**Algoritmo da Estratégia 4:**

```python
from datetime import date, timedelta

today = date.today()
cooldown = timedelta(days=7)

# Filtrar elegíveis
eligible = []
for item in watchlist:
    if item.source_id not in FAMILIA_PT2030: continue
    if item.id in DEPUBLISHED_SLUGS: continue
    last_attempt = parse_date(item.get('last_websearch_attempt'))
    if last_attempt and (today - last_attempt) < cooldown:
        continue
    eligible.append(item)

# Ordenar: nunca tentado primeiro, depois mais antigo
eligible.sort(key=lambda i: (
    bool(i.get('last_websearch_attempt')),  # False (nunca) primeiro
    i.get('last_websearch_attempt', '0000-01-01'),  # mais antigo primeiro
))

# Processar até 15
for item in eligible[:15]:
    titulo = item.get('name', '')[:60]
    programa = item.get('programa_code', '')
    if not programa:
        # Skip se programa_code não definido
        continue

    # WebSearch refinada
    query = f'site:portugal2030.pt "{titulo[:40]}" "{programa}" filetype:pdf'
    results = WebSearch(query)

    found = False
    for url in results[:5]:
        if not url.endswith('.pdf'): continue
        # HEAD + GET + pdftotext
        pdf_bytes = curl_download(url)
        text = pdftotext(pdf_bytes)

        # Validar não-PAA
        if 'plano anual' in text.lower() or 'resumo de aviso' in text.lower():
            continue
        if len(text.split()) < 1500:
            continue

        # Extrair human_code do PDF
        match = re.search(
            r'(?i)C[oó]digo\s+do\s+aviso\s*:?\s*'
            r'([A-Z][A-ZÇÊÁÍÓ]+2030-\d{4}-\d+|PACS-\d{4}-\d+)',
            text
        )
        if match:
            human_code = normalize_human(match.group(1))
            # Validar similaridade titulo
            if title_similarity(titulo, extract_pdf_title(text)) < 0.6:
                continue

            # PROMOÇÃO LEGÍTIMA - todas as 5 regras v4.12.1 respeitadas:
            # 0. Não está em depublished
            # 1. human_code formato canónico (passou regex)
            # 2. regulation_url HTTP válida
            # 3. matched_portal seria portugal-2030, MAS este é um caso especial:
            #    estamos a usar central como FONTE do regulamento (não como portal de match)
            #    Por isso a regra 3 não se aplica aqui — registar como match_method especial.
            # 4. matched_portal != original_portal (sempre verdade aqui)

            item.human_code = human_code
            item.regulation_url = url
            item.cross_portal_match = {
                'original_codigo': item.codigo_api,
                'original_portal': item.source_id,
                'matched_portal': 'portugal-2030-central-uploads',  # SEMÂNTICA distinta
                'matched_human_code': human_code,
                'match_method': 'websearch_central_uploads',
                'matched_at': today.isoformat(),
            }
            # Atualizar lookup
            lookup.by_human_code[human_code] = item.id
            # Mover para queue.json
            queue.append(item)
            watchlist.remove(item)
            save(queue.json, watchlist.json, lookup.json)
            found = True
            break

    # Marcar tentativa (independente de sucesso ou falha)
    if not found:
        item.last_websearch_attempt = today.isoformat()
        # incrementar contador
        item.websearch_attempts = (item.get('websearch_attempts', 0) or 0) + 1
        save(watchlist.json)
```

**Nota sobre regra 3 (matched_portal != portugal-2030):**

A regra v4.12.1 proibia `matched_portal == 'portugal-2030'` porque na 1ª execução o agente estava a fazer match no central API JSON (Tipo B, mesmo PAA do qual o item veio — redundante).

A Estratégia 4 é diferente: usa o **portal central como FONTE de PDFs publicados** (não como portal de match JSON). Os PDFs em `portugal2030.pt/wp-content/uploads/sites/3/...` são **regulamentos reais**, não os PAAs da API JSON.

Para distinguir semanticamente, usar `matched_portal: "portugal-2030-central-uploads"` (string distinta de `"portugal-2030"`). A regra 3 continua a proibir `"portugal-2030"` puro mas permite a variante uploads.

**Reporting:**

```
PASSO 2.7 Estratégia 4 (WebSearch central uploads):
  Items elegíveis (cooldown OK): N
  Items processados (até 15): M
  Sucessos (promoção legítima): K
  Falhas (nenhum PDF válido encontrado): M - K
  Items com 5+ websearch_attempts sem sucesso: lista para revisão manual
```

**Após 5 tentativas sem sucesso (35+ dias), recomendar revisão manual:** o aviso pode ter sido cancelado, ou ter código humano formato não-padronizado.

⚠️ **CRÍTICO (correção 2026-05-12):** o critério inicial v4.11 limitava-se a `source_id == "portugal-2030"`, o que excluía a maioria da watchlist (items já com source regional). Agora aceita TODA a família PT2030 — quando o portal original deu PAA, tenta encontrar correspondência nos OUTROS 10 portais regionais.

**Algoritmo:**

```python
FAMILIA_PT2030 = {
    'portugal-2030', 'compete-2030', 'norte-2030', 'centro-2030',
    'lisboa-2030', 'alentejo-2030', 'algarve-2030', 'pessoas-2030',
    'sustentavel-2030', 'madeira-2030', 'acores-2030', 'pat-2030',
}

# 1. Identificar portais regionais CANDIDATOS (excluindo o source atual)
PROGRAM_TO_PORTAL = {
    'COMPETE':    'compete-2030',
    'PESSOAS':    'pessoas-2030',
    'NORTE':      'norte-2030',
    'CENTRO':     'centro-2030',
    'LISBOA':     'lisboa-2030',
    'ALENTEJO':   'alentejo-2030',
    'ALGARVE':    'algarve-2030',
    'ACORES':     'acores-2030',
    'MADEIRA':    'madeira-2030',
    'MAR':        'mar-2030',
    'SUSTENTAVEL':'sustentavel-2030',
    'PAT':        'pat-2030',
}

source_atual = item.get('source_id', '')
# Preferir lista pre-calculada se existir
portais_pre = item.get('regional_portals', [])
# Fallback: derivar de programa
programas = item.get('programa') or item.get('acf_programa', []) or []
if isinstance(programas, str): programas = [programas]
portais_candidatos = list(portais_pre)
if not portais_candidatos:
    for p in programas:
        for key, portal in PROGRAM_TO_PORTAL.items():
            if key in str(p).upper():
                portais_candidatos.append(portal)
portais_candidatos = list(set(portais_candidatos))
# Excluir o próprio source (não procurar onde já falhou)
portais_candidatos = [p for p in portais_candidatos if p != source_atual]
# Último recurso: se nenhum candidato derivado, tentar TODOS os regionais
if not portais_candidatos:
    portais_candidatos = [p for p in FAMILIA_PT2030 if p != source_atual and p != 'portugal-2030']

# 2. Para cada portal candidato, fetch da API e procurar match
for portal_id in portais_candidatos:
    portal_cfg = sources_scan[portal_id]
    api_url = portal_cfg.get('api_url') or portal_cfg.get('url')
    if not api_url: continue

    avisos = fetch_api(api_url, per_page=100, all_pages=True)

    # 3. Title fuzzy match (>= 85% similaridade)
    for av in avisos:
        title_regional = av['title']['rendered']
        similaridade = title_similarity(item['name'], title_regional)
        if similaridade >= 0.85:
            # MATCH ENCONTRADO
            match_aviso = av
            match_portal = portal_id
            break
    if match_aviso: break

# 4. Se match encontrado, promover para queue.json com dados regionais
if match_aviso:
    novo_item = construir_item_a_partir_de_aviso(match_aviso, match_portal)
    novo_item['priority_score'] = recompute_score_v4_11(novo_item)  # 500+
    novo_item['cross_portal_match'] = {
        'original_codigo': item['aviso_codigo'],
        'original_portal': item['source_id'],
        'matched_portal': match_portal,
        'matched_codigo': match_aviso['acf']['codigo'],
        'title_similarity': similaridade,
    }
    queue.append(novo_item)
    save(queue.json)
    # remover da watchlist (ordem crítica: queue primeiro)
    queue_plano_anual.queue.remove(item)
    save(queue_plano_anual.json)
    log(f'cross-portal match: {item.aviso_codigo} (central) -> {match_aviso.acf.codigo} ({match_portal})')

# 5. Se nenhum match após verificar todos os candidatos:
#    Apenas incrementar plano_anual_checks (comportamento normal do 2.6)
```

**Função `title_similarity`:**
```python
def title_similarity(a: str, b: str) -> float:
    """Levenshtein-based similarity normalizada [0,1]. Strip HTML entities
    primeiro (e.g., &#8211; -> -)."""
    from html import unescape
    import re
    a = re.sub(r'\s+', ' ', unescape(a).lower().strip())
    b = re.sub(r'\s+', ' ', unescape(b).lower().strip())
    # implementação Levenshtein normalizada ou difflib.SequenceMatcher
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()
```

**Limites por run (v4.11.2, 2026-05-12):**
- Cross-portal matching aplica-se a no máximo **15 items por run** (custo: 15 × ~9 fetches API + similarity checks, ~135 curls total, sem custo LLM)
- Items elegíveis ordenados por priority_score desc (PT2030 com 500+ vão primeiro)
- Com 100+ PAAs em watchlist, este cap garante ciclo completo de cobertura em ~7 dias (vs 20 dias com cap 5)

**Salvaguardas:**
- Threshold mínimo 85% para evitar falsos positivos
- Se múltiplos matches >= 85%, escolher o de maior similarity
- Se programa não mapear para nenhum portal regional (e.g., apenas "PT2030" genérico), pular item

**Relatório no final do monitor run:**
```
Cross-portal matching (PASSO 2.7):
  Items elegíveis: N (PAAs com data_inicio passada)
  Items processados: min(N, 5)
  Matches encontrados: M
  Promovidos para queue: M (com cross_portal_match preenchido)
  Sem match: N - M (permanecem na watchlist)
```

---

## PASSO 3: Registar alteracoes

### Se estado mudou (aberto -> fechado) - regime aviso apenas:

1. Atualizar item no shard:
```json
{ "state": "fechado", "last_check": "2026-04-16" }
```

2. Atualizar o artigo HTML:
- Hero meta-bar: alterar estado e classe CSS (`status-open` -> `status-closed`)
- Sidebar "Factos Rapidos": atualizar estado
- Adicionar aviso de encerramento no topo:
```html
<div class="instrument-closed-notice">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9A96E" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="0.5" fill="#C9A96E"/></svg>
  <span>Este instrumento encontra-se <strong>encerrado</strong>. As candidaturas já não estao abertas.</span>
</div>
```

3. Atualizar catálogo (`instruments-catalog.json`):
- `"estado": "fechado"`, `"status_text": "Fechado"`, `"status_class": "status-closed"`

### Se prazo mudou - regime aviso apenas:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catálogo (`status_text` com nova data)

### Se dotacao mudou - regime aviso apenas:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catálogo (`highlight0` ou `highlight1` com novo valor)

### Se integridade mudou (hash diferente) - regime aviso apenas:

1. Marcar `needs_review: true` no item do shard com `review_reason`
2. **NAO alterar artigo HTML.** O writer revisa manualmente.
3. Reportar no commit message: "monitor: [N] items com needs_review (adenda ou revisão)"

### Se link rot - regime catálogo apenas:

1. Marcar `needs_review: true` no item do shard com `review_reason`
2. Se foi redirect 301/302 para URL válido: actualizar `regulation_url` no shard
3. Não alterar artigo HTML

### Se nada mudou:

Apenas atualizar `last_check` no shard.

---

## PASSO 4: Atualizar index.json e integrity.json

Após processar o shard:
1. Recalcular contadores do shard (open, closed, planned)
2. Recalcular totais globais
3. Atualizar `last_monitor_run`
4. Guardar `registry/integrity.json` com novos hashes (apenas regime aviso)

---

## PASSO 5: Deploy

```bash
git -C "$REPO" add registry/index.json registry/shards/[shard].json registry/integrity.json instruments-catalog.json registry/lookup.json registry/queue.json registry/queue-plano-anual.json
# Se foi criado ficheiro de arquivo:
git -C "$REPO" add registry/queue-plano-anual-archived.json 2>/dev/null || true
# Se artigos foram alterados (estado/prazo/dotacao):
git -C "$REPO" add instrumentos/[slug1].html instrumentos/[slug2].html
git -C "$REPO" commit -m "monitor: [shard] - [N verificados], [N alteracoes], [N needs_review], [N promovidos do plano_anual]"
git -C "$REPO" push origin main
```

Se ha items com `needs_review: true`, mencionar explicitamente no commit para o writer ver na próxima batch.

---

## REGRAS DE SEGURANCA

1. **Nunca ler todos os shards de uma vez.** Max 1-2 por run.
2. **Nunca reescrever conteudo editorial automaticamente.** So alterar estado, prazo, dotacao (alteracoes factuais diretas da fonte) e aviso de encerramento.
3. **Nunca reescrever artigo quando integrity hash muda.** Marcar needs_review. Writer revisa.
4. **Nunca remover entradas de instruments-catalog.json.** So atualizar estado/prazo/dotacao.
5. **Nunca verificar estado ou prazo em shards catálogo.** So link rot.
6. **Se WebFetch falhar para uma fonte:** registar e continuar. Não parar.
7. **Instrumentos "fechado" raramente mudam.** Verificar 1 por cada 5 abertos.
8. **Nunca duplicar items em queue.json.** Antes de promover da watchlist, verificar sempre se o id já existe. Se existir, apenas remover da watchlist (sem adicionar novamente).

---

## RESUMO

```
1. Ler index.json + integrity.json
2. Selecionar 1-2 shards (antigos ou com deadlines próximos)
3. Ler shard(s) selecionado(s)

Regime "aviso":
  4a. Verificar estado/prazo/dotacao por lotes via super-fonte
  4b. Verificar integridade (hash SHA1 de PDFs) - max 10 por run
  4c. Se alteracao factual: atualizar shard + artigo + catálogo
  4d. Se hash mudou: needs_review (sem reescrever artigo)

Regime "catálogo":
  4a. Link rot apenas (HEAD/GET aos URLs)
  4b. Se 404/410: needs_review
  4c. Se 301/302: actualizar regulation_url

5. Re-verificar até 10 items da watchlist plano_anual (queue-plano-anual.json)
   - Se PDF real disponível: promover para queue.json como pending
   - Se ainda PAA: incrementar plano_anual_checks, atualizar plano_anual_last_check
   - Se 10+ checks falhados: arquivar em queue-plano-anual-archived.json
6. Atualizar index.json + integrity.json
7. git commit + push
8. Reportar: "Monitor: [shard] - [N verificados], [N alteracoes], [N needs_review], [N promovidos do plano_anual]."
```
