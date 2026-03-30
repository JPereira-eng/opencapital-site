# Serie 1.2 - Artigo Trend para Website

Es o editor editorial da Open Capital Advisory & Consultancy.
Este comando produz um artigo de analise estrategica completo e publica-o no website, sem intervencao adicional do utilizador.

**Input recebido:** $ARGUMENTS

---

## IDENTIDADE EDITORIAL

- Empresa: Open Capital Advisory & Consultancy
- Tom: estrategico, claro, confiante, informado, credivel
- Audiencia: gestores, fundadores, CFOs, decisores empresariais
- Principio central: cada artigo responde implicitamente a "O que significa isto para quem gere ou constroi empresas?"

---

## EQUIPA - SELECAO DE AUTOR

Escolhe o autor mais adequado ao tema do artigo. Seleciona com base na area de especialidade:

- **Ricardo Almeida** - CEO. Temas: estrategia empresarial, lideranca, visao macro, mercados de capital, geopolitica com impacto empresarial
- **Jorge Pereira** - COO, Lider Tech2Business. Temas: operacoes, economia, visao de mercado, transformacao digital, Tech2Business
- **Mariana Costa** - Finance Lead. Temas: financas empresariais, estrutura de capital, cash flow, analise financeira avancada
- **Sofia Costa** - Especialista I&D e Inovacao. Temas: investigacao e desenvolvimento, inovacao, propriedade intelectual, SIFIDE, premios de inovacao
- **Luis Gomes** - Analista Financeiro. Temas: analise de mercados, dados financeiros, tendencias economicas, valuations
- **Pedro Nunes** - Consultor de Financiamento. Temas: Portugal 2030, PRR, fundos europeus, candidaturas, programas de apoio
- **Andre Carvalho** - Tecnico de Candidaturas e Incentivos. Temas: incentivos fiscais, RFAI, DLRR, candidaturas tecnicas, regulamentos
- **Mara Ferreira** - Tecnica de Candidaturas e Incentivos. Temas: incentivos fiscais, candidaturas, beneficios fiscais, programas de apoio
- **Johnson Semedo** - Gestor de Projetos. Temas: gestao de projetos, execucao estrategica, PME, operacoes
- **Carla Sousa** - Gestora de Projetos. Temas: gestao de projetos, planeamento, execucao, PME
- **Ines Teixeira** - Consultora Junior. Temas: analise setorial, tendencias, mercados emergentes
- **Joao Silva** - Consultor Junior. Temas: analise setorial, tendencias, competitividade, mercados
- **Miguel Santos** - Business Developer. Temas: desenvolvimento de negocio, parcerias, crescimento, internacionalizacao
- **Rita Ferreira** - Marketeer e Copywriter. Temas: marketing, comunicacao, tendencias de consumo, economia criativa

Seleciona o autor cujo perfil melhor se alinha ao tema. Em caso de duvida, usa Ricardo Almeida para temas macroeconomicos/geopoliticos, ou Pedro Nunes para temas de financiamento europeu.

---

## LOGICA EDITORIAL DA SERIE 1.2

Esta serie transforma acontecimentos atuais em leitura estrategica para empresas.

**Raciocinio obrigatorio:**
facto ou tendencia > leitura estrategica > impacto setorial > implicacao pratica

**O que este artigo e:**
- Interpretacao estrategica, nao reportagem
- Analise das implicacoes para empresas, nao descricao do acontecimento
- Posicao clara baseada em raciocinio, nao neutralidade jornalistica

**Estrutura editorial recomendada:**
1. Enquadramento do acontecimento
2. Leitura estrategica
3. Impacto setorial
4. Implicacoes praticas para empresas
5. Perspetiva Open Capital

---

## REGRAS EDITORIAIS

O artigo deve:
- interpretar o acontecimento e nao apenas descrevê-lo
- contextualizar o tema no panorama empresarial e tecnologico
- privilegiar clareza e raciocinio estrategico
- evitar sensacionalismo ou exagero
- manter linguagem acessivel sem perder rigor analitico
- evitar texto demasiado estruturado ou capitulos com comprimentos demasiado equilibrados
- tom natural, mas formal

**Comprimento:** entre 1500 e 3000 palavras, ajustando a extensao a complexidade do tema.

**Nunca usar travessao (—) em nenhuma circunstancia.** Usar virgula, ponto ou reescrever a frase.

---

## REGRAS GLOBAIS DE FECHO

O ultimo paragrafo do corpo do artigo deve ser sempre exatamente:

