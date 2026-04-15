---
name: Radar v4.0 Architecture Decisions
description: Redesign decisions for scaling radar ecosystem - sharding, 4 skills, pipeline balancing, Phase 1 (19 agents) and Phase 2 plans
type: project
---

## Radar Ecosystem v4.0 - Decisoes de Arquitetura (2026-04-12)

### 10 Problemas Identificados e Solucoes Acordadas

1. **State files nao escalam** - Sharding por fonte/programa, indice ultra-leve, lookup.json para dedup O(1)
2. **Writer throughput baixo** - Sprint mode (5 artigos/batch, ate 2 batches/sessao = 10)
3. **Monitoring nao escala** - Batch monitoring via super-fontes, smart scheduling por risco
4. **Scanner nao cobre 85 fontes** - Prioridade por source_last_checked, 5 fontes/run
5. **Sem automacao** - 19 agentes programados (Fase 1)
6. **Single-threaded** - 4 skills independentes (scanner, downloader, monitor, writer)
7. **Catalogo client-side** - Paginado quando > 200 artigos
8. **Git/Pages limites** - Adiado
9. **Sem error recovery** - Commit por artigo, push pendentes no startup
10. **Deduplicacao O(n)** - lookup.json com indices por id e aviso_codigo

### Correcoes Criticas (4 bottlenecks resolvidos 2026-04-12)

- **Critico 1**: Writer commit por artigo (nao por batch) + push pendentes no startup
- **Critico 3**: source_last_checked per-source em registry/index.json
- **Medio 1**: Queue limitada a 100 items, overflow para queue-overflow.json
- **Medio 3**: Shard pt2030-compete subdividido em 3: compete, pessoas, central

### Correcoes de Dados

- PT2030 API NAO e superset completo (~220 de ~1500+ total)
- Programas regionais sao fontes independentes (sem covered_by)
- Paginacao: page=N (10/pagina), nao offset=N
- Nunca filtrar por tipo de beneficiario

### Estrutura de Shards (14 shards)

pt2030-compete, pt2030-pessoas, pt2030-central, pt2030-norte, pt2030-centro, pt2030-lisboa, pt2030-other, eic, eu-horizon, eu-other, pt-other, interreg

### Pipeline Fase 1 (Nascimento - 19 agentes, plano Max x5)

**Throughput alvo: ~32 artigos/dia, ~300 em 10 dias**

Pipeline interleaved: cada janela corre scanner→downloader→writer

| Janela C (19:00-00:00) | 7 agentes |
|---|---|
| scanner-C1 (19:15), monitor (19:45) |
| downloader-C1 (20:20), C2 (20:40), C3 (21:00) |
| writer-C1 (21:20), writer-C2 (23:00) |

| Janela D (00:00-05:00) | 8 agentes |
|---|---|
| scanner-D1 (00:15), scanner-D2 (00:45) |
| downloader-D1 (01:15), D2 (01:35), D3 (01:55), D4 (02:15) |
| writer-D1 (02:45) |
| downloader-D5 (04:30) |

| Janela E (05:00-09:00) | 3 agentes |
|---|---|
| downloader-E1 (05:15), E2 (05:35) |
| writer-E1 (06:00) |

| Janela B (15:30) | 1 agente |
|---|---|
| writer-emergencia (condicional, deadline < 30 dias) |

**Totais: 3 scanners + 10 downloaders + 5 writers + 1 monitor = 19**
**Tokens/dia: ~2.6M (17% do budget Max x5)**

### Pipeline Fase 2 (Maturidade - 7 agentes)

**Trigger: queue < 20 items durante 3 dias consecutivos**

Desactivar: scanner-C1, scanner-D2, 8 dos 10 downloaders, 3 dos 4 writers
Activar: monitor-2 (segundo monitor para cobrir 12+ shards)

Totais Fase 2: 2 scanners + 1 downloader + 2 writers + 2 monitors = 7
Tokens/dia: ~460K (3% do budget Max x5)

### IDs dos Agentes

Existentes (actualizados): radar-v4-scanner, radar-v4-downloader, radar-v4-monitor, radar-v4-writer, radar-v4-writer-noite, radar-v4-writer-emergencia
Novos (Fase 1): radar-f1-scanner-C1, radar-f1-scanner-D2, radar-f1-writer-C1, radar-f1-writer-D1, radar-f1-downloader-C1/C2/C3/D1/D2/D4/D5/E1/E2
Antigos (pausados): 18 agentes pre-v4.0, todos disabled
