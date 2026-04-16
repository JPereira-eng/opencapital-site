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
| `registry/queue.json` | Sempre (regime "aviso" - avisos com deadline formal) |
| `registry/queue-catalogo.json` | Sempre (regime "catalogo" - bancos, VC, premios, aceleradores) |
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

O writer opera em **1 batch de 5 artigos por sessao**. Cada batch:
1. Seleciona 5 items da queue (ou menos se queue menor)
2. Cria os artigos, **commit apos cada artigo individual**
3. Push apos completar o batch (ou apos cada artigo se rate limit proximo)
4. Termina. Nao inicia novo batch mesmo que a queue tenha mais items.

**Limites por sessao:**
- Max 5 artigos por batch
- **1 batch por sessao = 5 artigos max**
- Se queue < 5: criar todos os que houver
- Se queue vazia: terminar imediatamente sem criar artigos

**REGRA DE SEGURANCA: Commit por artigo.** Cada artigo criado e imediatamente commitado (sem push). O push acontece ao final do batch. Se o agente for bloqueado por rate limit entre artigos, o trabalho ja esta guardado localmente e sera enviado na proxima sessao (Passo 0.5).

---

## PASSO 1: Selecionar artigos

Ler **ambas as filas**: `registry/queue.json` (regime aviso) e `registry/queue-catalogo.json` (regime catalogo).

**Composicao do batch de 5 artigos:**
- Ate 4 items de `queue.json` (regime aviso), ordenados por `priority_score` descendente
- 1 item de `queue-catalogo.json` (regime catalogo), o mais antigo na fila (FIFO - para garantir que todas as fontes de catalogo sao cobertas em rotacao)
- Se `queue-catalogo.json` estiver vazia: usar o 5o slot para mais um item de `queue.json`
- Se `queue.json` estiver vazia mas `queue-catalogo.json` tiver items: processar ate 5 items do catalogo

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

### PASSO 3.5: Validar conteudo (ultima barreira antes de escrever)

Apos obter o texto do regulamento (por qualquer metodo), verificar se contem QUALQUER um destes markers (case-insensitive):
- "Plano Anual de Avisos"
- "Resumo de Aviso do Plano"
- "PAA2026" ou "PAA202"
- "Aviso a publicar em:"

**Se encontrar:** o item e um documento de plano anual, nao um aviso publicado. NAO escrever o artigo. Atualizar o item na queue para `status: "plano_anual"`. Passar ao proximo item do batch.

Esta verificacao existe como defesa contra falhas do downloader, que deveria ter bloqueado estes items antes.

---

## PASSO 4: Definir metadados, selecionar autor e criar artigo

### 4a. Metadados do artigo

Com o regulamento, definir:
- `slug`: kebab-case, descritivo (ex: `sifide-2`, `rfai`, `horizonte-europa`)
- `nome_instrumento`: nome completo e oficial
- `categoria_badge`: uma de `Financiamento Publico`, `Investimento Privado`, `Fiscal`, `Inovacao`, `Estrategia`
- `categoria_card`: codigo para o catalogo (ver mapeamento 4c)
- `estado`: `aberto`, `fechado`, ou `previsto`
- `fonte`: codigo da fonte/programa (`pt2030`, `ani`, `iapmei`, `bfomento`, `aicep`, `at`, `pventures`, `compete`, `prr`, `ue`)
- `beneficiario`: lista separada por virgulas (`empresa`, `entidade-publica`, `associacao`, `ensino-investigacao`, `empreendedor`)
- `regiao`: lista das regioes. Se nacional: `norte,centro,lisboa,alentejo,algarve,acores,madeira`. Se regional: apenas as cobertas.
- `hero_tagline`: 1 frase clara, max 20 palavras
- `meta_fact_1` a `meta_fact_4`: label + valor para a meta-bar do hero (ex: Dotacao: €23 mil milhoes)
- `sidebar_factos`: 5 a 8 pares chave/valor para o card "Factos Rapidos" na sidebar
- `sidebar_cta_text`: texto contextualizado ao instrumento (ex: "Quer calcular o beneficio SIFIDE para a sua empresa?")
- `instrumentos_relacionados`: 3 a 5 links para outros artigos em `instrumentos/`

### 4b. Selecao de autor

Escolher o autor com base na area de especialidade do instrumento. Aplicar pela ordem indicada, parar na primeira que encaixar:

1. Fundos europeus e candidaturas nao reembolsaveis (Portugal 2030, PRR, COMPETE 2030, Horizonte Europa, EIC Accelerator): **Mara Ferreira** - Tecnica de Candidaturas e Incentivos
2. Incentivos fiscais ao investimento (RFAI, DLRR, CFI, Patent Box): **Andre Carvalho** - Tecnico de Candidaturas e Incentivos
3. Premios de inovacao e vouchers (SIFIDE II, premios, vouchers IAPMEI): **Andre Carvalho** (se foco fiscal) ou **Sofia Costa** - Especialista I&D e Inovacao (se foco I&D/tecnologico)
4. Instrumentos de divida e credito (Banco de Fomento, linhas de credito, garantias): **Pedro Nunes** - Consultor de Financiamento
5. Investimento privado (VC, PE, Business Angels, Crowdfunding): **Luis Gomes** - Analista Financeiro ou **Mariana Costa** - Finance Lead
6. Internacionalizacao e atracao de investimento (AICEP, SAI): **Miguel Santos** - Business Developer

