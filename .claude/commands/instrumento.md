# Série 3.1 - Template Editorial de Instrumentos

REGRA CRÍTICA DE ORTOGRAFIA: Aplicar sempre o Acordo Ortográfico de 1990 (AO90) em PT-PT. Usar as grafias atualizadas: ação (não acção), setor/setorial (não sector/sectorial), ativo/atividade/atual (não activo/actividade/actual), objetivo/objeto (não objectivo/objecto), direto/diretamente (não directo/directamente), exato/exatamente (não exacto/exactamente), aspeto (não aspecto), exceção/exceto (não exceptao/excepto), receção (não recepcao), adoção (não adopcao), reação (não reaccao), corretor (não correcto/correctamente), eletrico (não electrico), otimo (não optimo), detetar (não detectar), afetar (não afectar), projeto (não projecto), arquiteto (não arquitecto). Manter "facto", "factual", "contacto", "convicção", "tacto" (PT-PT preserva estas). Nunca gerar artigos com ortografia pre-1990.

Template editorial para artigos de instrumentos de financiamento da Open Capital Advisory & Consultancy.
Este ficheiro define o tom, a estrutura HTML, o CSS e as regras visuais de cada artigo.

A seleção de autor, metadados e lógica de catálogo são definidos no radar-writer.md (que le este ficheiro antes de escrever).

REGRA CRÍTICA: Nunca usar travessão (—) em nenhum texto gerado. Usar vírgula, ponto, hífen (-) ou reescrever a frase.

---

## IDENTIDADE EDITORIAL

- Empresa: Open Capital Advisory & Consultancy
- Tom: técnico mas acessível, rigoroso, orientado para a ação
- Audiência: gestores, fundadores, CFOs, decisores que avaliam instrumentos concretos de financiamento
- Princípio central: cada artigo responde a "Este instrumento e para mim? Quanto vale? Como acedo?"

---

## LÓGICA EDITORIAL DA SÉRIE 3.1

Esta série cria fichas editoriais aprofundadas sobre instrumentos específicos de financiamento, fiscalidade ou investimento.

**Raciocínio obrigatório:**
o que e o instrumento > quem pode aceder > quanto vale e em que condições > como funcionar na prática > o que a Open Capital recomenda

**O que este artigo e:**
- Ficha de referência: clara, completa, atualizada
- Orientação prática para decisores que avaliam se o instrumento se aplica ao seu caso
- Análise crítica dos pontos fortes, limitações e armadilhas comuns

**O que não e:**
- Uma mera transcrição do regulamento oficial
- Um artigo de opinião (esse e a Série 6.2)
- Uma peça de marketing vaga

---

## LIBERDADE CRIATIVA DO CORPO DO ARTIGO

Cada instrumento e diferente. O Claude tem liberdade para decidir a estrutura editorial mais adequada ao instrumento específico.

**Building blocks disponíveis (usar os que fazem sentido, na ordem que fizer sentido):**

- Seccoes de texto com eyebrow + titulo + parágrafos
- Listas com bullet diamond dourado
- Caixas de destaque (highlight-box) com borda gold
- Grelha de estatisticas (stats-row) em 2, 3 ou 4 colunas
- Tabelas de comparação (ex: taxas por escalao, fases de investimento)
- Exemplos de cálculo (ex: "uma empresa com 500K em I&D poupa X")
- Diagramas SVG inline simples (timelines, funis, matrizes) em navy/gold, monoline
- Seccao de perguntas frequentes
- Seccao "Para que tipo de empresa?"
- Avisos e alertas (ex: "Prazo a fechar em X", "Novo aviso aberto")
- Comparação com instrumentos similares

**Seccao obrigatória: "Para que serve" (mapeamento das necessidades)**

Todos os artigos devem incluir uma secção explicita que mapeia o instrumento as 1-3 tags de `necessidades` definidas pelo radar-writer (passo 4g). Esta secção torna visivel ao leitor a lógica do filtro "Necessidade" da biblioteca: porque e que este instrumento aparece quando se filtra por X.

**Posição recomendada:** segunda secção do corpo, imediatamente após "O que e [instrumento]". O leitor já tem o conceito, agora precisa de saber se serve para o seu caso concreto.

**Estrutura padrao:**

