# Radar Monitor v4.1: Verificacao de Estados e Integridade

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o monitor do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e verificar se instrumentos publicados mudaram de estado, prazo, dotacao ou conteudo do regulamento.

**Esta skill so monitoriza.** Nao descobre instrumentos, nao descarrega regulamentos, nao cria artigos.

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
| `registry/index.json` | Sempre (para decidir que shard verificar) |
| `registry/shards/[shard].json` | 1-2 shards por run |
| `registry/integrity.json` | Sempre (hashes de PDFs dos regulamentos) |
| `registry/queue-plano-anual.json` | Sempre (watchlist de PAAs - Passo 2.6) |
| `registry/queue.json` | Ler para promocao de PAAs que abriram |
| `sources-scan.json` | Para access_method e regime das fontes |

**NAO ler todos os shards.** Ler apenas o(s) shard(s) a verificar nesta run.

**MUDANCA v4.1 (2026-04-17):** A watchlist de PAAs migrou de `lookup.json > plano_anual` para ficheiro dedicado `queue-plano-anual.json`. Capacidade duplicada (10 items/run vs 5).

---

## SEPARACAO CRITICA POR REGIME

O monitor actua de forma DIFERENTE consoante o regime da fonte do item:

### Regime "aviso" (shards: pt2030-*, eu-*, eic, interreg, pt-other)
- Verifica **estado** (aberto/fechado/previsto)
- Verifica **prazo** (data_fim)
- Verifica **dotacao** (budget)
- Verifica **integridade do regulamento** (SHA1 hash do PDF - detecta adendas)

### Regime "catalogo" (shards: catalogo-bancos, catalogo-vc, catalogo-premios, catalogo-aceleradores)
- **NAO verifica estado.** Produtos bancarios, fundos VC e aceleradores operam em candidatura continua. Assumir sempre "aberto" (status "cont").
- **NAO verifica prazo** (nao existe deadline formal).
- Verifica **link rot** apenas: URL continua a responder 200?
- Se pagina foi removida ou redireccionada: marcar `needs_review: true` no shard.

---

## PASSO 1: Selecionar shard a verificar

Ler `registry/index.json`. Selecionar **1-2 shards** por run, priorizando:

1. Shards com mais items "aberto" ou "previsto" (regime aviso)
2. Shards cujas fontes nao foram verificadas ha mais tempo
3. Shards com deadlines proximos (< 30 dias) - so regime aviso
4. Shards catalogo verificados ha > 90 dias (rotacao trimestral)

**Smart scheduling por risco (regime aviso):**
- Items com deadline < 30 dias: verificar sempre
- Items com deadline < 90 dias: verificar a cada 3 runs
- Items com deadline > 90 dias: verificar a cada 10 runs
- Items "fechado": verificar 1 por cada 5 abertos (para confirmar se reabriram)

**Smart scheduling regime catalogo:**
- Items catalogo: verificar 1 vez por trimestre (link rot apenas)

---

## PASSO 2: Verificar por lotes via super-fonte

### 2.A - Shards de regime "aviso" - verificacao completa

Verificar **fonte a fonte** em vez de instrumento a instrumento:

#### Para shards PT2030:

```
WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?page=1
(percorrer todas as paginas)
```

Um unico ciclo de WebFetch retorna todos os avisos da API central. Comparar com os items no shard:
- Para cada item do shard, procurar o aviso correspondente na API (por aviso_codigo ou titulo)
- Verificar: estado mudou? prazo mudou? dotacao mudou?

#### Para portais regionais PT2030 (centro-2030, lisboa-2030, alentejo-2030, etc.):

Portais com WordPress API (ver `api_url` em sources-scan.json): usar a API directamente.
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

### 2.B - Shards catalogo - link rot apenas

Para cada item no shard catalogo, fazer HEAD request ao `regulation_url` (ou GET leve via WebFetch):

```bash
curl -sI "[regulation_url]" -o /dev/null -w "%{http_code}"
```

- Se retorna 200: OK, actualizar `last_check` no shard
- Se retorna 404/410 (removido): marcar `needs_review: true` no shard, `review_reason: "URL removida (HTTP [codigo])"`
- Se retorna 301/302 (redirect): seguir redirect, se destino final OK, actualizar `regulation_url` no shard. Se destino tambem 404: marcar needs_review
- Se retorna 403/500/timeout: nao alterar (pode ser erro transitorio), tentar na proxima run

**Nunca reescrever artigos de catalogo automaticamente.** So marcar needs_review.

---

## PASSO 2.5: Verificacao de integridade do regulamento (APENAS regime aviso)

**Objectivo:** detectar adendas, alteracoes ou novas versoes de regulamentos que normalmente sao publicadas sob o mesmo aviso_codigo mas com conteudo diferente. Um regulamento alterado pode mudar dotacao, beneficiarios, criterios - afectando o artigo.

**Este passo NAO se aplica a regime catalogo.** Saltar.

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
   - **Diferentes:** regulamento foi alterado (adenda, revisao, nova versao).
     - Marcar item no shard com `needs_review: true`, `review_reason: "Hash do PDF mudou desde [data anterior]. Possivel adenda/revisao do regulamento."`
     - Guardar nova versao do PDF: `[id]-v[data].pdf` (manter historico)
     - Actualizar `registry/integrity.json` com novo hash
     - **NAO reescrever o artigo automaticamente.** Writer revisa manualmente na proxima batch.

5. Se URL do PDF nao responde:
   - Marcar `needs_review: true`, `review_reason: "PDF original inacessivel"`
   - Nao apagar PDF local (manter conteudo editorial)

**Limite:** max 10 verificacoes de integridade por run (sao pesadas - curl + sha1sum). Rodar entre os items do shard seleccionado.

