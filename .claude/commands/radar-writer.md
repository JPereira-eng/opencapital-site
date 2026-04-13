# Radar Writer v4.0: Criacao de Artigos em Sprint

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o writer do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e criar artigos de instrumentos de financiamento a partir da fila.

**Esta skill so escreve artigos.** Nao descobre instrumentos, nao descarrega regulamentos, nao monitoriza estados.

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
| `registry/index.json` | Sempre |
| `registry/queue.json` | Sempre |
| `.claude/commands/instrumento.md` | **OBRIGATORIO antes de escrever** |

---

## PASSO 0.5: RECUPERACAO DE TRABALHO PENDENTE

**Antes de iniciar qualquer batch, verificar se ha commits locais nao enviados:**

```bash
LOCAL_AHEAD=$(git -C "$REPO" rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$LOCAL_AHEAD" -gt "0" ]; then
  echo "RECUPERACAO: $LOCAL_AHEAD commits locais pendentes. A enviar..."
  git -C "$REPO" push origin main
fi
```

Se o push falhar: `git -C "$REPO" pull --rebase origin main && git -C "$REPO" push origin main`

**Isto garante que artigos criados numa sessao anterior (que foi bloqueada por rate limit antes do push) sao publicados.**

---

## MODO SPRINT

O writer opera em **batches de 5 artigos**. Cada batch:
1. Seleciona 5 items da queue (ou menos se queue menor)
2. Cria os artigos, **commit apos cada artigo individual**
3. Push apos completar o batch (ou apos cada artigo se rate limit proximo)
4. Se queue ainda tem items E nao atingiu 20 artigos na sessao: inicia novo batch

**Limites por sessao:**
- Max 5 artigos por batch
- Max 4 batches por sessao = **20 artigos max**
- Se queue < 5: criar todos os que houver

**REGRA DE SEGURANCA: Commit por artigo.** Cada artigo criado e imediatamente commitado (sem push). O push acontece ao final do batch. Se o agente for bloqueado por rate limit entre artigos, o trabalho ja esta guardado localmente e sera enviado na proxima sessao (Passo 0.5).

---

## PASSO 1: Selecionar artigos

Ler `registry/queue.json`. Ordenar por `priority_score` descendente.

**Priorizar items com `status: "ready"`** (regulamento ja descarregado) sobre `status: "pending"`.

**IGNORAR completamente** items com `status: "plano_anual"` - sao previsoes do plano anual, nao avisos publicados. Nao contar, nao processar, nao remover da queue.

Selecionar os primeiros 5 (ou menos) para este batch.

**REGRA CRITICA - O QUE E "PUBLICADO":**
Um item esta publicado SE E SOMENTE SE existir o ficheiro `instrumentos/[id].html` no repositorio.
- Estar no `lookup.json` NAO significa publicado - o scanner adiciona ao lookup ao descobrir
- Estar num shard NAO e suficiente por si so - o ficheiro HTML tem de existir
- NUNCA remover um item da queue sem ter criado o ficheiro HTML correspondente
- NUNCA apagar a queue com base em "ja esta no lookup"

Se encontrares items na queue que ja tem o ficheiro HTML em `instrumentos/`: remover da queue (e apenas nesses casos).
Se encontrares items na queue que NAO tem ficheiro HTML: sao trabalho por fazer, manter na queue e escrever.

---

## PASSO 2: Ler template obrigatorio

**ANTES de escrever qualquer artigo:**
```
Read .claude/commands/instrumento.md
```

Este ficheiro contem o template HTML completo, classes CSS, estrutura da navbar, hero, sidebar e footer. NUNCA escrever sem ter lido.

---

## PASSO 3: Obter regulamento

Para cada artigo selecionado, seguir esta cascata:

1. **Se `regulation_local` existe:** Ler diretamente. Se > 3000 palavras: usar primeiras 3000.
2. **Se `regulation_local` e null mas `regulation_url` existe:** Usar WebFetch.
3. **Se tudo falhou:** Usar WebSearch + dados do campo `notes`. Artigos criados: 0 e sempre falha do agente.

---

