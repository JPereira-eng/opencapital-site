# Radar de Instrumentos: Agente Autonomo

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o agente autonomo da Open Capital Advisory & Consultancy.
A tua missao e monitorizar fontes de financiamento, detectar novos instrumentos, e criar artigos automaticamente.

---

## PASSO 0: CONFIGURACAO DE AMBIENTE

**Executar antes de qualquer outra operacao.**

```bash
if [ -d "C:/Users/Utilizador/Desktop/opencapital-website" ]; then
  echo "AMBIENTE: LOCAL"
else
  echo "AMBIENTE: REMOTO"
fi
```

**Se LOCAL:** usar `C:/Users/Utilizador/Desktop/opencapital-website` como base (`$REPO`) em todos os caminhos e comandos git desta execucao.

**Se REMOTO:**
1. Clonar o repositorio:
```bash
git clone https://github.com/JPereira-eng/opencapital-site.git /tmp/opencapital
```
2. Usar `/tmp/opencapital` como `$REPO` em todos os caminhos e comandos git desta execucao.
3. No final, apos o push com sucesso, limpar: `rm -rf /tmp/opencapital`

Todos os caminhos de ficheiros e comandos `git -C` nas instrucoes seguintes referem-se a `$REPO`.

---

## FICHEIROS DE ESTADO

Os ficheiros estao divididos por funcao (cada um abaixo de 5.000 tokens):

| Ficheiro | Conteudo |
|---|---|
| `registry.json` | stats + source_last_checked (~500 tokens) |
| `registry-queue.json` | fila de instrumentos a escrever (~3.300 tokens) |
| `registry-published.json` | IDs publicados para dedup (~1.800 tokens) |
| `sources-scan.json` | lista leve de fontes (~4.500 tokens) |

Ler sempre no inicio: `registry.json`, `registry-queue.json`, `sources-scan.json`.
Ler `registry-published.json` apenas para verificar duplicados.

---

## MODO DE OPERACAO

Le o `registry-queue.json` e conta os items na `queue`. Decide o modo:

| Fila | Modo | State updates | Artigos | Scan |
|---|---|---|---|---|
| 0 items | **Monitorizacao** | 10 | 0 | Sim |
| 1-4 items | **Normal** | 10 | 1 | Sim |
| 5-9 items | **Intensivo** | 5 | 2 | Nao |
| >= 10 items | **Urgente** | 3 | 2 | Nao |

**State updates acontecem SEMPRE**, independentemente do tamanho da fila.

---

## PASSO 1: Verificar o estado

```
1. Read registry.json            (stats + source_last_checked, ~500 tokens)
2. Read registry-queue.json      (fila completa, ~3.300 tokens)
3. Read sources-scan.json        (fontes para scanning, ~4.500 tokens)
4. Read registry-published.json  (para selecionar instrumentos a monitorizar)
5. Contar items na queue (registry-queue.json > queue.length)
6. Decidir o modo (Monitorizacao / Normal / Intensivo / Urgente)
7. Selecionar instrumentos para state update (ver Passo 3B.0)
8. Se modo Monitorizacao/Normal: identificar quais fontes verificar (ver Passo 2)
9. Aplicar state updates (ver Passo 3B) - TODOS os modos
10. Se modo Normal/Intensivo/Urgente: criar artigos (ver Passo 4)
```

---

## PASSO 2: Selecionar fontes a verificar (so em modo Normal)

Verificar no maximo **3 fontes por execucao**.

**Prioridade de selecao:**
1. Fontes com `priority: "high"` que nao foram verificadas ha mais de 7 dias
2. Fontes com `priority: "medium"` que nao foram verificadas ha mais de 14 dias
3. Fontes com `priority: "low"` que nao foram verificadas ha mais de 30 dias
4. Se nenhuma fonte precisa de verificacao: saltar para Passo 3B (state updates)

Consultar `registry.json > source_last_checked` para saber a ultima vez que cada fonte foi verificada.

---

## PASSO 3: Scan de fontes

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
2. Verificar se ja existe em `registry-published.json > published` (comparar por `id`)
3. Se ja existe: verificar alteracoes de estado (ver abaixo)
4. Se e novo: adicionar a `queue`

**Alteracoes de estado (instrumentos ja publicados):**
Para cada instrumento que ja existe em `published`, comparar os dados atuais da fonte com os dados do artigo:
1. **Estado mudou** (ex: aberto → fechado, previsto → aberto): registar em `state_updates` queue
2. **Prazo alterado** (extensao ou antecipacao): registar em `state_updates` queue
3. **Dotacao alterada** (aumento ou reducao): registar em `state_updates` queue
4. Se nada mudou: ignorar

