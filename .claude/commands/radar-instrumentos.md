# Radar de Instrumentos v4.0: Orquestrador

**DEPRECADO em v4.0.** Este skill foi dividido em 4 skills independentes:

| Skill | Funcao | Comando |
|---|---|---|
| `/radar-scanner` | Descobrir novos instrumentos | Diario, 00:30 |
| `/radar-downloader` | Descarregar regulamentos | Diario, 02:00 |
| `/radar-monitor` | Verificar estados publicados | Diario, 11:00 |
| `/radar-writer` | Criar artigos (sprint de 5) | Diario, 06:00 |

## Se foste invocado como agente programado:

Os agentes antigos (radar-noite, radar-dia, radar-writer-manha, etc.) foram desactivados em 2026-04-12 durante a migracao v4.0. Se chegaste aqui por erro, nao executes nenhuma operacao. Reportar: "radar-instrumentos v3 invocado por erro. Agentes v4.0 devem ser usados."

## Se foste invocado manualmente:

Podes executar uma run completa (scan + download + monitor + write) usando as 4 skills em sequencia. Mas recomenda-se usar cada skill individualmente para melhor controlo.

### Estrutura de ficheiros v4.0:

```
registry/
  index.json          - contadores globais + source_last_checked
  lookup.json         - dedup O(1)
  queue.json          - fila do writer (max 100 items)
  queue-overflow.json - overflow quando queue >= 100
  shards/             - instrumentos publicados, por fonte
    pt2030-compete.json   - COMPETE 2030 apenas
    pt2030-pessoas.json   - PESSOAS 2030 (FSE+)
    pt2030-central.json   - API central, multi-programa
    pt2030-norte.json, pt2030-centro.json, pt2030-lisboa.json
    pt2030-other.json     - regionais menores (Alentejo, Algarve, Acores, Madeira, MAR, etc.)
    eu-horizon.json, eu-other.json, eic.json
    pt-other.json, interreg.json
  archive/            - fechados antigos (trimestral)
```

Os ficheiros antigos (`registry.json`, `registry-queue.json`, `registry-published.json`) existem para referencia mas nao sao mais a fonte de verdade.
