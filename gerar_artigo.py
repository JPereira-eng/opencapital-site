#!/usr/bin/env python3
"""
Open Capital — Agente de Geração e Publicação de Artigos
=========================================================
Uso:
  python gerar_artigo.py "tema, título ou URL da notícia"
  python gerar_artigo.py  (modo interativo — pede o input)

O agente:
  1. Gera um artigo editorial completo em HTML
  2. Guarda-o em conhecimento/[slug].html
  3. Injeta o card do artigo em conhecimento.html
  4. Atualiza o contador de artigos
"""

import anthropic
import sys
import os
import re
import json
import datetime
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "conhecimento"
CONHECIMENTO_HTML = BASE_DIR / "conhecimento.html"
MODEL = "claude-opus-4-6"

MESES_PT = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março",
    "April": "Abril", "May": "Maio", "June": "Junho",
    "July": "Julho", "August": "Agosto", "September": "Setembro",
    "October": "Outubro", "November": "Novembro", "December": "Dezembro",
}
_now = datetime.datetime.now()
MES_PT = MESES_PT.get(_now.strftime("%B"), _now.strftime("%B"))
ANO = _now.strftime("%Y")
DATE_PT = f"{MES_PT} {ANO}"

# Categorias válidas e suas classes CSS
CATEGORIAS = {
    "financiamento": "cat-financiamento",
    "fiscalidade":   "cat-fiscalidade",
    "estrategia":    "cat-estrategia",
    "inovacao":      "cat-inovacao",
    "mercados":      "cat-mercados",
    "opiniao":       "cat-opiniao",
}

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — REGRAS EDITORIAIS + DESIGN SYSTEM + OUTPUT JSON
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = f"""És o editor editorial da Open Capital Advisory & Consultancy.
A tua função é produzir artigos de análise de alta qualidade para o website da empresa.

Data de hoje: {DATE_PT}

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

=== ELEMENTOS HTML DISPONÍVEIS PARA O CORPO DO ARTIGO ===

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

DESTAQUE (border-left gold):
<div class="art-highlight">
  <div class="art-highlight-label">Nota</div>
  <div class="art-highlight-text">Texto...</div>
</div>

PULL QUOTE:
<div class="pull-quote reveal">
  <div class="pull-quote-text">"Citação de impacto."</div>
</div>

ESTATÍSTICAS (cols-2, cols-3 ou cols-4):
<div class="stats-row cols-3 reveal">
  <div class="stat-cell">
    <div class="stat-num">42<sup>%</sup></div>
    <div class="stat-label">Descrição</div>
  </div>
</div>

DIVISOR:
<div class="art-divider"></div>

=== FORMAT DO OUTPUT ===
Deves devolver um JSON válido com EXACTAMENTE esta estrutura (sem markdown, sem texto antes ou depois):

{{
  "slug": "nome-em-kebab-case",
  "titulo": "Título completo do artigo",
  "descricao_seo": "Descrição para meta description (150-160 chars)",
  "standfirst": "Lead do artigo (1-2 frases)",
  "categoria": "uma de: financiamento, fiscalidade, estrategia, inovacao, mercados, opiniao",
  "categoria_display": "Nome a mostrar (ex: Mercados, Estratégia, Financiamento, etc.)",
  "badge_text": "Categoria · Tipo (ex: Mercados · Análise)",
  "breadcrumb_cat": "Categoria no breadcrumb",
  "tempo_leitura": "X min",
  "corpo_html": "<div class=\\"article-section reveal\\">... TODO O CORPO DO ARTIGO ...</div>",
  "sidebar_cta_text": "Texto do CTA da sidebar contextualizado ao tema",
  "excerpt": "Excerto para o card na lista (2 frases max, ~150 chars)"
}}

REGRAS IMPORTANTES:
- O "corpo_html" deve conter APENAS o conteúdo dentro de <article class="article-body">
- Usa as classes CSS listadas acima
- Não incluas navbar, hero, sidebar, footer — apenas o corpo do artigo
- O JSON deve ser válido — escapa aspas dentro de strings
- A categoria deve ser uma das 6 listadas acima (lowercase, sem acentos)
"""

