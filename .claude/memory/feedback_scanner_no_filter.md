---
name: Scanner must not filter by beneficiary type
description: Never filter instruments by beneficiario (privado/publico) in scanner - cover all types, all organizations, all sources
type: feedback
---

Scanner deve cobrir TODOS os tipos de instrumentos e beneficiarios sem excepcao.

**Why:** O scan inicial filtrou por beneficiario privado e registou 42 abertos quando o numero real era 500-1100. Isto subestimou o problema de escalabilidade em 10-25x e levou a decisoes arquiteturais erradas.

**How to apply:**
- Nunca filtrar por beneficiario no scanner (publico, privado, misto - tudo entra)
- Nunca tratar a API central do PT2030 como superset completo - os portais regionais tem avisos adicionais
- Cada programa regional (Norte, Centro, Lisboa, etc.) e uma fonte independente
- A decisao editorial (que artigos priorizar) e do writer, nao do scanner