```html
<div class="article-section reveal">
  <div class="section-eyebrow">Para que serve</div>
  <h2 class="section-h2">Necessidades que este instrumento resolve</h2>
  <p class="section-text">[1 parágrafo a enquadrar a lógica: que tipo de necessidade(s) este instrumento cobre, e porque e relevante o cruzamento dessas necessidades neste instrumento específico]</p>
  <ul class="article-list">
    <li><strong style="color:var(--navy);font-weight:600;">[Necessidade 1, ex: I&amp;D e ciencia]:</strong> [explicacao de 2-3 linhas concreta ao instrumento, não generica]</li>
    <li><strong style="color:var(--navy);font-weight:600;">[Necessidade 2]:</strong> [...]</li>
  </ul>
</div>
```

**Regras:**

1. As necessidades listadas tem de coincidir com o array `necessidades` do `instruments-catalog.json` (definido no passo 4g do radar-writer). Se houver divergência, e bug, alinhar.
2. Não listar 4+ necessidades. Se o instrumento tem mais de 3 tags no JSON, escolher as 3 mais materialmente relevantes e omitir as restantes da prosa.
3. As explicacoes tem de ser concretas ao instrumento, não definições genericas das tags. Mau: "I&D e ciencia: investigação e desenvolvimento". Bom: "I&D e ciencia: o SIFIDE II reembolsa via deducao a coleta as despesas com pessoal técnico afeto a I&D, contratacao de entidades acreditadas pela ANI e equipamentos."
4. Usar os labels visiveis das tags (ex: "I&D e ciencia", "Capitalizacao e crescimento") em sentence case ou title case, não os slugs.

**PROIBIDO:**
- Nunca incluir secções tipo "Passo a passo", "Guia de processo", "Como candidatar-se passo a passo", "Steps", ou qualquer lista numerada de etapas sequenciais de candidatura. O artigo não e um manual de instrucoes. E uma ficha editorial analítica.

**Princípios de escolha por tipo de instrumento:**
- Instrumentos fiscais (SIFIDE, RFAI, DLRR): incluir exemplos de cálculo e tabelas de taxas
- Fundos europeus (PT2030, PRR): incluir diagrama de processo ou timeline de candidatura
- Investimento privado (VC, PE): incluir diagrama de fases e comparação de perfis
- Premios e vouchers: incluir calendario visual e criterios de seleção

**Elegibilidade geografica e setorial (obrigatório quando aplicavel):**

Sempre que o instrumento tenha restrições explicitas de:
- **Localizacao** (regioes NUTS II, territorios de baixa densidade, regioes menos desenvolvidas, áreas geograficas elegíveis ou excluidas), ou
- **CAE de atividade** (códigos CAE elegíveis, setores cobertos ou excluidos),

o artigo deve explicitar essas restrições com rigor e profundidade adequados, deixando claro ao leitor empresarial se o instrumento se aplica ao seu caso. Apresentar:

- Que regioes/NUTS são elegíveis (e taxas diferenciadas por regiao, se houver)
- Que CAE ou divisoes CAE estao cobertos, e quais estao explicitamente excluidos
- Listar a divisao CAE (2 dígitos) ou a secção quando a lista de CAE a 5 dígitos for longa; listar códigos completos apenas quando curtos e relevantes
- Indicar a fonte normativa (aviso, portaria, regulamento) e respetiva data quando os criterios podem variar entre avisos

Usar os building blocks adequados: `highlight-box` para destacar restrições críticas, `art-table` para taxas regionais ou listas estruturadas, `article-list` para enumerar setores.

Adicionalmente, sempre que aplicavel, incluir nos Factos Rapidos da sidebar:
- `<div class="sidebar-fact-key">Localizacao</div>` com resumo (ex: "Norte, Centro, Alentejo, Algarve, Acores, Madeira" ou "Territorios de baixa densidade")
- `<div class="sidebar-fact-key">CAE elegíveis</div>` com resumo (ex: "Industria transformadora (C), TIC (J)" ou "Transversal a todos os setores")

**Quando NAO aplicar:** se o instrumento e transversal (qualquer empresa, qualquer regiao), não criar secção artificial. Indicar simplesmente nos Factos Rapidos que e transversal.

**Nunca inventar códigos CAE nem regioes elegíveis.** Se o regulamento disponível não específica, indicar que os criterios são definidos no aviso de abertura e não detalhar.

**Comprimento:** idealmente entre 1500 e 2500 palavras, ajustando a extensão a complexidade do instrumento.

