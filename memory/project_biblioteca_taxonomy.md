---
name: Biblioteca necessidades taxonomy (12 tags, locked)
description: 12-tag closed taxonomy for the demand-side filter on biblioteca.html, locked governance, mapping rules
type: project
---

Biblioteca de instrumentos tem filtro "Necessidade" com 12 tags fechadas (eixo demand-side, complementar a `setores` que e supply-side). Taxonomia foi desenhada para ser estavel e nao deve crescer ad-hoc.

12 tags (slug → label):
1. arranque-validacao → Arranque e validação de negócio
2. contratacao-rh → Contratação de RH
3. formacao-qualificacao → Formação e qualificação
4. id-ciencia → I&D e ciência
5. digitalizacao-ia → Digitalização e IA
6. investimento-produtivo → Investimento produtivo e equipamentos
7. capitalizacao-crescimento → Capitalização e crescimento
8. tesouraria-credito-garantias → Tesouraria, crédito e garantias
9. internacionalizacao → Internacionalização
10. sustentabilidade-energia-clima → Sustentabilidade, energia e clima
11. impacto-social-inclusao → Impacto social e inclusão
12. premios-visibilidade → Prémios e visibilidade

**Why:** taxonomia inverte o catalogo de "como a burocracia organiza" (fonte, categoria) para "como o utilizador procura" (necessidade). Captura a logica de decisao de PMEs/CFOs que chegam ao site com problema, nao com referencia regulamentar.

**How to apply:**
- Alteracoes a esta lista sao breaking change. Tem de ser feitas em 3 sitios em paralelo: `biblioteca.html` (dropdown), `.claude/commands/radar-writer.md` (passo 4g), `instruments-catalog.json` (campo `necessidades` em todos os instrumentos). Avisar antes de mexer.
- Fronteiras criticas a manter:
  - Setor = o que a empresa e. Necessidade = o que a empresa quer fazer. Eixos diferentes.
  - id-ciencia (descobrir conhecimento) vs investimento-produtivo (produzir pos-I&D).
  - digitalizacao-ia + investimento-produtivo: industria 4.0 leva ambas; software puro so digitalizacao.
  - arranque-validacao (pre-receita) vs capitalizacao-crescimento (com tracao).
- Nao usar wildcard "todos" como em setores. Forcar 1-3 tags por instrumento.
- Catalogo backfilled em 2026-05 com heuristica + correcao manual. Distribuicao dominante e id-ciencia (62%) por causa dos 608 instrumentos UE genuinamente focados em I&D, nao por over-tagging.
