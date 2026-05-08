---
name: User collaboration style
description: User prefers progressive validation, hybrid strategies, tradeoff analysis before implementation, and concise terminology decisions
type: feedback
---

User pattern observed across multi-hour sessions: prefers progressive validation over big-bang delivery, hybrid (script + manual review) over pure-manual or pure-automated, and explicit tradeoff analysis before any implementation that touches scope.

Concrete signals:
- Asks "o que vais mudar exatamente?" before authorizing edits to skills/templates. Wants the diff to be visualizable in prose before it lands.
- Picks "híbrido" when offered manual vs automated, after the tradeoffs are presented as a table. Volume-of-work tradeoffs land well in 4-column tables (Como funciona | Tempo | Qualidade | Risco).
- Uses short signals to greenlight: "Ok", "Avança", "Podes avançar". Treat these as authorization to ship the next coherent unit, not all pending work at once.
- For terminology decisions (e.g. "Necessidade" vs "Objetivo"), wants honest analysis with a recommendation. Picks the more inclusive/honest term over grandiose marketing language even when positioning is premium.

**Why:** sustained over-explanation slows them down; sustained autonomy without analysis surfaces nasty surprises. The middle gear, "explain the tradeoff in 5 lines, recommend, then ship", is where they trust me to operate.

**How to apply:** when a task could go in 2-3 directions, present the tradeoff in a tight table or 3-bullet list, recommend, and wait for the short greenlight. After greenlight, ship one coherent piece (not an entire roadmap). Re-prompt for next unit explicitly.
