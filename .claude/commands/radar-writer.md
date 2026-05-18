---
name: radar-writer
model: claude-sonnet-4-6
---

# Radar Writer v4.2: Criação de Artigos em Sprint

REGRA CRÍTICA: Nunca usar travessão (—) em nenhum texto gerado. Usar vírgula, ponto, hífen (-) ou reescrever a frase.

REGRA CRÍTICA DE ORTOGRAFIA: Aplicar sempre o Acordo Ortográfico de 1990 (AO90) em PT-PT. Usar as grafias atualizadas: ação (não acção), setor/setorial (não sector/sectorial), ativo/atividade/atual (não activo/actividade/actual), objetivo/objeto (não objectivo/objecto), direto/diretamente (não directo/directamente), exato/exatamente (não exacto/exactamente), aspeto (não aspecto), exceção/exceto (não exceptao/excepto), receção (não recepcao), adoção (não adopcao), reação (não reaccao), corretor (não correcto/correctamente), eletrico (não electrico), otimo (não optimo), detetar (não detectar), afetar (não afectar), projeto (não projecto), arquiteto (não arquitecto). Manter "facto", "factual", "contacto", "convicção", "tacto" (PT-PT preserva estas). Nunca gerar artigos com ortografia pre-1990.

Es o writer do sistema radar da Open Capital Advisory & Consultancy.
A tua missão e criar artigos de instrumentos de financiamento a partir da fila.

**Esta skill so escreve artigos.** Não descobre instrumentos, não descarrega regulamentos, não monitoriza estados.

---

## PASSO 0: CONFIGURACAO DE AMBIENTE

```bash
if [ -d "C:/Users/Utilizador/Desktop/opencapital-website" ]; then
  echo "AMBIENTE: LOCAL"
else
  echo "AMBIENTE: REMOTO"
fi
```

**Se LOCAL:** usar `C:/Users/Utilizador/Desktop/opencapital-website` como base (`$REPO`).
**Se REMOTO:** clonar e usar `/tmp/opencapital`. Limpar após push.

---

## FICHEIROS DE ESTADO (v4.2)

| Ficheiro | Quando ler/escrever |
|---|---|
| `registry/index.json` | Sempre |
| `registry/queue.json` | Sempre (regime "aviso") - escrita ao remover items concluídos ou PAA disfarçados |
| `registry/queue-catálogo.json` | Sempre (regime "catálogo") - escrita ao remover items concluídos ou PAA |
| `registry/queue-plano-anual.json` | Escrita quando defesa anti-PAA (PASSO 1.5) deteta PAA disfarçado |
| `.claude/commands/instrumento-template.md` | **OBRIGATÓRIO antes de escrever** |

---

## PASSO 0.5: RECUPERACAO DE TRABALHO PENDENTE (v4.14, 2026-05-17 REFORÇADA)

**Antes de iniciar qualquer batch, executar 3 verificações de recuperação em sequência:**

### Verificação 1: ficheiros não-commitados (mais crítico)

Se a sessão anterior criou ficheiros (artigos HTML, updates a catalog/shards) mas falhou ANTES do commit final, esses ficheiros estão "soltos" no working tree.

```bash
UNCOMMITTED=$(git -C "$REPO" status --short | wc -l)
if [ "$UNCOMMITTED" -gt "0" ]; then
  echo "RECUPERACAO: $UNCOMMITTED ficheiros não-commitados detectados. A commitar como recovery..."
  git -C "$REPO" add -A
  git -C "$REPO" commit -m "writer recovery: batch parcial recuperado da sessão anterior"
fi
```

### Verificação 2: commits locais não-pushed

Após Verificação 1, podem existir commits locais que não foram enviados (rate limit do push, falha de rede, etc.).

```bash
LOCAL_AHEAD=$(git -C "$REPO" rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$LOCAL_AHEAD" -gt "0" ]; then
  echo "RECUPERACAO: $LOCAL_AHEAD commits locais pendentes. A enviar..."
  git -C "$REPO" push origin main
fi
```

Se o push falhar (rejected por estar atrás do remote):
```bash
git -C "$REPO" pull --rebase origin main && git -C "$REPO" push origin main
```

### Verificação 3: validação de coerência state files

Após recovery, validar que os ficheiros de estado (queue.json, catalog, shards) estão coerentes:

```bash
# Validar JSON parse
for f in registry/queue.json registry/queue-plano-anual.json instruments-catalog.json registry/lookup.json; do
  python -c "import json; json.load(open('$REPO/$f'))" || echo "AVISO: $f tem JSON inválido"
done
```

Se algum JSON estiver inválido (incomum), **abortar batch** e reportar para intervenção manual.

**Garantia:** artigos criados em sessões anteriores que falharam (qualquer fase: pre-commit, pre-push, post-push) são recuperados na próxima sessão.

---

## MODO SPRINT (v4.14.1, 2026-05-17 — commit por artigo + push único)

O writer opera em **1 batch de 5 artigos por sessao**. Cada batch:

1. **Selecionar** 5 items da queue (PASSO 1) + pre-flight validation (PASSO 1.5)
2. **Para cada artigo:**
   - Criar HTML, atualizar catalog/shard/lookup
   - `git add` + `git commit -m "instrumento: [nome]"` (COMMIT INDIVIDUAL)
   - **NÃO push intermédio**
3. **Após o batch completo (ou parcial):** UM ÚNICO push:
   ```bash
   git push origin main
   ```
4. Terminar. Não iniciar novo batch.

**Racional v4.14.1 (revisão de v4.14):**
A v4.14 batchava commits para reduzir builds. Mas após análise (2026-05-17), confirmámos que:
- Build failures atribuídos a rate limit eram na verdade submódulos fantasma (`.claude/worktrees/*`) — corrigido em commit 687149a8
- Rate real de builds (17/dia, max 2-3/hora) está bem abaixo do limite GitHub Pages (10/hora)
- Granularidade do histórico (1 commit por artigo) tem valor editorial:
  - Atribuição clara de quando cada artigo foi publicado
  - Revert preciso de um único artigo se necessário
  - Mensagem de commit serve como "log de publicação"

**Trade-off aceitável:** 5 commits por batch = 1 push = 1 build do GitHub Pages (porque GitHub Pages triggera 1 build por push, não por commit). Logo, batch ou não-batch ao nível de commit dá o mesmo número de builds desde que push seja único.

**Limites por sessao:**
- Max 5 artigos por batch
- **1 batch por sessao = 5 artigos max**
- Se queue < 5: criar todos os que houver
- Se queue vazia: terminar imediatamente sem criar artigos

**REGRA DE SEGURANCA: Commit por artigo (granular), push único (eficiente).**
- Cada artigo é commitado individualmente após criação
- Se sessão falhar entre artigos: artigos já feitos estão commited localmente
- Se sessão falhar antes do push final: PASSO 0.5 da próxima sessão push
- Se sessão falhar mid-artigo (ficheiro parcial sem commit): PASSO 0.5 recupera via `git status --short`

**NUNCA push intermédio.** O push acontece UMA VEZ no final do batch. Isto garante 1 build por sessão writer (eficiência) sem perder granularidade do histórico.

---

## PASSO 1: Selecionar artigos

Ler **ambas as filas**: `registry/queue.json` (regime aviso) e `registry/queue-catálogo.json` (regime catálogo).

**Composicao do batch de 5 artigos:**
- Até 4 items de `queue.json` (regime aviso), ordenados por: **(1) shard `pt2030-*` antes de qualquer outro shard, (2) `priority_score` descendente dentro de cada grupo**
- 1 item de `queue-catálogo.json` (regime catálogo), o mais antigo na fila (FIFO - para garantir que todas as fontes de catálogo são cobertas em rotacao)
- Se `queue-catálogo.json` estiver vazia: usar o 5o slot para mais um item de `queue.json` (mesma regra de ordenacao PT2030 primeiro)
- Se `queue.json` estiver vazia mas `queue-catálogo.json` tiver items: processar até 5 items do catálogo

**REGRA DE PRIORIDADE PT2030 (absoluta, v4.1):** Qualquer item cujo `shard` comece por `pt2030-` (pt2030-central, pt2030-centro, pt2030-compete, pt2030-lisboa, pt2030-norte, pt2030-other, pt2030-pessoas) e selecionado **antes de qualquer item de outro shard** (eu-horizon, eu-other, pt-other, interreg, etc.), independentemente do `priority_score`. Um aviso PT2030 com score 5 vence um aviso Horizon com score 100. Os shards EU/resto so entram nos slots restantes após esgotar a tier PT2030. Razao: a Open Capital serve maioritariamente PME portuguesas; o catálogo deve crescer primeiro em instrumentos PT2030.

**Priorizar items com `status: "ready"`** (regulamento já descarregado) sobre `status: "pending"` **dentro de cada tier**. Ordem final dos 4 slots de `queue.json`:
1. PT2030 com `status: ready` (priority_score desc)
2. PT2030 com `status: pending` (priority_score desc)
3. Resto com `status: ready` (priority_score desc)
4. Resto com `status: pending` (priority_score desc)

O slot 5 (catálogo) não e afectado por esta regra — segue FIFO normal.

**IGNORAR completamente** items com `status: "plano_anual"` - são previsoes do plano anual, não avisos publicados. Não contar, não processar, não remover da queue.

Selecionar os primeiros 5 (ou menos) para este batch.

---

## PASSO 1.5: Defesa anti-PAA pre-flight (v4.13.1, 2026-05-13 REFORÇADA)

⚠️ **REGRA ABSOLUTAMENTE BLOQUEANTE — NUNCA CONTORNAR:**

> **Um artigo NUNCA pode ser publicado sem um regulamento técnico .txt válido no disco.** Sem .txt → SKIP. Sem exceções. WebFetch ao portal não substitui o ficheiro local. Conhecimento contextual do tema não substitui o regulamento.

### PRE-FLIGHT VALIDATION (NOVO v4.13.1)

**Antes de escrever QUALQUER artigo do batch (ANTES de gastar tokens de geração):**

Executar validação completa sobre os 5 items selecionados:

```python
def validate_batch(selected_items):
    """Devolve (valid, rejected) tuples."""
    valid, rejected = [], []
    for item in selected_items:
        # 1. regulation_local deve apontar para ficheiro existente
        rl = item.get('regulation_local')
        if not rl or not Path(rl).exists():
            rejected.append((item, 'regulation_local missing or file not on disk'))
            continue

        # 2. .txt deve ter >= 500 palavras (mínimo para regulamento mesmo curto)
        text = Path(rl).read_text(encoding='utf-8', errors='ignore')
        word_count = len(text.split())
        if word_count < 500:
            rejected.append((item, f'regulamento too short ({word_count} words)'))
            continue

        # 3. .txt NÃO pode conter marcadores PAA
        lower = text[:3000].lower()
        paa_keywords = [
            'plano anual de avisos', 'resumo de aviso do plano',
            'paa2026', 'paa202', 'aviso a publicar em:',
            'previsao aproximada', 'previsão aproximada',
        ]
        if any(k in lower for k in paa_keywords):
            rejected.append((item, f'PAA keyword detected in .txt'))
            continue

        # 4. Para PT2030 família: data_status deve ser "verified"
        if item.get('source_id') in FAMILIA_PT2030:
            if item.get('data_status') != 'verified':
                rejected.append((item, f'PT2030 sem data_status=verified ({item.get("data_status")})'))
                continue

        # 5. Item NÃO pode estar em registry/depublished.json
        if item.get('id') in DEPUBLISHED_SLUGS or item.get('codigo') in DEPUBLISHED_CODES:
            rejected.append((item, 'item em depublished.json'))
            continue

        valid.append(item)

    return valid, rejected
```

**Comportamento:**

1. **Pre-flight ANTES da escrita** — economiza tokens (não tentar gerar artigo para item que vai ser rejeitado depois).
2. **Para cada item rejected:**
   - Log estruturado: `[REJECTED] {item.id}: {reason}`
   - **Não tentar substituir por WebFetch ao portal** — só vai gerar PAA artigo
   - Se item PT2030 com `data_status: forecast` e regulamento PAA → mover para watchlist (status `plano_anual`)
   - Se item sem .txt → manter na queue como `pending` (downloader vai retentar)
3. **Substituir slots vazios:**
   - Após pre-flight, se restam menos de 5 items válidos, **selecionar mais items da queue por prioridade desc** e re-aplicar pre-flight
   - Continuar até ter 5 válidos ou esgotar elegíveis
4. **Só após pre-flight passar 5 items é que começa a escrita.**

### EXCLUSÕES ABSOLUTAS (qualquer das condições → NUNCA escrever)

```
NUNCA escrever artigo para item que:
  ❌ Não tem regulation_local apontando para .txt existente
  ❌ .txt tem < 500 palavras
  ❌ .txt contém keywords PAA
  ❌ É PT2030 família com data_status != "verified"
  ❌ Está em registry/depublished.json
  ❌ Slug ou codigo já existe noutro item publicado (duplicado)
```

### Histórico do bug (para contexto)

- **2026-05-12:** 11 PAAs publicados em 13-15 abril foram detectados retroativamente. Despublicados.
- **2026-05-13:** Agent do writer publicou 2 novos PAAs (gestao-recursos-hidricos-acores2030, combate-a-privacao-material-2-aviso). Despublicados. Esta regra v4.13.1 fecha definitivamente a brecha.

### Detalhes operacionais antigos (continuam válidos)

**Razão:** Em 2026-05-05, o radar-scanner v4.7 promoveu 114 items PAA por engano (acf.pdf populado mas com PAA placeholder, não com regulamento real). Embora o scanner v4.7.1 corrija isto via verificação 2-tier, o writer adiciona aqui defesa em profundidade. Catches: bugs futuros do scanner, items legados com status pendente herdado, qualquer anomalia onde regulamento local seja PAA.

**Para cada item selecionado nos 5 slots, ANTES de prosseguir para Passo 2:**

1. Determinar caminho do regulamento local: `regulamentos/[source_id]/[id].txt`
2. Se o ficheiro **não existe**:
   - Item ainda não foi descarregado pelo downloader. **Skip + remover do batch.**
   - Não devolver à watchlist (não sabemos se é PAA). Apenas evitar escrita prematura.
   - Log: "[id] sem regulamento local; downloader ainda não processou. Skip."
3. Se o ficheiro **existe**, ler conteúdo e procurar **case-insensitive** por qualquer keyword PAA:
   - `"Plano Anual de Avisos"`
   - `"Resumo de Aviso do Plano"`
   - `"Aviso a publicar em:"`
   - `"PAA202"` (qualquer ano)
   - `"previsão aproximada"` / `"previsao aproximada"`
4. **Se encontrar qualquer keyword:**
   - Item é PAA disfarçado de aviso publicado. **Não escrever.**
   - Mover item de `queue.json` (ou `queue-catálogo.json`) para `queue-plano-anual.json`:
     - Status: `plano_anual`
     - `download_error: "PAA detectado pelo writer pre-flight em [data] (palavra-chave: [match])"`
     - Apagar `regulation_local` (path) e o ficheiro físico para forçar re-download
   - Adicionar warning ao relatório do batch
   - Selecionar item alternativo da queue para este slot (próximo elegível)