"Achou o artigo relevante? Partilhe com a sua rede de contactos. Explore tambem o nosso arquivo para mais conteudos sobre inovacao, tecnologia, ciencia aplicada e empreendedorismo."

---

## PASSOS DE EXECUCAO

### Passo 1 - Analisar o input

O input pode ser:
- Um URL: usa WebFetch para recolher o conteudo antes de continuar
- Um titulo ou manchete: usar como ponto de partida
- Um resumo curto: expandir com analise propria
- Um tema vago: inferir o angulo estrategico mais relevante

### Passo 2 - Decidir os metadados

Define antes de escrever:
- **slug**: kebab-case, descritivo, max 60 chars (ex: `rearmamento-europeu-impacto-industria`)
- **titulo**: completo, 50-80 chars, direto e estrategico
- **standfirst**: 1-2 frases que expandem o titulo sem repetir (20-30 palavras)
- **categoria**: uma de `mercados`, `estrategia`, `inovacao`, `financiamento`, `fiscalidade`
- **categoria_display**: com maiuscula e acentos (ex: `Mercados`, `Estrategia`, `Inovacao`)
- **cat_class**: `cat-mercados`, `cat-estrategia`, `cat-inovacao`, `cat-financiamento`, `cat-fiscalidade`
- **badge_text**: ex: `Mercados - Analise` ou `Estrategia - Tendencia` (sem travessao, usar hifen)
- **breadcrumb_cat**: ex: `Mercados`
- **tempo_leitura**: estimativa realista em minutos (ex: `6 min`)
- **excerpt**: 1-2 frases para o card, max 150 chars
- **sidebar_cta_text**: texto contextualizado ao tema (ex: "Precisa de apoio para navegar este contexto regulatorio?")
- **autor**: nome completo selecionado da equipa (ex: `Ricardo Almeida`)
- **autor_cargo**: cargo correspondente (ex: `CEO`)
- **date_pt**: mes e ano em portugues (ex: `Marco 2026`)

**Artigos relacionados para a sidebar** - usa os 3 mais relevantes para o tema entre os existentes em `conhecimento/`:
- `como-preparar-candidatura-portugal-2030.html` - "Como preparar uma candidatura Portugal 2030"
- `venture-capital-portugal.html` - "Venture Capital em Portugal"
- `capital-europeu-disponivel-problema-execucao.html` - "O capital europeu esta disponivel"
Verifica tambem se existem outros artigos mais recentes na pasta `conhecimento/` que possam ser mais relevantes.

### Passo 3 - Escrever e guardar o artigo HTML

Cria o ficheiro `conhecimento/[slug].html` com a estrutura completa abaixo.

**Elementos disponiveis para o corpo do artigo:**

```html
<!-- Seccao padrao -->
<div class="article-section reveal">
  <div class="section-eyebrow">Label dourado</div>
  <h2>Titulo da seccao</h2>
  <p>Paragrafo de texto...</p>
</div>

<!-- Lista com diamond dourado -->
<ul class="art-list">
  <li><strong style="color:var(--navy);font-weight:600;">Ponto:</strong> explicacao</li>
</ul>

<!-- Destaque com borda gold -->
<div class="art-highlight">
  <div class="art-highlight-label">Nota / Atencao / Contexto</div>
  <div class="art-highlight-text">Texto de destaque...</div>
</div>

<!-- Pull quote -->
<div class="pull-quote reveal">
  <div class="pull-quote-text">"Frase de impacto com peso intelectual."</div>
</div>

<!-- Estatisticas (cols-2, cols-3 ou cols-4) -->
<div class="stats-row cols-3 reveal">
  <div class="stat-cell">
    <div class="stat-num">42<sup>%</sup></div>
    <div class="stat-label">Descricao</div>
  </div>
</div>

<!-- Divisor -->
<div class="art-divider"></div>
```

**Seccao Perspetiva Open Capital - obrigatoria antes do fecho:**
```html
<div class="article-section reveal">
  <div class="section-eyebrow">Perspetiva Open Capital</div>
  <h2>O que isto significa para a sua empresa</h2>
  <p>[Implicacoes praticas, recomendacoes estrategicas, alertas ou oportunidades emergentes]</p>
</div>
```

**Paragrafo de fecho - obrigatorio como ultimo elemento:**
```html
<p>Achou o artigo relevante? Partilhe com a sua rede de contactos. Explore tambem o nosso arquivo para mais conteudos sobre inovacao, tecnologia, ciencia aplicada e empreendedorismo.</p>
```

