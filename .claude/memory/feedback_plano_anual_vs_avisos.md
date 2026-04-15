---
name: Plano Anual vs Avisos Reais PT2030
description: Nunca usar dados de Plano Anual de Avisos. API aviso-2024 contem avisos reais, nao plano. Distinguir aberto vs previsto por data_inicio.
type: feedback
---

A API WordPress aviso-2024 nos portais PT2030 contem avisos REAIS publicados (com codigo FA, regulamento aprovado). O Plano Anual de Avisos e um PDF separado com previsoes que NAO correspondem aos dados efectivos.

**Why:** O utilizador detectou que estavam a ser publicados artigos com informacao do plano anual (datas prospectivas, dotacoes indicativas) que nao correspondia aos avisos reais quando abrem. O plano anual e sempre uma perspectiva e deve ser desconsiderado.

**How to apply:**
- Scanner deve usar APENAS secoes "Avisos" / "Avisos de Concurso", nunca "Plano Anual de Avisos"
- API aviso-2024 e segura - contem avisos publicados, nao plano
- Classificar avisos por data_inicio: se futuro = "previsto", se passado = "aberto"
- Guardar sempre o campo `link` da API como regulation_url (nunca URL generico do portal)
- Campo `acf.natureza` (Concurso/Convite) deve ser registado nas notes