5. **Se não encontrar:** prosseguir normalmente para Passo 2.

**Regra de paranoia:** este passo corre SEMPRE, mesmo em items com `status: "ready"`. O custo é trivial (1 grep por item) e os danos editoriais de um falso negativo (artigo público sobre PAA) seriam graves.

**REGRA CRÍTICA - O QUE E "PUBLICADO":**
Um item esta publicado SE E SOMENTE SE existir o ficheiro `instrumentos/[id].html` no repositorio.
- Estar no `lookup.json` NAO significa publicado - o scanner adiciona ao lookup ao descobrir
- Estar num shard NAO e suficiente por si so - o ficheiro HTML tem de existir
- NUNCA remover um item da queue sem ter criado o ficheiro HTML correspondente
- NUNCA apagar a queue com base em "já esta no lookup"

Se encontrares items na queue que já tem o ficheiro HTML em `instrumentos/`: remover da queue (e apenas nesses casos).
Se encontrares items na queue que NAO tem ficheiro HTML: são trabalho por fazer, manter na queue e escrever.

---

## PASSO 2: Ler template obrigatório

**ANTES de escrever qualquer artigo:**
```
Read .claude/commands/instrumento-template.md
```

Este ficheiro contem o template HTML completo, classes CSS, estrutura da navbar, hero, sidebar e footer. NUNCA escrever sem ter lido.

### Apresentação de códigos no artigo (v4.12, 2026-05-12)

**Para items da família PT2030** (source_id em portugal-2030, compete-2030, norte-2030, centro-2030, lisboa-2030, alentejo-2030, algarve-2030, pessoas-2030, sustentavel-2030, madeira-2030, acores-2030, pat-2030, mar-2030):

1. **Se `human_code` está populado** (e.g., "ACORES2030-2026-12"):
   - Mostrar `human_code` como **código principal** do aviso no header e sidebar.
   - Mostrar `codigo_api` como referência secundária ("ref API: FA0302/2025") em caption pequena.
   - Exemplo de HTML: `<div>Código: <strong>ACORES2030-2026-12</strong> <span class="ref-api">(ref API: FA0302/2025)</span></div>`

2. **Se `human_code` está vazio**:
   - Mostrar apenas `codigo_api` ou `aviso_codigo` como antes.

**Para items de OUTRAS famílias** (EU Horizon, ANI, IAPMEI, etc.):
- Mostrar o código tal como veio da API (`aviso_codigo` ou equivalente).
- NÃO aplicar lógica human_code (não é relevante).

**Slug interno (id) NUNCA muda** com base em human_code. Apenas o display do código no artigo.

---

## PASSO 3: Obter regulamento

Para cada artigo selecionado, seguir esta cascata:

1. **Se `regulation_local` existe:** Ler diretamente. Se > 3000 palavras: usar primeiras 3000.
2. **Se `regulation_local` e null mas `regulation_url` existe:** Usar WebFetch.
3. **Se tudo falhou:** Usar WebSearch + dados do campo `notes`. Artigos criados: 0 e sempre falha do agente.

### PASSO 3.5: Validar conteudo (última barreira antes de escrever)

Após obter o texto do regulamento (por qualquer metodo), verificar se contem QUALQUER um destes markers (case-insensitive):
- "Plano Anual de Avisos"
- "Resumo de Aviso do Plano"
- "PAA2026" ou "PAA202"
- "Aviso a publicar em:"

**Se encontrar:** o item e um documento de plano anual, não um aviso publicado. NAO escrever o artigo. Atualizar o item na queue para `status: "plano_anual"`. Passar ao próximo item do batch.

Esta verificação existe como defesa contra falhas do downloader, que deveria ter bloqueado estes items antes.

---

## PASSO 4: Definir metadados, selecionar autor e criar artigo

### 4a. Metadados do artigo

Com o regulamento, definir:
- `slug`: kebab-case, descritivo (ex: `sifide-2`, `rfai`, `horizonte-europa`)
- `nome_instrumento`: nome completo e oficial
- `categoria_badge`: uma de `Financiamento Público`, `Investimento Privado`, `Fiscal`, `Inovação`, `Estrategia`
- `categoria_card`: código para o catálogo (ver mapeamento 4c)
- `estado`: `aberto`, `fechado`, ou `previsto`
- `fonte`: código da fonte/programa (`pt2030`, `ani`, `iapmei`, `bfomento`, `aicep`, `at`, `pventures`, `compete`, `prr`, `ue`)
- `beneficiario`: lista separada por virgulas (`empresa`, `entidade-pública`, `associacao`, `ensino-investigação`, `empreendedor`)
- `setores`: array de setores elegíveis (ver 4f). Campo invisivel, usado apenas pelo filtro do catálogo.
- `regiao`: lista das regioes. Se nacional: `norte,centro,lisboa,alentejo,algarve,acores,madeira`. Se regional: apenas as cobertas.
- `hero_tagline`: 1 frase clara, max 20 palavras
- `meta_fact_1` a `meta_fact_4`: label + valor para a meta-bar do hero (ex: Dotacao: €23 mil milhoes)
- `sidebar_factos`: 5 a 8 pares chave/valor para o card "Factos Rapidos" na sidebar
- `sidebar_cta_text`: texto contextualizado ao instrumento (ex: "Quer calcular o beneficio SIFIDE para a sua empresa?")
- `instrumentos_relacionados`: 3 a 5 links para outros artigos em `instrumentos/`

