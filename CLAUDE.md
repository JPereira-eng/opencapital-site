# OPEN CAPITAL — CLAUDE CODE INSTRUCTIONS
# Design System v1.3 — Single Source of Truth

Read this file at the start of every session.
All code produced must be 100% consistent with the rules below.
Reference file for visual output: `assets/design-system.html`

---

## ⚠️ REGRA CRÍTICA — SKILLS & AGENTS

**Sempre que um ficheiro em `.claude/commands/` (skills) ou agentes for criado ou modificado, fazer imediatamente commit + push ao GitHub.**

Duas pessoas trabalham no mesmo repositório em computadores diferentes. Se as skills ficarem apenas locais, a outra pessoa usa versões desatualizadas.

Procedimento:
1. `git add .claude/commands/[ficheiro]`
2. `git commit -m "skill: [descrição da alteração]"`
3. `git push` (se rejeitado: `git stash && git pull --rebase && git stash pop && git push`)

Fazer isto sem que o utilizador peça. É uma instrução permanente.

---

## 🏢 BRAND

**Name:** Open Capital Advisory & Consultancy
**Tagline:** O capital de que a sua empresa precisa.
**Sub-tagline:** Menos burocracia. Mais clareza. Mais crescimento.
**Positioning:** Premium strategic advisory firm. Clarity · Confidence · Intelligence.

---

## 🎨 CSS VARIABLES — ALWAYS INCLUDE, NEVER MODIFY

```css
:root {
  --navy:       #1A3A5C;
  --navy-deep:  #0D1F33;
  --gold:       #C9A96E;
  --white:      #FFFFFF;
  --grey-light: #E5E5E5;
  --grey-mid:   #7A7A7A;
  --grey-dark:  #2A2A2A;
  --font: 'Montserrat', sans-serif;
  --transition: all 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --shadow: 0 8px 40px rgba(26,58,92,0.10);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:var(--font); background:var(--white); color:var(--grey-dark); -webkit-font-smoothing:antialiased; }
```

### Colour usage rules
| Token | Hex | Use |
|---|---|---|
| `--navy` | `#1A3A5C` | Primary · Hero BG · Headings · Structure |
| `--navy-deep` | `#0D1F33` | Footer · depth layers |
| `--gold` | `#C9A96E` | Accent ONLY — use sparingly |
| `--white` | `#FFFFFF` | Primary section background |
| `--grey-light` | `#E5E5E5` | Borders · dividers · UI elements |
| `--grey-mid` | `#7A7A7A` | Secondary text · captions |
| `--grey-dark` | `#2A2A2A` | Body text |

**Gold rule:** Never overuse gold. Every gold element must feel deliberate and exclusive.

---

## 🔤 TYPOGRAPHY — MONTSERRAT ONLY

**Google Fonts import (every page):**
```html
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
```

No other fonts. No serif. No system fonts. No decorative fonts.

### Type scale — v1.3 (applied +25% to all non-title sizes vs. original)

| Role | Class | Size | Weight | Tracking | Other |
|---|---|---|---|---|---|
| Eyebrow / Label | `.t-eyebrow` | 14px | 600 | 0.30em | uppercase, color: gold |
| H1 / Hero | `.t-h1` | 54px | 700 | -0.01em | color: navy, line-height: 1.05 |
| H2 | `.t-h2` | 36px | 600 | 0.01em | color: navy, line-height: 1.15 |
| H3 | `.t-h3` | 28px | 500 | 0.03em | color: navy |
| H4 / Subheading | `.t-h4` | 19px | 500 | 0.07em | color: navy |
| Tagline | `.t-tagline` | 24px | 100 | 0.14em | color: navy |
| Body | `.t-body` | 18px | 400 | — | line-height: 1.85, max-width: 580px |
| Small / Caption | `.t-small` | 15px | 300 | 0.04em | color: grey-mid |