# ---------------------------------------------------------------------------
# TEMPLATE HTML DO ARTIGO
# ---------------------------------------------------------------------------
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo} | Open Capital</title>
  <meta name="description" content="{descricao_seo}">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy:#1A3A5C; --navy-deep:#0D1F33; --gold:#C9A96E;
      --white:#FFFFFF; --grey-light:#E5E5E5; --grey-mid:#7A7A7A;
      --grey-dark:#2A2A2A; --font:'Montserrat',sans-serif;
      --transition:all 0.32s cubic-bezier(0.25,0.46,0.45,0.94);
      --shadow:0 8px 40px rgba(26,58,92,0.10);
    }}
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{font-family:var(--font);background:var(--white);color:var(--grey-dark);-webkit-font-smoothing:antialiased;}}
    .navbar{{display:flex;align-items:center;justify-content:space-between;padding:0 48px;height:74px;position:fixed;top:0;left:0;right:0;z-index:200;background:var(--navy);border-bottom:1px solid rgba(255,255,255,0.07);transition:var(--transition);}}
    .navbar.scrolled{{background:rgba(255,255,255,0.97);backdrop-filter:blur(20px);border-bottom:1px solid var(--grey-light);}}
    .nav-logo-img{{height:57px;width:auto;display:block;filter:brightness(0) invert(1);transition:var(--transition);}}
    .navbar.scrolled .nav-logo-img{{filter:none;}}
    .nav-links{{display:flex;align-items:center;gap:24px;list-style:none;margin-left:auto;}}
    .nav-links a{{font-size:15px;font-weight:500;letter-spacing:0.08em;text-transform:none;color:rgba(255,255,255,0.68);text-decoration:none;transition:var(--transition);position:relative;padding-bottom:3px;white-space:nowrap;}}
    .nav-links a::after{{content:'';position:absolute;bottom:0;left:0;width:0;height:1px;background:var(--gold);transition:width 0.3s ease;}}
    .nav-links a:hover,.nav-links a.active{{color:var(--white);}}
    .nav-links a:hover::after,.nav-links a.active::after{{width:100%;}}
    .navbar.scrolled .nav-links a{{color:var(--grey-dark);}}
    .navbar.scrolled .nav-links a:hover,.navbar.scrolled .nav-links a.active{{color:var(--navy);}}
    .nav-badge{{font-size:10px;font-weight:600;text-transform:none;color:var(--gold);border:1px solid var(--gold);padding:1px 4px;margin-left:3px;vertical-align:super;line-height:1;}}
    .nav-dropdown{{position:relative;}}
    .nav-dropdown-menu{{position:absolute;top:calc(100% + 8px);right:0;background:var(--white);border:1px solid var(--grey-light);min-width:160px;box-shadow:var(--shadow);display:none;z-index:100;}}
    .nav-dropdown:hover .nav-dropdown-menu{{display:block;}}
    .nav-dropdown-menu a{{display:block;font-size:13px;font-weight:500;color:var(--grey-dark);padding:11px 18px;text-decoration:none;transition:var(--transition);border-bottom:1px solid var(--grey-light);}}
    .nav-dropdown-menu a:last-child{{border-bottom:none;}}
    .nav-dropdown-menu a:hover{{color:var(--navy);background:#FAFAFA;}}
    .nav-dropdown-menu a::after{{display:none!important;}}
    .nav-cta{{font-size:16px;font-weight:600;letter-spacing:0.08em;text-transform:none;color:var(--white);text-decoration:none;border:1px solid rgba(255,255,255,0.28);padding:9px 18px;margin-left:28px;transition:var(--transition);white-space:nowrap;}}
    .nav-cta:hover{{border-color:var(--white);background:rgba(255,255,255,0.08);}}
    .navbar.scrolled .nav-cta{{color:var(--navy);border-color:var(--navy);}}
    .navbar.scrolled .nav-cta:hover{{background:var(--navy);color:var(--white);}}
    .nav-hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px;background:none;border:none;}}
    .nav-hamburger span{{display:block;width:22px;height:1px;background:var(--white);}}
    .navbar.scrolled .nav-hamburger span{{background:var(--navy);}}
    .article-hero{{background:var(--navy);padding:160px 80px 72px;position:relative;overflow:hidden;}}
    .article-hero::before{{content:'';position:absolute;top:-100px;right:-100px;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(201,169,110,0.07) 0%,transparent 70%);pointer-events:none;}}
    .article-hero-inner{{position:relative;z-index:1;max-width:900px;}}
    .breadcrumb{{display:flex;align-items:center;gap:10px;margin-bottom:40px;flex-wrap:wrap;}}
    .breadcrumb a{{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.32);text-decoration:none;transition:var(--transition);}}
    .breadcrumb a:hover{{color:rgba(255,255,255,0.7);}}
    .breadcrumb-sep{{font-size:13px;color:rgba(255,255,255,0.16);}}
    .breadcrumb-current{{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);}}
    .hero-gold-line{{width:1px;height:44px;background:linear-gradient(to bottom,var(--gold),transparent);margin-bottom:20px;}}
    .hero-cat-badge{{display:inline-block;font-size:12px;font-weight:600;letter-spacing:0.20em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(201,169,110,0.35);padding:4px 12px;margin-bottom:20px;}}
    .article-title{{font-size:48px;font-weight:700;color:var(--white);line-height:1.06;letter-spacing:-0.015em;margin-bottom:20px;max-width:820px;}}
    .article-standfirst{{font-size:20px;font-weight:300;color:rgba(255,255,255,0.52);line-height:1.7;max-width:640px;margin-bottom:36px;}}
    .article-meta-bar{{display:flex;align-items:center;gap:20px;flex-wrap:wrap;padding-top:24px;border-top:1px solid rgba(255,255,255,0.08);}}
    .meta-tag{{font-size:12px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.36);}}
    .meta-tag span{{color:rgba(255,255,255,0.7);}}
    .meta-dot{{width:3px;height:3px;background:rgba(255,255,255,0.2);border-radius:50%;}}
    .back-bar{{background:#FAFAFA;border-bottom:1px solid var(--grey-light);padding:14px 80px;}}
    .back-link{{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey-mid);text-decoration:none;display:inline-flex;align-items:center;gap:10px;transition:var(--transition);}}
    .back-link:hover{{color:var(--navy);}}
    .article-layout{{display:grid;grid-template-columns:1fr 300px;gap:56px;max-width:1160px;margin:0 auto;padding:72px 80px 96px;align-items:start;}}
    .article-body .section-eyebrow{{font-size:12px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:12px;}}
    .article-body h2{{font-size:26px;font-weight:600;color:var(--navy);line-height:1.2;margin-bottom:18px;letter-spacing:-0.01em;}}
    .article-body h3{{font-size:19px;font-weight:600;color:var(--navy);line-height:1.3;margin-bottom:12px;margin-top:28px;}}
    .article-body p{{font-size:18px;font-weight:300;color:var(--grey-dark);line-height:1.9;margin-bottom:22px;}}
    .article-body p:last-child{{margin-bottom:0;}}
    .article-section{{margin-bottom:52px;}}
    .art-list{{list-style:none;padding:0;margin:20px 0;display:flex;flex-direction:column;gap:12px;}}
    .art-list li{{display:flex;align-items:flex-start;gap:14px;font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.75;}}
    .art-list li::before{{content:'';width:5px;height:5px;border:1px solid var(--gold);transform:rotate(45deg);flex-shrink:0;margin-top:8px;}}
    .art-highlight{{background:#FAFAFA;border-left:3px solid var(--gold);padding:22px 26px;margin:24px 0;}}
    .art-highlight-label{{font-size:11px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}}
    .art-highlight-text{{font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.8;}}
    .pull-quote{{border-left:3px solid var(--gold);padding:24px 28px;margin:36px 0;}}
    .pull-quote-text{{font-size:22px;font-weight:300;color:var(--navy);line-height:1.5;letter-spacing:-0.01em;font-style:italic;}}
    .stats-row{{display:grid;gap:1px;background:var(--grey-light);border:1px solid var(--grey-light);margin:28px 0;}}
    .stats-row.cols-2{{grid-template-columns:repeat(2,1fr);}}
    .stats-row.cols-3{{grid-template-columns:repeat(3,1fr);}}
    .stats-row.cols-4{{grid-template-columns:repeat(4,1fr);}}
    .stat-cell{{background:var(--white);padding:22px 20px;}}
    .stat-num{{font-size:28px;font-weight:700;color:var(--navy);line-height:1;margin-bottom:6px;}}
    .stat-num sup{{color:var(--gold);font-size:13px;font-weight:300;}}
    .stat-label{{font-size:12px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey-mid);}}
    .art-divider{{height:1px;background:var(--grey-light);margin:44px 0;}}
    .article-sidebar{{position:sticky;top:100px;}}
    .sidebar-card{{border:1px solid var(--grey-light);padding:24px;margin-bottom:16px;position:relative;overflow:hidden;}}
    .sidebar-card::before{{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:var(--gold);}}
    .sidebar-label{{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}}
    .sidebar-info-row{{display:flex;flex-direction:column;gap:3px;padding:10px 0;border-bottom:1px solid var(--grey-light);}}
    .sidebar-info-row:last-child{{border-bottom:none;padding-bottom:0;}}
    .sidebar-info-key{{font-size:11px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey-mid);}}
    .sidebar-info-val{{font-size:15px;font-weight:600;color:var(--navy);}}
    .sidebar-cta{{background:var(--navy);padding:24px;margin-bottom:16px;}}
    .sidebar-cta-title{{font-size:17px;font-weight:600;color:var(--white);line-height:1.3;margin-bottom:8px;}}
    .sidebar-cta-text{{font-size:14px;font-weight:300;color:rgba(255,255,255,0.5);line-height:1.65;margin-bottom:18px;}}
    .sidebar-cta-btn{{display:block;text-align:center;font-family:var(--font);font-size:12px;font-weight:600;letter-spacing:0.18em;text-transform:uppercase;color:var(--white);background:var(--gold);text-decoration:none;padding:13px 16px;transition:var(--transition);}}
    .sidebar-cta-btn:hover{{background:#B8945A;}}
    .sidebar-related-label{{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--grey-mid);margin-bottom:12px;}}
    .related-item{{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--grey-light);text-decoration:none;transition:var(--transition);}}
    .related-item:last-child{{border-bottom:none;}}
    .related-item-title{{font-size:14px;font-weight:500;color:var(--navy);line-height:1.3;transition:var(--transition);max-width:200px;}}
    .related-item:hover .related-item-title{{color:var(--gold);}}
    .related-item-arrow{{font-size:14px;color:var(--grey-mid);flex-shrink:0;transition:var(--transition);}}
    .related-item:hover .related-item-arrow{{color:var(--gold);}}
    .reveal{{opacity:0;transform:translateY(18px);transition:opacity 0.65s ease,transform 0.65s ease;}}
    .reveal.visible{{opacity:1;transform:translateY(0);}}
    .reveal-d1{{transition-delay:0.1s;}}
    .reveal-d2{{transition-delay:0.2s;}}
    .footer{{background:var(--navy-deep);padding:56px 80px 34px;}}
    .footer-grid{{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:44px;margin-bottom:40px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,0.07);}}
    .f-logo-img{{height:57px;width:auto;display:block;filter:brightness(0) invert(1);opacity:0.85;}}
    .f-desc{{font-size:15px;font-weight:300;color:rgba(255,255,255,0.36);line-height:1.85;margin-top:18px;max-width:260px;}}
    .f-tagline{{font-size:16px;font-weight:100;letter-spacing:0.14em;color:var(--gold);margin-top:12px;}}
    .f-col-label{{font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:rgba(255,255,255,0.24);margin-bottom:16px;}}
    .f-links{{list-style:none;}}
    .f-links li{{margin-bottom:10px;}}
    .f-links a{{font-size:15px;font-weight:300;color:rgba(255,255,255,0.48);text-decoration:none;transition:var(--transition);}}
    .f-links a:hover{{color:var(--white);}}
    .f-badge{{font-size:9px;font-weight:600;color:var(--gold);border:1px solid rgba(201,169,110,0.45);padding:1px 5px;margin-left:5px;vertical-align:middle;}}
    .footer-bottom{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}}
    .f-copy{{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);}}
    .f-legal{{display:flex;gap:20px;}}
    .f-legal a{{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);text-decoration:none;transition:var(--transition);}}
    .f-legal a:hover{{color:rgba(255,255,255,0.45);}}
    @media(max-width:1024px){{.article-layout{{grid-template-columns:1fr;padding:52px 48px 80px;}}.article-sidebar{{position:static;}}}}
    @media(max-width:768px){{.navbar{{padding:0 24px;}}.nav-links,.nav-cta{{display:none;}}.nav-hamburger{{display:flex;}}.article-hero{{padding:120px 24px 56px;}}.article-title{{font-size:34px;}}.article-standfirst{{font-size:17px;}}.article-layout{{padding:36px 24px 60px;gap:36px;}}.back-bar{{padding:12px 24px;}}.stats-row.cols-3,.stats-row.cols-4{{grid-template-columns:1fr 1fr;}}.footer{{padding:40px 24px 28px;}}.footer-grid{{grid-template-columns:1fr;gap:32px;}}}}
  </style>