---

## PASSO 2.6: Re-verificar watchlist (queue-plano-anual.json)

**MUDANCA v4.1:** Ler `registry/queue-plano-anual.json` (nao `lookup.json`). Contem items detectados como Plano Anual pelo downloader que podem ter aberto entretanto.

**Max 10 items por run** (duplicou vs v4.0, dado que agora existe ficheiro dedicado).

**Ordem de selecao:**
1. Items com `plano_anual_last_check` mais antigo (ou sem check ainda)
2. Em caso de empate: items com `priority_score` mais alto
3. Ignorar items ja verificados ha menos de 7 dias

Para cada item na watchlist:
1. Verificar na API da fonte se o aviso ja tem regulamento publicado
2. Para fontes PT2030 com API WordPress: `GET https://[portal]/wp-json/wp/v2/aviso-2024?slug=[id]` e verificar se `acf.pdf` agora aponta para regulamento real. Descarregar PDF rapidamente (1-2 paginas) e correr TESTE A (PAA detection).
3. Para outras fontes: WebFetch na URL e verificar se ha PDF de regulamento

### Se o aviso abriu (PDF existe E passa TESTE A - nao e PAA):
1. **Remover** item de `queue-plano-anual.json`
2. **Adicionar** a `queue.json` com `"status": "pending"`, `"fail_count": 0`, limpar `download_error`
3. O downloader ira processa-lo na proxima run normalmente
4. Reportar: "Watchlist: [id] abriu - movido para queue.json como pending"

### Se continua como plano anual:
1. Atualizar apenas `plano_anual_last_check: "[data]"` e incrementar `plano_anual_checks` no item
2. Nao fazer mais nada

### Se o aviso foi removido/cancelado (URL 404 + nao encontrado via WebSearch):
1. Atualizar item com `plano_anual_last_check: "[data]"`, `plano_anual_status: "url_removed"`, incrementar `plano_anual_checks`
2. **Apos 10 checks sem sucesso** (cerca de 10 semanas de verificacoes): mover item para `queue-plano-anual-archived.json` (criar se nao existir). Nao eliminar - preservar para auditoria.

**Nota importante:** Nunca remover o item de `lookup.json` (seccoes `by_id` e `by_aviso_codigo`) mesmo se for arquivado. Isto garante que o scanner nao o re-detete.

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
  <span>Este instrumento encontra-se <strong>encerrado</strong>. As candidaturas ja nao estao abertas.</span>
</div>
```

3. Atualizar catalogo (`instruments-catalog.json`):
- `"estado": "fechado"`, `"status_text": "Fechado"`, `"status_class": "status-closed"`

### Se prazo mudou - regime aviso apenas:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catalogo (`status_text` com nova data)

### Se dotacao mudou - regime aviso apenas:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catalogo (`highlight0` ou `highlight1` com novo valor)

### Se integridade mudou (hash diferente) - regime aviso apenas:

1. Marcar `needs_review: true` no item do shard com `review_reason`
2. **NAO alterar artigo HTML.** O writer revisa manualmente.
3. Reportar no commit message: "monitor: [N] items com needs_review (adenda ou revisao)"

### Se link rot - regime catalogo apenas:

1. Marcar `needs_review: true` no item do shard com `review_reason`
2. Se foi redirect 301/302 para URL valido: actualizar `regulation_url` no shard
3. Nao alterar artigo HTML

### Se nada mudou:

Apenas atualizar `last_check` no shard.

---

## PASSO 4: Atualizar index.json e integrity.json

Apos processar o shard:
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

Se ha items com `needs_review: true`, mencionar explicitamente no commit para o writer ver na proxima batch.

---

## REGRAS DE SEGURANCA

1. **Nunca ler todos os shards de uma vez.** Max 1-2 por run.
2. **Nunca reescrever conteudo editorial automaticamente.** So alterar estado, prazo, dotacao (alteracoes factuais directas da fonte) e aviso de encerramento.
3. **Nunca reescrever artigo quando integrity hash muda.** Marcar needs_review. Writer revisa.
4. **Nunca remover entradas de instruments-catalog.json.** So atualizar estado/prazo/dotacao.
5. **Nunca verificar estado ou prazo em shards catalogo.** So link rot.
6. **Se WebFetch falhar para uma fonte:** registar e continuar. Nao parar.
7. **Instrumentos "fechado" raramente mudam.** Verificar 1 por cada 5 abertos.

---

## RESUMO

```
1. Ler index.json + integrity.json
2. Selecionar 1-2 shards (antigos ou com deadlines proximos)
3. Ler shard(s) selecionado(s)

Regime "aviso":
  4a. Verificar estado/prazo/dotacao por lotes via super-fonte
  4b. Verificar integridade (hash SHA1 de PDFs) - max 10 por run
  4c. Se alteracao factual: atualizar shard + artigo + catalogo
  4d. Se hash mudou: needs_review (sem reescrever artigo)

Regime "catalogo":
  4a. Link rot apenas (HEAD/GET aos URLs)
  4b. Se 404/410: needs_review
  4c. Se 301/302: actualizar regulation_url

5. Re-verificar ate 10 items da watchlist plano_anual (queue-plano-anual.json)
   - Se PDF real disponivel: promover para queue.json como pending
   - Se ainda PAA: incrementar plano_anual_checks, atualizar plano_anual_last_check
   - Se 10+ checks falhados: arquivar em queue-plano-anual-archived.json
6. Atualizar index.json + integrity.json
7. git commit + push
8. Reportar: "Monitor: [shard] - [N verificados], [N alteracoes], [N needs_review], [N promovidos do plano_anual]."
```