```css
.t-eyebrow { font-size:14px; font-weight:600; letter-spacing:0.30em; text-transform:uppercase; color:var(--gold); }
.t-h1      { font-size:54px; font-weight:700; letter-spacing:-0.01em; color:var(--navy); line-height:1.05; }
.t-h2      { font-size:36px; font-weight:600; letter-spacing:0.01em;  color:var(--navy); line-height:1.15; }
.t-h3      { font-size:28px; font-weight:500; letter-spacing:0.03em;  color:var(--navy); }
.t-h4      { font-size:19px; font-weight:500; letter-spacing:0.07em;  color:var(--navy); }
.t-tagline { font-size:24px; font-weight:100; letter-spacing:0.14em;  color:var(--navy); }
.t-body    { font-size:18px; font-weight:400; color:var(--grey-dark); line-height:1.85; max-width:580px; }
.t-small   { font-size:15px; font-weight:300; letter-spacing:0.04em;  color:var(--grey-mid); }
```

---

## 03 NAVBAR

Height: 74px. Logo left · Nav links **right-aligned** · CTA right (with left margin gap).
Fixed on scroll with backdrop blur. Border-bottom: 1px solid grey-light.

**Nav links are sentence case (e.g. "Soluções", NOT "SOLUÇÕES").**

### Light variant (white bg pages)
```css
.navbar { display:flex; align-items:center; justify-content:space-between; padding:0 40px; height:74px; background:var(--white); border-bottom:1px solid var(--grey-light); }
.nav-links { display:flex; align-items:center; gap:24px; list-style:none; margin-left:auto; }
.nav-links a { font-size:15px; font-weight:500; letter-spacing:0.08em; text-transform:none; color:var(--grey-dark); text-decoration:none; transition:var(--transition); position:relative; padding-bottom:3px; white-space:nowrap; }
.nav-links a::after { content:''; position:absolute; bottom:0; left:0; width:0; height:1px; background:var(--gold); transition:width 0.3s ease; }
.nav-links a:hover { color:var(--navy); }
.nav-links a:hover::after { width:100%; }
.nav-cta { font-size:16px; font-weight:600; letter-spacing:0.08em; text-transform:none; color:var(--navy); text-decoration:none; border:1px solid var(--navy); padding:9px 18px; margin-left:28px; transition:var(--transition); white-space:nowrap; }
.nav-cta:hover { background:var(--navy); color:var(--white); }
```

### Dark variant (navy bg sections)
```css
.navbar-dark { background:var(--navy); border-bottom:1px solid rgba(255,255,255,0.07); }
.nav-links-light a { color:rgba(255,255,255,0.58); }
.nav-links-light a:hover { color:var(--white); }
.nav-cta-light { color:var(--white); border-color:rgba(255,255,255,0.28); }
.nav-cta-light:hover { border-color:var(--white); background:rgba(255,255,255,0.08); }
```

### "Em breve" badge — superscript style
```css
.nav-badge {
  font-size:10px; font-weight:600; letter-spacing:0.06em;
  text-transform:none; color:var(--gold);
  border:1px solid var(--gold); padding:1px 4px;
  margin-left:3px; vertical-align:super; line-height:1;
}
```
**Usage:** `Soluções<sup class="nav-badge">em breve</sup>` — lowercase, no brackets.

### Dropdown submenu (Oportunidades: Parceiros & Carreiras)
"Parceiros" and "Carreiras" are merged into a single nav item with dropdown labeled "Oportunidades".
```css
.nav-dropdown { position:relative; }
.nav-dropdown-menu { position:absolute; top:100%; right:0; background:var(--white); border:1px solid var(--grey-light); min-width:160px; box-shadow:var(--shadow); display:none; z-index:100; }
.nav-dropdown:hover .nav-dropdown-menu { display:block; }
.nav-dropdown-menu a { display:block; font-size:13px; font-weight:500; letter-spacing:0.05em; color:var(--grey-dark); padding:11px 18px; text-decoration:none; transition:var(--transition); border-bottom:1px solid var(--grey-light); }
.nav-dropdown-menu a:last-child { border-bottom:none; }
.nav-dropdown-menu a:hover { color:var(--navy); background:#FAFAFA; }
```

### Navigation items (all pages)
Logo (→ index.html) · Soluções · Conhecimento · Capital Simulator `em breve` · Tech2Business `em breve` · Sobre Nós · Oportunidades ▾ (dropdown: Parceiros · Carreiras) · [Contactar CTA]

⚠️ Logo: usar `<img src="logo_opencapital_azul_semfundo.png" class="nav-logo-img">` (ficheiro na raiz).
- Navbar dark/hero: `filter:brightness(0) invert(1)`
- Navbar scrolled/light: `filter:none`
- **Altura: 57px** (não usar nav-mark + nav-sep + nav-wordmark)