</head>
<body>

  <nav class="navbar" id="navbar">
    <a href="../index.html" class="nav-logo">
      <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="nav-logo-img" onerror="this.style.display='none'">
    </a>
    <ul class="nav-links">
      <li><a href="../solucoes.html">Soluções</a></li>
      <li><a href="../conhecimento.html" class="active">Conhecimento</a></li>
      <li><a href="../capital-simulator.html">Capital Simulator<sup class="nav-badge">em breve</sup></a></li>
      <li><a href="../tech2business.html">Tech2Business<sup class="nav-badge">em breve</sup></a></li>
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
    <button class="nav-hamburger" id="hamburger"><span></span><span></span><span></span></button>
  </nav>

  <section class="article-hero">
    <div class="article-hero-inner">
      <nav class="breadcrumb">
        <a href="../index.html">Início</a>
        <span class="breadcrumb-sep">/</span>
        <a href="../conhecimento.html">Conhecimento</a>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{breadcrumb_cat}</span>
      </nav>
      <div class="hero-gold-line"></div>
      <span class="hero-cat-badge">{badge_text}</span>
      <h1 class="article-title">{titulo}</h1>
      <p class="article-standfirst">{standfirst}</p>
      <div class="article-meta-bar">
        <span class="meta-tag">Categoria <span>{categoria_display}</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Data <span>{date_pt}</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Leitura <span>{tempo_leitura}</span></span>
        <span class="meta-dot"></span>
        <span class="meta-tag">Autor <span>Open Capital</span></span>
      </div>
    </div>
  </section>

  <div class="back-bar">
    <a href="../conhecimento.html" class="back-link">&larr; Voltar ao Conhecimento</a>
  </div>

  <div class="article-layout">
    <article class="article-body">
{corpo_html}
    </article>

    <aside class="article-sidebar">
      <div class="sidebar-card">
        <div class="sidebar-label">Sobre este artigo</div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Categoria</div>
          <div class="sidebar-info-val">{categoria_display}</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Publicado</div>
          <div class="sidebar-info-val">{date_pt}</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Leitura</div>
          <div class="sidebar-info-val">{tempo_leitura}</div>
        </div>
        <div class="sidebar-info-row">
          <div class="sidebar-info-key">Autor</div>
          <div class="sidebar-info-val">Open Capital</div>
        </div>
      </div>

      <div class="sidebar-cta">
        <div class="sidebar-cta-title">Precisa de apoio nesta área?</div>
        <div class="sidebar-cta-text">{sidebar_cta_text}</div>
        <a href="../index.html#contactar" class="sidebar-cta-btn">Falar com um especialista</a>
      </div>

      <div class="sidebar-card">
        <div class="sidebar-related-label">Artigos relacionados</div>
        <a href="como-preparar-candidatura-portugal-2030.html" class="related-item">
          <span class="related-item-title">Como preparar uma candidatura Portugal 2030</span>
          <span class="related-item-arrow">&rarr;</span>
        </a>
        <a href="venture-capital-portugal.html" class="related-item">
          <span class="related-item-title">Venture Capital em Portugal</span>
          <span class="related-item-arrow">&rarr;</span>
        </a>
        <a href="capital-europeu-disponivel-problema-execucao.html" class="related-item">
          <span class="related-item-title">O capital europeu está disponível</span>
          <span class="related-item-arrow">&rarr;</span>
        </a>
      </div>
    </aside>
  </div>

  <footer class="footer">
    <div class="footer-grid">
      <div>
        <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="f-logo-img" onerror="this.style.display='none'">
        <p class="f-desc">Assessoria estratégica em financiamento, fiscalidade e investimento. Ajudamos empresas a aceder ao capital certo, no momento certo.</p>
        <p class="f-tagline">Capital, made clear.</p>
      </div>
      <div>
        <div class="f-col-label">Soluções</div>
        <ul class="f-links">
          <li><a href="../solucoes.html">Portugal 2030</a></li>
          <li><a href="../solucoes.html">Fundos de Investimento</a></li>
          <li><a href="../solucoes.html">Benefícios Fiscais</a></li>
          <li><a href="../solucoes.html">Prémios de Inovação</a></li>
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
          <li><a href="../sobre-nos.html">Sobre Nós</a></li>
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
    window.addEventListener('scroll', () => {{ navbar.classList.toggle('scrolled', window.scrollY > 60); }}, {{passive:true}});
    document.getElementById('hamburger').addEventListener('click', () => {{}});
    const observer = new IntersectionObserver((entries) => {{ entries.forEach(e => {{ if(e.isIntersecting){{e.target.classList.add('visible');observer.unobserve(e.target);}} }}); }}, {{threshold:0.08}});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  </script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# CARD TEMPLATE PARA conhecimento.html
