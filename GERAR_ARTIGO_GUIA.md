# 📝 Guia: Como Gerar Artigos com o Claude Agent

## ⚡ Quick Start

1. **Ir a GitHub** → `github.com/JPereira-eng/opencapital-site`
2. **Actions** tab → **Gerar Artigo** workflow
3. **Run workflow** → Preencher o campo **Topic_or_url**
4. **Submit** → Aguardar ~60 segundos
5. ✅ Artigo live em `conhecimento.html`

---

## 🔧 Setup (primeira vez apenas)

### 1️⃣ Configurar o segredo ANTHROPIC_API_KEY

```
GitHub.com/JPereira-eng/opencapital-site
  → Settings → Secrets and variables → Actions
  → New repository secret

  Name: ANTHROPIC_API_KEY
  Value: sk-ant-v7-... (sua chave da Anthropic)
```

Obtém a chave em: https://console.anthropic.com/account/keys

### 2️⃣ Verificar que o repositório local está atualizado

```bash
cd ~/Desktop/opencapital-website
git pull origin main
```

✅ Pronto! Agora podes gerar artigos.

---

## 🎬 Como usar

### Opção A: Gerar de um **Tema**

```
GitHub Actions → Gerar Artigo → Run workflow

  topic_or_url: "Portugal 2030: Oportunidades de financiamento verde"
  category: "Financiamento Público" (default)

  ✅ Submit
```

O Claude vai investigar o tema e criar um artigo completo.

### Opção B: Gerar de uma **URL** (PDF ou notícia)

```
GitHub Actions → Gerar Artigo → Run workflow

  topic_or_url: "https://www.example.com/documento.pdf"
  category: "Fiscal" (ou outro)

  ✅ Submit
```

O Claude vai:
1. Buscar o conteúdo da URL
2. Analisar o documento
3. Extrair insights e estrutura
4. Gerar um artigo editorial

---

## 📊 Workflow Automático

```
Tu clicas "Run workflow"
    ↓
GitHub Actions executa Node.js
    ↓
Node.js chama Claude API (Opus 4.6)
    ↓
Claude gera artigo em HTML + JSON
    ↓
Script valida e injeta em conhecimento.html
    ↓
Card adicionado à grid
    ↓
Git commit automático
    ↓
GitHub push → Netlify webhook
    ↓
Netlify auto-deploy
    ↓
Site live (1-2 minutos)
```

**Nenhuma ação manual necessária après o click inicial.**

---

## 🎨 Características do artigo gerado

✅ **Navbar** — logo, links, dropdown "Oportunidades", CTA
✅ **Hero** — breadcrumb, badge de categoria, título, standfirst
✅ **Artigo** — estrutura livre (o Claude decide o que melhor serve)
✅ **Sidebar** — "Factos Rápidos" + CTA + "Instrumentos Relacionados"
✅ **Footer** — 4 colunas completas
✅ **Design System v1.3** — cores, tipografia, variáveis CSS
✅ **Card em Soluções** — auto-injectado no catálogo

---

## 🔍 Monitorizar o progresso

1. **GitHub Actions** → Workflow em execução (círculo azul)
2. **Detalhes** → Ver logs em tempo real
3. **Se falhar** → Ler mensagem de erro

---

## ⚙️ Troubleshooting

### ❌ "API key invalid"
Verificar que `ANTHROPIC_API_KEY` está definida corretamente em Secrets.

### ❌ "Node command not found"
O GitHub Actions deve instalar automaticamente. Se falhar, rerun o workflow.

### ❌ "Git push failed"
Verificar permissões do token de autenticação. O repositório deve ter Actions ativado.

### ❌ "Claude API timeout"
Alguns prompts longos podem levar >30s. Rerun o workflow — não há problema em repetir.

---

## 📄 Exemplos de inputs

**Tema simples:**
```
"SIFIDE II: Benefícios fiscais para I&D"
```

**URL de PDF:**
```
"https://www.inovacao.pt/documentos/sifide-2024.pdf"
```

**URL de notícia:**
```
"https://www.publico.pt/economia/noticia/portugal-2030-financiamento-novo-2024"
```

**Tema descritivo:**
```
"Venture Capital: Como funcionam os fundos de investimento em startups portuguesas, diferenças entre seed, série A, B, C"
```

---

## 🎯 O que o Claude Agent faz

1. **Analisa** o input (tema ou URL)
2. **Pesquisa** contexto e detalhes
3. **Estrutura** o artigo de forma editorial (não genérica)
4. **Gera** HTML completo com Design System v1.3
5. **Valida** que todo o CSS está inline e paths estão corretos
6. **Injeta** o card em `conhecimento.html`
7. **Publica** via git commit automático
8. **Netlify** detecta push e faz deploy

**Tempo total:** 30–60 segundos.

---

## 📞 Suporte

Se encontrares problemas:
1. Verificar os **logs do GitHub Actions**
2. Confirmar que `scripts/gerar-artigo.js` existe e está acessível
3. Testar manualmente: `ANTHROPIC_API_KEY=sk-... node scripts/gerar-artigo.js "tema"` (local)

---

**Pronto! 🚀 A plataforma está operacional.**