---

## 04 BUTTONS

**No border-radius anywhere. Sharp corners on all buttons, cards, inputs.**

```css
.btn { display:inline-flex; align-items:center; gap:8px; font-family:var(--font); font-size:14px; font-weight:600; letter-spacing:0.26em; text-transform:uppercase; border:none; cursor:pointer; transition:var(--transition); text-decoration:none; }

/* Primary — navy bg */
.btn-primary { background:var(--navy); color:var(--white); padding:16px 38px; }
.btn-primary:hover { background:#0F2A45; box-shadow:0 6px 20px rgba(26,58,92,0.22); transform:translateY(-1px); }

/* Outline — transparent, navy border */
.btn-outline { background:transparent; color:var(--navy); padding:15px 37px; border:1px solid var(--navy); }
.btn-outline:hover { background:var(--navy); color:var(--white); }

/* Gold — gold bg */
.btn-gold { background:var(--gold); color:var(--white); padding:16px 38px; }
.btn-gold:hover { background:#B8945A; box-shadow:0 6px 20px rgba(201,169,110,0.28); transform:translateY(-1px); }

/* Ghost — for use on navy backgrounds only */
.btn-ghost { background:transparent; color:var(--white); padding:15px 37px; border:1px solid rgba(255,255,255,0.28); }
.btn-ghost:hover { border-color:var(--white); background:rgba(255,255,255,0.07); }

/* Text — arrow suffix */
.btn-text { background:transparent; color:var(--navy); padding:6px 0; font-size:14px; }
.btn-text::after { content:' →'; font-weight:300; font-size:15px; }
.btn-text:hover { color:var(--gold); }
```

---

## 05 CARDS

**No border-radius. Hover: top gold line animates width 0→100% + translateY(-3px) + shadow.**

```css
/* Standard white card */
.card { background:var(--white); border:1px solid var(--grey-light); padding:44px 36px; position:relative; overflow:hidden; transition:var(--transition); }
.card::before { content:''; position:absolute; top:0; left:0; width:0; height:2px; background:var(--gold); transition:width 0.4s ease; }
.card:hover { box-shadow:var(--shadow); transform:translateY(-3px); }
.card:hover::before { width:100%; }

.card-eyebrow { font-size:13px; font-weight:600; letter-spacing:0.28em; text-transform:uppercase; color:var(--gold); margin-bottom:12px; }
.card-title   { font-size:23px; font-weight:600; color:var(--navy); line-height:1.3; margin-bottom:10px; }
.card-body    { font-size:18px; font-weight:300; color:var(--grey-mid); line-height:1.9; margin-bottom:22px; }
.card-link    { font-size:13px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--navy); text-decoration:none; transition:var(--transition); }
.card-link:hover { color:var(--gold); }

/* Navy card variant */
.card-navy { background:var(--navy); border-color:transparent; }
.card-navy .card-title { color:var(--white); }
.card-navy .card-body  { color:rgba(255,255,255,0.48); }
.card-navy .card-link  { color:var(--gold); }
.card-navy::before     { background:var(--gold); }

/* Grey card variant */
.card-grey { background:#FAFAFA; }
```

---

## 06 DIVIDERS

```css
/* Standard */
.div-std { height:1px; background:var(--grey-light); margin:20px 0; }

/* Gold gradient */
.div-gold { height:1px; background:linear-gradient(to right, transparent, var(--gold) 40%, transparent); margin:20px 0; }

/* Diamond ornament */
.div-ornament { display:flex; align-items:center; gap:14px; margin:28px 0; }
.div-ornament::before, .div-ornament::after { content:''; flex:1; height:1px; background:var(--grey-light); }
.div-diamond { width:5px; height:5px; border:1px solid var(--gold); transform:rotate(45deg); flex-shrink:0; }
```

---

## 07 TAGS & BADGES

```css
.tag { font-size:10px; font-weight:500; letter-spacing:0.16em; text-transform:uppercase; padding:5px 12px; transition:var(--transition); cursor:pointer; }

.tag-navy    { background:rgba(26,58,92,0.07);    color:var(--navy);    border:1px solid transparent; }
.tag-navy:hover { border-color:var(--navy); }

.tag-gold    { background:rgba(201,169,110,0.10); color:#9A7040;        border:1px solid transparent; }
.tag-gold:hover { border-color:var(--gold); }

.tag-outline { background:transparent; color:var(--grey-mid); border:1px solid var(--grey-light); }
.tag-outline:hover { border-color:var(--grey-mid); color:var(--grey-dark); }

.tag-soon    { background:transparent; color:var(--gold); border:1px solid var(--gold); }
```