**Regra de fecho para material limitado (aplicavel a instrumentos de regime catálogo - bancos, VC, premios, aceleradores):**

Se o regulamento/material disponível no `regulation_local` tem menos de 500 palavras de conteudo útil, produzir artigo mais curto (entre 800 e 1200 palavras em vez de 1500-2500).

**Nunca inventar informação.** Se não ha dados sobre taxa de juro, prazo, dotacao, criterios - não escrever sobre esses pontos. Focar apenas no que e conhecido:
- O que e o instrumento e o seu proposito estratégico
- Quem e a entidade que o oferece (banco, fundo, acelerador, promotor)
- Que tipo de empresa ou projeto se adequa
- Contexto do instrumento no ecossistema português
- Análise crítica da sua relevância

**Nunca incluir "Como candidatar", "Passos para acesso", "Guia de candidatura" ou similares.** Esta e a identidade editorial da Open Capital: ficha analítica, não manual. Mesmo em artigos curtos. Se o leitor quiser candidatar-se, o CTA da sidebar dirige-o para uma reuniao com a equipa.

Artigos curtos mantem a mesma qualidade editorial, a mesma estrutura (navbar + hero + back-bar + corpo + sidebar + footer), os mesmos building blocks. So o corpo e mais conciso. A sidebar permanece completa (Factos Rapidos + CTA + Instrumentos Relacionados).

**Layout:** dividir o conteudo em duas colunas, com a coluna da direita (sidebar) mais estreita, contendo ficha resumo e outras informações relevantes. A sidebar já existe no template (Factos Rapidos + CTA + Instrumentos Relacionados).

O artigo deve:
- basear-se na informação presente nos documentos fornecidos
- evitar linguagem burocratica ou juridica sempre que possível
- privilegiar clareza e utilidade prática
- organizar a informação de forma lógica para leitores empresariais
- evitar estruturacao artificial ou capitulos demasiado equilibrados em tamanho
- transparecer naturalidade na escrita com tom formal

**Nunca usar travessão em nenhuma circunstancia.** Usar vírgula, ponto ou reescrever a frase.

**No hero, apenas o badge de categoria pode usar dourado. Titulo, subtitulo, breadcrumb e meta-bar devem ser brancos ou brancos transparentes.**

**Na sidebar, evitar texto dourado exceto para titulos de secção (labels) e para estados de programa (ex: 'Aberto', 'Ativo'). Valores monetarios e outros dados usam navy.**

---

## REGRAS GLOBAIS DE FECHO

O último parágrafo do corpo do artigo deve ser sempre exatamente (em italico, visualmente distinto do corpo: font-size:15px, color:grey-mid, font-style:italic, margin-top:40px):

"Comentários, correções ou contrapontos são bem-vindos: geral@opencapital.pt"

---

## TEMPLATE HTML

Criar o ficheiro `instrumentos/[slug].html` com a estrutura abaixo. Os metadados (slug, autor, categoria, etc.) são definidos pelo radar-writer antes de chamar este template.

**Elementos disponíveis para o corpo do artigo:**

```html
<!-- Seccao padrao -->
<div class="article-section reveal">
  <div class="section-eyebrow">Label dourado</div>
  <h2 class="section-h2">Titulo da secção</h2>
  <p class="section-text">Parágrafo de texto...</p>
</div>

<!-- Lista com diamond dourado -->
<ul class="article-list">
  <li><strong style="color:var(--navy);font-weight:600;">Ponto:</strong> explicacao</li>
</ul>

<!-- Destaque com borda gold -->
<div class="highlight-box">
  <div class="highlight-box-title">Nota / Atencao / Contexto</div>
  <div class="highlight-box-text">Texto de destaque...</div>
</div>

<!-- Estatisticas (cols-2, cols-3 ou cols-4) -->
<div class="stats-row reveal" style="grid-template-columns:repeat(3,1fr);">
  <div class="stat-cell">
    <div class="stat-num">82<sup>%</sup></div>
    <div class="stat-label">Taxa de deducao</div>
  </div>
</div>

<!-- Passos numerados -->
<div class="steps-list">
  <div class="step-item">
    <div class="step-num">01</div>
    <div class="step-content">
      <div class="step-title">Titulo do passo</div>
      <div class="step-desc">Descrição do passo...</div>
    </div>
  </div>
</div>

<!-- Tabela -->
<table class="art-table">
  <thead><tr><th>Coluna 1</th><th>Coluna 2</th><th>Coluna 3</th></tr></thead>
  <tbody>
    <tr><td><strong>Linha 1</strong></td><td>Valor</td><td>Valor</td></tr>
  </tbody>
</table>

<!-- Divisor -->
<div class="art-divider"></div>
```

