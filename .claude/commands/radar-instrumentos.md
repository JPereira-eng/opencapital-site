# Radar de Instrumentos — Agente Autonomo

Es o agente autonomo da Open Capital Advisory & Consultancy.
A tua missao e monitorizar fontes de financiamento, detectar novos instrumentos, e criar artigos automaticamente.

---

## FICHEIROS DE ESTADO

- **`sources.json`** — lista de 35 fontes com URLs e metodo de acesso
- **`registry.json`** — estado do agente: fila, publicados, ultima verificacao

Le ambos no inicio de cada execucao.

---

## MODO DE OPERACAO

Le o `registry.json` e conta os items na `queue`. Decide o modo:

| Fila | Modo | Acao |
|---|---|---|
| < 5 items | **Normal** | Scan de fontes + state updates (max 3) + criar 1 artigo da fila |
| 5-9 items | **Intensivo** | Sem scan, sem state updates, criar 2 artigos da fila |
| >= 10 items | **Urgente** | Sem scan, sem state updates, criar 2 artigos da fila |

---

## PASSO 1 — Verificar o estado

```
1. Read registry.json
2. Read sources.json
3. Contar items na queue
4. Decidir o modo (Normal / Intensivo / Urgente)
5. Se modo Normal: identificar quais fontes verificar (ver Passo 2)
6. Se modo Normal: apos scan, aplicar state updates (ver Passo 3B)
7. Se modo Intensivo/Urgente: saltar para Passo 4 (criar artigos)
```

---

## PASSO 2 — Selecionar fontes a verificar (so em modo Normal)

Verificar no maximo **3 fontes por execucao**.

**Prioridade de selecao:**
1. Fontes com `priority: "high"` que nao foram verificadas ha mais de 7 dias
2. Fontes com `priority: "medium"` que nao foram verificadas ha mais de 14 dias
3. Fontes com `priority: "low"` que nao foram verificadas ha mais de 30 dias
4. Se nenhuma fonte precisa de verificacao: saltar para Passo 3B (state updates)

Consultar `registry.json > source_last_checked` para saber a ultima vez que cada fonte foi verificada.

---

## PASSO 3 — Scan de fontes

Para cada fonte selecionada:

### 3a. Aceder a fonte

Consultar o campo `access_method` no `sources.json`:

- Se `"webfetch"`: usar WebFetch no `url_avisos` da fonte
- Se `"websearch"`: usar WebSearch com query `"[nome_fonte] avisos abertos 2026"`

**Prompt para WebFetch:**
```
Lista todos os avisos/instrumentos/programas de financiamento visiveis nesta pagina.
Para cada um, extrai:
- Nome/titulo do aviso
- Codigo do aviso (se disponivel)
- Estado (aberto/fechado/previsto)
- Prazo de candidatura (se disponivel)
- Dotacao/orcamento (se disponivel)
- URL do regulamento ou ficha tecnica (se disponivel)
- URL do PDF do regulamento (se disponivel)
```

### 3b. Comparar com publicados e detectar alteracoes de estado

Para cada instrumento detectado na pagina da fonte:

**Novos instrumentos:**
1. Gerar um `id` slug (kebab-case do nome)
2. Verificar se ja existe em `registry.json > published` (comparar por `id`)
3. Se ja existe: verificar alteracoes de estado (ver abaixo)
4. Se e novo: adicionar a `queue`

**Alteracoes de estado (instrumentos ja publicados):**
Para cada instrumento que ja existe em `published`, comparar os dados atuais da fonte com os dados do artigo:
1. **Estado mudou** (ex: aberto → fechado, previsto → aberto): registar em `state_updates` queue
2. **Prazo alterado** (extensao ou antecipacao): registar em `state_updates` queue
3. **Dotacao alterada** (aumento ou reducao): registar em `state_updates` queue
4. Se nada mudou: ignorar

### 3c. Adicionar a fila

Para cada instrumento novo, adicionar ao array `queue` do `registry.json`:

```json
{
  "id": "slug-do-instrumento",
  "name": "Nome completo do aviso",
  "source_id": "compete-2030",
  "detected_date": "2026-04-09",
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

### 3d. Atualizar source_last_checked

```json
"source_last_checked": {
  "compete-2030": "2026-04-09",
  "ani": "2026-04-09"
}
```

### 3e. Guardar registry.json

Atualizar `stats.sources_checked_this_week` com as fontes verificadas.

---

## PASSO 3B — Atualizar estados de instrumentos publicados

Este passo executa-se **apenas em modo Normal**, apos o scan de fontes.
Maximo de **3 state updates por execucao** (para caber no budget de tokens).

### 3B.1 Identificar instrumentos com estado alterado

Durante o Passo 3b, os instrumentos com alteracoes foram registados em `state_updates`.
Se `state_updates` esta vazio, saltar para Passo 4.

Cada entrada em `state_updates` tem:
```json
{
  "id": "slug-do-instrumento",
  "changes": {
    "estado": { "old": "aberto", "new": "fechado" },
    "deadline": { "old": "2026-09-30", "new": null },
    "budget": { "old": "2.000.000 EUR", "new": "3.500.000 EUR" }
  }
}
```

Ordenar por prioridade:
1. Mudanca de estado (aberto → fechado) — mais urgente
2. Mudanca de prazo — urgente
3. Mudanca de dotacao — informativo

Se mais de 3 updates pendentes, processar os 3 mais urgentes. Os restantes ficam para a proxima run.

### 3B.2 Atualizar o artigo HTML

Para cada instrumento a atualizar, ler o ficheiro `instrumentos/[slug].html` e aplicar as alteracoes:

**Se o estado mudou (ex: aberto → fechado):**
- Hero meta-bar: alterar o valor do item "Estado" (ex: "Aberto ate 30/09/2026" → "Fechado")
- Hero meta-bar: alterar a classe CSS do status (ex: `status-open` → `status-closed`)
- Sidebar "Factos Rapidos": atualizar o campo de estado
- Se fechou: adicionar aviso no topo do artigo:
```html
<div class="instrument-closed-notice">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9A96E" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="0.5" fill="#C9A96E"/></svg>
  <span>Este instrumento encontra-se <strong>encerrado</strong>. As candidaturas ja nao estao abertas.</span>