# ---------------------------------------------------------------------------
CARD_TEMPLATE = """
      <!-- Article: {titulo} -->
      <article class="article-card{type_class} reveal"
               data-category="{categoria}"
               data-href="conhecimento/{slug}.html">
        <div class="article-card-header">
          <span class="art-cat-badge {cat_class}">{categoria_display}</span>
          <span class="art-read-time">{tempo_leitura}</span>
        </div>
        <h3 class="article-card-title">{titulo}</h3>
        <p class="article-card-excerpt">{excerpt}</p>
        <div class="article-card-footer">
          <span class="art-date">{date_pt}</span>
          <a href="conhecimento/{slug}.html" class="art-link">Ler</a>
        </div>
      </article>"""

# ---------------------------------------------------------------------------
# FETCH URL
# ---------------------------------------------------------------------------
def fetch_url(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:12000]
    except Exception as e:
        print(f"  [aviso] Não foi possível fazer fetch do URL: {e}")
        return ""

# ---------------------------------------------------------------------------
# GERA O ARTIGO VIA API
# ---------------------------------------------------------------------------
def gerar_artigo(input_text: str) -> dict:
    """Retorna dict com todos os campos do artigo."""
    client = anthropic.Anthropic()

    fetched = ""
    if input_text.strip().startswith(("http://", "https://")):
        print("  → A recolher conteúdo do URL...")
        fetched = fetch_url(input_text.strip())
        if fetched:
            print(f"  → {len(fetched)} caracteres recolhidos.")

    user_prompt = f"Input do utilizador:\n{input_text}\n"
    if fetched:
        user_prompt += f"\nConteúdo da página/notícia:\n{fetched}\n"
    user_prompt += f"\nData atual: {DATE_PT}\n"
    user_prompt += "\nGera o JSON do artigo conforme as instruções."

    print("\n  → A gerar artigo com Claude Opus 4.6...\n")

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extrai o texto (ignora thinking blocks)
    raw_text = ""
    for block in response.content:
        if block.type == "text":
            raw_text += block.text

    # Limpa markdown code fences se existirem
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        # Tenta encontrar JSON dentro do texto
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            data = json.loads(match.group(0))
        else:
            print(f"\n  ERRO ao parsear JSON: {e}")
            print(f"  Resposta bruta (primeiros 500 chars):\n{raw_text[:500]}")
            sys.exit(1)

    # Valida campos obrigatórios
    required = ["slug", "titulo", "descricao_seo", "standfirst", "categoria",
                 "categoria_display", "badge_text", "breadcrumb_cat",
                 "tempo_leitura", "corpo_html", "sidebar_cta_text", "excerpt"]
    for field in required:
        if field not in data:
            print(f"  ERRO: campo '{field}' em falta no JSON gerado.")
            sys.exit(1)

    # Normaliza categoria
    data["categoria"] = data["categoria"].lower().strip()
    if data["categoria"] not in CATEGORIAS:
        print(f"  [aviso] Categoria '{data['categoria']}' não reconhecida, a usar 'estrategia'.")
        data["categoria"] = "estrategia"

    return data

