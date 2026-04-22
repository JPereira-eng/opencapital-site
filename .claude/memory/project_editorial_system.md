---
name: Sistema Editorial Open Capital
description: Series e subserias de marketing digital -- logica, skills criadas e estrutura de automacao
type: project
---

Sistema editorial com 7 series e 14 subserias. Foco atual: subserias com output para website, usando skills Claude Code (Option C -- sem scripts externos).

**Skills em `.claude/commands/` -- todas criadas:**
- `/trend` -> Serie 1.2 -- Artigo Trend para Website (`conhecimento/`) - injecta card em conhecimento.html + atualiza index.html
- `/informativo` -> Serie 2.1 -- Artigo Informativo para Website (`conhecimento/`) - injecta card em conhecimento.html + atualiza index.html
- `/opiniao` -> Serie 6.2 -- Opiniao Controversa para Website (`conhecimento/`) - injecta card em conhecimento.html + atualiza index.html
- `/instrumento` -> Serie 3.1 -- Instrumento de Financiamento (`instrumentos/`) - NAO injeta card (ja existem em biblioteca.html com data-href)

**Pipeline skills conhecimento/ (trend, informativo, opiniao):**
1. Processar input (WebFetch se URL)
2. Gerar HTML completo em `conhecimento/[slug].html`
3. Injetar card em `conhecimento.html` apos `<div class="articles-grid" id="articlesGrid">`
4. Atualizar contador `id="filterCount">X artigos</span>`
5. Atualizar destaques editoriais em `index.html` (seccao `id="conhecimento"`)
6. git add + commit + push -> GitHub Pages auto-deploy

**Pipeline skill instrumentos/ (instrumento):**
1. Processar input (WebFetch se URL, regulamento ou brief)
2. Gerar HTML completo em `instrumentos/[slug].html`
3. git add + commit + push -> GitHub Pages auto-deploy (sem injecao de card)

**Artigos existentes em `conhecimento/`:** verificar sempre a pasta `conhecimento/` para a lista atualizada (ex: `como-funciona-horizonte-europa.html`, `preparar-ronda-investimento-startup.html`, `ai-act-o-que-muda-para-empresas.html`, `tarifas-trump-impacto-empresas-portuguesas.html`).

**Artigos existentes em `instrumentos/`:**
- `portugal-2030.html`

**Regras criticas incorporadas em todas as skills:**
- Nunca usar travessao (--) em nenhum output
- Nunca incluir elemento `hero-gold-line` (CSS ou HTML)
- Autor selecionado por tema, nao aleatoriamente
- Paragrafo de fecho fixo obrigatorio
- Seccao "Perspetiva Open Capital" obrigatoria antes do fecho

**Why:** Utilizador quer workflow zero-friccao: fornece input -> Claude faz tudo ate deploy.
**How to apply:** Nunca sugerir scripts externos ou Python. Usar sempre skills.