---

## 08 FORMS

**No border-radius on inputs. Focus: navy border + subtle navy shadow.**

```css
.form-label { display:block; font-size:10px; font-weight:600; letter-spacing:0.22em; text-transform:uppercase; color:var(--grey-mid); margin-bottom:8px; }

.form-input { width:100%; padding:12px 15px; font-family:var(--font); font-size:14px; font-weight:300; color:var(--grey-dark); background:var(--white); border:1px solid var(--grey-light); outline:none; transition:var(--transition); border-radius:0; }
.form-input::placeholder { color:var(--grey-light); }
.form-input:focus { border-color:var(--navy); box-shadow:0 0 0 3px rgba(26,58,92,0.05); }

/* On navy background */
/* background:rgba(255,255,255,0.05); border-color:rgba(255,255,255,0.12); color:var(--white); */
```

---

## 09 HERO SECTION

```css
.hero { background:var(--navy); padding:0 8%; min-height:100vh; position:relative; overflow:hidden; display:flex; align-items:center; }

/* Left gold bar */
.hero-gold-bar { position:absolute; left:0; top:0; bottom:0; width:4px; background:linear-gradient(to bottom, var(--gold) 0%, rgba(201,169,110,0.3) 60%, transparent 100%); z-index:2; }

/* Content column */
.hero-inner { position:relative; z-index:1; width:100%; max-width:600px; padding:140px 0 80px; }

/* Illustration */
.hero-visual { position:absolute; right:8%; bottom:0; pointer-events:none; z-index:0; }
.hero-visual img { height:calc((100vh - 74px) * 1.5); width:auto; display:block; margin-bottom:-2px; }

/* Scroll indicator */
.hero-scroll { position:absolute; left:3%; top:70%; transform:translateY(-50%); display:flex; flex-direction:column; align-items:center; gap:8px; z-index:2; }

.hero-eyebrow { font-size:14px; font-weight:600; letter-spacing:0.34em; text-transform:uppercase; color:var(--gold); margin-bottom:20px; }
.hero-h1      { font-size:58px; font-weight:700; color:var(--white); line-height:1.06; letter-spacing:-0.015em; margin-bottom:24px; }
.hero-h1 em   { font-style:normal; color:var(--gold); font-weight:100; }
.hero-sub     { font-size:19px; font-weight:300; color:rgba(255,255,255,0.48); line-height:1.9; max-width:420px; margin-bottom:44px; letter-spacing:0.02em; }
.hero-actions { display:flex; gap:12px; align-items:center; }
```

---

## 10 FOOTER

```css
.footer { background:var(--navy-deep); padding:56px 80px 34px; }
.footer-grid { display:grid; grid-template-columns:2.2fr 1fr 1fr 1fr; gap:44px; margin-bottom:40px; padding-bottom:40px; border-bottom:1px solid rgba(255,255,255,0.07); }

.f-desc    { font-size:15px; font-weight:300; color:rgba(255,255,255,0.36); line-height:1.85; margin-top:18px; max-width:260px; }
.f-tagline { font-size:16px; font-weight:100; letter-spacing:0.14em; color:var(--gold); margin-top:12px; }

.f-col-label { font-size:11px; font-weight:600; letter-spacing:0.28em; text-transform:uppercase; color:rgba(255,255,255,0.24); margin-bottom:16px; }
.f-links li { margin-bottom:9px; }
.f-links a  { font-size:15px; font-weight:300; color:rgba(255,255,255,0.48); text-decoration:none; transition:var(--transition); letter-spacing:0.03em; }
.f-links a:hover { color:var(--white); }

.f-badge { font-size:9px; font-weight:600; letter-spacing:0.1em; color:var(--gold); border:1px solid rgba(201,169,110,0.45); padding:1px 5px; margin-left:5px; vertical-align:middle; }

.footer-bottom { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }
.f-copy    { font-size:14px; font-weight:300; color:rgba(255,255,255,0.18); letter-spacing:0.05em; }
.f-legal a { font-size:14px; font-weight:300; color:rgba(255,255,255,0.18); text-decoration:none; letter-spacing:0.05em; transition:var(--transition); }
.f-legal a:hover { color:rgba(255,255,255,0.45); }
```