**Guidance para meta-bar por tipo de instrumento (não obrigatória - escolher os 4 factos mais relevantes):**

| Tipo | meta_fact_1 | meta_fact_2 | meta_fact_3 | meta_fact_4 |
|---|---|---|---|---|
| Fundo público (PT2030, PRR) | Dotacao | Taxa cofinanciamento | Prazo | Beneficiario |
| Incentivo fiscal (SIFIDE, RFAI) | Beneficio fiscal | Despesas elegíveis | Período aplicação | Elegibilidade |
| Banco (linhas credito, garantias) | Montante maximo | Prazo amortizacao | Taxa/Spread | Garantias exigidas |
| Fundo VC/PE | Ticket medio | Fase de investimento | Setores alvo | Dimensao fundo |
| Premio/Voucher | Valor premio | Prazo candidatura | Elegibilidade | Periodicidade |
| Acelerador | Duracao programa | Equity/não-equity | Setores | Perfil participante |

**O writer tem liberdade editorial total.** Pode usar factos diferentes se forem mais relevantes para o instrumento específico. Esta tabela existe apenas para guiar em tipos de instrumentos menos comuns (bancos, VC, premios) que ainda não tem muitos artigos de referência.

### 4b. Seleção de autor

Escolher o autor com base na área de especialidade do instrumento. Aplicar pela ordem indicada, parar na primeira que encaixar:

1. Fundos europeus e candidaturas não reembolsáveis (Portugal 2030, PRR, COMPETE 2030, Horizonte Europa, EIC Accelerator): **Mara Ferreira** - Técnica de Candidaturas e Incentivos
2. Incentivos fiscais ao investimento (RFAI, DLRR, CFI, Patent Box): **André Carvalho** - Técnico de Candidaturas e Incentivos
3. Premios de inovação e vouchers (SIFIDE II, premios, vouchers IAPMEI): **André Carvalho** (se foco fiscal) ou **Sofia Costa** - Especialista I&D e Inovação (se foco I&D/tecnologico)
4. Instrumentos de divida e credito (Banco de Fomento, linhas de credito, garantias): **Pedro Nunes** - Consultor de Financiamento
5. Investimento privado (VC, PE, Business Angels, Crowdfunding): **Luís Gomes** - Analista Financeiro ou **Mariana Costa** - Finance Lead
6. Internacionalizacao e atracao de investimento (AICEP, SAI): **Miguel Santos** - Business Developer

Outros autores disponíveis:
- **Johnson Semedo** - Gestor de Projetos (execução operacional, PME)
- **Carla Sousa** - Gestora de Projetos (planeamento, reporting, financiamento público)
- **Inês Teixeira** - Consultora Junior (análise setorial, tendências emergentes)
- **João Silva** - Consultor Junior (competitividade, benchmarking setorial)
- **Rita Ferreira** - Marketeer e Copywriter (economia criativa, consumo)

**Jorge Pereira não pode ser selecionado para artigos de instrumento.**

**Mapeamento de fotos (usar com prefix `../Retratos Equipa/`):**
Jorge Pereira: `retrato_jorgepereira.png` · Mariana Costa: `retrato_marianacosta.png` · Sofia Costa: `retrato_sofiacosta.png` · Luís Gomes: `retrato_luísgomes.png` · Pedro Nunes: `retrato_pedronunes.png` · André Carvalho: `retrato_andrecarvalho.png` · Mara Ferreira: `retrato_maraferreira.png` · Johnson Semedo: `retrato_Johnson Semedo.png` · Carla Sousa: `retrato_carlasousa.png` · Inês Teixeira: `retrato_inêsteixeira.png` · João Silva: `retrato_joaosilva.png` · Miguel Santos: `retrato_miguelsantos.png` · Rita Ferreira: `retrato_ritaferreira.png`

### 4c. Mapeamento categoria_card → label

- `nr` → "Não Reembolsavel" (fundo perdido, subsidio, premio, voucher)
- `div` → "Divida" (empréstimo, linha de credito, garantia)
- `priv` → "Investimento Privado" (VC, PE, business angels, crowdfunding)
- `hib` → "Hibridos" (componente reembolsável + não reembolsável)
- `fiscal` → "Incentivos Fiscais" (deducao IRC, beneficio fiscal)
- `outros` → "Outros" (internacionalização, apoio técnico)

### 4d. Highlights do card (para instruments-catalog.json)

Cada card tem 3 highlights com função fixa:
- `highlight0`: beneficio principal em poucas palavras (ex: "Até 65% fundo não reembolsável", "Divida sem juros com período de carencia", "Deducao fiscal até 82.5% das despesas de I&D")
- `highlight1`: tipos de beneficiarios (ex: "PME e Grandes Empresas", "Entidades públicas", "Startups e empreendedores")
- `highlight2`: localizacoes (ex: "Norte, Centro, Lisboa", "Madeira", "Nacional")

