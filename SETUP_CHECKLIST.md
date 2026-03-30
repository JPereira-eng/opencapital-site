# ✅ Setup Checklist: Agente de Geração de Artigos

## Status Atual (2026-03-30)

### ✅ Arquivos Criados
- [x] `scripts/gerar-artigo.js` — 600+ linhas, node.js puro, sem dependências
- [x] `.github/workflows/gerar-artigo.yml` — GitHub Actions workflow
- [x] `GERAR_ARTIGO_GUIA.md` — Instruções de uso
- [x] Integração com design system v1.3

### ✅ Funcionalidades Implementadas
- [x] Claude Opus 4.6 API integration (adaptive thinking)
- [x] HTML template generator (navbar, hero, sidebar, footer)
- [x] Card injection em `conhecimento.html`
- [x] Git automation (commit + push)
- [x] Netlify webhook trigger (auto-deploy)
- [x] Error handling e logging

### ⏳ Próximas ações (5 minutos)

1. **GitHub Repository Secret Setup**
   ```
   URL: https://github.com/JPereira-eng/opencapital-site/settings/secrets/actions
   Name: ANTHROPIC_API_KEY
   Value: (sua chave sk-ant-v7-...)
   ```

   ✅ **Esta é a ÚNICA configuração manual necessária**

2. **Verificar que o repo local está sincronizado**
   ```bash
   cd ~/Desktop/opencapital-website
   git pull origin main
   ```

3. **Testar o workflow (opcional, mas recomendado)**
   - Ir a GitHub Actions
   - Click "Gerar Artigo"
   - Preencher: `topic_or_url: "Teste: Portugal 2030 - Financiamento"`
   - Click "Run workflow"
   - Aguardar ~60 segundos
   - Verificar se o artigo aparece em `conhecimento.html`

---

## 🎯 Pronto para usar?

Uma vez que a `ANTHROPIC_API_KEY` esteja configurada:

**Qualquer artigo é gerado em 3 passos:**

```
1. GitHub.com → Actions → Gerar Artigo
2. Preencher: topic ou URL
3. Click "Run workflow"
   ↓
   ✅ Artigo live em ~60 segundos
```

Sem necessidade de:
- ❌ Python
- ❌ Setup local
- ❌ Deploy manual
- ❌ Editar ficheiros HTML diretamente
- ❌ Git commands

---

## 📋 O que foi entregue

| Item | Ficheiro | Descrição |
|---|---|---|
| **Gerador** | `scripts/gerar-artigo.js` | Node.js puro, sem npm dependencies |
| **CI/CD** | `.github/workflows/gerar-artigo.yml` | GitHub Actions (manual trigger) |
| **Documentação** | `GERAR_ARTIGO_GUIA.md` | Instruções completas de uso |
| **Tech Stack** | HTML+CSS+JS | Aligned com resto do website |
| **Integração** | Netlify auto-deploy | Commit → Deploy automático |

---

## 🔐 Instruções: Adicionar o API Key Secret

### Passo-a-passo visual

1. Abrir: https://github.com/JPereira-eng/opencapital-site
2. **Settings** (tabela superior)
3. **Secrets and variables** → **Actions** (sidebar)
4. **New repository secret** (botão verde)
5. Preencher:
   - **Name:** `ANTHROPIC_API_KEY`
   - **Secret:** `sk-ant-v7-...` (sua chave da Anthropic)
6. **Add secret**

✅ **Pronto!** A GitHub Actions pode aceder ao API.

---

## 🚀 Teste rápido (2 minutos)

```bash
# Simulação local (opcional, para testar antes de usar GitHub Actions)
cd ~/Desktop/opencapital-website
export ANTHROPIC_API_KEY="sk-ant-v7-..."
export TOPIC_OR_URL="Portugal 2030: Oportunidades de financiamento"
node scripts/gerar-artigo.js "$TOPIC_OR_URL"
```

Esperado:
- Novo ficheiro em `conhecimento/[slug].html`
- Novo card injectado em `conhecimento.html`
- Git commit automático
- Log em stdout com progresso

---

## 📞 Troubleshooting Rápido

| Problema | Solução |
|---|---|
| API Key invalid | Verificar `ANTHROPIC_API_KEY` em Secrets |
| Node not found | Usar GitHub Actions (não requer setup local) |
| Git push fails | Verificar permissões do repo |
| Artigo não aparece | Ver logs do GitHub Actions para erro específico |
| Timeout | Rerun o workflow (alguns temas são maiores) |

---

## ✨ Resultado Final

**O que o utilizador vê em GitHub:**

```
GitHub.com/JPereira-eng/opencapital-site
  → Actions tab
    → "Gerar Artigo" workflow
      → Run workflow button
        → Input field: "Tema ou URL"
          → 60 segundos depois...
            → ✅ Novo artigo em conhecimento.html
```

**Nada mais.** Totalmente automatizado.

---

## 🎓 Resumo técnico (para referência futura)

**Stack:**
- Node.js (native, no npm)
- Claude API (Opus 4.6, adaptive thinking)
- GitHub Actions (CI/CD, manual trigger)
- Git (commit/push automation)
- Netlify (deployment webhook)
- HTML+CSS (design system v1.3)

**Flow:**
```
User input (GitHub UI)
  → Node.js script
    → Claude API call
      → HTML generation
        → File save
          → Git commit
            → GitHub push
              → Netlify webhook
                → Auto-deploy
```

**Sem dependências externas (npm, Python, etc)**

---

**Status: ✅ PRONTO PARA USAR**

Falta apenas: Configurar `ANTHROPIC_API_KEY` em GitHub Secrets.