### Footer columns
- **Col 1 (2.2fr):** Logo (72px, `.f-logo-img`) + description + tagline "O capital de que a sua empresa precisa."
- **Col 2:** Soluções — Portugal 2030 · Fundos de Investimento · Benefícios Fiscais · Prémios de Inovação
- **Col 3:** Plataforma — Capital Simulator `em breve` · Tech2Business `em breve` · Conhecimento · Parceiros
- **Col 4:** Empresa — Sobre Nós · Equipa · Carreiras · Contacto
- **Bottom:** © 2009 Open Capital Advisory & Consultancy · Privacidade · Termos · Cookies

---

## 📄 ARTIGOS DE INSTRUMENTOS — `instrumentos/`

### Conceito
A pasta `instrumentos/` é uma biblioteca de artigos editoriais — um por instrumento de financiamento, fiscal ou investimento. Cada artigo é uma página HTML autónoma, criada a partir de um regulamento, ficha técnica ou brief fornecido.

### Princípio fundamental
**Cada instrumento pode ter uma estrutura diferente.** O Claude tem liberdade total para escolher como organizar o conteúdo e que elementos gráficos incluir — desde que respeite as regras abaixo.

---

### ✅ OBRIGATÓRIO em todos os artigos

**1. Navbar** — idêntica ao resto do site (v1.3), com paths relativos `../`
- Logo: `../logo_opencapital_azul_semfundo.png`, height 57px
- Links com `../` prefix (ex: `../biblioteca.html`, `../index.html`)
- Active state em "Soluções" (pois os artigos pertencem a esse menu)

**2. Hero do artigo** — secção navy com:
- Breadcrumb: `Início → Soluções → [Nome do instrumento]`
- Linha dourada vertical (1px, 44px)
- Badge de categoria (Financiamento Público · Investimento Privado · Fiscal · Inovação · Estratégia)
- Título do instrumento (54px/700/white)
- Tagline (20px/300/white 52%)
- Barra de meta-factos (4 itens: dotação/benefício, limite, elegibilidade, estado)

**3. Barra "Voltar ao catálogo"** — imediatamente abaixo do hero
```html
<div class="back-bar">
  <a href="../biblioteca.html" class="back-link">← Voltar ao catálogo de instrumentos</a>
</div>
```

**4. Sidebar** — sempre presente no layout, com:
- Card "Factos Rápidos" (dados chave do instrumento)
- Card CTA navy ("Falar com um especialista" → `../index.html#contactar`)
- Lista "Instrumentos relacionados" (3–5 links para outros artigos)

**5. Footer** — idêntico ao resto do site, paths com `../`

**6. Design system v1.3** — CSS variables, tipografia, cores, border-radius:0, Montserrat

---

### 🎨 LIBERDADE CRIATIVA — o que o Claude pode decidir

O corpo do artigo (`<article>`) pode ser estruturado livremente. O Claude deve escolher os elementos que melhor servem o instrumento específico:

**Building blocks disponíveis** (usar os que fazem sentido, na ordem que fizer sentido):
- Secções de texto corrido com eyebrow + h2 + parágrafos
- Listas com bullet diamond dourado
- Caixas de destaque (`highlight-box`) com border-left gold
- Grelha de estatísticas (`stats-row`) — 2, 3 ou 4 colunas
- Passos numerados (`steps-list`) para processos
- Tabelas de comparação (ex: taxas por escalão, fases de investimento)
- Exemplos de cálculo (ex: SIFIDE II — quanto poupa uma empresa com €500K em I&D)
- Diagramas SVG inline — timelines, funis, matrizes — monoline, navy/gold
- Citações ou notas de destaque (callouts)
- Infográficos simples em HTML+CSS puro
- Secção "Perguntas frequentes" (accordion ou lista simples)
- Secção "Casos de uso" ou "Para que tipo de empresa?"
- Avisos e alertas (ex: "Prazo a fechar em X", "Novo aviso aberto")
- Comparação com instrumentos similares

