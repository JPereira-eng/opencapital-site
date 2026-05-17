---
name: instrumento
model: claude-sonnet-4-7
---

# Série 3.1 - Publicar Instrumento (caminho manual)

REGRA CRÍTICA: Nunca usar travessao (--) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

REGRA CRÍTICA DE ORTOGRAFIA: Aplicar sempre o Acordo Ortografico de 1990 (AO90) em PT-PT. Ver `instrumento-template.md` para a lista completa de grafias.

Es a skill de publicacao manual de instrumentos da Open Capital Advisory & Consultancy.

**Esta skill e o caminho manual.** Recebe um input livre (URL, regulamento, brief, ficha tecnica) e cria um artigo na pasta `instrumentos/`, atualizando o catalogo dinamico, shards, lookup, integrity e fazendo deploy. Para criacao automatizada a partir da queue do radar, usar `/radar-writer` em vez disto.

**Input recebido:** $ARGUMENTS

---

## ARQUITETURA — porque esta skill existe separada do radar-writer

O `radar-writer` orquestra a publicacao a partir da `queue.json` (descoberta automatica pelo scanner). Esta skill orquestra a publicacao a partir de input manual. Ambas partilham:

- `instrumento-template.md` (regras editoriais + template HTML, fonte unica da verdade visual)
- A logica de publicacao (atualizacao de catalogo, shards, lookup, integrity)
- A regra de auto-deploy

A unica diferenca e a origem do input: queue automatica vs input manual.

---

## PASSO 0: CONFIGURACAO DE AMBIENTE

```bash
if [ -d "C:/Users/Utilizador/Desktop/opencapital-website" ]; then
  echo "AMBIENTE: LOCAL (Utilizador)"
elif [ -d "C:/Users/jmcpe/Desktop/opencapital-site" ]; then
  echo "AMBIENTE: LOCAL (jmcpe)"
else
  echo "AMBIENTE: REMOTO"
fi
```

Usar a pasta correta como `$REPO`. Se REMOTO, clonar `https://github.com/JPereira-eng/opencapital-site.git` para `/tmp/opencapital`.

---

## PASSO 1: Ler a fonte unica da verdade editorial

**OBRIGATORIO antes de tudo:**

```
Read .claude/commands/instrumento-template.md
```

Este ficheiro contem identidade editorial, logica da Serie 3.1, building blocks, secao obrigatoria "Para que serve", regras de elegibilidade geografica/setorial, regra de fecho fixo, mapeamentos de categorias/setores/necessidades, e o template HTML completo.

**Nunca escrever um artigo sem ter lido este ficheiro.** As regras evoluem com o tempo e a memoria nao substitui leitura fresca.

---

## PASSO 2: Processar input

O input pode vir em varios formatos:

1. **URL** (regulamento, ficha tecnica, pagina oficial): usar `WebFetch` para extrair o conteudo.
2. **PDF/TXT local em `regulamentos/[source]/[slug].txt`**: ler diretamente.
3. **Brief descritivo livre** colado no prompt: usar como base, complementar com `WebSearch` se necessario.
4. **Ficheiro local fora de regulamentos/**: ler com `Read`.

**Validacao anti-PAA (mesma logica do radar-writer):**

Se o conteudo recolhido contem QUALQUER um destes markers (case-insensitive):
- "Plano Anual de Avisos"
- "Resumo de Aviso do Plano"
- "PAA2026" / "PAA202[0-9]"
- "Aviso a publicar em:"
- "previsao aproximada"

ABORTAR. Reportar ao utilizador: "O documento fornecido e Plano Anual, nao um aviso publicado. Nao posso publicar artigos sobre PAAs (decisao editorial fixa). Verifique se existe regulamento real."

---

## PASSO 3: Definir metadados editoriais

Seguir as mesmas regras do PASSO 4 do `radar-writer` (que tambem ficam descritas em `instrumento-template.md` quando aplicavel):

- `slug`: kebab-case, descritivo
- `nome_instrumento`: nome completo e oficial
- `categoria_badge`: "Financiamento Publico" / "Investimento Privado" / "Fiscal" / "Inovacao" / "Estrategia"
- `categoria_card`: codigo para o catalogo (`nr` / `div` / `priv` / `hib` / `fiscal` / `outros`)
- `estado`: `aberto` / `fechado` / `previsto` / `cont` (catalogo continuo)
- `fonte`: codigo (`pt2030`, `ani`, `iapmei`, `bfomento`, `aicep`, `at`, `pventures`, `compete`, `prr`, `ue`)
- `beneficiario`: lista CSV (`empresa`, `entidade-publica`, `associacao`, `ensino-investigacao`, `empreendedor`)
- `setores`: array (ver tabela completa em `instrumento-template.md`/passo 4f do `radar-writer.md`)
- `necessidades`: array de 1 a 3 codigos (ver tabela em `radar-writer.md` passo 4g)
- `regiao`: lista CSV ou `nacional`
- `hero_tagline`, `meta_fact_1` a `meta_fact_4`, `sidebar_factos` (5-8 pares), `sidebar_cta_text`, `instrumentos_relacionados` (3-5)

**Selecao de autor:** seguir tabela do `radar-writer.md` passo 4b. Ler essa skill para a tabela completa se duvidoso.

**Highlights do card (para o catalogo):**
- `highlight0`: beneficio principal em poucas palavras
- `highlight1`: tipos de beneficiarios
- `highlight2`: localizacoes

**Shard:** decidir o shard adequado para o item:
- PT2030 central / regionais → `pt2030-compete`, `pt2030-norte`, `pt2030-centro`, `pt2030-lisboa`, `pt2030-pessoas`, `pt2030-other`
- Horizonte Europa / EIC → `eu-horizon` ou `eic`
- Outros EU → `eu-other`
- Interreg → `interreg`
- Catalogo regime continuo (VC, BA, bancos, premios, aceleradores) → `catalogo-vc`, `catalogo-ba`, `catalogo-bancos`, `catalogo-premios`, `catalogo-aceleradores`, `catalogo-crowdfunding`
- Privado individual (BAs nominais) → `priv-ba`
- Outros nacionais (IEFP, IFAP, etc.) → `pt-other`

---

## PASSO 4: Criar o artigo HTML

Aplicar **literalmente** o template HTML de `instrumento-template.md`:

1. Substituir todos os placeholders `[NOME_INSTRUMENTO]`, `[HERO_TAGLINE]`, `[META_FACT_*]`, `[CORPO_DO_ARTIGO]`, `[AUTOR]`, `[AUTOR_FOTO]`, `[AUTOR_CARGO]`, `[SIDEBAR_FACTOS]`, `[SIDEBAR_CTA_TEXT]`, `[INSTRUMENTOS_RELACIONADOS]`.
2. Compor o corpo seguindo a logica editorial da Serie 3.1 (raciocinio obrigatorio, building blocks adequados ao tipo de instrumento, secao "Para que serve" obrigatoria, "Perspetiva Open Capital" obrigatoria antes do fecho, paragrafo de fecho fixo).
3. Respeitar todas as regras criticas: AO90, sem travessao, sem `hero-gold-line`, sem secoes "Como candidatar", classes de cor consistentes para estado.
4. Escrever em `instrumentos/[slug]/index.html`.

**Comprimento:** 1500-2500 palavras (regra geral). 800-1200 palavras se material de regime catalogo limitado.

---

## PASSO 5: Adicionar ao catalogo dinamico

**REGRA CRITICA: nunca editar `biblioteca.html`. O catalogo e 100% dinamico via JSON.**

Adicionar entrada ao FINAL de `instruments-catalog.json > instruments`:

```json
{
  "id": "[slug]",
  "category": "[categoria_card]",
  "category_label": "[Label]",
  "estado": "[estado]",
  "status_text": "[ex: Aberto ate 31/12/2026]",
  "status_class": "status-[open/closed/planned/cont]",
  "fonte": "[fonte]",
  "beneficiario": "[beneficiario]",
  "setores": ["[setor1]", "[setor2]"],
  "necessidades": ["[nec1]", "[nec2]"],
  "regiao": "[regiao]",
  "title": "[nome curto para card]",
  "tagline": "[1 frase clara, max 20 palavras]",
  "highlight0": "[beneficio principal]",
  "highlight1": "[beneficiarios]",
  "highlight2": "[localizacoes]",
  "href": "/instrumentos/[slug]/",
  "featured": false
}
```

**Antes de adicionar, verificar duplicados:** se o `id` ja existe em `instruments-catalog.json`, perguntar ao utilizador se quer atualizar (refazer) ou abortar.

---

## PASSO 6: Atualizar registry

### 6a. Adicionar ao shard

Em `registry/shards/[shard].json`, adicionar:
```json
{ "id": "[slug]", "file": "instrumentos/[slug]/index.html", "source": "[source_id]", "state": "[estado]", "last_check": "[hoje]" }
```

### 6b. Adicionar ao lookup (dedup O(1))

Em `registry/lookup.json`:
```json
"by_id": { "[slug]": true }
```

Se houver `aviso_codigo` aplicavel:
```json
"by_aviso_codigo": { "[codigo]": "[slug]" }
```

### 6c. Calcular SHA1 do regulamento (apenas regime aviso)

Se existir `regulamentos/[source_id]/[slug].txt` ou `.pdf`:

```bash
sha1sum "$REPO/regulamentos/[source_id]/[slug].txt"
```

Adicionar a `registry/integrity.json`:
```json
"[slug]": { "sha1": "[hash]", "checked": "[hoje]", "size": [bytes], "source_dir": "[source_id]", "file": "[slug].txt" }
```

Saltar para regime catalogo (sem regulamento formal).

### 6d. Atualizar index

Em `registry/index.json`:
- `totals.published` + 1
- `totals.[open/closed/planned]` + 1 conforme estado
- Para o shard tocado, incrementar TODOS estes campos (criar o campo se ainda nao existe):
  - `count` + 1
  - `published` + 1 (ESSENCIAL)
  - `open` / `closed` / `planned` + 1 conforme estado
- `_meta.last_writer_run`: hoje

---

## PASSO 7: Auto-validacao de paridade

Apos os passos 4-6, validar localmente que tudo ficou alinhado:

1. Existe `instrumentos/[slug]/index.html`? Se nao: ABORTAR e reportar erro grave.
2. O slug aparece em `instruments-catalog.json` exatamente uma vez? Se 0: re-aplicar passo 5. Se >1: remover duplicados (manter o primeiro).
3. O slug aparece no shard correto em `registry/shards/[shard].json`? Se nao: re-aplicar passo 6a.
4. O slug aparece em `registry/lookup.json > by_id`? Se nao: re-aplicar passo 6b.

Esta verificacao deteta o tipo de regressao que originou os 13 orfaos detectados em 2026-05-09 (HTML criado, restante em falta).

---

## PASSO 8: Build do footer

```bash
python build_footer.py instrumentos/[slug]/index.html
```

Preenche os marcadores `<!-- FOOTER:START --> ... <!-- FOOTER:END -->` no novo ficheiro.

---

## PASSO 9: Auto-deploy

Regra global do CLAUDE.md: toda a skill que cria/modifica ficheiros do site deve fazer commit + push automaticamente.

```bash
git -C "$REPO" add instrumentos/[slug]/index.html instruments-catalog.json registry/
git -C "$REPO" commit -m "instrumento: [nome do instrumento] (manual)"
git -C "$REPO" push origin main
```

Se push falhar: `git stash && git pull --rebase && git stash pop && git push`.

**Nunca skipar este passo. Nunca perguntar "quer comitar?".**

---

## REGRAS DE SEGURANCA

1. **Nunca escrever sem ler `instrumento-template.md` primeiro.**
2. **Nunca editar `biblioteca.html`.** Catalogo e 100% dinamico via `instruments-catalog.json`.
3. **Nunca duplicar.** Verificar `lookup.json` antes de criar.
4. **Nunca publicar PAAs.** A validacao do passo 2 e absoluta.
5. **Auto-validacao 7 e obrigatoria.** Nenhum artigo sai com paridade incompleta.
6. **Auto-deploy 9 e obrigatorio.** Nunca terminar sessao com commits locais por enviar.

---

## RESUMO DO FLUXO

```
Input manual ($ARGUMENTS)
    |
    v
0. Detetar ambiente, $REPO
1. Ler instrumento-template.md (regras + template)
2. Processar input + validacao anti-PAA
3. Definir metadados editoriais (slug, autor, categorias, setores, necessidades, shard)
4. Criar instrumentos/[slug]/index.html via template
5. Adicionar entrada a instruments-catalog.json
6a-d. Atualizar shard + lookup + integrity + index
7. Auto-validacao de paridade
8. build_footer.py
9. git add + commit + push
    |
    v
Reportar: "Artigo [slug] publicado. Paridade verificada. Commit [hash]."
```