Outros autores disponiveis:
- **Johnson Semedo** - Gestor de Projetos (execucao operacional, PME)
- **Carla Sousa** - Gestora de Projetos (planeamento, reporting, financiamento publico)
- **Ines Teixeira** - Consultora Junior (analise setorial, tendencias emergentes)
- **Joao Silva** - Consultor Junior (competitividade, benchmarking sectorial)
- **Rita Ferreira** - Marketeer e Copywriter (economia criativa, consumo)

**Jorge Pereira nao pode ser selecionado para artigos de instrumento.**

**Mapeamento de fotos (usar com prefix `../Retratos Equipa/`):**
Jorge Pereira: `retrato_jorgepereira.png` · Mariana Costa: `retrato_marianacosta.png` · Sofia Costa: `retrato_sofiacosta.png` · Luis Gomes: `retrato_luísgomes.png` · Pedro Nunes: `retrato_pedronunes.png` · Andre Carvalho: `retrato_andrecarvalho.png` · Mara Ferreira: `retrato_maraferreira.png` · Johnson Semedo: `retrato_Johnson Semedo.png` · Carla Sousa: `retrato_carlasousa.png` · Ines Teixeira: `retrato_inêsteixeira.png` · Joao Silva: `retrato_joaosilva.png` · Miguel Santos: `retrato_miguelsantos.png` · Rita Ferreira: `retrato_ritaferreira.png`

### 4c. Mapeamento categoria_card → label

- `nr` → "Nao Reembolsavel" (fundo perdido, subsidio, premio, voucher)
- `div` → "Divida" (emprestimo, linha de credito, garantia)
- `priv` → "Investimento Privado" (VC, PE, business angels, crowdfunding)
- `hib` → "Hibridos" (componente reembolsavel + nao reembolsavel)
- `fiscal` → "Incentivos Fiscais" (deducao IRC, beneficio fiscal)
- `outros` → "Outros" (internacionalizacao, apoio tecnico)

### 4d. Highlights do card (para instruments-catalog.json)

Cada card tem 3 highlights com funcao fixa:
- `highlight0`: beneficio principal em poucas palavras (ex: "Ate 65% fundo nao reembolsavel", "Divida sem juros com periodo de carencia", "Deducao fiscal ate 82.5% das despesas de I&D")
- `highlight1`: tipos de beneficiarios (ex: "PME e Grandes Empresas", "Entidades publicas", "Startups e empreendedores")
- `highlight2`: localizacoes (ex: "Norte, Centro, Lisboa", "Madeira", "Nacional")

### 4e. Criar artigo

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
  "highlight0": "[BENEFICIO_PRINCIPAL]",
  "highlight1": "[BENEFICIARIOS]",
  "highlight2": "[LOCALIZACOES]",
  "href": "instrumentos/[SLUG].html",
  "featured": false
}
```

**REGRA CRITICA:** Nunca editar `solucoes.html`. Catalogo e 100% dinamico via JSON.

---

## PASSO 6: Atualizar estado

Para cada artigo criado:

1. **Remover da queue correcta**: se o item veio de `queue.json` remover de `queue.json`; se veio de `queue-catalogo.json` remover de `queue-catalogo.json`
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

**Apos push bem-sucedido:** Terminar sessao. O proximo writer agendado tratara dos restantes.

---

## REGRAS DE SEGURANCA

1. **Max 5 artigos por sessao (1 batch). Terminar apos o push, nunca iniciar segundo batch.**
2. **Nunca criar artigo sem ler instrumento.md primeiro.**
3. **Nunca editar solucoes.html.**
4. **Nunca duplicar.** Verificar lookup antes de publicar.
5. **Artigos criados: 0 e sempre falha do agente.** Mesmo sem regulamento, os dados do campo notes sao suficientes.
6. **Commit entre batches.** Nunca acumular mais de 5 artigos sem commit.

---

## RESUMO

```
BATCH UNICO (1 vez por sessao):
  1. Ler queue.json + instrumento.md
  2. Se queue vazia: terminar imediatamente
  3. Selecionar ate 5 items (ready primeiro, depois pending)
  4. Para cada: ler regulamento, criar HTML, atualizar catalogo
  5. Atualizar queue + shard + lookup + index
  6. git commit + push
  7. Terminar. Nao iniciar segundo batch.

Reportar: "Writer: [N] artigos criados. Fila restante: [N]."
```