**Princípios de escolha:**
- Instrumentos fiscais (SIFIDE, RFAI, DLRR) → beneficiam de exemplos de cálculo e tabelas de taxas
- Fundos europeus (PT2030, PRR) → beneficiam de diagramas de processo e timelines
- Investimento privado (VC, PE) → beneficiam de diagrama de fases e comparação de perfis
- Prémios e vouchers → beneficiam de calendário visual e critérios de júri

---

### 📐 Layout obrigatório

```css
/* Grid artigo + sidebar */
.article-layout {
  display:grid;
  grid-template-columns: 1fr 320px;
  gap: 64px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 80px 96px;
  align-items: start;
}
/* Sidebar sticky */
.article-sidebar { position:sticky; top:100px; }
/* Mobile: stack */
@media (max-width:1024px) {
  .article-layout { grid-template-columns:1fr; }
  .article-sidebar { position:static; }
}
```

---

### 📁 Nomenclatura de ficheiros

| Instrumento | Ficheiro |
|---|---|
| Portugal 2030 | `portugal-2030.html` ✅ |
| PRR | `prr.html` |
| COMPETE 2030 | `compete-2030.html` |
| Horizonte Europa | `horizonte-europa.html` |
| Banco de Fomento | `banco-fomento.html` |
| Venture Capital | `venture-capital.html` |
| Private Equity | `private-equity.html` |
| Business Angels | `business-angels.html` |
| Equity Crowdfunding | `crowdfunding.html` |
| SIFIDE II | `sifide-2.html` |
| RFAI | `rfai.html` |
| DLRR | `dlrr.html` |
| Patent Box | `patent-box.html` |
| Prémios de Inovação | `premios-inovacao.html` |
| EIC Accelerator | `eic-accelerator.html` |
| Vouchers IAPMEI | `vouchers-inovacao.html` |
| AICEP | `aicep.html` |
| SAI | `sai.html` |

**Referência:** `instrumentos/portugal-2030.html` é o primeiro artigo publicado — serve como referência visual e estrutural, não como template rígido.

---

### 🔄 Como criar um novo artigo

1. O utilizador fornece: regulamento, ficha técnica, URL oficial, ou brief descritivo do instrumento
2. O Claude lê o material, decide a melhor estrutura editorial para esse instrumento específico
3. Cria `instrumentos/[slug].html` seguindo as regras obrigatórias acima
4. O card correspondente em `biblioteca.html` já tem o `data-href` correto — não é necessário alterar o catálogo

---

## 🗺️ SITE ARCHITECTURE

| # | Menu Label | File | Status |
|---|---|---|---|
| 🏠 | Logo → Homepage | `index.html` | ✅ Built |
| 1 | Soluções | `biblioteca.html` | ✅ Built |
| 2 | Conhecimento | `conhecimento.html` | ✅ Built |
| 3 | Capital Simulator | `capital-simulator.html` | ✅ Built (em breve) |
| 4 | Tech2Business | `tech2business.html` | ✅ Built (em breve) |
| 5 | Parceiros | `parceiros.html` | ✅ Built |
| 6 | Sobre Nós | `sobre-nos.html` | ✅ Built |
| 7 | Carreiras | `carreiras.html` | ✅ Built |

---

## 📁 FILE STRUCTURE

```
opencapital-website/
├── CLAUDE.md
├── index.html
├── biblioteca.html
├── conhecimento.html
├── capital-simulator.html
├── tech2business.html
├── parceiros.html
├── sobre-nos.html
├── carreiras.html
├── logo_opencapital_azul_semfundo.png
├── hero-illustration.jpg.png
└── assets/
    └── design-system.html
```

---

## ⚙️ TECH STACK

- Pure HTML + CSS + Vanilla JS
- Google Fonts: Montserrat only
- SVG icons: inline, monoline, geometric, no fills
- No external CSS libraries (no Bootstrap, Tailwind, etc.)
- No JS frameworks (no React, Vue, etc.)
- Deployment: GitHub Pages (continuous deployment from `main` branch, DNS via Cloudflare)

---

## 📞 CTA DE CONTACTO — REGRA GLOBAL

**Todos os botões e links de contacto apontam para Calendly.**

URL: `https://calendly.com/opencapital`

Isto aplica-se a TODOS os CTAs com texto tipo:
- "Contactar" / "Contacte-nos" / "Contacto"
- "Falar com um especialista" / "Falar com a equipa" / "Falar connosco"
- "Agendar reunião" / "Marcar conversa"
- Qualquer CTA cujo propósito é iniciar contacto com a Open Capital