**Seccao Perspetiva Open Capital - obrigatória antes do fecho:**
```html
<div class="article-section reveal">
  <div class="section-eyebrow">Perspetiva Open Capital</div>
  <h2 class="section-h2">O que recomendamos</h2>
  <p class="section-text">[Análise crítica, alertas práticos, quando faz sentido candidatar, erros comuns a evitar]</p>
</div>
```

**Parágrafo de fecho - obrigatório como último elemento:**
```html
<p style="font-size:12px;color:var(--grey-mid);margin-top:40px;text-align:right;">Comentários, correções ou contrapontos são bem-vindos: <a href="mailto:geral@opencapital.pt" style="color:inherit;text-decoration:underline;">geral@opencapital.pt</a></p>
```

**Template HTML completo:**

```html
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[NOME_INSTRUMENTO]: Open Capital</title>
  <meta name="description" content="[DESCRICAO_SEO 150-160 chars]">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@100;200;300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root{--navy:#1A3A5C;--navy-deep:#0D1F33;--gold:#C9A96E;--white:#FFFFFF;--grey-light:#E5E5E5;--grey-mid:#7A7A7A;--grey-dark:#2A2A2A;--font:'Montserrat',sans-serif;--transition:all 0.32s cubic-bezier(0.25,0.46,0.45,0.94);--shadow:0 8px 40px rgba(26,58,92,0.10);}
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:var(--font);background:var(--white);color:var(--grey-dark);-webkit-font-smoothing:antialiased;}

    /* NAVBAR */
    .navbar{display:flex;align-items:center;justify-content:space-between;padding:0 48px;height:74px;position:fixed;top:0;left:0;right:0;z-index:200;background:var(--navy);border-bottom:1px solid rgba(255,255,255,0.07);transition:var(--transition);}
    .navbar.scrolled{background:rgba(255,255,255,0.97);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--grey-light);}
    .nav-logo{display:flex;align-items:center;text-decoration:none;flex-shrink:0;}
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
    .nav-hamburger span{display:block;width:22px;height:1px;background:var(--white);transition:var(--transition);}
    .navbar.scrolled .nav-hamburger span{background:var(--navy);}
    .nav-mobile-menu{display:none;position:fixed;top:74px;left:0;right:0;background:var(--navy);padding:24px 32px 32px;border-bottom:1px solid rgba(255,255,255,0.07);z-index:199;}
    .nav-mobile-menu.open{display:block;}
    .nav-mobile-menu a{display:block;font-size:15px;font-weight:500;color:rgba(255,255,255,0.7);text-decoration:none;padding:13px 0;border-bottom:1px solid rgba(255,255,255,0.06);transition:var(--transition);}
    .nav-mobile-menu a:hover{color:var(--white);}
    .nav-mobile-cta{display:inline-block!important;margin-top:22px;font-size:14px;font-weight:600;color:var(--white)!important;border:1px solid rgba(255,255,255,0.28);padding:12px 24px;}

    /* ARTICLE HERO */
    .article-hero{background:var(--navy);padding:160px 80px 80px;position:relative;overflow:hidden;}
    .article-hero::before{content:'';position:absolute;top:-120px;right:-120px;width:480px;height:480px;border-radius:50%;background:radial-gradient(circle,rgba(201,169,110,0.07) 0%,transparent 70%);pointer-events:none;}
    .article-hero-inner{position:relative;z-index:1;max-width:860px;}
    .breadcrumb{display:flex;align-items:center;gap:10px;margin-bottom:44px;flex-wrap:wrap;}
    .breadcrumb a{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.32);text-decoration:none;transition:var(--transition);}
    .breadcrumb a:hover{color:rgba(255,255,255,0.7);}
    .breadcrumb-sep{font-size:13px;color:rgba(255,255,255,0.16);}
    .breadcrumb-current{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.7);}
    .hero-cat{font-size:13px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--gold);margin-bottom:18px;}
    .hero-title{font-size:54px;font-weight:700;color:var(--white);line-height:1.06;letter-spacing:-0.015em;margin-bottom:18px;}
    .hero-tagline{font-size:20px;font-weight:300;color:rgba(255,255,255,0.52);line-height:1.7;max-width:560px;margin-bottom:36px;}
    .hero-meta{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding-top:28px;border-top:1px solid rgba(255,255,255,0.08);}
    .meta-item{display:flex;flex-direction:column;gap:4px;}
    .meta-label{font-size:10px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:rgba(255,255,255,0.28);}
    .meta-value{font-size:15px;font-weight:500;color:var(--white);}
    .meta-value.gold{color:var(--white);}
    .meta-value.status-open{color:#2E7D52;font-weight:600;}
    .meta-value.status-closed{color:#A63228;font-weight:600;}
    .meta-value.status-cont{color:#2E7D52;font-weight:600;}
    .meta-sep{width:1px;height:36px;background:rgba(255,255,255,0.10);}

    /* BACK BAR */
    .back-bar{background:#FAFAFA;border-top:1px solid var(--grey-light);border-bottom:1px solid var(--grey-light);padding:16px 80px;}
    .back-link{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--grey-mid);text-decoration:none;display:inline-flex;align-items:center;gap:10px;transition:var(--transition);}
    .back-link:hover{color:var(--navy);}

    /* ARTICLE LAYOUT */
    .article-layout{display:grid;grid-template-columns:1fr 300px;gap:56px;padding:80px 80px 96px;align-items:start;}
    .article-body{}
    .article-section{margin-bottom:56px;}
    .article-section:last-child{margin-bottom:0;}
    .section-eyebrow{font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:14px;}
    .section-h2{font-size:28px;font-weight:600;color:var(--navy);line-height:1.2;margin-bottom:20px;}
    .section-text{font-size:18px;font-weight:300;color:var(--grey-dark);line-height:1.9;margin-bottom:20px;}
    .section-text:last-child{margin-bottom:0;}
    .article-list{list-style:none;padding:0;display:flex;flex-direction:column;gap:12px;margin:20px 0;}
    .article-list li{position:relative;padding-left:20px;font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.75;}
    .article-list li::before{content:'';position:absolute;left:0;top:10px;width:5px;height:5px;border:1px solid var(--gold);transform:rotate(45deg);}
    .highlight-box{background:#FAFAFA;border-left:3px solid var(--gold);padding:24px 28px;margin:28px 0;}
    .highlight-box-title{font-size:12px;font-weight:600;letter-spacing:0.22em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
    .highlight-box-text{font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.8;}
    .stats-row{display:grid;gap:1px;background:var(--grey-light);border:1px solid var(--grey-light);margin:28px 0;}
    .stat-cell{background:var(--white);padding:24px 20px;}
    .stat-num{font-size:30px;font-weight:700;color:var(--navy);line-height:1;margin-bottom:6px;}
    .stat-num sup{color:var(--gold);font-size:14px;font-weight:300;}
    .stat-label{font-size:12px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey-mid);}
    .steps-list{display:flex;flex-direction:column;gap:0;margin:20px 0;}
    .step-item{display:flex;align-items:flex-start;gap:20px;padding:20px 0;border-bottom:1px solid var(--grey-light);}
    .step-item:first-child{padding-top:0;}
    .step-item:last-child{border-bottom:none;padding-bottom:0;}
    .step-num{font-size:11px;font-weight:700;color:var(--gold);border:1px solid rgba(201,169,110,0.4);width:32px;height:32px;min-width:32px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;}
    .step-title{font-size:17px;font-weight:600;color:var(--navy);margin-bottom:6px;}
    .step-desc{font-size:16px;font-weight:300;color:var(--grey-mid);line-height:1.75;}
    .art-divider{height:1px;background:var(--grey-light);margin:48px 0;}
    .art-divider-gold{height:1px;background:linear-gradient(to right,var(--gold),transparent);margin:48px 0;}
    .art-table{width:100%;border-collapse:collapse;margin:28px 0;font-size:15px;}
    .art-table thead{border-bottom:2px solid var(--navy);}
    .art-table th{font-size:11px;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey-mid);padding:12px 16px;text-align:left;}
    .art-table td{padding:14px 16px;border-bottom:1px solid var(--grey-light);font-weight:300;color:var(--grey-dark);line-height:1.6;}
    .art-table tr:last-child td{border-bottom:none;}
    .art-table td strong{font-weight:600;color:var(--navy);}

    /* SIDEBAR */
    .article-sidebar{position:sticky;top:100px;}
    .sidebar-author{border:1px solid var(--grey-light);padding:24px;margin-bottom:20px;position:relative;overflow:hidden;}
    .sidebar-author::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:var(--gold);}
    .sidebar-author-label{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--grey-mid);margin-bottom:14px;}
    .sidebar-author-inner{display:flex;align-items:center;gap:14px;}
    .sidebar-author-photo{width:56px;height:56px;border-radius:50%;object-fit:cover;flex-shrink:0;}
    .sidebar-author-name{font-size:15px;font-weight:600;color:var(--navy);line-height:1.3;}
    .sidebar-author-role{font-size:12px;font-weight:400;color:var(--grey-mid);letter-spacing:0.04em;margin-top:2px;}
    .sidebar-card{border:1px solid var(--grey-light);padding:28px;margin-bottom:20px;position:relative;overflow:hidden;}
    .sidebar-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:var(--gold);}
    .sidebar-card-label{font-size:11px;font-weight:600;letter-spacing:0.26em;text-transform:uppercase;color:var(--gold);margin-bottom:16px;}
    .sidebar-fact{display:flex;flex-direction:column;gap:3px;padding:12px 0;border-bottom:1px solid var(--grey-light);}
    .sidebar-fact:last-child{border-bottom:none;padding-bottom:0;}
    .sidebar-fact-key{font-size:11px;font-weight:500;letter-spacing:0.16em;text-transform:uppercase;color:var(--grey-mid);}
    .sidebar-fact-val{font-size:15px;font-weight:600;color:var(--navy);}
    .sidebar-fact-val.val-gold{color:var(--gold);}
    .sidebar-fact-val.val-open{color:#2E7D52;font-weight:600;}
    .sidebar-fact-val.val-closed{color:#A63228;font-weight:600;}
    .sidebar-fact-val.val-cont{color:#2E7D52;font-weight:600;}
    .sidebar-cta{background:var(--navy);padding:28px;margin-bottom:20px;}
    .sidebar-cta-title{font-size:18px;font-weight:600;color:var(--white);line-height:1.3;margin-bottom:10px;}
    .sidebar-cta-text{font-size:15px;font-weight:300;color:rgba(255,255,255,0.52);line-height:1.7;margin-bottom:20px;}
    .sidebar-cta-btn{display:block;text-align:center;font-family:var(--font);font-size:13px;font-weight:600;letter-spacing:0.20em;text-transform:uppercase;color:var(--white);background:var(--gold);text-decoration:none;padding:14px 20px;transition:var(--transition);}
    .sidebar-cta-btn:hover{background:#B8945A;}
    .sidebar-related-title{font-size:11px;font-weight:600;letter-spacing:0.26em;text-transform:uppercase;color:var(--grey-mid);margin-bottom:14px;}
    .related-link{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--grey-light);text-decoration:none;transition:var(--transition);}
    .related-link:last-child{border-bottom:none;}
    .related-link-name{font-size:15px;font-weight:500;color:var(--navy);transition:var(--transition);}
    .related-link:hover .related-link-name{color:var(--gold);}
    .related-link-arrow{font-size:14px;font-weight:300;color:var(--grey-mid);transition:var(--transition);}
    .related-link:hover .related-link-arrow{color:var(--gold);transform:translateX(3px);}

    /* SCROLL REVEAL */
    .reveal{opacity:0;transform:translateY(18px);transition:opacity 0.65s ease,transform 0.65s ease;}
    .reveal.visible{opacity:1;transform:translateY(0);}

    /* FOOTER */
    .footer{background:var(--navy-deep);padding:56px 80px 34px;}
    .footer-grid{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:44px;margin-bottom:40px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,0.07);}
    .f-logo-row{display:flex;align-items:center;}
    .f-logo-img{height:72px;width:auto;filter:brightness(0) invert(1);opacity:0.75;}
    .f-tagline{font-size:16px;font-weight:100;letter-spacing:0.14em;color:var(--gold);margin-top:12px;}
    .f-col-label{font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:rgba(255,255,255,0.24);margin-bottom:16px;}
    .f-links{list-style:none;}
    .f-links li{margin-bottom:10px;}
    .f-links a{font-size:15px;font-weight:300;color:rgba(255,255,255,0.48);text-decoration:none;transition:var(--transition);}
    .f-links a:hover{color:var(--white);}
    .f-badge{font-size:9px;font-weight:600;color:var(--gold);border:1px solid rgba(201,169,110,0.45);padding:1px 5px;margin-left:5px;vertical-align:middle;}
    .footer-bottom{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .f-copy{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);letter-spacing:0.05em;}
    .f-legal{display:flex;gap:20px;}
    .f-legal a{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);text-decoration:none;transition:var(--transition);}
    .f-legal a:hover{color:rgba(255,255,255,0.45);}

    /* RESPONSIVE */
    @media(max-width:1024px){.article-layout{grid-template-columns:1fr;padding:60px 48px 80px;}.article-sidebar{position:static;}}
    @media(max-width:768px){.navbar{padding:0 24px;}.nav-links,.nav-cta{display:none;}.nav-hamburger{display:flex;}.article-hero{padding:120px 28px 60px;}.hero-title{font-size:38px;}.hero-tagline{font-size:17px;}.article-layout{padding:40px 24px 60px;gap:36px;}.stats-row{grid-template-columns:1fr 1fr!important;}.back-bar{padding:14px 24px;}.footer{padding:40px 24px 28px;}.footer-grid{grid-template-columns:1fr;gap:32px;}}
  </style>
</head>
<body>

<nav class="navbar" id="navbar">
  <a href="../index.html" class="nav-logo">
    <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="nav-logo-img">
  </a>
  <ul class="nav-links">
    <li><a href="../biblioteca.html" class="active">Biblioteca</a></li>
    <li><a href="../conhecimento.html">Conhecimento</a></li>
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
  <a href="https://calendly.com/opencapital" class="nav-cta">Contactar</a>
  <button class="nav-hamburger" id="hamburger"><span></span><span></span><span></span></button>
</nav>
<div class="nav-mobile-menu" id="mobileMenu">
  <a href="../biblioteca.html">Biblioteca</a>
  <a href="../conhecimento.html">Conhecimento</a>
  <a href="../capital-simulator.html">Capital Simulator<sup class="nav-badge">em breve</sup></a>
  <a href="../tech2business.html">Tech2Business<sup class="nav-badge">em breve</sup></a>
  <a href="../sobre-nos.html">Sobre Nós</a>
  <a href="../parceiros.html">Parceiros</a>
  <a href="../carreiras.html">Carreiras</a>
  <a href="https://calendly.com/opencapital" class="nav-mobile-cta">Contactar</a>
</div>

<section class="article-hero">
  <div class="article-hero-inner">
    <nav class="breadcrumb">
      <a href="../index.html">Início</a>
      <span class="breadcrumb-sep">/</span>
      <a href="../biblioteca.html">Biblioteca</a>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-current">[NOME_INSTRUMENTO]</span>
    </nav>
    <p class="hero-cat">[CATEGORIA_BADGE]</p>
    <h1 class="hero-title">[NOME_INSTRUMENTO]</h1>
    <p class="hero-tagline">[HERO_TAGLINE]</p>
    <div class="hero-meta">
      <div class="meta-item">
        <span class="meta-label">[META_FACT_1_LABEL]</span>
        <span class="meta-value gold">[META_FACT_1_VALOR]</span>
      </div>
      <div class="meta-sep"></div>
      <div class="meta-item">
        <span class="meta-label">[META_FACT_2_LABEL]</span>
        <span class="meta-value">[META_FACT_2_VALOR]</span>
      </div>
      <div class="meta-sep"></div>
      <div class="meta-item">
        <span class="meta-label">[META_FACT_3_LABEL]</span>
        <span class="meta-value">[META_FACT_3_VALOR]</span>
      </div>
      <div class="meta-sep"></div>
      <div class="meta-item">
        <span class="meta-label">[META_FACT_4_LABEL]</span>
        <span class="meta-value gold">[META_FACT_4_VALOR]</span>
      </div>
    </div>
  </div>
</section>

<div class="back-bar">
  <a href="../biblioteca.html" class="back-link">&larr; Voltar ao catálogo de instrumentos</a>
</div>

<div class="article-layout">
  <article class="article-body">
    [CORPO_DO_ARTIGO]
  </article>

  <aside class="article-sidebar">
    <div class="sidebar-author">
      <div class="sidebar-author-label">Autor</div>
      <div class="sidebar-author-inner">
        <img src="../Retratos Equipa/[AUTOR_FOTO]" alt="[AUTOR]" class="sidebar-author-photo">
        <div>
          <div class="sidebar-author-name">[AUTOR]</div>
          <div class="sidebar-author-role">[AUTOR_CARGO]</div>
        </div>
      </div>
    </div>

    <div class="sidebar-card">
      <div class="sidebar-card-label">Factos Rapidos</div>
      [SIDEBAR_FACTOS - formato abaixo]
    </div>

    <div class="sidebar-cta">
      <div class="sidebar-cta-title">Falar com um especialista</div>
      <div class="sidebar-cta-text">[SIDEBAR_CTA_TEXT]</div>
      <a href="https://calendly.com/opencapital" class="sidebar-cta-btn">Contactar</a>
    </div>

    <div class="sidebar-card">
      <div class="sidebar-related-title">Instrumentos relacionados</div>
      [INSTRUMENTOS_RELACIONADOS - formato abaixo]
    </div>
  </aside>
</div>

<footer class="footer">
  <div class="footer-grid">
    <div>
      <div class="f-logo-row">
        <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="f-logo-img">
      </div>
      <p class="f-tagline">O capital de que a sua empresa precisa.</p>
    </div>
    <div>
      <div class="f-col-label">Biblioteca</div>
      <ul class="f-links">
        <li><a href="../biblioteca.html">Portugal 2030</a></li>
        <li><a href="../biblioteca.html">Fundos de Investimento</a></li>
        <li><a href="../biblioteca.html">Benefícios Fiscais</a></li>
        <li><a href="../biblioteca.html">Prémios de Inovação</a></li>
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
        <li><a href="https://calendly.com/opencapital">Contacto</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span class="f-copy">&copy; 2009 Open Capital Advisory &amp; Consultancy</span>
    <div class="f-legal">
      <a href="#">Privacidade</a>
      <a href="#">Termos</a>
      <a href="#">Cookies</a>
    </div>
  </div>
</footer>

<script>
  const navbar = document.getElementById('navbar');
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  window.addEventListener('scroll', () => { navbar.classList.toggle('scrolled', window.scrollY > 60); }, {passive:true});
  hamburger.addEventListener('click', () => { mobileMenu.classList.toggle('open'); });
  const observer = new IntersectionObserver((entries) => { entries.forEach(e => { if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target);} }); }, {threshold:0.08});
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
</script>
</body>
</html>
```

