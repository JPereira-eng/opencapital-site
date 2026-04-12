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
  index.json          - contadores globais
  lookup.json         - dedup O(1)
  queue.json          - fila do writer
  shards/             - instrumentos publicados, por fonte
    pt2030-compete.json, pt2030-norte.json, ...
    eu-horizon.json, eu-other.json, ...
    pt-other.json, interreg.json
  archive/            - fechados antigos (trimestral)
```

Os ficheiros antigos (`registry.json`, `registry-queue.json`, `registry-published.json`) existem para referencia mas nao sao mais a fonte de verdade.