</div>
```
```css
.instrument-closed-notice {
  display:flex; align-items:center; gap:12px;
  background:rgba(201,169,110,0.07); border-left:3px solid var(--gold);
  padding:16px 24px; margin-bottom:32px;
  font-size:15px; font-weight:400; color:var(--grey-dark);
}
```

**Se o prazo mudou:**
- Hero meta-bar: atualizar o valor do prazo
- Sidebar "Factos Rapidos": atualizar o prazo
- Se o prazo foi estendido: adicionar nota no artigo "Prazo estendido ate [nova data]"

**Se a dotacao mudou:**
- Hero meta-bar: atualizar o valor da dotacao
- Sidebar "Factos Rapidos": atualizar a dotacao

### 3B.3 Atualizar o card em solucoes.html

Para cada instrumento atualizado, encontrar o card correspondente em `solucoes.html` por `data-id="[slug]"`:

**Se o estado mudou:**
- Alterar `data-estado` no card (ex: `data-estado="aberto"` → `data-estado="fechado"`)
- Alterar a `status-pill`: classe e texto
  - `<span class="status-pill status-open">Aberto ate [DATA]</span>` → `<span class="status-pill status-closed">Fechado</span>`

**Se o prazo mudou:**
- Alterar o texto da `status-pill` com a nova data (ex: "Aberto ate 31/12/2026")

**Se a dotacao mudou:**
- Alterar o `hl-value` correspondente no card

### 3B.4 Atualizar registry.json

Adicionar ou atualizar o campo `state_history` para cada instrumento em `published`:
```json
{
  "id": "slug-do-instrumento",
  "source": "compete-2030",
  "file": "instrumentos/slug.html",
  "published_date": "2026-04-01",
  "detected_date": "2026-04-01",
  "current_state": "fechado",
  "last_state_check": "2026-04-09",
  "state_history": [
    { "date": "2026-04-01", "state": "aberto", "note": "publicacao inicial" },
    { "date": "2026-04-09", "state": "fechado", "note": "candidaturas encerradas" }
  ]
}
```

---

## PASSO 4 — Criar artigos da fila

### 4a. Ler obrigatoriamente a skill de instrumento

**ANTES de escrever qualquer artigo, ler o ficheiro `.claude/commands/instrumento.md`.**

Este ficheiro contém o template HTML completo, as classes CSS obrigatórias, a estrutura da navbar, do hero, da sidebar e do footer. Nunca escrever um artigo sem ter lido este ficheiro nesta execução — o contexto de conversas anteriores não é suficiente.

```
Read .claude/commands/instrumento.md
```

Só avançar para os passos seguintes depois de ter o template em contexto ativo.

### 4b. Selecionar artigos da fila

Ordenar a `queue` por `priority_score` (descendente).

- Modo Normal: selecionar o **1 artigo** com maior score
- Modo Intensivo/Urgente: selecionar os **2 artigos** com maior score

### 4b. Obter o regulamento

Para cada artigo selecionado, seguir esta cascata (parar na primeira que funcionar):

1. **Se `regulation_local` existe e nao e null:**
   - Ler o ficheiro diretamente: `Read regulamentos/[fonte]/[id].txt`
   - Se o texto tem mais de 3000 palavras: usar apenas as primeiras 3000
   - Esta e a via preferencial — o scanner ja descarregou e extraiu o texto

2. **Se `regulation_local` e null mas `pdf_url` existe:**
   - Criar pasta `regulamentos/[source_id]/` se nao existir
   - Descarregar: `curl -sL "[pdf_url]" -o "regulamentos/[source_id]/[id].pdf"`
   - Extrair: `pdftotext -enc UTF-8 "regulamentos/[source_id]/[id].pdf" "regulamentos/[source_id]/[id].txt"`
   - Atualizar o item na queue: `"regulation_local": "regulamentos/[source_id]/[id].txt"`
   - Se o texto tem mais de 3000 palavras: usar apenas as primeiras 3000

3. **Se `regulation_url` existe (sem PDF nem local):**
   - Consultar `access_method` da fonte em `sources.json`
   - Se `"webfetch"`: usar WebFetch para extrair o conteudo da pagina
   - Se `"chrome"`: usar Chrome MCP tools (navigate → get_page_text)
   - Extrair: titulo, dotacao, elegibilidade, despesas elegiveis, taxas, prazos
   - Guardar em `regulamentos/[source_id]/[id].txt` e atualizar `regulation_local`

4. **Se nenhum URL existe:**
   - Usar WebSearch para encontrar informacao sobre o instrumento
   - Combinar resultados de multiplas fontes

### 4c. Criar o artigo

Com o texto do regulamento recolhido, executar a logica da skill `/instrumento`:

**Metadados a definir:**
- `slug`: kebab-case do nome do instrumento
- `nome_instrumento`: nome oficial
- `categoria_card`: `nr`, `priv`, `div`, `hib`, `fiscal`, ou `outros`
- `estado`: `aberto`, `fechado`, ou `previsto`
- `fonte`: codigo da fonte (ex: `pt2030`, `compete`, `ani`)
- `beneficiario`: lista separada por virgulas (ex: `empresa,entidade-publica`)
- `regiao`: lista separada por virgulas (se nacional: `norte,centro,lisboa,alentejo,algarve,acores,madeira`)

**Categorias de beneficiario simplificadas:**
- `empresa` — qualquer tipo de empresa (startups, micro, PME, grandes empresas)
- `entidade-publica` — municipios, autarquias, entidades publicas
- `associacao` — associacoes empresariais, clusters, entidades sem fins lucrativos
- `ensino-investigacao` — universidades, centros de investigacao, laboratorios
- `empreendedor` — empreendedores individuais, pre-incorporacao

Um instrumento pode ter multiplos beneficiarios (ex: `empresa,associacao`).

**Passos de criacao:**

1. Definir metadados com base no regulamento
2. Selecionar o autor adequado (ver regras da skill `/instrumento`)
3. Escrever o artigo HTML completo em `instrumentos/[slug].html`
4. Seguir TODAS as regras do CLAUDE.md (design system, navbar com "Biblioteca", footer, etc.)

### 4d. Injetar card em solucoes.html

Adicionar o card do novo instrumento ao grid em `solucoes.html`, imediatamente antes do comentario `</div>` que fecha o `instruments-grid`:

```html
<div class="instrument-card reveal" data-category="[CAT]" data-estado="[ESTADO]" data-fonte="[FONTE]" data-beneficiario="[BENEFICIARIO]" data-regiao="[REGIAO]" data-id="[SLUG]" data-href="instrumentos/[SLUG].html">
  <div class="card-header">
    <span class="cat-badge cat-[CAT]">[CATEGORIA_LABEL]</span>
    <span class="status-pill status-[open/closed/planned]">[ESTADO_LABEL]</span>
  </div>
  <h3 class="card-title">[NOME]</h3>
  <p class="card-tagline">[TAGLINE]</p>
  <div class="card-highlights">
    <div class="card-highlight"><span class="hl-label">[LABEL1]</span><span class="hl-value">[VALOR1]</span></div>
    <div class="card-highlight"><span class="hl-label">[LABEL2]</span><span class="hl-value">[VALOR2]</span></div>
  </div>
  <div class="card-footer">
    <a href="instrumentos/[SLUG].html" class="card-link">Ver instrumento →</a>
  </div>
