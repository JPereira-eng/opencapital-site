# Radar Monitor v4.0: Verificacao de Estados

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o monitor do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e verificar se instrumentos publicados mudaram de estado, prazo ou dotacao.

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

## FICHEIROS DE ESTADO (v4.0)

| Ficheiro | Quando ler |
|---|---|
| `registry/index.json` | Sempre (para decidir que shard verificar) |
| `registry/shards/[shard].json` | 1-2 shards por run |
| `sources-scan.json` | Para access_method das fontes |

**NAO ler todos os shards.** Ler apenas o(s) shard(s) a verificar nesta run.

---

## PASSO 1: Selecionar shard a verificar

Ler `registry/index.json`. Cada shard tem contadores. Selecionar **1-2 shards** por run, priorizando:

1. Shards com mais items "aberto" ou "previsto"
2. Shards cujas fontes nao foram verificadas ha mais tempo
3. Shards com instrumentos cujo deadline esta proximo (< 30 dias)

**Smart scheduling por risco:**
- Items com deadline < 30 dias: verificar sempre
- Items com deadline < 90 dias: verificar a cada 3 runs
- Items com deadline > 90 dias: verificar a cada 10 runs
- Items "fechado": verificar 1 por cada 5 abertos (para confirmar se reabriram)

---

## PASSO 2: Verificar por lotes via super-fonte

Em vez de verificar instrumento a instrumento, verificar **fonte a fonte**:

### Para shards PT2030:

```
WebFetch: https://portugal2030.pt/wp-json/wp/v2/aviso-2024?page=1
(percorrer todas as paginas)
```

Um unico ciclo de WebFetch retorna todos os avisos da API central. Comparar com os items no shard:
- Para cada item do shard, procurar o aviso correspondente na API (por aviso_codigo ou titulo)
- Verificar: estado mudou? prazo mudou? dotacao mudou?

### Para portais regionais PT2030 (centro-2030, lisboa-2030, alentejo-2030, etc.):

Portais com WordPress API (ver `api_url` em sources-scan.json): usar a API directamente.
```
WebFetch: https://centro2030.pt/wp-json/wp/v2/aviso-2024?page=1
WebFetch: https://lisboa.portugal2030.pt/wp-json/wp/v2/aviso-2024?page=1
```
Comparar `acf.data_fim`, `acf.df`, e estado com os dados do shard.

Portais sem API (norte-2030, compete-2030): usar WebFetch na pagina de concursos.
```
WebFetch: https://www.norte2030.pt/concursos/
WebFetch: https://www.compete2030.gov.pt/avisos
```
Procurar cada item do shard na pagina da fonte.

### Para shards EU:

```
WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{topic-id}.json
```

Verificar `actions[0].status.abbreviation` para cada item.

### Para pt-other:

Verificar cada item individualmente na sua fonte (WebFetch/Chrome/WebSearch).
Max 10 verificacoes individuais por run.

---

## PASSO 3: Registar alteracoes

### Se estado mudou (aberto -> fechado):

1. Atualizar item no shard:
```json
{ "state": "fechado", "last_check": "2026-04-12" }
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

### Se prazo mudou:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catalogo (`status_text` com nova data)

### Se dotacao mudou:

1. Atualizar item no shard
2. Atualizar artigo HTML (hero meta-bar + sidebar)
3. Atualizar catalogo (`highlight1` com novo valor)

### Se nada mudou:

Apenas atualizar `last_check` no shard.

---

## PASSO 4: Atualizar index.json

Apos processar o shard:
1. Recalcular contadores do shard (open, closed, planned)
2. Recalcular totais globais
3. Atualizar `last_monitor_run`

---

## PASSO 5: Deploy

```bash
git -C "$REPO" add registry/index.json registry/shards/[shard].json instruments-catalog.json
# Se artigos foram alterados:
git -C "$REPO" add instrumentos/[slug1].html instrumentos/[slug2].html
git -C "$REPO" commit -m "monitor: [shard] - [N verificados], [N alteracoes]"
git -C "$REPO" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca ler todos os shards de uma vez.** Max 1-2 por run.
2. **Nunca reescrever conteudo editorial.** So alterar estado, prazo, dotacao e aviso de encerramento.
3. **Nunca remover entradas de instruments-catalog.json.** So atualizar estado/prazo/dotacao.
4. **Se WebFetch falhar para uma fonte:** registar e continuar. Nao parar.
5. **Instrumentos "fechado" raramente mudam.** Verificar 1 por cada 5 abertos.

---

## RESUMO

```
1. Ler index.json
2. Selecionar 1-2 shards (o mais antigo ou com deadlines proximos)
3. Ler shard selecionado
4. Verificar por lotes via super-fonte (1 API call = muitos updates)
5. Se alteracoes: atualizar shard + artigo HTML + catalogo JSON
6. Atualizar index.json
7. git commit + push
8. Reportar: "Monitor: [shard] - [N verificados], [N alteracoes] ([detalhe])."
```
