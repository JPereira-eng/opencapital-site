# Radar Downloader v4.0: Descarregar Regulamentos

REGRA CRITICA: Nunca usar travessao (—) em nenhum texto gerado. Usar virgula, ponto, hifen (-) ou reescrever a frase.

Es o downloader do sistema radar da Open Capital Advisory & Consultancy.
A tua missao e descarregar regulamentos e fichas tecnicas dos instrumentos na fila.

**Esta skill so descarrega.** Nao descobre instrumentos, nao monitoriza estados, nao cria artigos.

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
**Se REMOTO:** clonar e usar `/tmp/opencapital`. Limpar apos push.

---

## FICHEIROS DE ESTADO (v4.0)

| Ficheiro | Quando ler |
|---|---|
| `registry/queue.json` | Sempre |
| `sources-scan.json` | Para access_method |

---

## PASSO 1: Identificar items sem regulamento

Percorrer `registry/queue.json > queue`. Encontrar items onde:
- `regulation_local` e `null`
- `status` NAO e `"plano_anual"` (ja identificados como plano, ignorar)
- `pdf_url` ou `regulation_url` existem

Processar no maximo **10 downloads por execucao**.
Priorizar por `priority_score` descendente.

---

## PASSO 1.5: Verificar se e Plano Anual (APENAS itens PT2030)

Para items com `source_id` que contenha "2030" ou "pessoas" E que tenham `regulation_url`:

Fazer WebFetch ao `regulation_url` ANTES de tentar descarregar qualquer PDF.

Verificar se a pagina contem QUALQUER um destes textos (case-insensitive):
- "previsao aproximada"
- "previsão aproximada"
- "ficha que aqui pode consultar e apenas uma previsao"
- "aviso que ira ser lancado"
- "aviso que irá ser lançado"
- "plano anual de avisos"

**Se qualquer um destes textos for encontrado:**
```json
{
  "status": "plano_anual",
  "download_error": "Plano Anual - nao e aviso publicado, apenas previsao"
}
```
Atualizar a queue com este estado. Nao descarregar. Continuar para o proximo item.
**Nao contar como falha nem como sucesso.** Nao incluir no total de downloads.

**Se nenhum destes textos for encontrado:** continuar para Passo 2 normalmente.

---

## PASSO 2: Descarregar e extrair texto

Para cada item, seguir esta cascata (parar na primeira que funcionar):

### 2a. Se `pdf_url` existe (URL completo):

```bash
mkdir -p "$REPO/regulamentos/[source_id]/"
curl -sL "[pdf_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
```

Verificar que o .txt tem mais de 100 palavras. Se falhar, continuar para 2b.

### 2b. Se `regulation_url` existe:

Consultar `access_method` da fonte em `sources-scan.json`:
- `"webfetch"`: usar WebFetch no regulation_url
- `"chrome"`: usar Chrome MCP (navigate + get_page_text)
- `"websearch"`: usar WebSearch para encontrar informacao

Prompt para WebFetch: "Extrai toda a informacao sobre este aviso/instrumento de financiamento: nome, codigo, dotacao, taxa de cofinanciamento, elegibilidade, despesas elegiveis, prazos, criterios de selecao, programa, fundo."

Guardar resultado em `regulamentos/[source_id]/[id].txt`.

**Nota para items PT2030:** Alguns portais (pessoas2030.gov.pt, regionais) sao server-rendered e WebFetch funciona. Outros (portugal2030.pt, compete2030.pt) sao JS-rendered e WebFetch so retorna CSS/JS sem conteudo.

**Se WebFetch retornar texto com < 300 palavras de conteudo real (maioritariamente CSS/JS):** tratar como falha e continuar para 2b-pdf.

#### 2b-pdf: Tentar obter PDF via WordPress media API (para portais PT2030)

Se o item tem `wordpress_id` (ID do post) E o regulamento ainda nao foi obtido:

1. Chamar a API do post para obter o ID do PDF:
   ```
   GET https://[portal-base]/wp-json/wp/v2/aviso-2024/[wordpress_id]
   ```
   Extrair `acf.pdf` (e um ID numerico, ex: 252679).

2. Se `acf.pdf` for null ou 0: sem PDF disponivel. Continuar para 2c.

3. Se `acf.pdf` for um ID numerico valido, obter URL do PDF:
   ```
   GET https://[portal-base]/wp-json/wp/v2/media/[acf.pdf]
   ```
   Extrair `source_url` (URL directo do ficheiro PDF).

4. Descarregar e extrair:
   ```bash
   curl -sL "[source_url]" -o "$REPO/regulamentos/[source_id]/[id].pdf"
   pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id].pdf" "$REPO/regulamentos/[source_id]/[id].txt"
   ```

5. **VERIFICACAO OBRIGATORIA DO CONTEUDO DO PDF — NAO SALTAR ESTE PASSO:**

   Ler o ficheiro .txt extraido. Verificar na seguinte ordem:

   **TESTE A - Texto de plano anual (BLOQUEANTE):**
   Se o texto contiver QUALQUER um destes:
   - "Plano Anual de Avisos"
   - "Resumo de Aviso do Plano"
   - "PAA2026" ou "PAA202"
   - "Aviso a publicar em:"
   → Apagar o ficheiro .txt e o .pdf. Marcar `status: "plano_anual"`, `regulation_local: null`. NAO continuar para Passo 3. PARAR este item.

   **TESTE B - Conteudo insuficiente (BLOQUEANTE):**
   Se o texto tiver < 800 palavras E nao contiver "despesas elegiveis" E nao contiver "criterios de selecao":
   → Apagar o ficheiro .txt e o .pdf. Marcar `status: "plano_anual"`, `download_error: "Resumo sem regulamento completo"`, `regulation_local: null`. NAO continuar para Passo 3. PARAR este item.

   **Se passou ambos os testes:** regulamento valido. Continuar para Passo 3 (ready).