## PASSO 4: Criar artigo

Com o regulamento, definir metadados:
- `slug`: kebab-case
- `nome_instrumento`: nome oficial
- `categoria_card`: `nr`, `priv`, `div`, `hib`, `fiscal`, ou `outros`
- `estado`: `aberto`, `fechado`, ou `previsto`
- `fonte`: codigo da fonte
- `beneficiario`: lista separada por virgulas (`empresa`, `entidade-publica`, `associacao`, `ensino-investigacao`, `empreendedor`)
- `regiao`: lista separada por virgulas

Criar `instrumentos/[slug].html` seguindo TODAS as regras do CLAUDE.md e do template instrumento.md.

---

## PASSO 5: Atualizar catalogo

Adicionar entrada ao FINAL de `instruments-catalog.json > instruments`:

```json
{
  "id": "[SLUG]",
  "category": "[CAT]",
  "category_label": "[LABEL]",
  "estado": "[ESTADO]",
  "status_text": "[TEXTO]",
  "status_class": "status-[open/closed/planned/cont]",
  "fonte": "[FONTE]",
  "beneficiario": "[BENEF]",
  "regiao": "[REGIAO]",
  "title": "[NOME]",
  "tagline": "[TAGLINE]",
  "highlight1": "[VALOR1]",
  "highlight2": "[VALOR2]",
  "href": "instrumentos/[SLUG].html",
  "featured": false
}
```

**REGRA CRITICA:** Nunca editar `solucoes.html`. Catalogo e 100% dinamico via JSON.

---

## PASSO 6: Atualizar estado

Para cada artigo criado:

1. **Remover da queue** (`registry/queue.json`)
2. **Adicionar ao shard** (`registry/shards/[shard].json`):
```json
{ "id": "[slug]", "file": "instrumentos/[slug].html", "source": "[source_id]", "state": "[estado]", "last_check": "[hoje]" }
```
3. **Adicionar ao lookup** (`registry/lookup.json`):
```json
"by_id": { "[slug]": true },
"by_aviso_codigo": { "[codigo]": "[slug]" }
```
4. **Atualizar index** (`registry/index.json`):
   - `totals.published` + N
   - `totals.in_queue` - N
   - `totals.[open/planned]` + N
   - Shard counters
   - `last_writer_run`: hoje

---

## PASSO 7: Deploy (commit por artigo, push por batch)

### 7a. Commit por artigo (apos cada artigo criado nos passos 4-6):

```bash
git -C "$REPO" add instrumentos/[slug].html instruments-catalog.json registry/
git -C "$REPO" commit -m "instrumento: [nome do instrumento]"
```

**Cada artigo tem o seu proprio commit.** Isto garante que se o agente for bloqueado por rate limit, os artigos ja criados ficam guardados localmente.

### 7b. Push por batch (apos os 5 commits do batch):

```bash
git -C "$REPO" push origin main
```

Se push falhar: `git -C "$REPO" pull --rebase origin main && git -C "$REPO" push origin main`

**Apos push bem-sucedido:** Se queue ainda tem items E total < 20, iniciar novo batch (voltar ao Passo 1).

---

## REGRAS DE SEGURANCA

1. **Max 5 artigos por batch, max 20 por sessao.**
2. **Nunca criar artigo sem ler instrumento.md primeiro.**
3. **Nunca editar solucoes.html.**
4. **Nunca duplicar.** Verificar lookup antes de publicar.
5. **Artigos criados: 0 e sempre falha do agente.** Mesmo sem regulamento, os dados do campo notes sao suficientes.
6. **Commit entre batches.** Nunca acumular mais de 5 artigos sem commit.

---

## RESUMO

```
BATCH (repete ate 4x ou queue vazia):
  1. Ler queue.json + instrumento.md
  2. Selecionar 5 items (ready primeiro, depois pending)
  3. Para cada: ler regulamento, criar HTML, atualizar catalogo
  4. Atualizar queue + shard + lookup + index
  5. git commit + push
  6. Se queue > 0 e total < 20: novo batch

Reportar: "Writer: [N] artigos criados. Fila restante: [N]."
```