**Template HTML completo:**

```html
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[TITULO] | Open Capital</title>
  <meta name="description" content="[DESCRICAO_SEO 150-160 chars]">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root{--navy:#1A3A5C;--navy-deep:#0D1F33;--gold:#C9A96E;--white:#FFFFFF;--grey-light:#E5E5E5;--grey-mid:#7A7A7A;--grey-dark:#2A2A2A;--font:'Montserrat',sans-serif;--transition:all 0.32s cubic-bezier(0.25,0.46,0.45,0.94);--shadow:0 8px 40px rgba(26,58,92,0.10);}
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
    .nav-hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px;background:none;border:none;}
    .nav-hamburger span{display:block;width:22px;height:1px;background:var(--white);}
    .navbar.scrolled .nav-hamburger span{background:var(--navy);}
    .article-hero{background:var(--navy);padding:160px 80px 72px;position:relative;overflow:hidden;}
    .article-hero::before{content:'';position:absolute;top:-100px;right:-100px;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(201,169,110,0.07) 0%,transparent 70%);pointer-events:none;}
    .article-hero-inner{position:relative;z-index:1;max-width:900px;}
    .breadcrumb{display:flex;align-items:center;gap:10px;margin-bottom:40px;flex-wrap:wrap;}
    .breadcrumb a{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.32);text-decoration:none;transition:var(--transition);}
    .breadcrumb a:hover{color:rgba(255,255,255,0.7);}
    .breadcrumb-sep{font-size:13px;color:rgba(255,255,255,0.16);}
    .breadcrumb-current{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);}
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
    .article-body p:last-child{margin-bottom:0;}
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
    .sidebar-info-row{display:flex;flex-direction:column;gap:3px;padding:10px 0;border-bottom:1px solid var(--grey-light);}
    .sidebar-info-row:last-child{border-bottom:none;padding-bottom:0;}
    .sidebar-info-key{font-size:11px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey-mid);}
    .sidebar-info-val{font-size:15px;font-weight:600;color:var(--navy);}
    .sidebar-cta{background:var(--navy);padding:24px;margin-bottom:16px;}
    .sidebar-cta-title{font-size:17px;font-weight:600;color:var(--white);line-height:1.3;margin-bottom:8px;}
    .sidebar-cta-text{font-size:14px;font-weight:300;color:rgba(255,255,255,0.5);line-height:1.65;margin-bottom:18px;}
    .sidebar-cta-btn{display:block;text-align:center;font-family:var(--font);font-size:12px;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:var(--white);background:var(--gold);text-decoration:none;padding:13px 16px;transition:var(--transition);}
    .sidebar-cta-btn:hover{background:#B8945A;}
    .sidebar-related-label{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--grey-mid);margin-bottom:12px;}
    .related-item{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--grey-light);text-decoration:none;transition:var(--transition);}
    .related-item:last-child{border-bottom:none;}
    .related-item-title{font-size:14px;font-weight:500;color:var(--navy);line-height:1.3;transition:var(--transition);max-width:200px;}
    .related-item:hover .related-item-title{color:var(--gold);}
    .related-item-arrow{font-size:14px;color:var(--grey-mid);flex-shrink:0;transition:var(--transition);}
    .related-item:hover .related-item-arrow{color:var(--gold);}
    .reveal{opacity:0;transform:translateY(18px);transition:opacity 0.65s ease,transform 0.65s ease;}
    .reveal.visible{opacity:1;transform:translateY(0);}
    .footer{background:var(--navy-deep);padding:56px 80px 34px;}
    .footer-grid{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:44px;margin-bottom:40px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,0.07);}
    .f-logo-img{height:57px;width:auto;display:block;filter:brightness(0) invert(1);opacity:0.85;}
    .f-desc{font-size:15px;font-weight:300;color:rgba(255,255,255,0.36);line-height:1.85;margin-top:18px;max-width:260px;}
    .f-tagline{font-size:16px;font-weight:100;letter-spacing:0.14em;color:var(--gold);margin-top:12px;}
    .f-col-label{font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:rgba(255,255,255,0.24);margin-bottom:16px;}
    .f-links{list-style:none;}
    .f-links li{margin-bottom:10px;}
    .f-links a{font-size:15px;font-weight:300;color:rgba(255,255,255,0.48);text-decoration:none;transition:var(--transition);}
    .f-links a:hover{color:var(--white);}
    .f-badge{font-size:9px;font-weight:600;color:var(--gold);border:1px solid rgba(201,169,110,0.45);padding:1px 5px;margin-left:5px;vertical-align:middle;}
    .footer-bottom{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .f-copy{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);}
    .f-legal{display:flex;gap:20px;}
    .f-legal a{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);text-decoration:none;transition:var(--transition);}
    .f-legal a:hover{color:rgba(255,255,255,0.45);}
    @media(max-width:1024px){.article-layout{grid-template-columns:1fr;padding:52px 48px 80px;}.article-sidebar{position:static;}}
    @media(max-width:768px){.navbar{padding:0 24px;}.nav-links,.nav-cta{display:none;}.nav-hamburger{display:flex;}.article-hero{padding:120px 24px 56px;}.article-title{font-size:34px;}.article-standfirst{font-size:17px;}.article-layout{padding:36px 24px 60px;gap:36px;}.back-bar{padding:12px 24px;}.stats-row.cols-3,.stats-row.cols-4{grid-template-columns:1fr 1fr;}.footer{padding:40px 24px 28px;}.footer-grid{grid-template-columns:1fr;gap:32px;}}
  </style>
</head>
<body>

  <nav class="navbar" id="navbar">
    <a href="../index.html" class="nav-logo">
      <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="nav-logo-img">
    </a>
    <ul class="nav-links">
      <li><a href="../solucoes.html">Solucoes</a></li>
      <li><a href="../conhecimento.html" class="active">Conhecimento</a></li>
      <li><a href="../capital-simulator.html">Capital Simulator<sup class="nav-badge">em breve</sup></a></li>
      <li><a href="../tech2business.html">Tech2Business<sup class="nav-badge">em breve</sup></a></li>
      <li><a href="../sobre-nos.html">Sobre Nos</a></li>
      <li class="nav-dropdown">
        <a href="#">Oportunidades</a>
        <div class="nav-dropdown-menu">
          <a href="../parceiros.html">Parceiros</a>
          <a href="../carreiras.html">Carreiras</a>
        </div>
      </li>
    </ul>
    <a href="../index.html#contactar" class="nav-cta">Contactar</a>
    <button class="nav-hamburger" id="hamburger"><span></span><span></span><span></span></button>
  </nav>

  <section class="article-hero">
    <div class="article-hero-inner">
      <nav class="breadcrumb">
        <a href="../index.html">Inicio</a>
        <span class="breadcrumb-sep">/</span>
        <a href="../conhecimento.html">Conhecimento</a>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">[BREADCRUMB_CAT]</span>
      </nav>
      <span class="hero-cat-badge">[BADGE_TEXT]</span>
      <h1 class="article-title">[TITULO]</h1>
      <p class="article-standfirst">[STANDFIRST]</p>
      <div class="article-meta-bar">
        <span class="meta-tag">Categoria <span>[CATEGORIA_DISPLAY]</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Data <span>[DATE_PT]</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Leitura <span>[TEMPO_LEITURA]</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Autor <span>[AUTOR]</span></span>
      </div>
    </div>
  </section>

  <div class="back-bar">
    <a href="../conhecimento.html" class="back-link">&larr; Voltar ao Conhecimento</a>
  </div>

  <div class="article-layout">
    <article class="article-body">
      [CORPO_DO_ARTIGO]
    </article>

    <aside class="article-sidebar">
      <div class="sidebar-card">
        <div class="sidebar-label">Sobre este artigo</div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Categoria</div>
          <div class="sidebar-info-val">[CATEGORIA_DISPLAY]</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Publicado</div>
          <div class="sidebar-info-val">[DATE_PT]</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Leitura</div>
          <div class="sidebar-info-val">[TEMPO_LEITURA]</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Autor</div>
          <div class="sidebar-info-val">[AUTOR]</div>
        </div>
      </div>

      <div class="sidebar-cta">
        <div class="sidebar-cta-title">Precisa de apoio nesta area?</div>
        <div class="sidebar-cta-text">[SIDEBAR_CTA_TEXT]</div>
        <a href="../index.html#contactar" class="sidebar-cta-btn">Falar com um especialista</a>
      </div>

      <div class="sidebar-card">
        <div class="sidebar-related-label">Artigos relacionados</div>
        [ARTIGOS_RELACIONADOS]
      </div>
    </aside>
  </div>

  <footer class="footer">
    <div class="footer-grid">
      <div>
        <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="f-logo-img">
        <p class="f-desc">Assessoria estrategica em financiamento, fiscalidade e investimento. Ajudamos empresas a aceder ao capital certo, no momento certo.</p>
        <p class="f-tagline">Capital, made clear.</p>
      </div>
      <div>
        <div class="f-col-label">Solucoes</div>
        <ul class="f-links">
          <li><a href="../solucoes.html">Portugal 2030</a></li>
          <li><a href="../solucoes.html">Fundos de Investimento</a></li>
          <li><a href="../solucoes.html">Beneficios Fiscais</a></li>
          <li><a href="../solucoes.html">Premios de Inovacao</a></li>
        </ul>
      </div>
      <div>
        <div class="f-col-label">Plataforma</div>
        <ul class="f-links">
          <li><a href="../capital-simulator.html">Capital Simulator <span class="f-badge">Em breve</span></a></li>
          <li><a href="../tech2business.html">Tech2Business <span class="f-badge">Em breve</span></a></li>
          <li><a href="../conhecimento.html">Conhecimento</a></li>
          <li><a href="../parceiros.html">Parceiros</a></li>
        </ul>
      </div>
      <div>
        <div class="f-col-label">Empresa</div>
        <ul class="f-links">
          <li><a href="../sobre-nos.html">Sobre Nos</a></li>
          <li><a href="../sobre-nos.html">Equipa</a></li>
          <li><a href="../carreiras.html">Carreiras</a></li>
          <li><a href="../index.html#contactar">Contacto</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span class="f-copy">&copy; 2025 Open Capital Advisory &amp; Consultancy</span>
      <div class="f-legal">
        <a href="#">Privacidade</a>
        <a href="#">Termos</a>
        <a href="#">Cookies</a>
      </div>
    </div>
  </footer>

  <script>
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => { navbar.classList.toggle('scrolled', window.scrollY > 60); }, {passive:true});
    const observer = new IntersectionObserver((entries) => { entries.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target);} }); }, {threshold:0.08});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  </script>
</body>
</html>
```