### 4e. Criar artigo

Criar `instrumentos/[slug]/index.html` seguindo TODAS as regras do CLAUDE.md e do template instrumento.md.

### 4f. Definir setores (campo invisivel)

**Pergunta orientadora:** "Que beneficiario pode ser alvo de financiamento a este instrumento? A que setor(es) pertence?"

Preencher o array `setores` no `instruments-catalog.json` com 1 a N códigos da tabela. O campo e invisivel (so usado pelo filtro do catálogo), logo o artigo em si não menciona setores - limita-se a esclarecer o tipo de beneficiario elegível.

**Valores permitidos (10 setores + wildcard):**

| Código | Beneficiario típico |
|---|---|
| `agroalimentar` | Agricultores, agroindustria, transformação alimentar, floresta |
| `comercio` | Retalho, comercio por grosso, distribuição |
| `economia-criativa` | Cultura, design, audiovisual, media, artes, patrimonio |
| `energia-ambiente` | Renovaveis, eficiência energetica, cleantech, economia circular, residuos, agua |
| `industria` | Industria transformadora, metalomecanica, textil, quimica, materiais |
| `mar-pescas` | Pescas, aquicultura, biotecnologia marinha, economia azul |
| `mobilidade-transportes` | Transporte passageiros/mercadorias, logistica, mobilidade eletrica/sustentavel, ferrovia, portos, aeroportos |
| `saude-ciencias-vida` | Saude, biotecnologia, farmaceutica, medtech, dispositivos medicos |
| `tecnologia-digital` | TIC, software, deep tech, startups digitais, espaco, IA |
| `turismo` | Hotelaria, restauracao, operadores turisticos, animacao turistica |
| `todos` | **Wildcard** para instrumentos transversais (aparece em qualquer filtro de setor) |

**Regras de decisão:**

1. Se o instrumento tem restrição setorial explicita (CAE elegíveis, ou "apenas empresas de X"): listar os setores cobertos.
2. Se o instrumento cobre 2-3 setores específicos: listar todos (ex: `["industria", "energia-ambiente"]` para descarbonizacao industrial).
3. Se o instrumento e transversal (qualquer empresa/entidade): usar `["todos"]`.
4. Se o beneficiario e académico/investigação sem foco setorial: usar `["todos"]`.
5. Não combinar `todos` com outros setores (e redundante).

**Exemplos:**
- SIFIDE II (qualquer empresa com I&D) → `["todos"]`
- Linha Turismo de Portugal → `["turismo"]`
- STEP Descarbonizacao Industrial → `["industria", "energia-ambiente"]`
- EIT Urban Mobility → `["mobilidade-transportes"]`
- EIC Accelerator (startups deep tech multi-setor) → `["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"]`
- PEPAC / Mar 2030 → `["agroalimentar"]` / `["mar-pescas"]`
- Linha Banco de Fomento generica → `["todos"]`

### 4g. Definir necessidades (campo invisivel)

**Pergunta orientadora:** "Que necessidade da empresa este instrumento resolve?"

Preencher o array `necessidades` no `instruments-catalog.json` com 1 a 3 códigos da tabela. O campo e invisivel (so usado pelo filtro "Necessidade" do catálogo), logo o artigo em si não menciona necessidades - limita-se a explicar o que o instrumento financia.

Eixo demand-side, complementar a `setores` (que e supply-side por industria). Setor responde "que tipo de empresa beneficia?". Necessidade responde "que problema/objetivo da empresa o instrumento resolve?".

**Valores permitidos (12 tags fechadas, sem wildcard):**

| Código | Necessidade que resolve |
|---|---|
| `arranque-validacao` | Criar empresa, validar ideia de negocio, prova de conceito, pre-receita |
| `contratacao-rh` | Contratar pessoas, criar postos de trabalho, estagios, integração laboral |
| `formação-qualificação` | Formar e qualificar a equipa existente, upskilling, certificacao profissional |
| `id-ciencia` | Investigação cientifica, I&D&I, projetos académicos, ciencia aplicada |
| `digitalização-ia` | Digitalizar processos, software, automacao, IA, transformação digital |
| `investimento-produtivo` | Investir em equipamentos, instalacoes, capacidade produtiva, ativos fixos tangiveis |
| `capitalização-crescimento` | Equity, growth capital, scale-up, reforco de capitais próprios, expansão |
| `tesouraria-credito-garantias` | Liquidez, working capital, dividas correntes, linhas de credito, garantias mutuas |
| `internacionalização` | Exportar, abrir mercados externos, presença internacional, missões empresariais |
| `sustentabilidade-energia-clima` | Descarbonizacao, eficiência energetica, renovaveis, economia circular, clima |
| `impacto-social-inclusao` | Inclusao social, economia social, comunidades vulneraveis, igualdade |
| `premios-visibilidade` | Premios, reconhecimento, distincoes, eventos, visibilidade institucional |