**Formato dos factos rapidos na sidebar:**
```html
<div class="sidebar-fact">
  <div class="sidebar-fact-key">Dotacao</div>
  <div class="sidebar-fact-val">€23 mil milhoes</div>
</div>
<div class="sidebar-fact">
  <div class="sidebar-fact-key">Elegibilidade</div>
  <div class="sidebar-fact-val">PME e grandes empresas</div>
</div>
```
NAO usar `val-gold` para valores monetarios, dotacoes ou taxas. Valores monetarios e outros dados usam `sidebar-fact-val` simples (cor navy).

**Para estados de programa na sidebar, usar as classes de cor consistentes com os cards da Biblioteca:**
- Estado aberto: `<div class="sidebar-fact-val val-open">Aberto até DD/MM/AAAA</div>` (verde #2E7D52)
- Estado fechado: `<div class="sidebar-fact-val val-closed">Fechado</div>` (vermelho #A63228)
- Candidatura continua: `<div class="sidebar-fact-val val-cont">Candidatura Contínua</div>` (verde #2E7D52), para instrumentos sem prazo fixo
- Nunca usar `val-gold` para estados. O dourado e reservado para labels de secção.

**Para estados no hero meta-bar, usar as mesmas classes:**
- `<span class="meta-value status-open">Aberto até DD/MM/AAAA</span>` (verde #2E7D52)
- `<span class="meta-value status-closed">Fechado</span>` (vermelho #A63228)
- `<span class="meta-value status-cont">Candidatura Contínua</span>` (verde #2E7D52), para instrumentos sem prazo fixo (EIC, candidatura permanente, etc.)
- Nunca usar `gold` class para o estado no hero.

**Formato dos instrumentos relacionados na sidebar:**
```html
<a href="portugal-2030.html" class="related-link">
  <span class="related-link-name">Portugal 2030</span>
  <span class="related-link-arrow">&rarr;</span>
</a>
```

- GitHub Pages fara o deploy automaticamente via push