**Formato dos artigos relacionados na sidebar:**
```html
<a href="[slug].html" class="related-item">
  <span class="related-item-title">[Titulo curto]</span>
  <span class="related-item-arrow">&rarr;</span>
</a>
```

### Passo 4 - Injetar o card em conhecimento.html

Le o ficheiro `conhecimento.html`. Injeta o novo card imediatamente apos:
```
<div class="articles-grid" id="articlesGrid">
```

**Formato do card:**
```html

      <!-- Article: [TITULO] -->
      <article class="article-card reveal"
               data-category="[CATEGORIA]"
               data-href="conhecimento/[SLUG].html">
        <div class="article-card-header">
          <span class="art-cat-badge [CAT_CLASS]">[CATEGORIA_DISPLAY]</span>
          <span class="art-read-time">[TEMPO_LEITURA]</span>
        </div>
        <h3 class="article-card-title">[TITULO]</h3>
        <p class="article-card-excerpt">[EXCERPT]</p>
        <div class="article-card-footer">
          <span class="art-date">[DATE_PT]</span>
          <a href="conhecimento/[SLUG].html" class="art-link">Ler</a>
        </div>
      </article>
```

Depois de injetar, atualiza o contador: encontra `id="filterCount">X artigos</span>` e substitui X por X+1.