**Regras de decisão:**

1. Atribuir 1 a 3 tags por instrumento. **Mais de 3 e sinal de etiquetagem preguicosa.**
2. Sem wildcard "todos" - aqui forcar a escolha mesmo em instrumentos transversais. Um instrumento que financia "tudo" normalmente serve `capitalização-crescimento` ou `tesouraria-credito-garantias`.
3. **Ortogonalidade com setores:** Setor = *o que a empresa e* (industria, agroalimentar). Necessidade = *o que a empresa quer fazer* (digitalizar, internacionalizar). Não confundir.
4. **Fronteiras críticas:**
   - `id-ciencia` (fase de conhecimento: SIFIDE, ANI, FCT, Horizonte) vs `investimento-produtivo` (aplicação industrial pos-I&D: RFAI, PT2030 inovação produtiva). I&D = descobrir. Investimento produtivo = produzir.
   - `digitalização-ia` vs `investimento-produtivo`. Industria 4.0 / automacao fabril = ambas. Software puro = so digitalização. Equipamento sem componente digital = so investimento produtivo.
   - `arranque-validacao` (pre-receita, ideia em validacao) vs `capitalização-crescimento` (empresa com tracao a procura de escala). Não misturar.
5. Se duvida entre duas tags fechadas, escolher a mais restritiva. Não etiquetar com 5 tags "para não falhar".

**Exemplos:**
- SIFIDE II → `["id-ciencia"]` (fiscal puro de I&D, single-tag)
- IEFP Estagios INICIAR → `["contratacao-rh", "formação-qualificação"]` (estagio = contrata + qualifica)
- EIC Accelerator → `["arranque-validacao", "id-ciencia", "capitalização-crescimento"]` (startup deep tech com grant + equity)
- RFAI → `["investimento-produtivo", "contratacao-rh"]` (exige criação de postos)
- COMPETE SIAC Internacionalizacao → `["internacionalização"]`
- Sustentavel 2030 (descarbonizacao industrial) → `["sustentabilidade-energia-clima", "investimento-produtivo"]`
- Vouchers IAPMEI Digitalizacao → `["digitalização-ia"]`
- Linha BPF Garantida PME → `["tesouraria-credito-garantias"]`
- Programa Bairros Mais Resilientes → `["impacto-social-inclusao"]`
- Premios Nacionais de Inovação COTEC → `["premios-visibilidade"]`
- Portugal Ventures Call (early-stage tech) → `["arranque-validacao", "capitalização-crescimento"]`
- ANI Born from Knowledge → `["arranque-validacao", "id-ciencia"]`

---

## PASSO 5: Atualizar catálogo

Adicionar entrada ao FINAL de `instruments-catalog.json > instruments`:

```json
{
  "id": "[SLUG]",
  "category": "[CAT]",
  "category_label": "[LABEL]",
  "estado": "[ESTADO]",
  "status_text": "[TEXTO]",
  "status_class": "status-[open/closed/planned/cont]",
  "fonte": "[FONTE]",
  "beneficiario": "[BENEF]",
  "setores": ["[SETOR1]", "[SETOR2]"],
  "necessidades": ["[NECESSIDADE1]", "[NECESSIDADE2]"],
  "regiao": "[REGIAO]",
  "title": "[NOME]",
  "tagline": "[TAGLINE]",
  "highlight0": "[BENEFICIO_PRINCIPAL]",
  "highlight1": "[BENEFICIARIOS]",
  "highlight2": "[LOCALIZACOES]",
  "href": "/instrumentos/[SLUG]/",
  "featured": false
}
```

**Nota:** `setores` e `necessidades` são ambos obrigatórios. Usar valores das tabelas em 4f e 4g respetivamente. `setores` aceita `["todos"]` para transversais; `necessidades` não tem wildcard, escolher 1-3 códigos sempre.

**REGRA CRÍTICA:** Nunca editar `biblioteca.html`. Catálogo e 100% dinâmico via JSON.

---

## PASSO 6: Atualizar estado

Para cada artigo criado:

1. **Remover da queue correcta**: se o item veio de `queue.json` remover de `queue.json`; se veio de `queue-catálogo.json` remover de `queue-catálogo.json`
2. **Adicionar ao shard** (`registry/shards/[shard].json`):
```json
{ "id": "[slug]", "file": "instrumentos/[slug]/index.html", "source": "[source_id]", "state": "[estado]", "last_check": "[hoje]" }
```
3. **Adicionar ao lookup** (`registry/lookup.json`):
```json
"by_id": { "[slug]": true },
"by_aviso_codigo": { "[código]": "[slug]" }
```
4. **Calcular SHA1 do regulamento e gravar em `registry/integrity.json`** (apenas regime aviso):
   ```
   sha1sum "$REPO/regulamentos/[source_id]/[slug].txt" (ou .pdf)
   ```
   Adicionar entrada:
   ```json
   "[slug]": { "sha1": "[hash]", "checked": "[hoje]", "size": [bytes], "source_dir": "[source_id]", "file": "[slug].txt" }
   ```
   Esta operacao garante que o monitor pode detectar adendas/revisoes no futuro. Saltar para regime catálogo (sem regulamento formal).