# ---------------------------------------------------------------------------
# MONTA E GUARDA O FICHEIRO HTML DO ARTIGO
# ---------------------------------------------------------------------------
def guardar_artigo(data: dict) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    html = ARTICLE_TEMPLATE.format(
        titulo=data["titulo"],
        descricao_seo=data["descricao_seo"],
        breadcrumb_cat=data["breadcrumb_cat"],
        badge_text=data["badge_text"],
        standfirst=data["standfirst"],
        categoria_display=data["categoria_display"],
        date_pt=DATE_PT,
        tempo_leitura=data["tempo_leitura"],
        corpo_html=data["corpo_html"],
        sidebar_cta_text=data["sidebar_cta_text"],
    )

    slug = data["slug"]
    filepath = OUTPUT_DIR / f"{slug}.html"
    if filepath.exists():
        i = 2
        while filepath.exists():
            filepath = OUTPUT_DIR / f"{slug}-{i}.html"
            slug = f"{data['slug']}-{i}"
            i += 1
        data["slug"] = slug

    filepath.write_text(html, encoding="utf-8")
    return filepath

# ---------------------------------------------------------------------------
# INJETA O CARD EM conhecimento.html
# ---------------------------------------------------------------------------
def publicar_card(data: dict) -> bool:
    if not CONHECIMENTO_HTML.exists():
        print("  [aviso] conhecimento.html não encontrado — card não injetado.")
        return False

    html = CONHECIMENTO_HTML.read_text(encoding="utf-8")

    # Verifica se o artigo já existe
    if f"conhecimento/{data['slug']}.html" in html:
        print("  [info] Card para este artigo já existe em conhecimento.html.")
        return True

    # Monta o card
    cat_class = CATEGORIAS.get(data["categoria"], "cat-estrategia")
    type_class = " type-opiniao" if data["categoria"] == "opiniao" else ""

    card_html = CARD_TEMPLATE.format(
        titulo=data["titulo"],
        categoria=data["categoria"],
        slug=data["slug"],
        cat_class=cat_class,
        categoria_display=data["categoria_display"],
        tempo_leitura=data["tempo_leitura"],
        excerpt=data["excerpt"],
        date_pt=DATE_PT,
        type_class=type_class,
    )

    # Injeta o card como PRIMEIRO item dentro de .articles-grid
    marker = '<div class="articles-grid" id="articlesGrid">'
    if marker not in html:
        print("  [aviso] Não encontrei o marcador articles-grid — card não injetado.")
        return False

    html = html.replace(marker, marker + card_html, 1)

    # Atualiza o contador de artigos
    count_match = re.search(r'id="filterCount">(\d+) artigos?</span>', html)
    if count_match:
        old_count = int(count_match.group(1))
        new_count = old_count + 1
        html = html.replace(
            f'id="filterCount">{old_count} artigos</span>',
            f'id="filterCount">{new_count} artigos</span>',
        )
        # Caso singular
        html = html.replace(
            f'id="filterCount">{old_count} artigo</span>',
            f'id="filterCount">{new_count} artigos</span>',
        )

    CONHECIMENTO_HTML.write_text(html, encoding="utf-8")
    return True