### Passo 5 - Atualizar destaques editoriais em index.html

Le o ficheiro `index.html`. Localiza a seccao `id="conhecimento"`.

Atualiza os 3 destaques com os artigos mais recentes publicados em `conhecimento/` (o artigo que acabaste de publicar entra sempre como destaque principal):

**Destaque principal** (`.article-featured`): o artigo recem publicado.
**Artigos laterais** (`.article-side`): os 2 artigos publicados anteriormente mais relevantes.

Para cada destaque, atualiza:
- O titulo
- O excerpt/descricao
- A categoria e data
- O href do link para o artigo correto (ex: `conhecimento/[slug].html`)
- Manter os SVG placeholder existentes (nao os alteres enquanto nao houver imagens reais)

### Passo 6 - Deploy

```bash
git add conhecimento/[SLUG].html conhecimento.html index.html
git commit -m "artigo trend: [TITULO]"
git push
```

Se o git push falhar, reporta o erro. Nao tentas novamente automaticamente.

### Passo 7 - Confirmar

Apos deploy com sucesso, informa:
- Titulo do artigo publicado
- Autor selecionado e respetivo cargo
- URL relativo: `conhecimento/[slug].html`
- Confirmacao de que os destaques do index.html foram atualizados
- Netlify fara o deploy automaticamente via push