### 3c. Adicionar a fila

Para cada instrumento novo, adicionar ao array `queue` do `registry-queue.json`:

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

### 3e. Guardar ficheiros de estado

Atualizar `stats.sources_checked_this_week` com as fontes verificadas.

---

## PASSO 3B: Atualizar estados de instrumentos publicados

**Este passo executa-se em TODOS os modos.** O numero maximo de state updates depende do modo:
- Monitorizacao: 10
- Normal: 10
- Intensivo: 5
- Urgente: 3

### 3B.0 Selecionar instrumentos a verificar

Ler `registry-published.json` e ordenar os instrumentos por `last_state_check` (data mais antiga primeiro). Selecionar os primeiros N instrumentos (conforme o limite do modo) cujo `current_state` e `"aberto"` ou `"previsto"`.

Instrumentos com `current_state: "fechado"` nao precisam de monitorizacao frequente. Verificar apenas 1 fechado por cada 5 abertos, para confirmar se reabriram.

Para cada instrumento selecionado:
1. Consultar a fonte original (WebFetch no URL do aviso, se disponivel)
2. Comparar estado atual, prazo e dotacao com os dados publicados
3. Se houve alteracao, registar em `state_updates`

Se nenhum instrumento precisar de verificacao (todos verificados recentemente), saltar para Passo 4.

### 3B.1 Identificar instrumentos com estado alterado

Os instrumentos com alteracoes foram registados em `state_updates` (via Passo 3b do scan e/ou via 3B.0 da monitorizacao).
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
1. Mudanca de estado (aberto → fechado) - mais urgente
2. Mudanca de prazo - urgente
3. Mudanca de dotacao - informativo

Se mais updates pendentes do que o limite do modo, processar os mais urgentes. Os restantes ficam para a proxima run.

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

### 3B.3 Atualizar o catalogo JSON

Para cada instrumento atualizado, encontrar a entrada correspondente em `instruments-catalog.json` por `"id": "[slug]"`:

**Se o estado mudou:**
- Alterar `"estado"` (ex: `"aberto"` → `"fechado"`)
- Alterar `"status_text"` (ex: `"Aberto ate 30/04/2026"` → `"Fechado"`)
- Alterar `"status_class"` (ex: `"status-open"` → `"status-closed"`)

**Se o prazo mudou:**
- Alterar `"status_text"` com a nova data (ex: `"Aberto ate 31/12/2026"`)

**Se a dotacao mudou:**
- Alterar `"highlight1"` com o novo valor

### 3B.4 Atualizar ficheiros de estado

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

## PASSO 4: Criar artigos da fila

### 4a. Ler obrigatoriamente a skill de instrumento

**ANTES de escrever qualquer artigo, ler o ficheiro `.claude/commands/instrumento.md`.**

Este ficheiro contém o template HTML completo, as classes CSS obrigatórias, a estrutura da navbar, do hero, da sidebar e do footer. Nunca escrever um artigo sem ter lido este ficheiro nesta execucao. O contexto de conversas anteriores nao e suficiente.

```
Read .claude/commands/instrumento.md
```

Só avançar para os passos seguintes depois de ter o template em contexto ativo.

### 4b. Selecionar artigos da fila

Ordenar a `queue` por `priority_score` (descendente).

- Modo Normal: selecionar o **1 artigo** com maior score
- Modo Intensivo/Urgente: selecionar os **2 artigos** com maior score

### 4b. Obter o regulamento

REGRA CRITICA: NUNCA abortar a criacao de artigos por falta de `regulation_local`. A cascata abaixo garante que sempre e possivel escrever. Mesmo que todas as etapas falhem, os dados do campo `notes` no registry sao suficientes para criar um artigo de qualidade. **Artigos criados: 0 e sempre uma falha do agente, nao uma falha do sistema.**

Para cada artigo selecionado, seguir esta cascata (parar na primeira que funcionar):

1. **Se `regulation_local` existe e nao e null:**
   - Ler o ficheiro diretamente: `Read regulamentos/[fonte]/[id].txt`
   - Se o texto tem mais de 3000 palavras: usar apenas as primeiras 3000
   - Esta e a via preferencial. O scanner ja descarregou e extraiu o texto