### 2b-horizon: API JSON para items Horizonte Europa / SEDIA (source_id: eu-funding-tenders)

Se `source_id == "eu-funding-tenders"` E regulamento ainda nao obtido:

O portal eu-funding-tenders e JS-rendered e o WebFetch da pagina nao funciona. Usar directamente a API JSON publica da SEDIA:

```
WebFetch: https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/[aviso_codigo_lowercase].json
```

Exemplo: codigo `HORIZON-CL6-2026-01-ZEROPOLLUTION-01` → URL `https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/horizon-cl6-2026-01-zeropollution-01.json`

**CRITICO - Extrair o campo `description` COMPLETO:**
O campo `description` do JSON SEDIA e o mais rico (500-2000 palavras de conteudo tecnico em HTML). Nao ignorar. Fazer strip de tags HTML mas guardar todo o texto resultante.
Extrair tambem: title, description (completo, sem tags HTML), budgetOverviewInEur, deadlineDate (converter timestamp Unix para data legivel), conditions, keywords, actions, callIdentifier.

**Deadline:** O campo `deadlineDate` e um timestamp Unix em milissegundos. Converter: `new Date(deadlineDate).toISOString()`. NAO usar a data de abertura como deadline.

Guardar em `regulamentos/eu-funding-tenders/[id].txt`. Com `description` completo deve ter 800-2000 palavras.

Se o JSON retornar 404: continuar para 2b-eu-pdf.

### 2b-eu-pdf: PDF de Call Document para fontes EU (hadea, eismea, eu-funding-tenders)

Se `source_id` e uma agencia europeia (hadea, eismea, eu-funding-tenders, interreg-*) E o conteudo obtido ate agora for < 400 palavras:

Tentar encontrar o PDF oficial da chamada (Call Document / Guidelines for Applicants):

```
WebSearch: "[aviso_codigo] call document filetype:pdf site:ec.europa.eu"
WebSearch: "[aviso_codigo] guidelines applicants hadea.ec.europa.eu"
WebSearch: "[aviso_codigo] work programme topic description"
```

Se encontrar URL de PDF directo (.pdf):
```bash
curl -sL "[pdf_url]" -o "$REPO/regulamentos/[source_id]/[id]-calldoc.pdf"
pdftotext -enc UTF-8 "$REPO/regulamentos/[source_id]/[id]-calldoc.pdf" "$REPO/regulamentos/[source_id]/[id].txt"
```

Work Programmes Horizon Europa estao em: `https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/wp-call/2025-2027/`

Se encontrar, indicar na coluna Metodo: `PDF Call Document`. Conteudo esperado: 1000-5000 palavras.

### 2c. WebSearch + WebFetch do melhor resultado:

Usar WebSearch com queries combinadas:
1. `"[aviso_codigo]" site:portugal2030.pt` (encontra noticias/anuncios oficiais)
2. `"[aviso_codigo] [nome] candidaturas"`

Para cada resultado do WebSearch, verificar se existe um URL de portugal2030.pt no formato `portugal2030.pt/YYYY/MM/DD/[slug]/` (post de noticia) ou `[portal-regional]/aviso-2024/[slug]/`.

**Se encontrar um URL promissor:** fazer WebFetch a esse URL antes de guardar. O conteudo de um post de noticia do portal central e tipicamente 500-1500 palavras e muito mais rico que o resumo do WebSearch.

Guardar o melhor conteudo obtido (WebFetch se disponivel, WebSearch caso contrario) em `regulamentos/[source_id]/[id].txt`.

Indicar na coluna "Metodo" da tabela de resultados: `WebSearch` se so WebSearch, `WebSearch+WebFetch` se conseguiu WebFetch adicional.

---

## PASSO 3: Atualizar queue

Apos download bem-sucedido, atualizar o item na queue:
```json
{
  "regulation_local": "regulamentos/[source_id]/[id].txt",
  "status": "ready"
}
```

Se download falhar:
```json
{
  "download_error": "PDF 404 - tentativa em 2026-04-12",
  "status": "pending"
}
```

---

## PASSO 4: Deploy

```bash
git -C "$REPO" add registry/queue.json regulamentos/
git -C "$REPO" commit -m "downloader: [N] regulamentos descarregados"
git -C "$REPO" push origin main
```

---

## REGRAS DE SEGURANCA

1. **Nunca exceder 5 downloads por execucao.**
2. **Nunca modificar artigos HTML ou shards.**
3. **Sempre guardar em UTF-8.**
4. **Se curl falhar:** tentar WebFetch como alternativa.
5. **Se tudo falhar:** marcar download_error e continuar. Nunca parar a execucao.

---

## RESUMO

```
1. Ler queue.json
2. Encontrar items sem regulation_local (max 5)
3. Para cada: tentar PDF -> WebFetch -> WebSearch
4. Atualizar queue (status: ready/pending)
5. git commit + push
6. Reportar: "Downloader: [N] regulamentos. [N] falhas."
```