5. **Atualizar index** (`registry/index.json`):
   - **Totals globais:** `totals.published` + 1, `totals.in_queue` - 1, `totals.[open/planned]` + 1
   - **Counters por shard (OBRIGATORIO, nunca omitir):** para o shard tocado, incrementar TODOS estes campos correctos:
     - `count` + 1
     - `published` + 1 (ESSENCIAL — campo historicamente em falta nos shards PT2030; nunca deixar este passo de fora)
     - `open` + 1 OU `planned` + 1 OU `closed` + 1 conforme o estado do item
   - `_meta.last_writer_run`: hoje
   - Se algum dos campos `published`/`open`/`closed`/`planned` ainda nao existir no objeto do shard, criar com valor 1 (nunca assumir que ja existe).

6. **Auto-validacao de paridade (v4.3, 2026-05-09):**
   Apos os passos 1-5, validar localmente:
   - O ficheiro `instrumentos/[slug]/index.html` existe? Se não: ABORTAR e reportar erro grave.
   - O slug aparece em `instruments-catalog.json` exactamente uma vez? Se aparece 0 vezes: re-aplicar passo 5 da skill (adicionar entrada). Se aparece >1 vez: remover duplicados mantendo o primeiro.
   - O slug aparece no shard correcto? Se não: re-aplicar passo 6.2.
   - O slug aparece em `lookup.json > by_id`? Se não: re-aplicar passo 6.3.
   Esta verificacao deteta regressoes onde o agente cria o HTML mas falha ou pula passos seguintes (causa raiz dos 13 orfaos detectados em 2026-05-09).

---

## PASSO 7: Deploy (commit por artigo + push único — v4.14.1, 2026-05-17)

### 7a. Commit por artigo (após cada artigo criado nos passos 4-6):

Antes do commit, preencher os marcadores de footer e navbar (o template emite `<!-- NAVBAR:START/END -->` e `<!-- FOOTER:START/END -->` — nunca embeber HTML manualmente):

```bash
python build_footer.py "instrumentos/[slug]/index.html"
python build_navbar.py "instrumentos/[slug]/index.html"
```

Depois commit:

```bash
git -C "$REPO" add instrumentos/[slug]/index.html instruments-catalog.json registry/
git -C "$REPO" commit -m "instrumento: [nome do instrumento]"
```

**Cada artigo tem o seu próprio commit.** History granular permite atribuição precisa e revert pontual.

### 7b. UM ÚNICO push após batch completo (5 commits ou menos):

```bash
git -C "$REPO" push origin main
```

Se push falhar: `git -C "$REPO" pull --rebase origin main && git -C "$REPO" push origin main`

**Eficiência:** 1 push = 1 trigger do GitHub Pages = 1 build (mesmo com 5 commits push'ados juntos). Granularidade do histórico **não custa** builds extras.

### 7c. Recovery garantido (Passo 0.5)

Cenários de falha cobertos pelo PASSO 0.5 da próxima sessão:

| Onde falhou | Estado | Como recupera |
|---|---|---|
| Mid-criação artigo 3 | Ficheiro parcial sem commit | V1: `git status --short` + commit "recovery: batch parcial" |
| Após criar 3 commits, antes push | 3 commits locais | V2: `git push origin main` |
| Rate limit/network durante push | Commits locais preservados | V2: retry push |
| Pre-flight rejeita item | Sem commit | Pre-flight skip; substituir slot |

**Não há perda possível.** Cada artigo está commited individualmente, push acontece UMA vez no fim.

**Após push bem-sucedido:** Terminar sessao. O próximo writer agendado tratara dos restantes.

---

## REGRAS DE SEGURANCA

1. **Max 5 artigos por sessao (1 batch). Terminar após o push, nunca iniciar segundo batch.**
2. **Nunca criar artigo sem ler instrumento.md primeiro.**
3. **Nunca editar biblioteca.html.**
4. **Nunca duplicar.** Verificar lookup antes de publicar.
5. **Artigos criados: 0 e sempre falha do agente.** Mesmo sem regulamento, os dados do campo notes são suficientes.
6. **Commit entre batches.** Nunca acumular mais de 5 artigos sem commit.

---

## RESUMO

```
BATCH UNICO (1 vez por sessao):
  0. PASSO 0.5: Recovery (uncommitted + unpushed)
  1. Ler queue.json + instrumento.md
  2. Se queue vazia: terminar imediatamente
  3. Selecionar até 5 items: PT2030 sempre primeiro (qualquer shard pt2030-*),
     depois resto. Dentro de cada tier: ready antes de pending, score desc.
  4. PRE-FLIGHT validation (PASSO 1.5): rejeitar items inválidos, substituir
  5. Para cada item válido:
     a. Ler regulamento, criar HTML, atualizar catálogo/shard/lookup/index
     b. git add + git commit "instrumento: [nome]"  (commit individual)
  6. UM ÚNICO git push após todos os commits (v4.14.1)
  7. Terminar. Não iniciar segundo batch.

Reportar: "Writer: [N] artigos criados. Fila restante: [N]."
```