2. **Se `regulation_local` e null mas `pdf_url` existe (url completo, nao um ID numerico):**
   - Criar pasta `regulamentos/[source_id]/` se nao existir
   - Descarregar: `curl -sL "[pdf_url]" -o "regulamentos/[source_id]/[id].pdf"`
   - Extrair: `pdftotext -enc UTF-8 "regulamentos/[source_id]/[id].pdf" "regulamentos/[source_id]/[id].txt"`
   - Atualizar o item na queue: `"regulation_local": "regulamentos/[source_id]/[id].txt"`
   - Se o texto tem mais de 3000 palavras: usar apenas as primeiras 3000
   - Se o download falhar: continuar para passo 3

3. **Se `regulation_url` existe:**
   - Usar WebFetch diretamente no `regulation_url` (independentemente do `access_method` da fonte)
   - Prompt: "Extrai toda a informacao disponivel sobre este aviso/instrumento de financiamento: nome, codigo, dotacao, taxa de cofinanciamento, elegibilidade, despesas elegiveis, prazos, criterios de selecao, programa, fundo."
   - Guardar o resultado em `regulamentos/[source_id]/[id].txt` e atualizar `regulation_local`
   - Se WebFetch retornar pagina vazia ou erro JS: tentar Chrome MCP (navigate + get_page_text)

4. **Se tudo falhou ou nao ha URLs:**
   - Usar WebSearch: `"[aviso_codigo] [nome] financiamento portugal 2030"` e `"[nome] aviso candidaturas elegibilidade"`
   - Combinar resultados de 2-3 pesquisas
   - Complementar com os dados do campo `notes` no registry (codigo, programa, dotacao, beneficiario, prazo)

**Nota para items PT2030:** Para items com `source_id: "portugal-2030"` e URL do tipo `portugal2030.pt/aviso-2024/[slug]/`, o WebFetch funciona directamente - sao paginas WordPress com render server-side. Usar sempre como passo 3.

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
- `empresa`: qualquer tipo de empresa (startups, micro, PME, grandes empresas)
- `entidade-publica`: municipios, autarquias, entidades publicas
- `associacao`: associacoes empresariais, clusters, entidades sem fins lucrativos
- `ensino-investigacao`: universidades, centros de investigacao, laboratorios
- `empreendedor`: empreendedores individuais, pre-incorporacao

Um instrumento pode ter multiplos beneficiarios (ex: `empresa,associacao`).

**Passos de criacao:**

1. Definir metadados com base no regulamento
2. Selecionar o autor adequado (ver regras da skill `/instrumento`)
3. Escrever o artigo HTML completo em `instrumentos/[slug].html`
4. Seguir TODAS as regras do CLAUDE.md (design system, navbar com "Biblioteca", footer, etc.)

### 4d. Adicionar entrada ao catalogo JSON

O catalogo de instrumentos e carregado dinamicamente a partir de `instruments-catalog.json`. Nao editar `solucoes.html`.

Abrir `instruments-catalog.json`, ler o array `instruments`, e adicionar uma nova entrada ao FINAL do array:

```json
{
  "id": "[SLUG]",
  "category": "[CAT]",
  "category_label": "[CATEGORIA_LABEL]",
  "estado": "[ESTADO]",
  "status_text": "[ESTADO_LABEL]",
  "status_class": "status-[open/closed/planned/cont]",
  "fonte": "[FONTE]",
  "beneficiario": "[BENEFICIARIO]",
  "regiao": "[REGIAO]",
  "title": "[NOME]",
  "tagline": "[TAGLINE]",
  "highlight1": "[VALOR1 - ex: 301M EUR de dotacao - Cofinanciamento ate 70%]",
  "highlight2": "[VALOR2 - ex: Empresas - Norte, Centro, Alentejo - FEDER]",
  "href": "instrumentos/[SLUG].html",
  "featured": false
}
```

**Mapeamento de category_label:**
- `nr` → "Não Reembolsável"
- `priv` → "Investimento Privado"
- `div` → "Dívida"
- `hib` → "Híbrido"
- `fiscal` → "Incentivo Fiscal"
- `outros` → "Outro"

**Mapeamento de status_text e status_class:**
- estado `aberto` → status_text: "Aberto ate [DATA]", status_class: "status-open"
- estado `aberto` (continuo) → status_text: "Candidatura Continua", status_class: "status-cont"
- estado `fechado` → status_text: "Fechado", status_class: "status-closed"
- estado `previsto` → status_text: "Previsto", status_class: "status-planned"

**REGRA CRITICA:** Nunca editar `solucoes.html`. O catalogo e 100% dinamico via JSON.

---

## PASSO 5: Atualizar ficheiros de estado

### Para cada artigo criado:

1. Remover o item de `registry-queue.json > queue`
2. Adicionar a `registry-published.json > published`:
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
3. Atualizar `registry.json > stats.total_published` (+1 por artigo)
4. Atualizar `registry.json > stats.total_in_queue` (novo tamanho da fila)

### Para cada state update aplicado:

1. Atualizar o registo em `registry-published.json > published` com:
   - `current_state`: novo estado
   - `last_state_check`: data de hoje
   - `state_history`: adicionar nova entrada
2. Atualizar `registry.json > stats.total_state_updates` (+1 por update)

---

## PASSO 6: Deploy

**Usar sempre `git -C "C:/Users/Utilizador/Desktop/opencapital-website"` para todos os comandos git. Nunca usar `cd ... && git`. O formato `git -C` garante execucao sem prompt de permissao.**

**Usar sempre `git -C "$REPO"` (ver Passo 0 para o valor de $REPO).**

Se foi criado 1 artigo:
```bash
git -C "$REPO" add instrumentos/[slug].html instruments-catalog.json registry.json registry-queue.json registry-published.json
git -C "$REPO" commit -m "instrumento: [nome do instrumento] ([fonte])"
git -C "$REPO" push origin main
```

Se foram criados 2 artigos:
```bash
git -C "$REPO" add instrumentos/[slug1].html instrumentos/[slug2].html instruments-catalog.json registry.json registry-queue.json registry-published.json
git -C "$REPO" commit -m "radar: [nome1] + [nome2]"
git -C "$REPO" push origin main
```

Se houve state updates sem artigos novos:
```bash
git -C "$REPO" add instrumentos/[slug1].html instrumentos/[slug2].html instruments-catalog.json registry.json registry-published.json
git -C "$REPO" commit -m "radar: estado atualizado [slug1] (fechado), [slug2] (prazo estendido)"
git -C "$REPO" push origin main
```

Se houve apenas scan sem novidades:
```bash
git -C "$REPO" add registry.json
git -C "$REPO" commit -m "radar: scan [fonte1], [fonte2], [fonte3], sem novidades"
git -C "$REPO" push origin main
```

Se o push falhar:
```bash
git -C "$REPO" pull --rebase origin main
git -C "$REPO" push origin main
```

Se ambiente REMOTO, apos push com sucesso:
```bash
rm -rf /tmp/opencapital
```

---

## REGRAS DE SEGURANCA

1. **Nunca duplicar artigos.** Verificar sempre `registry-published.json > published` antes de criar.
2. **Nunca exceder 2 artigos por execucao.** Se a fila tem 10 items, criar 2 e guardar os restantes.
3. **Nunca exceder o limite de state updates do modo atual** (3 em Urgente, 5 em Intensivo, 10 em Normal/Monitorizacao). Se ha mais updates pendentes, processar os mais urgentes e guardar os restantes.
4. **Modificar artigos existentes APENAS para state updates.** Alteracoes permitidas: estado (aberto/fechado/previsto), prazo, dotacao, e aviso de encerramento. Nunca reescrever o conteudo editorial do artigo.
5. **Nunca remover entradas de instruments-catalog.json.** So adicionar ou atualizar estado/prazo/dotacao. Nunca editar solucoes.html.
5. **Se WebFetch falhar para uma fonte:** registar o erro em `source_last_checked` com nota de falha e continuar para a proxima fonte. Nao parar a execucao.
6. **Se pdftotext falhar:** usar apenas o conteudo disponivel via WebFetch (pagina HTML). O artigo pode ser menos detalhado mas deve ser publicado.
7. **Se o git push falhar:** tentar `git pull --rebase && git push`. Se falhar novamente, guardar as alteracoes locais e reportar.

---

## RESUMO DE UMA EXECUCAO TIPICA

```
1. Ler registry.json + registry-queue.json + sources-scan.json + registry-published.json
2. Decidir modo (Monitorizacao/Normal/Intensivo/Urgente)
3. [Monitorizacao/Normal] Scan 3 fontes → detectar novos → adicionar a fila
4. [TODOS os modos] Selecionar instrumentos por last_state_check (mais antigo primeiro)
5. [TODOS os modos] Aplicar state updates (3-10 conforme modo) em artigos + instruments-catalog.json
6. [Normal/Intensivo/Urgente] Criar 1-2 artigos da fila + adicionar ao instruments-catalog.json
7. Atualizar registry.json + registry-queue.json + registry-published.json + instruments-catalog.json
8. git commit + push
9. Reportar: "Modo: [X]. Scan: [fontes]. Novos: [N]. Criados: [N]. Updates: [N]. Fila: [N]."
```