</div>
```

**Mapeamento de labels:**
- `cat-nr` → "Nao Reembolsavel"
- `cat-priv` → "Investimento Privado"
- `cat-div` → "Divida"
- `cat-hib` → "Hibrido"
- `cat-fiscal` → "Incentivo Fiscal"
- `cat-outros` → "Outro"

**Mapeamento de estado:**
- `status-open` → "Aberto ate [DATA]"
- `status-closed` → "Fechado"
- `status-planned` → "Previsto"

---

## PASSO 5 — Atualizar registry.json

### Para cada artigo criado:

1. Remover da `queue`
2. Adicionar a `published`:
```json
{
  "id": "[slug]",
  "source": "[source_id]",
  "file": "instrumentos/[slug].html",
  "published_date": "[data_hoje]",
  "detected_date": "[data_detecao]",
  "current_state": "aberto",
  "last_state_check": "[data_hoje]",
  "regulation_local": "[regulamentos/source_id/slug.txt ou null]"
}
```
3. Atualizar `stats.total_published` (+1 por artigo)
4. Atualizar `stats.total_in_queue` (novo tamanho da fila)

### Para cada state update aplicado:

1. Atualizar o registo em `published` com:
   - `current_state`: novo estado
   - `last_state_check`: data de hoje
   - `state_history`: adicionar nova entrada
2. Atualizar `stats.total_state_updates` (+1 por update)

---

## PASSO 6 — Deploy

**Usar sempre `git -C "C:/Users/Utilizador/Desktop/opencapital-website"` para todos os comandos git. Nunca usar `cd ... && git`. O formato `git -C` garante execucao sem prompt de permissao.**

Se foi criado 1 artigo:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" add instrumentos/[slug].html solucoes.html registry.json
git -C "C:/Users/Utilizador/Desktop/opencapital-website" commit -m "instrumento: [nome do instrumento] ([fonte])"
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

Se foram criados 2 artigos:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" add instrumentos/[slug1].html instrumentos/[slug2].html solucoes.html registry.json
git -C "C:/Users/Utilizador/Desktop/opencapital-website" commit -m "radar: [nome1] + [nome2]"
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

Se houve state updates sem artigos novos:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" add instrumentos/[slug1].html instrumentos/[slug2].html solucoes.html registry.json
git -C "C:/Users/Utilizador/Desktop/opencapital-website" commit -m "radar: estado atualizado [slug1] (fechado), [slug2] (prazo estendido)"
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

Se houve apenas scan sem novidades:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" add registry.json
git -C "C:/Users/Utilizador/Desktop/opencapital-website" commit -m "radar: scan [fonte1], [fonte2], [fonte3], sem novidades"
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

Se o push falhar:
```bash
git -C "C:/Users/Utilizador/Desktop/opencapital-website" pull --rebase origin main
git -C "C:/Users/Utilizador/Desktop/opencapital-website" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca duplicar artigos.** Verificar sempre `registry.json > published` antes de criar.
2. **Nunca exceder 2 artigos por execucao.** Se a fila tem 10 items, criar 2 e guardar os restantes.
3. **Nunca exceder 3 state updates por execucao.** Se ha mais updates pendentes, processar 3 e guardar os restantes.
4. **Modificar artigos existentes APENAS para state updates.** Alteracoes permitidas: estado (aberto/fechado/previsto), prazo, dotacao, e aviso de encerramento. Nunca reescrever o conteudo editorial do artigo.
5. **Nunca remover cards de solucoes.html.** So adicionar ou atualizar estado/prazo/dotacao.
5. **Se WebFetch falhar para uma fonte:** registar o erro em `source_last_checked` com nota de falha e continuar para a proxima fonte. Nao parar a execucao.
6. **Se pdftotext falhar:** usar apenas o conteudo disponivel via WebFetch (pagina HTML). O artigo pode ser menos detalhado mas deve ser publicado.
7. **Se o git push falhar:** tentar `git pull --rebase && git push`. Se falhar novamente, guardar as alteracoes locais e reportar.

---

## RESUMO DE UMA EXECUCAO TIPICA

```
1. Ler registry.json + sources.json
2. Decidir modo (Normal/Intensivo/Urgente)
3. [Normal] Scan 3 fontes → detectar novos → adicionar a fila → detectar state changes
4. [Normal] Aplicar ate 3 state updates (artigo + card + registry)
5. Criar 1-2 artigos da fila (por prioridade)
6. Atualizar registry.json
7. git commit + push
8. Reportar: "Scan: [fontes]. Novos: [N]. Criados: [N]. Updates: [N]. Fila: [N]."
```
