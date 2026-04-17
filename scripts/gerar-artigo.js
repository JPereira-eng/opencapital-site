#!/usr/bin/env node

/**
 * Open Capital — Agente de Geração de Artigos
 * =============================================
 *
 * Uso:
 *   node scripts/gerar-artigo.js "tema ou URL"
 *
 * Ou via GitHub Actions (recomendado):
 *   gh workflow run gerar-artigo.yml -f input="tema"
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const { execSync } = require("child_process");

// ---------------------------------------------------------------------------
// CONFIGURAÇÃO
// ---------------------------------------------------------------------------
const BASE_DIR = path.resolve(__dirname, "..");
const OUTPUT_DIR = path.join(BASE_DIR, "conhecimento");
const CONHECIMENTO_HTML = path.join(BASE_DIR, "conhecimento.html");
const MODEL = "claude-opus-4-6";

const MESES_PT = {
  January: "Janeiro",
  February: "Fevereiro",
  March: "Março",
  April: "Abril",
  May: "Maio",
  June: "Junho",
  July: "Julho",
  August: "Agosto",
  September: "Setembro",
  October: "Outubro",
  November: "Novembro",
  December: "Dezembro",
};

const now = new Date();
const MES_PT = MESES_PT[now.toLocaleString("en-US", { month: "long" })];
const ANO = now.getFullYear();
const DATE_PT = `${MES_PT} ${ANO}`;

const CATEGORIAS = {
  financiamento: "cat-financiamento",
  fiscalidade: "cat-fiscalidade",
  estrategia: "cat-estrategia",
  inovacao: "cat-inovacao",
  mercados: "cat-mercados",
  opiniao: "cat-opiniao",
};

// ---------------------------------------------------------------------------
// SYSTEM PROMPT
// ---------------------------------------------------------------------------
const SYSTEM_PROMPT = `És o editor editorial da Open Capital Advisory & Consultancy.
A tua função é produzir artigos de análise de alta qualidade para o website da empresa.

Data de hoje: ${DATE_PT}

=== IDENTIDADE EDITORIAL ===
- Empresa: Open Capital Advisory & Consultancy
- Tagline: Capital, made clear.
- Tom: estratégico · claro · confiante · informado · credível
- Audiência: gestores, fundadores, CFOs, decisores empresariais
- Princípio central: cada artigo deve responder a "O que significa isto para quem gere ou constrói empresas?"

=== REGRAS EDITORIAIS ===
1. Interpretar o acontecimento — não apenas descrevê-lo
2. Contextualizar no panorama empresarial e tecnológico português/europeu
3. Privilegiar clareza e raciocínio estratégico
4. Evitar sensacionalismo ou exagero
5. Linguagem acessível sem perder rigor analítico
6. Estruturação natural — evitar capítulos demasiado equilibrados em tamanho
7. Tom formal mas com naturalidade na escrita
8. Comprimento ideal: 1500–3000 palavras

=== SECÇÃO OBRIGATÓRIA: PERSPETIVA OPEN CAPITAL ===
Incluir secção com section-eyebrow "Perspetiva Open Capital" com:
- Implicações para empresas
- Recomendações estratégicas
- Alertas ou oportunidades emergentes

=== FECHO OBRIGATÓRIO ===
O último parágrafo deve ser EXATAMENTE:
"Achou o artigo relevante? Partilhe com a sua rede de contactos. Explore também o nosso arquivo para mais conteúdos sobre inovação, tecnologia, ciência aplicada e empreendedorismo."

=== ELEMENTOS HTML DISPONÍVEIS ===
SECÇÃO:
<div class="article-section reveal">
  <div class="section-eyebrow">Label</div>
  <h2>Título</h2>
  <p>Texto...</p>
</div>

LISTA:
<ul class="art-list">
  <li><strong style="color:var(--navy);font-weight:600;">Ponto:</strong> texto</li>
</ul>

DESTAQUE:
<div class="art-highlight">
  <div class="art-highlight-label">Nota</div>
  <div class="art-highlight-text">Texto...</div>
</div>

PULL QUOTE:
<div class="pull-quote reveal">
  <div class="pull-quote-text">"Citação de impacto."</div>
</div>

ESTATÍSTICAS:
<div class="stats-row cols-3 reveal">
  <div class="stat-cell">
    <div class="stat-num">42<sup>%</sup></div>
    <div class="stat-label">Descrição</div>
  </div>
</div>

DIVISOR:
<div class="art-divider"></div>

=== FORMAT DO OUTPUT ===
Deves devolver um JSON válido com EXACTAMENTE esta estrutura:

{
  "slug": "nome-em-kebab-case",
  "titulo": "Título completo",
  "descricao_seo": "Descrição para meta (150-160 chars)",
  "standfirst": "Lead (1-2 frases)",
  "categoria": "uma de: financiamento, fiscalidade, estrategia, inovacao, mercados, opiniao",
  "categoria_display": "Nome a mostrar",
  "badge_text": "Categoria · Tipo",
  "breadcrumb_cat": "Categoria no breadcrumb",
  "tempo_leitura": "X min",
  "corpo_html": "<div class=\\"article-section reveal\\">...</div>",
  "sidebar_cta_text": "Texto do CTA contextualizado",
  "excerpt": "2 frases max, ~150 chars"
}

REGRAS:
- corpo_html deve conter APENAS o conteúdo dentro de <article>
- Usa as classes CSS listadas
- Não incluas navbar, hero, sidebar, footer
- JSON válido — escapa aspas dentro de strings
- Categoria lowercase, sem acentos`;

// ---------------------------------------------------------------------------
// TEMPLATE HTML
// ---------------------------------------------------------------------------
const ARTICLE_TEMPLATE = (data) => `<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${data.titulo} | Open Capital</title>
  <meta name="description" content="${data.descricao_seo}">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --navy:#1A3A5C; --navy-deep:#0D1F33; --gold:#C9A96E;
      --white:#FFFFFF; --grey-light:#E5E5E5; --grey-mid:#7A7A7A;
      --grey-dark:#2A2A2A; --font:'Montserrat',sans-serif;
      --transition:all 0.32s cubic-bezier(0.25,0.46,0.45,0.94);
      --shadow:0 8px 40px rgba(26,58,92,0.10);
    }
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:var(--font);background:var(--white);color:var(--grey-dark);-webkit-font-smoothing:antialiased;}
    .navbar{display:flex;align-items:center;justify-content:space-between;padding:0 48px;height:74px;position:fixed;top:0;left:0;right:0;z-index:200;background:var(--navy);border-bottom:1px solid rgba(255,255,255,0.07);transition:var(--transition);}
    .navbar.scrolled{background:rgba(255,255,255,0.97);backdrop-filter:blur(20px);border-bottom:1px solid var(--grey-light);}
    .nav-logo-img{height:57px;width:auto;display:block;filter:brightness(0) invert(1);transition:var(--transition);}
    .navbar.scrolled .nav-logo-img{filter:none;}
    .nav-links{display:flex;align-items:center;gap:24px;list-style:none;margin-left:auto;}
    .nav-links a{font-size:15px;font-weight:500;letter-spacing:0.08em;text-transform:none;color:rgba(255,255,255,0.68);text-decoration:none;transition:var(--transition);position:relative;padding-bottom:3px;white-space:nowrap;}
    .nav-links a::after{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:var(--gold);transition:width 0.3s ease;}
    .nav-links a:hover,.nav-links a.active{color:var(--white);}
    .nav-links a:hover::after,.nav-links a.active::after{width:100%;}
    .navbar.scrolled .nav-links a{color:var(--grey-dark);}
    .navbar.scrolled .nav-links a:hover,.navbar.scrolled .nav-links a.active{color:var(--navy);}
    .nav-badge{font-size:10px;font-weight:600;text-transform:none;color:var(--gold);border:1px solid var(--gold);padding:1px 4px;margin-left:3px;vertical-align:super;line-height:1;}
    .nav-dropdown{position:relative;}
    .nav-dropdown-menu{position:absolute;top:calc(100% + 8px);right:0;background:var(--white);border:1px solid var(--grey-light);min-width:160px;box-shadow:var(--shadow);display:none;z-index:100;}
    .nav-dropdown:hover .nav-dropdown-menu{display:block;}
    .nav-dropdown-menu a{display:block;font-size:13px;font-weight:500;color:var(--grey-dark);padding:11px 18px;text-decoration:none;transition:var(--transition);border-bottom:1px solid var(--grey-light);}
    .nav-dropdown-menu a:last-child{border-bottom:none;}
    .nav-dropdown-menu a:hover{color:var(--navy);background:#FAFAFA;}
    .nav-dropdown-menu a::after{display:none!important;}
    .nav-cta{font-size:16px;font-weight:600;letter-spacing:0.08em;text-transform:none;color:var(--white);text-decoration:none;border:1px solid rgba(255,255,255,0.28);padding:9px 18px;margin-left:28px;transition:var(--transition);white-space:nowrap;}
    .nav-cta:hover{border-color:var(--white);background:rgba(255,255,255,0.08);}
    .navbar.scrolled .nav-cta{color:var(--navy);border-color:var(--navy);}
    .navbar.scrolled .nav-cta:hover{background:var(--navy);color:var(--white);}
    .article-hero{background:var(--navy);padding:160px 80px 72px;position:relative;overflow:hidden;}
    .article-hero::before{content:'';position:absolute;top:-100px;right:-100px;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(201,169,110,0.07) 0%,transparent 70%);pointer-events:none;}
    .article-hero-inner{position:relative;z-index:1;max-width:900px;}
    .breadcrumb{display:flex;align-items:center;gap:10px;margin-bottom:40px;flex-wrap:wrap;}
    .breadcrumb a{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.32);text-decoration:none;transition:var(--transition);}
    .breadcrumb a:hover{color:rgba(255,255,255,0.7);}
    .breadcrumb-sep{font-size:13px;color:rgba(255,255,255,0.16);}
    .breadcrumb-current{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);}
    .hero-gold-line{width:1px;height:44px;background:linear-gradient(to bottom,var(--gold),transparent);margin-bottom:20px;}
    .hero-cat-badge{display:inline-block;font-size:12px;font-weight:600;letter-spacing:0.20em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(201,169,110,0.35);padding:4px 12px;margin-bottom:20px;}
    .article-title{font-size:48px;font-weight:700;color:var(--white);line-height:1.06;letter-spacing:-0.015em;margin-bottom:20px;max-width:820px;}
    .article-standfirst{font-size:20px;font-weight:300;color:rgba(255,255,255,0.52);line-height:1.7;max-width:640px;margin-bottom:36px;}
    .article-meta-bar{display:flex;align-items:center;gap:20px;flex-wrap:wrap;padding-top:24px;border-top:1px solid rgba(255,255,255,0.08);}
    .meta-tag{font-size:12px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.36);}
    .meta-tag span{color:rgba(255,255,255,0.7);}
    .meta-dot{width:3px;height:3px;background:rgba(255,255,255,0.2);border-radius:50%;}
    .back-bar{background:#FAFAFA;border-bottom:1px solid var(--grey-light);padding:14px 80px;}
    .back-link{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey-mid);text-decoration:none;display:inline-flex;align-items:center;gap:10px;transition:var(--transition);}
    .back-link:hover{color:var(--navy);}
    .article-layout{display:grid;grid-template-columns:1fr 300px;gap:56px;max-width:1160px;margin:0 auto;padding:72px 80px 96px;align-items:start;}
    .article-body .section-eyebrow{font-size:12px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:12px;}
    .article-body h2{font-size:26px;font-weight:600;color:var(--navy);line-height:1.2;margin-bottom:18px;letter-spacing:-0.01em;}
    .article-body h3{font-size:19px;font-weight:600;color:var(--navy);line-height:1.3;margin-bottom:12px;margin-top:28px;}
    .article-body p{font-size:18px;font-weight:300;color:var(--grey-dark);line-height:1.9;margin-bottom:22px;}
    .article-section{margin-bottom:52px;}
    .art-list{list-style:none;padding:0;margin:20px 0;display:flex;flex-direction:column;gap:12px;}
    .art-list li{display:flex;align-items:flex-start;gap:14px;font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.75;}
    .art-list li::before{content:'';width:5px;height:5px;border:1px solid var(--gold);transform:rotate(45deg);flex-shrink:0;margin-top:8px;}
    .art-highlight{background:#FAFAFA;border-left:3px solid var(--gold);padding:22px 26px;margin:24px 0;}
    .art-highlight-label{font-size:11px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
    .art-highlight-text{font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.8;}
    .pull-quote{border-left:3px solid var(--gold);padding:24px 28px;margin:36px 0;}
    .pull-quote-text{font-size:22px;font-weight:300;color:var(--navy);line-height:1.5;letter-spacing:-0.01em;font-style:italic;}
    .stats-row{display:grid;gap:1px;background:var(--grey-light);border:1px solid var(--grey-light);margin:28px 0;}
    .stats-row.cols-2{grid-template-columns:repeat(2,1fr);}
    .stats-row.cols-3{grid-template-columns:repeat(3,1fr);}
    .stats-row.cols-4{grid-template-columns:repeat(4,1fr);}
    .stat-cell{background:var(--white);padding:22px 20px;}
    .stat-num{font-size:28px;font-weight:700;color:var(--navy);line-height:1;margin-bottom:6px;}
    .stat-num sup{color:var(--gold);font-size:13px;font-weight:300;}
    .stat-label{font-size:12px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey-mid);}
    .art-divider{height:1px;background:var(--grey-light);margin:44px 0;}
    .article-sidebar{position:sticky;top:100px;}
    .sidebar-card{border:1px solid var(--grey-light);padding:24px;margin-bottom:16px;position:relative;overflow:hidden;}
    .sidebar-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:var(--gold);}
    .sidebar-label{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}
    .sidebar-cta{background:var(--navy);color:var(--white);padding:16px;text-align:center;text-decoration:none;font-size:13px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;transition:var(--transition);}
    .sidebar-cta:hover{background:#0F2A45;}
    .reveal{opacity:0;transform:translateY(20px);animation:reveal 0.6s ease-out forwards;}
    @keyframes reveal{to{opacity:1;transform:translateY(0);}}
    .reveal.visible{animation:none;opacity:1;transform:translateY(0);}
    .footer{background:var(--navy-deep);padding:56px 80px 34px;}
    .footer-grid{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:44px;margin-bottom:40px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,0.07);}
    .f-logo-img{height:57px;width:auto;margin-bottom:12px;}
    .f-desc{font-size:15px;font-weight:300;color:rgba(255,255,255,0.36);line-height:1.85;margin-top:18px;max-width:260px;}
    .f-tagline{font-size:16px;font-weight:100;letter-spacing:0.14em;color:var(--gold);margin-top:12px;}
    .f-col-label{font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:rgba(255,255,255,0.24);margin-bottom:16px;}
    .f-links li{margin-bottom:9px;}
    .f-links a{font-size:15px;font-weight:300;color:rgba(255,255,255,0.48);text-decoration:none;transition:var(--transition);letter-spacing:0.03em;}
    .f-links a:hover{color:var(--white);}
    .f-badge{font-size:9px;font-weight:600;letter-spacing:0.1em;color:var(--gold);border:1px solid rgba(201,169,110,0.45);padding:1px 5px;margin-left:5px;vertical-align:middle;}
    .footer-bottom{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .f-copy{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);letter-spacing:0.05em;}
    .f-legal a{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);text-decoration:none;letter-spacing:0.05em;transition:var(--transition);}
    .f-legal a:hover{color:rgba(255,255,255,0.45);}
    @media(max-width:1024px){.article-layout{grid-template-columns:1fr;}.article-sidebar{position:static;}}
  </style>
</head>
<body>
  <nav class="navbar" id="navbar">
    <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="nav-logo-img">
    <ul class="nav-links">
      <li><a href="../index.html">Soluções</a></li>
      <li><a href="../conhecimento.html" class="active">Conhecimento</a></li>
      <li><a href="../capital-simulator.html">Capital Simulator <sup class="nav-badge">em breve</sup></a></li>
      <li><a href="../tech2business.html">Tech2Business <sup class="nav-badge">em breve</sup></a></li>
      <li><a href="../sobre-nos.html">Sobre Nós</a></li>
      <li class="nav-dropdown">
        <a href="#">Oportunidades</a>
        <div class="nav-dropdown-menu">
          <a href="../parceiros.html">Parceiros</a>
          <a href="../carreiras.html">Carreiras</a>
        </div>
      </li>
    </ul>
    <a href="../index.html#contactar" class="nav-cta">Contactar</a>
  </nav>

  <section class="article-hero">
    <div class="article-hero-inner">
      <div class="breadcrumb">
        <a href="../index.html">Início</a>
        <span class="breadcrumb-sep">→</span>
        <a href="../conhecimento.html">Conhecimento</a>
        <span class="breadcrumb-sep">→</span>
        <span class="breadcrumb-current">${data.breadcrumb_cat}</span>
      </div>
      <div class="hero-gold-line"></div>
      <div class="hero-cat-badge">${data.badge_text}</div>
      <h1 class="article-title">${data.titulo}</h1>
      <p class="article-standfirst">${data.standfirst}</p>
      <div class="article-meta-bar">
        <span class="meta-tag">Categoria: <span>${data.categoria_display}</span></span>
        <div class="meta-dot"></div>
        <span class="meta-tag">Leitura: <span>${data.tempo_leitura}</span></span>
        <div class="meta-dot"></div>
        <span class="meta-tag">Publicado: <span>${DATE_PT}</span></span>
      </div>
    </div>
  </section>

  <div class="back-bar">
    <a href="../conhecimento.html" class="back-link">← Voltar ao conhecimento</a>
  </div>

  <div class="article-layout">
    <article class="article-body">
      ${data.corpo_html}
    </article>

    <aside class="article-sidebar">
      <div class="sidebar-card">
        <div class="sidebar-label">Fale connosco</div>
        <a href="../index.html#contactar" class="sidebar-cta">${data.sidebar_cta_text}</a>
      </div>
      <div class="sidebar-card">
        <div class="sidebar-label">Artigos relacionados</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <a href="portugal-2030.html" style="font-size:13px;color:var(--navy);text-decoration:none;">Portugal 2030 →</a>
          <a href="venture-capital-portugal.html" style="font-size:13px;color:var(--navy);text-decoration:none;">Venture Capital →</a>
        </div>
      </div>
    </aside>
  </div>

  <footer class="footer">
    <div class="footer-grid">
      <div>
        <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="f-logo-img" onerror="this.style.display='none'">
        <p class="f-desc">Assessoria estratégica em financiamento, fiscalidade e investimento.</p>
        <p class="f-tagline">Capital, made clear.</p>
      </div>
      <div>
        <div class="f-col-label">Soluções</div>
        <ul class="f-links" style="list-style:none;padding:0;">
          <li><a href="../biblioteca.html">Portugal 2030</a></li>
          <li><a href="../biblioteca.html">Fundos Europeus</a></li>
          <li><a href="../biblioteca.html">Benefícios Fiscais</a></li>
        </ul>
      </div>
      <div>
        <div class="f-col-label">Plataforma</div>
        <ul class="f-links" style="list-style:none;padding:0;">
          <li><a href="../capital-simulator.html">Capital Simulator <span class="f-badge">em breve</span></a></li>
          <li><a href="../conhecimento.html">Conhecimento</a></li>
          <li><a href="../parceiros.html">Parceiros</a></li>
        </ul>
      </div>
      <div>
        <div class="f-col-label">Empresa</div>
        <ul class="f-links" style="list-style:none;padding:0;">
          <li><a href="../sobre-nos.html">Sobre Nós</a></li>
          <li><a href="../carreiras.html">Carreiras</a></li>
          <li><a href="../index.html#contactar">Contacto</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span class="f-copy">&copy; 2009 Open Capital Advisory &amp; Consultancy</span>
    </div>
  </footer>

  <script>
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => { navbar.classList.toggle('scrolled', window.scrollY > 60); }, {passive:true});
    const observer = new IntersectionObserver((entries) => { entries.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target);} }); }, {threshold:0.08});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  </script>
</body>
</html>`;

// ---------------------------------------------------------------------------
// CARD TEMPLATE
// ---------------------------------------------------------------------------
const CARD_TEMPLATE = (data) => `
      <!-- Article: ${data.titulo} -->
      <article class="article-card reveal"
               data-category="${data.categoria}"
               data-href="conhecimento/${data.slug}.html">
        <div class="article-card-header">
          <span class="art-cat-badge ${CATEGORIAS[data.categoria]}">${data.categoria_display}</span>
          <span class="art-read-time">${data.tempo_leitura}</span>
        </div>
        <h3 class="article-card-title">${data.titulo}</h3>
        <p class="article-card-excerpt">${data.excerpt}</p>
        <div class="article-card-footer">
          <span class="art-date">${DATE_PT}</span>
          <a href="conhecimento/${data.slug}.html" class="art-link">Ler</a>
        </div>
      </article>`;

// ---------------------------------------------------------------------------
// CLAUDE API
// ---------------------------------------------------------------------------
function callClaudeAPI(userPrompt) {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      reject(new Error("ANTHROPIC_API_KEY não está definida"));
      return;
    }

    const payload = JSON.stringify({
      model: MODEL,
      max_tokens: 16000,
      thinking: { type: "adaptive" },
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: userPrompt }],
    });

    const options = {
      hostname: "api.anthropic.com",
      path: "/v1/messages",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        if (res.statusCode === 200) {
          try {
            const json = JSON.parse(body);
            resolve(json);
          } catch (e) {
            reject(new Error(`Erro ao parsear resposta: ${e.message}`));
          }
        } else {
          reject(new Error(`API Error ${res.statusCode}: ${body}`));
        }
      });
    });

    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

// ---------------------------------------------------------------------------
// FETCH URL (para PDFs e notícias)
// ---------------------------------------------------------------------------
function fetchURL(url) {
  return new Promise((resolve) => {
    const isHttps = url.startsWith("https");
    const http = isHttps ? https : require("http");

    http
      .get(url, { timeout: 15000 }, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          let text = data
            .replace(/<script[^>]*>.*?<\/script>/gi, " ")
            .replace(/<style[^>]*>.*?<\/style>/gi, " ")
            .replace(/<[^>]+>/g, " ")
            .replace(/\s+/g, " ")
            .trim();
          resolve(text.slice(0, 12000));
        });
      })
      .on("error", () => resolve(""));
  });
}

// ---------------------------------------------------------------------------
// GERAR ARTIGO
// ---------------------------------------------------------------------------
async function gerarArtigo(inputText) {
  console.log("\n  → A gerar artigo com Claude Opus 4.6...\n");

  let fetched = "";
  if (inputText.match(/^https?:\/\//)) {
    console.log("  → A recolher conteúdo do URL...");
    fetched = await fetchURL(inputText);
    if (fetched) {
      console.log(`  → ${fetched.length} caracteres recolhidos.`);
    }
  }

  let userPrompt = `Input do utilizador:\n${inputText}\n`;
  if (fetched) {
    userPrompt += `\nConteúdo da página/notícia:\n${fetched}\n`;
  }
  userPrompt += `\nData atual: ${DATE_PT}\n`;
  userPrompt += "\nGera o JSON do artigo conforme as instruções.";

  const response = await callClaudeAPI(userPrompt);

  let rawText = "";
  for (const block of response.content) {
    if (block.type === "text") {
      rawText += block.text;
    }
  }

  rawText = rawText.trim();
  if (rawText.startsWith("```")) {
    rawText = rawText.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");
  }

  let data;
  try {
    data = JSON.parse(rawText);
  } catch (e) {
    const match = rawText.match(/\{[\s\S]*\}/);
    if (match) {
      data = JSON.parse(match[0]);
    } else {
      throw new Error(`Erro ao parsear JSON: ${e.message}`);
    }
  }

  // Validação
  const required = [
    "slug",
    "titulo",
    "descricao_seo",
    "standfirst",
    "categoria",
    "categoria_display",
    "badge_text",
    "breadcrumb_cat",
    "tempo_leitura",
    "corpo_html",
    "sidebar_cta_text",
    "excerpt",
  ];

  for (const field of required) {
    if (!data[field]) {
      throw new Error(`Campo obrigatório '${field}' em falta`);
    }
  }

  data.categoria = data.categoria.toLowerCase().trim();
  if (!CATEGORIAS[data.categoria]) {
    console.log(
      `  [aviso] Categoria '${data.categoria}' não reconhecida, a usar 'estrategia'.`
    );
    data.categoria = "estrategia";
  }

  return data;
}

// ---------------------------------------------------------------------------
// GUARDAR ARTIGO
// ---------------------------------------------------------------------------
function guardarArtigo(data) {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  let slug = data.slug;
  let filepath = path.join(OUTPUT_DIR, `${slug}.html`);

  let i = 2;
  while (fs.existsSync(filepath)) {
    slug = `${data.slug}-${i}`;
    filepath = path.join(OUTPUT_DIR, `${slug}.html`);
    i++;
  }

  data.slug = slug;
  const html = ARTICLE_TEMPLATE(data);
  fs.writeFileSync(filepath, html, "utf-8");

  return { filepath, slug };
}

// ---------------------------------------------------------------------------
// PUBLICAR CARD
// ---------------------------------------------------------------------------
function publicarCard(data) {
  if (!fs.existsSync(CONHECIMENTO_HTML)) {
    console.log(
      "  [aviso] conhecimento.html não encontrado — card não injetado."
    );
    return false;
  }

  let html = fs.readFileSync(CONHECIMENTO_HTML, "utf-8");

  if (html.includes(`conhecimento/${data.slug}.html`)) {
    console.log("  [info] Card para este artigo já existe.");
    return true;
  }

  const cardHTML = CARD_TEMPLATE(data);
  const marker = '<div class="articles-grid" id="articlesGrid">';

  if (!html.includes(marker)) {
    console.log("  [aviso] articles-grid não encontrado.");
    return false;
  }

  html = html.replace(marker, marker + cardHTML);

  const countMatch = html.match(/id="filterCount">(\d+) artigos?<\/span>/);
  if (countMatch) {
    const oldCount = parseInt(countMatch[1]);
    const newCount = oldCount + 1;
    html = html.replace(
      `id="filterCount">${oldCount} artigo`,
      `id="filterCount">${newCount} artigo`
    );
  }

  fs.writeFileSync(CONHECIMENTO_HTML, html, "utf-8");
  return true;
}

// ---------------------------------------------------------------------------
// DEPLOY — Git + GitHub
// ---------------------------------------------------------------------------
function fazerDeploy(data, slug) {
  console.log("\n  → A fazer deploy automático...");

  try {
    execSync(`git add conhecimento/${slug}.html conhecimento.html`, {
      cwd: BASE_DIR,
    });

    const commitMsg = `artigo: ${data.titulo}`;
    execSync(`git commit -m "${commitMsg}"`, { cwd: BASE_DIR });
    console.log(`  ✓ Commit: "${commitMsg}"`);

    execSync(`git push`, { cwd: BASE_DIR });
    console.log("  ✓ git push concluído → Netlify irá fazer deploy.");

    return true;
  } catch (err) {
    if (err.message.includes("nothing to commit")) {
      console.log("  [info] Nada novo para commitar.");
      return true;
    }
    console.log(`  ✗ Deploy falhou: ${err.message}`);
    return false;
  }
}

// ---------------------------------------------------------------------------
// MAIN
// ---------------------------------------------------------------------------
async function main() {
  console.log();
  console.log(
    "╔══════════════════════════════════════════════════════╗"
  );
  console.log(
    "║  Open Capital — Agente de Geração de Artigos        ║"
  );
  console.log(
    "║  Gera + Publica automaticamente                      ║"
  );
  console.log(
    "╚══════════════════════════════════════════════════════╝"
  );
  console.log();

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("ERRO: ANTHROPIC_API_KEY não está definida.");
    console.error("  export ANTHROPIC_API_KEY=sk-ant-...");
    process.exit(1);
  }

  let inputText = process.argv[2];
  if (!inputText) {
    console.log(
      "Fornece o ponto de partida para o artigo (tema, URL ou PDF).\n"
    );
    process.exit(1);
  }

  console.log(
    `  Input: ${inputText.slice(0, 100)}${inputText.length > 100 ? "..." : ""}`
  );

  try {
    // PASSO 1
    const data = await gerarArtigo(inputText);
    console.log(`\n  ✓ Artigo gerado: "${data.titulo}"`);
    console.log(`    Slug: ${data.slug}`);
    console.log(`    Categoria: ${data.categoria_display}`);
    console.log(`    Tempo: ${data.tempo_leitura}`);

    // PASSO 2
    const { filepath, slug } = guardarArtigo(data);
    console.log(`\n  ✓ Ficheiro HTML: ${filepath}`);

    // PASSO 3
    if (publicarCard(data)) {
      console.log(`  ✓ Card publicado em conhecimento.html`);
    } else {
      console.log(`  ✗ Card não foi injetado`);
    }

    // PASSO 4
    const deployOk = fazerDeploy(data, slug);

    // RESUMO
    console.log();
    console.log("─".repeat(56));
    console.log(`  Artigo:  conhecimento/${slug}.html`);
    console.log(`  Título:  ${data.titulo}`);
    if (deployOk) {
      console.log(
        `  Deploy:  ✓ publicado no GitHub → Netlify a processar`
      );
    } else {
      console.log(`  Deploy:  ✗ não foi feito (ver avisos acima)`);
    }
    console.log("─".repeat(56));
    console.log();
  } catch (err) {
    console.error(`\n  ERRO: ${err.message}`);
    process.exit(1);
  }
}

main();
