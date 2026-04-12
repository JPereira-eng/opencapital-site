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
- `pdf_url` ou `regulation_url` existem

Processar no maximo **5 downloads por execucao**.
Priorizar por `priority_score` descendente.

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

**Nota para items PT2030:** URLs do tipo `portugal2030.pt/aviso-2024/[slug]/` sao paginas WordPress server-rendered. WebFetch funciona diretamente.

### 2c. Se tudo falhou:

Usar WebSearch: `"[aviso_codigo] [nome] financiamento"` + `"[nome] aviso candidaturas elegibilidade"`
Guardar resultado combinado em `regulamentos/[source_id]/[id].txt`.

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
