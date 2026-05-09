---
name: Sistema Editorial Open Capital
description: Series e subserias de marketing digital, skills criadas e estrutura de automacao
type: project
---

Sistema editorial com 7 series e 14 subserias. Foco atual: subserias com output para website, usando skills Claude Code (Option C, sem scripts externos).

**Skills editoriais (input manual, 1 artigo cada):**
- `/trend` -> Serie 1.2, artigo trend para website (`conhecimento/`), injecta card em conhecimento.html + atualiza index.html
- `/informativo` -> Serie 2.1, artigo informativo para website (`conhecimento/`), injecta card em conhecimento.html + atualiza index.html
- `/youtube` -> Serie 2.2, artigo informativo baseado em video do YouTube (`conhecimento/`), injecta card em conhecimento.html + atualiza index.html
- `/opiniao` -> Serie 6.2, opiniao controversa para website (`conhecimento/`), injecta card em conhecimento.html + atualiza index.html
- `/instrumento` -> Serie 3.1, instrumento de financiamento (`instrumentos/`), template editorial usado tambem pelo radar-writer

**Skills do radar (pipeline automatizado, 4 agentes independentes):**
- `/radar-scanner` -> descobre novos instrumentos, escreve queue.json/queue-overflow.json/queue-plano-anual.json
- `/radar-downloader` -> descarrega regulamentos da queue, max 10/run, deteta PAA e move para watchlist
- `/radar-monitor` -> verifica estados/prazos/dotacoes/integridade SHA1 dos PDFs em shards publicados, cobertura minima da watchlist
- `/radar-writer` -> cria artigos a partir da queue, sprint mode 5/sessao, prioridade absoluta PT2030, valida paridade catalog/shard/lookup ao final

**Pipeline skills conhecimento/ (trend, informativo, youtube, opiniao):**
1. Processar input (WebFetch se URL ou video)
2. Gerar HTML completo em `conhecimento/[slug].html`
3. Injetar card em `conhecimento.html` apos `<div class="articles-grid" id="articlesGrid">`
4. Atualizar contador `id="filterCount">X artigos</span>`
5. Atualizar destaques editoriais em `index.html` (seccao `id="conhecimento"`)
6. git add + commit + push -> GitHub Pages auto-deploy

**Pipeline skill instrumentos/ (instrumento, manual ou via radar-writer):**
1. Processar input (WebFetch, regulamento ou brief)
2. Gerar HTML completo em `instrumentos/[slug].html`
3. Adicionar entrada ao `instruments-catalog.json` (catalogo dinamico, biblioteca.html nao tem cards estaticos)
4. Adicionar ao shard correto + lookup + integrity hash
5. git add + commit + push -> GitHub Pages auto-deploy

**Catalogo dinamico:** `biblioteca.html` faz `fetch('instruments-catalog.json')` em runtime. NUNCA editar biblioteca.html manualmente para adicionar cards. So mexer no JSON.

**Numeros operacionais (snapshot 2026-05-09):**
- 1037 ficheiros HTML em `instrumentos/`
- 1037 entradas no catalogo (paridade 100%)
- 43 artigos em `conhecimento/`
- 921 hashes em `registry/integrity.json`
- 14 shards em `registry/shards/`

**Regras criticas incorporadas em todas as skills:**
- Nunca usar travessao (--) em nenhum output
- Nunca incluir elemento `hero-gold-line` (CSS ou HTML)
- Acordo Ortografico de 1990 (AO90) em PT-PT
- Autor selecionado por tema, nao aleatoriamente
- Paragrafo de fecho fixo obrigatorio
- Seccao "Perspetiva Open Capital" obrigatoria antes do fecho
- Nas skills de conhecimento: max 1 antitese por artigo

**Why:** Utilizador quer workflow zero-friccao: fornece input -> Claude faz tudo ate deploy.
**How to apply:** Nunca sugerir scripts externos ou Python para criar artigos. Usar sempre as skills.