**Regras:**
- `href="https://calendly.com/opencapital"`
- `target="_blank"` (abre em nova aba)
- Aplica-se em todas as páginas: raiz, `instrumentos/`, `conhecimento/`, e qualquer pasta futura
- Inclui: navbar CTA, sidebar CTAs, hero CTAs, footer "Contacto", mobile CTAs
- **Exceção:** links `mailto:geral@opencapital.pt` em contexto de texto informativo (ex: "o nosso email é geral@opencapital.pt") podem manter o mailto

**Nunca usar:**
- `#contactar` como href de CTA
- `../index.html#contactar` como href de CTA
- `mailto:` em botões de CTA

---

## 🧬 VISUAL STYLE RULES

### Always
- `border-radius: 0` everywhere — buttons, cards, inputs, all elements
- Gold used sparingly — highlights, lines, hover states, badges only
- Sections alternate: white bg ↔ navy bg
- Section padding: `96px 60px`
- Scroll reveal: `.reveal` class + IntersectionObserver
- Inline SVG icons: monoline, 1–1.5px stroke, geometric
- Nav links: sentence case (not uppercase)
- "Em breve" badges: `<sup class="nav-badge">em breve</sup>` inline after link text

### Never
- No rounded corners anywhere
- No other fonts besides Montserrat
- No colours outside the palette
- No heavy box shadows
- No corporate stock image style
- No Bootstrap, Tailwind or any CSS framework
- No filled icons, colour gradients, or rounded playful icon styles
- No uppercase nav links
- No `hero-gold-line` element in any page or article
- No em dashes (—) in any text output, ever — use a comma, period, or rewrite the sentence

---

## 🎨 ILLUSTRATION STYLE

Two distinct visual languages coexist in this project — use each in the right context:

### A) Functional icons (UI elements, cards, section markers)
- Inline SVG, monoline, 1–1.5px stroke
- Geometric, minimal, no fills
- Colour: `#1A3A5C` (navy) or `#C9A96E` (gold) stroke only

### B) Editorial illustrations (human, contextual, expressive)
- Style: **ink sketch — loose gestural line drawing, black on white/light grey**
- Expressive, organic strokes — NOT geometric or rigid
- Black (`#2A2A2A`) on white or very light grey background
- No colour fills — pure line work
- Conveys warmth, intelligence, human connection
- Reference: sketch illustration style, editorial quality

**Where to use editorial illustrations:**
- Sobre Nós — team scene or work moment
- Hero sections of interior pages — as secondary visual element
- Parceiros — relationship/partnership scene
- Carreiras — team culture, people at work

**Where NOT to use:**
- UI icons and functional elements (use monoline SVG instead)
- Cards with dense information
- Small UI components

**How to generate:**
Midjourney prompt base:
> "ink sketch illustration, expressive gestural line drawing, black ink on white, loose confident strokes, [describe scene], no color, editorial style, premium advisory firm context"

---

## ✅ QUALITY CHECKLIST (before finishing any page)

- [ ] CSS variables block present and unmodified
- [ ] Montserrat Google Fonts imported
- [ ] All colours from palette only — no hex outside the 7 defined
- [ ] No border-radius anywhere
- [ ] Gold used sparingly
- [ ] Navbar: logo 57px, links right-aligned, sentence case, "em breve" as `<sup>`
- [ ] Dropdown for "Sobre Nós" contains: Sobre Nós · Carreiras
- [ ] Footer identical to design system (all 4 columns, updated font sizes)
- [ ] Active nav link state on current page
- [ ] "Em breve" superscript on Capital Simulator and Tech2Business
- [ ] Hover states on all interactive elements
- [ ] Scroll reveal animations on sections below the fold
- [ ] Mobile responsive (breakpoint: 768px)

---

## ✍️ ESTILO EDITORIAL — REGRA GLOBAL DE ESCRITA

Aplica-se a **todas as skills de escrita** (`/trend`, `/opiniao`, `/informativo`, e futuras) e a qualquer texto editorial gerado para o site.

### Antíteses — máximo 1 por artigo

Antítese = construção retórica que opõe duas ideias para criar contraste. Exemplos:
- "Não é X, é Y."
- "Menos A, mais B."
- "Não basta X, é preciso Y."
- "X não chega, Y é o que importa."
- "O problema não é A, é B."