# ---------------------------------------------------------------------------
# DEPLOY AUTOMÁTICO — git push + Netlify hook
# ---------------------------------------------------------------------------
def fazer_deploy(data: dict, filepath: Path) -> bool:
    """
    1. git add os ficheiros alterados
    2. git commit com mensagem automática
    3. git push → Netlify faz deploy automático via integração GitHub

    Opcionalmente: se NETLIFY_DEPLOY_HOOK estiver definida,
    faz também trigger manual da Netlify Deploy Hook URL.
    """
    titulo = data["titulo"]
    slug = data["slug"]

    # Paths relativos ao BASE_DIR para o git add
    artigo_rel = f"conhecimento/{slug}.html"
    conhecimento_rel = "conhecimento.html"

    print("\n  → A fazer deploy automático...")

    try:
        # 1. git add
        result = subprocess.run(
            ["git", "add", artigo_rel, conhecimento_rel],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ✗ git add falhou: {result.stderr.strip()}")
            return False

        # 2. git commit
        commit_msg = f"artigo: {titulo}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Se não há nada novo para commitar (already up to date)
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                print("  [info] Nada novo para commitar.")
                return True
            print(f"  ✗ git commit falhou: {result.stderr.strip()}")
            return False

        print(f"  ✓ Commit: \"{commit_msg}\"")

        # 3. git push
        result = subprocess.run(
            ["git", "push"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ✗ git push falhou: {result.stderr.strip()}")
            print("    Verifica se o repositório remoto está configurado (git remote -v).")
            return False

        print("  ✓ git push concluído → Netlify irá fazer deploy automaticamente.")

        # 4. Netlify Deploy Hook (opcional)
        hook_url = os.environ.get("NETLIFY_DEPLOY_HOOK", "").strip()
        if hook_url:
            try:
                req = urllib.request.Request(
                    hook_url,
                    data=b"{}",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pass
                print("  ✓ Netlify Deploy Hook acionado.")
            except Exception as e:
                print(f"  [aviso] Deploy Hook falhou (o push já foi feito): {e}")

        return True

    except FileNotFoundError:
        print("  ✗ git não encontrado. Instala o Git e tenta novamente.")
        return False
    except Exception as e:
        print(f"  ✗ Erro no deploy: {e}")
        return False


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Open Capital — Agente de Geração de Artigos        ║")
    print("║  Gera + Publica automaticamente em conhecimento/    ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERRO: ANTHROPIC_API_KEY não está definida.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    # Recebe input
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
    else:
        print("Fornece o ponto de partida para o artigo.")
        print("Pode ser: URL, título, resumo, tema, acontecimento.\n")
        input_text = input("→ Input: ").strip()
        if not input_text:
            print("Input vazio. A sair.")
            sys.exit(1)

    print(f"\n  Input: {input_text[:100]}{'...' if len(input_text) > 100 else ''}")

    # --- PASSO 1: Gera o artigo ---
    data = gerar_artigo(input_text)
    print(f"\n  ✓ Artigo gerado: \"{data['titulo']}\"")
    print(f"    Slug: {data['slug']}")
    print(f"    Categoria: {data['categoria_display']}")
    print(f"    Tempo de leitura: {data['tempo_leitura']}")

    # --- PASSO 2: Guarda o HTML ---
    filepath = guardar_artigo(data)
    print(f"\n  ✓ Ficheiro HTML guardado: {filepath}")

    # --- PASSO 3: Injeta card em conhecimento.html ---
    if publicar_card(data):
        print(f"  ✓ Card publicado em conhecimento.html")
    else:
        print(f"  ✗ Card não foi injetado (ver avisos acima)")

    # --- PASSO 4: Deploy automático ---
    deploy_ok = fazer_deploy(data, filepath)

    # --- Resumo final ---
    print()
    print("─" * 56)
    print(f"  Artigo:  conhecimento/{data['slug']}.html")
    print(f"  Título:  {data['titulo']}")
    if deploy_ok:
        print(f"  Deploy:  ✓ publicado no GitHub → Netlify a processar")
    else:
        print(f"  Deploy:  ✗ não foi feito (ver avisos acima)")
        print(f"  Local:   file:///{filepath.as_posix()}")
    print("─" * 56)
    print()

if __name__ == "__main__":
    main()