Estas figuras são fortes quando usadas com parcimónia, e tornam-se tique editorial quando repetidas. Regra:

- **Máximo 1 antítese por artigo.** Idealmente reservada para um momento de viragem (fim de introdução, abertura de tese, ou conclusão).
- Nunca duas antíteses no mesmo parágrafo, nem em parágrafos consecutivos.
- Antes de fechar o artigo, reler e contar. Se houver mais do que uma, reescrever as restantes em prosa direta.

### Outras figuras a usar com moderação
- Listas tricolónicas ("X, Y e Z") seguidas — variar ritmo
- Perguntas retóricas — máx. 2 por artigo
- Frases curtas isoladas para efeito ("É isto.") — máx. 2 por artigo

O objetivo é prosa premium e confiante, não prosa enfática ou panfletária.

### Vírgula antes de "e" — proibida

Em PT-PT a vírgula antes de "e" coordenativo é estilisticamente pesada e quase sempre desnecessária. Aplicar em todo o texto editorial (corpo, standfirst, tagline, meta-description, excerpts, sidebars).

Exemplos a corrigir:
- "tem lógica, e está errada" → "tem lógica e está errada"
- "não é infinita, e não se substitui" → "não é infinita e não se substitui"
- "alternativas disponíveis, e uma conversa direta" → "alternativas disponíveis e uma conversa direta"

Antes de fechar qualquer artigo, varrer o texto à procura de `, e ` e eliminar todas as ocorrências. A exceção raríssima é quando o "e" inicia uma oração com sujeito diferente que pode confundir o leitor. Nesse caso reescrever a frase em vez de manter a vírgula.

---

## 🦶 FOOTER PARTIAL — SINGLE SOURCE OF TRUTH

O footer vive num único ficheiro: `_partials/footer.html`. Páginas HTML usam marcadores:

```html
<!-- FOOTER:START -->
<!-- FOOTER:END -->
```

O conteúdo entre os marcadores é gerado pelo script `build_footer.py`, que substitui `[[PREFIX]]` no partial pelo `../` adequado à profundidade do ficheiro.

**Regras para skills e agentes que criam páginas HTML:**
1. **Nunca embeber `<footer class="footer">...</footer>` em templates de skills.** Emitir apenas os dois marcadores no sítio onde o footer entraria.
2. **Após criar o ficheiro, correr:** `python build_footer.py [path/ficheiro.html]` (preenche o footer naquele ficheiro específico).
3. **Para alterações ao footer (link novo, copyright, etc.):** editar `_partials/footer.html` e correr `python build_footer.py` (sem args, processa todo o repo).

O CSS do footer (`.footer`, `.f-legal`, `.footer-grid`, etc.) continua dentro do `<style>` de cada página/skill — só o markup é centralizado.

---

## 🚀 AUTO-DEPLOY RULE

**Every skill/command that creates or modifies site files MUST auto-deploy at the end.**

After completing any skill (e.g. `/trend`, `/instrumento`, or any future command), follow these steps automatically without asking the user:

1. Se a skill criou um ficheiro HTML novo: `python build_footer.py [path]` (preenche o footer)
2. `git add` the specific files created or modified by the skill
3. `git commit` with a descriptive message (in Portuguese, lowercase, following the repo's commit style)
4. If on `main`: `git push origin main`
5. If on a worktree/branch: `git checkout main && git merge <branch> && git push origin main`

This ensures GitHub Pages deploys every change immediately. Never skip this step. Never ask "should I commit?" or "should I push?" after a skill completes.

If a push fails (e.g. conflict), inform the user and attempt to resolve.

---

## 📝 CHANGELOG

| Version | Date | Changes |
|---|---|---|
| v1.0 | — | Initial design system |
| v1.2 | — | Hero illustration, navbar logo image, carousel, site structure |
| v1.3 | 2026-03-22 | +25% typography scale (non-titles) · Nav sentence case · Logo 57px · "Em breve" as superscript · Nav right-aligned · Sobre Nós + Carreiras merged into dropdown |
| v1.4 | 2026-05-06 | Footer centralizado em `_partials/footer.html` + `build_footer.py`. Skills emitem marcadores em vez de footer HTML. Drift inter-página eliminado. |
