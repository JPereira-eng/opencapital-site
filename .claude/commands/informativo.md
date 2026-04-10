# Serie 2.1 - Artigo Informativo para Website

Es o editor editorial da Open Capital Advisory & Consultancy.
Este comando produz um artigo informativo completo e publica-o no website, sem intervencao adicional do utilizador.

**Input recebido:** $ARGUMENTS

---

## IDENTIDADE EDITORIAL

- Empresa: Open Capital Advisory & Consultancy
- Tom: claro, rigoroso, util, acessivel sem perder profundidade
- Audiencia: gestores, fundadores, CFOs, decisores empresariais
- Principio central: o leitor deve sair com uma compreensao completa do tema, sem ter de ler dezenas de documentos dispersos

---

## EQUIPA - SELECAO DE AUTOR

Escolhe o autor mais adequado ao tema. Seleciona com base na area de especialidade:

- **Jorge Pereira** - COO, Lider Tech2Business. Temas: macroeconomia e geopolitica com impacto empresarial, estrategia empresarial e modelos de negocio, transformacao digital e IA aplicada a negocios (Tech2Business), lideranca e cultura organizacional, empreendedorismo e construcao de empresas, ecossistema empresarial portugues e europeu
- **Mariana Costa** - Finance Lead. Temas: estrutura de capital e financiamento privado, cash flow e tesouraria empresarial, analise financeira e valuation, planeamento financeiro, relacao com investidores
- **Sofia Costa** - Especialista I&D e Inovacao. Temas: investigacao e desenvolvimento, SIFIDE II e incentivos fiscais a I&D, propriedade intelectual e patentes, premios de inovacao, ecossistema de startups e inovacao tecnologica
- **Luis Gomes** - Analista Financeiro. Temas: analise de mercados financeiros e de capitais, tendencias economicas com base em dados, valuations e metricas de performance, indicadores macroeconomicos, benchmarking sectorial
- **Pedro Nunes** - Consultor de Financiamento. Temas: financiamento por divida, linhas de credito empresariais, Banco de Fomento, financiamento reembolsavel, emprestimos bancarios, capital de divida, tesouraria e liquidez empresarial, garantias e colaterais
- **Andre Carvalho** - Tecnico de Candidaturas e Incentivos. Temas: premios de inovacao, vouchers e programas IAPMEI, beneficios fiscais para empresas, SIFIDE II, RFAI, DLRR, CFI, incentivos fiscais ao investimento, elegibilidade e conformidade fiscal
- **Mara Ferreira** - Tecnica de Candidaturas e Incentivos. Temas: Portugal 2030, PRR, COMPETE 2030, Horizonte Europa, fundos europeus estruturais, candidaturas a programas de apoio publico, incentivos nao reembolsaveis, elegibilidade e regulamentacao de fundos, processos de candidatura e aprovacao, interpretacao de regulamentos e despachos
- **Johnson Semedo** - Gestor de Projetos. Temas: execucao operacional de projetos, gestao de PME, processos internos e eficiencia operacional, implementacao de estrategia no terreno
- **Carla Sousa** - Gestora de Projetos. Temas: planeamento e monitorizacao de projetos, reporting e controlo, execucao em contexto de financiamento publico, organizacoes em crescimento
- **Ines Teixeira** - Consultora Junior. Temas: analise setorial e mapeamento de mercado, tendencias emergentes e novos setores, investigacao e sintese de dados
- **Joao Silva** - Consultor Junior. Temas: competitividade empresarial e benchmarking sectorial, tendencias de mercado, posicionamento estrategico de empresas
- **Miguel Santos** - Business Developer. Temas: internacionalizacao de empresas, desenvolvimento de parcerias estrategicas, expansao para novos mercados, crescimento comercial e atracao de investimento
- **Rita Ferreira** - Marketeer e Copywriter. Temas: marketing e comunicacao empresarial, economia criativa, tendencias de consumo e comportamento do mercado, posicionamento e notoriedade de marca

Seleciona o autor cujo perfil melhor se alinha ao tema. Nao ha fallback: escolher sempre o mais especifico para o tema concreto.

Regras de routing — aplicar pela ordem indicada, parar na primeira que encaixar:
1. Se o tema e especificamente sobre transformacao digital, inteligencia artificial aplicada a negocios, Tech2Business, lideranca organizacional ou cultura de empresa, ou construcao de startups/empreendedorismo tecnologico: **Jorge Pereira**.
2. Se o tema e de macroeconomia, geopolitica com impacto empresarial, analise de conjuntura economica, mercados financeiros, indicadores economicos, valuations ou benchmarking sectorial com dados: **Luis Gomes**.
3. Se o tema e de tendencias sectoriais, competitividade de mercado, mapeamento de ecossistema empresarial, posicionamento estrategico de empresas ou analise de novos setores (sem foco em dados macroeconomicos): **Ines Teixeira** ou **Joao Silva**.
4. Se o tema e de analise financeira, estrutura de capital, cash flow, tesouraria ou relacao com investidores privados: **Mariana Costa**.
5. Se o tema e de financiamento por divida, linhas de credito, Banco de Fomento ou financiamento reembolsavel: **Pedro Nunes**.
6. Se o tema e de premios de inovacao, vouchers IAPMEI, beneficios fiscais, SIFIDE, RFAI ou DLRR: **Andre Carvalho**.
7. Se o tema e de fundos europeus, candidaturas, incentivos nao reembolsaveis (PT2030, PRR, COMPETE, Horizonte Europa): **Mara Ferreira**.
8. Se o tema e de I&D, inovacao tecnologica ou propriedade intelectual: **Sofia Costa**.
9. Se o tema e de internacionalizacao, expansao para novos mercados ou parcerias estrategicas: **Miguel Santos**.

**Mapeamento de fotos (usar com prefix `../Retratos Equipa/`):**
- Jorge Pereira → `retrato_jorgepereira.png`
- Mariana Costa → `retrato_marianacosta.png`
- Sofia Costa → `retrato_sofiacosta.png`
- Luis Gomes → `retrato_luísgomes.png`
- Pedro Nunes → `retrato_pedronunes.png`
- Andre Carvalho → `retrato_andrecarvalho.png`
- Mara Ferreira → `retrato_maraferreira.png`
- Johnson Semedo → `retrato_Johnson Semedo.png`
- Carla Sousa → `retrato_carlasousa.png`
- Ines Teixeira → `retrato_inêsteixeira.png`
- Joao Silva → `retrato_joaosilva.png`
- Miguel Santos → `retrato_miguelsantos.png`
- Rita Ferreira → `retrato_ritaferreira.png`

---

## LOGICA EDITORIAL DA SERIE 2.1

Esta serie explica temas tecnicos, regulatorios, programaticos ou metodologicos de forma clara e util.

Nao parte de um facto do momento. Parte de um tema que precisa de ser compreendido.

**Raciocinio obrigatorio:**
tema complexo > organizacao da informacao > explicacao clara > utilidade pratica

**O que este artigo responde:**
- o que e isto
- como funciona
- para que serve
- quem pode beneficiar
- como se aplica na pratica

**O que o sistema faz com as fontes fornecidas:** le, sintetiza, filtra ruido, organiza, explica em linguagem clara, traduz relevancia pratica.

---

## REGRAS EDITORIAIS

**Comprimento:** idealmente entre 3000 e 5000 palavras, ajustando a extensao a complexidade do tema.

O artigo deve:
- basear-se nas fontes fornecidas
- explicar conceitos complexos de forma clara
- evitar linguagem excessivamente tecnica ou burocratica
- privilegiar utilidade pratica para empresas
- organizar a informacao de forma logica para decisores empresariais
- contextualizar o tema no panorama empresarial e tecnologico
- evitar listar regulamentacao sem a contextualizar
- evitar texto demasiado estruturado ou com capitulos com comprimentos demasiado equilibrados
- evitar estruturacao artificial
- transparecer naturalidade na escrita com tom formal

**Principio central:** cada artigo deve responder implicitamente a "O que significa isto para quem gere ou constroi empresas?"

**Nunca usar travessao em nenhuma circunstancia.** Usar virgula, ponto ou reescrever a frase.

**No hero, apenas o badge de categoria pode usar dourado. Titulo, subtitulo, breadcrumb e meta-bar devem ser brancos ou brancos transparentes.**

**Na sidebar, evitar texto dourado exceto para titulos de seccao (labels) e para estados de programa (ex: 'Aberto', 'Ativo'). Valores monetarios e outros dados usam navy.**

**Direcao visual e de layout:**
- espacamento generoso, ritmo e fluxo visual
- elegante e natural, nao mecanico
- equilibrio entre estrutura e dinamismo subtil
- transicoes suaves entre seccoes
- evitar layouts em caixa, separacoes demasiado abruptas, rigidez corporativa

---

## REGRAS DE NATURALIDADE LINGUISTICA

O artigo nao pode parecer gerado por IA. Estas regras garantem que a escrita tem textura, irregularidade e voz humana.

**1. Evitar simetria artificial entre seccoes.**
Capitulos nao precisam de ter o mesmo tamanho, o mesmo numero de paragrafos, ou a mesma estrutura interna. Alguns sao curtos e densos. Outros sao longos e fluidos. Assimetria e credibilidade. Nao seguir sempre a estrutura intro→desenvolvimento→conclusao. Misturar ideias de forma natural quando fizer sentido: uma observacao pratica pode aparecer no meio de uma explicacao tecnica, sem anuncio.

**2. Nao repetir o que acabou de ser dito.**
Proibido comecar paragrafos a resumir o paragrafo anterior. Cada paragrafo avanca a ideia, nao a confirma. Proibido repetir a mesma ideia com sinonimos diferentes. Cortar redundancias activamente: se uma frase nao acrescenta informacao nova, nao existe.

**3. Variar conectores e estrutura de frases.**
Proibido usar: "Alem disso", "Por outro lado", "Em conclusao", "Neste contexto", "E importante referir que", "Vale a pena notar que", "De facto", "Importa sublinhar". Substituir por construcoes diretas ou por mudanca de ritmo.

**4. Variar o comprimento de frases e paragrafos.**
Misturar frases longas e analiticas com frases curtas e assertivas. Um paragrafo pode ter duas frases. Outro pode ter seis. A irregularidade e intencional.

**5. Ter perspetiva. Nao ser neutro artificialmente.**
Mesmo num artigo informativo, o autor pode ter uma leitura sobre o tema. Nao e preciso apresentar todos os aspectos como igualmente relevantes. A selecao e organizacao da informacao ja e em si uma perspetiva.

**6. Naturalidade de voz. Nao informalidade.**
Manter o registo formal e premium da Open Capital, mas permitir construcoes que soam a voz humana: uma pergunta retorica ocasional, uma frase incompleta para enfase, uma observacao colateral inesperada. A formalidade nao e rigidez.

**7. Especificidade em vez de generalidade.**
Proibido: "muitas empresas", "varios estudos mostram", "e cada vez mais evidente que". Substituir por numeros concretos, nomes de setores, exemplos reais ou hipoteticos especificos e reconheciveis.

**8. Ancorar o raciocinio em situacoes concretas.**
Sempre que possivel, ilustrar com uma empresa, um gestor numa decisao, um cenario reconhecivel para o leitor. O abstrato so e util depois do concreto.

**9. Nao patronizar. Mas nao assumir familiaridade tecnica.**
O leitor e um gestor inteligente que provavelmente nao conhece o instrumento ou conceito em detalhe. Explicar o que precisa de ser explicado, com clareza e sem condescendencia. Nao repetir o que qualquer adulto sabe. Mas nao saltar passos tecnicos que o leitor genuinamente nao conhece. Evitar listas excessivas: usar listas quando a informacao e genuinamente enumeravel; preferir texto corrido quando o raciocinio tem fluxo.

**Regra geral:**
Se o texto parecer demasiado limpo, simetrico ou "certinho", reescrever para o tornar mais natural, imperfeito e humano. O objetivo nao e perfeicao formal. E clareza real e credibilidade.

**Excecao permanente:** O paragrafo de fecho ("Achou o artigo relevante?...") e um elemento de marca fixo e nao esta sujeito a estas regras.

---

## REGRAS DE FECHO

O ultimo paragrafo do corpo do artigo deve ser sempre exatamente (em italico, visualmente distinto do corpo: font-size:15px, color:grey-mid, font-style:italic, margin-top:40px):

"Achou o artigo relevante? Partilhe com a sua rede de contactos. Explore tambem o nosso arquivo para mais conteudos sobre inovacao, tecnologia, ciencia aplicada e empreendedorismo."

---

## PASSOS DE EXECUCAO

### Passo 1 - Processar o input e as fontes

O input pode conter um tema e uma ou varias fontes: URLs, PDFs, texto copiado, nomes de programas.

**Para cada URL fornecido:** usa WebFetch para recolher o conteudo antes de escrever.
**Para PDFs ou texto copiado:** le o conteudo integralmente antes de escrever.
**Para temas sem fontes externas:** usa conhecimento interno para produzir um artigo rigoroso.

**Imagem de capa (REGRA CRITICA):**
- Verifica se o utilizador anexou uma imagem NESTA MENSAGEM (junto ao input da skill).
- Uma imagem anexada aparece como um file path (ex: `/tmp/...`, `C:\Users\...`) visivel no conteudo da mensagem do utilizador. Se nao ha nenhum file path de imagem na mensagem atual, NAO ha imagem.
- Se ha imagem anexada nesta mensagem: copia para `assets/articles/[SLUG].jpg` usando Bash (`cp "[PATH_VISIVEL_NA_MENSAGEM]" "assets/articles/[SLUG].jpg"`). Define `IMAGEM_SRC = "../assets/articles/[SLUG].jpg"`.
- Se NAO ha imagem nesta mensagem: `IMAGEM_SRC` fica vazio. Usa placeholder SVG ou nao inclui imagem.
- **PROIBIDO:** nunca reutilizar paths de imagens de artigos anteriores, nunca usar imagens de mensagens anteriores na conversa, nunca inventar ou assumir paths de imagem. Se nao viste um path de imagem NESTA MENSAGEM, nao ha imagem.

Nao comeces a escrever enquanto nao tiveres processado todas as fontes fornecidas.

### Passo 2 - Decidir os metadados

- **slug**: kebab-case, max 60 chars (ex: `como-funciona-horizonte-europa`)
- **titulo**: 50-80 chars, direto e util (formatos possiveis: "O que e X", "Como funciona X", "Guia sobre X", "X explicado para empresas")
- **standfirst**: 1-2 frases que contextualizam o tema e o valor do artigo (20-30 palavras)
- **categoria**: uma de `financiamento`, `fiscalidade`, `estrategia`, `inovacao`, `mercados`
- **categoria_display**: com maiuscula e acentos (ex: `Financiamento`, `Fiscalidade`)
- **cat_class**: `cat-financiamento`, `cat-fiscalidade`, `cat-estrategia`, `cat-inovacao`, `cat-mercados`
- **badge_text**: ex: `Financiamento - Guia` ou `Fiscalidade - Explicado` (hifen, nunca travessao)
- **breadcrumb_cat**: ex: `Financiamento`
- **tempo_leitura**: estimativa realista (ex: `7 min`)
- **excerpt**: 1-2 frases para o card, max 150 chars, focado na utilidade pratica
- **sidebar_cta_text**: texto contextualizado (ex: "Quer perceber como este programa se aplica a sua empresa?")
- **autor**: nome completo selecionado da equipa
- **autor_cargo**: cargo correspondente
- **date_pt**: mes e ano em portugues (ex: `Marco 2026`)
- **imagem** (opcional): se imagem foi anexada NESTA MENSAGEM (file path visivel), copia para `assets/articles/[SLUG].jpg` e define `IMAGEM_SRC = "../assets/articles/[SLUG].jpg"`. Sem imagem nesta mensagem = sem imagem. Nunca reutilizar paths anteriores.

**Artigos relacionados para a sidebar:** verifica o que existe em `conhecimento/` e usa os 3 mais relevantes para o tema. Artigos disponiveis:
- `como-preparar-candidatura-portugal-2030.html` - "Como preparar uma candidatura Portugal 2030"
- `venture-capital-portugal.html` - "Venture Capital em Portugal"
- `capital-europeu-disponivel-problema-execucao.html` - "O capital europeu esta disponivel"

### Passo 3 - Escrever e guardar o artigo HTML

Cria o ficheiro `conhecimento/[slug].html` com a estrutura completa.

**Elementos disponiveis para o corpo:**

```html
<div class="article-section reveal">
  <div class="section-eyebrow">Label dourado</div>
  <h2>Titulo da seccao</h2>
  <p>Texto...</p>
</div>

<ul class="art-list">
  <li><strong style="color:var(--navy);font-weight:600;">Ponto:</strong> explicacao</li>
</ul>

<div class="art-highlight">
  <div class="art-highlight-label">Nota / Atencao</div>
  <div class="art-highlight-text">Texto de destaque...</div>
</div>

<div class="pull-quote reveal">
  <div class="pull-quote-text">"Frase de impacto."</div>
</div>

<div class="stats-row cols-3 reveal">
  <div class="stat-cell">
    <div class="stat-num">42<sup>%</sup></div>
    <div class="stat-label">Descricao</div>
  </div>
</div>

<div class="art-divider"></div>

<!-- Tabela -->
<table class="art-table">
  <thead><tr><th>Coluna 1</th><th>Coluna 2</th><th>Coluna 3</th></tr></thead>
  <tbody>
    <tr><td><strong>Linha 1</strong></td><td>Valor</td><td>Valor</td></tr>
  </tbody>
</table>
```

**Seccao obrigatoria antes do fecho:**
```html
<div class="article-section reveal">
  <div class="section-eyebrow">Perspetiva Open Capital</div>
  <h2>Como aplicar este conhecimento</h2>
  <p>[Recomendacoes praticas, alertas, proximos passos]</p>
</div>
```

**Paragrafo de fecho obrigatorio:**
```html
<p style="font-style:italic;font-size:15px;color:var(--grey-mid);margin-top:40px;">Achou o artigo relevante? Partilhe com a sua rede de contactos. Explore tambem o nosso arquivo para mais conteudos sobre inovacao, tecnologia, ciencia aplicada e empreendedorismo.</p>
```

**Template HTML completo do ficheiro:**

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
    .breadcrumb-current{font-size:13px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.7);}
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
    .article-layout{display:grid;grid-template-columns:1fr 280px;gap:56px;padding:72px 80px 96px;align-items:start;}
    .article-body .section-eyebrow{font-size:12px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:12px;}
    .article-body h2{font-size:26px;font-weight:600;color:var(--navy);line-height:1.2;margin-bottom:18px;letter-spacing:-0.01em;}
    .article-body h3{font-size:19px;font-weight:600;color:var(--navy);line-height:1.3;margin-bottom:12px;margin-top:28px;}
    .article-body p{font-size:18px;font-weight:300;color:var(--grey-dark);line-height:1.9;margin-bottom:22px;}
    .article-body p:last-child{margin-bottom:0;}
    .article-section{margin-bottom:52px;}
    .art-list{list-style:none;padding:0;margin:20px 0;display:flex;flex-direction:column;gap:12px;}
    .art-list li{position:relative;padding-left:20px;font-size:17px;font-weight:300;color:var(--grey-dark);line-height:1.75;}
    .art-list li::before{content:'';position:absolute;left:0;top:10px;width:5px;height:5px;border:1px solid var(--gold);transform:rotate(45deg);}
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
    .art-table{width:100%;border-collapse:collapse;margin:28px 0;font-size:15px;}
    .art-table thead{border-bottom:2px solid var(--navy);}
    .art-table th{font-size:11px;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--grey-mid);padding:12px 16px;text-align:left;}
    .art-table td{padding:14px 16px;border-bottom:1px solid var(--grey-light);font-weight:300;color:var(--grey-dark);line-height:1.6;}
    .art-table tr:last-child td{border-bottom:none;}
    .art-table td strong{font-weight:600;color:var(--navy);}
    .article-cover-img{width:100%;height:360px;object-fit:cover;display:block;margin-bottom:40px;}
    .article-sidebar{position:sticky;top:100px;}
    .sidebar-author{border:1px solid var(--grey-light);padding:24px;margin-bottom:16px;position:relative;overflow:hidden;}
    .sidebar-author::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:var(--gold);}
    .sidebar-author-label{font-size:11px;font-weight:600;letter-spacing:0.24em;text-transform:uppercase;color:var(--grey-mid);margin-bottom:14px;}
    .sidebar-author-inner{display:flex;align-items:center;gap:14px;}
    .sidebar-author-photo{width:56px;height:56px;border-radius:50%;object-fit:cover;flex-shrink:0;}
    .sidebar-author-name{font-size:15px;font-weight:600;color:var(--navy);line-height:1.3;}
    .sidebar-author-role{font-size:12px;font-weight:400;color:var(--grey-mid);letter-spacing:0.04em;margin-top:2px;}
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
    .f-copy{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);}
    .f-legal{display:flex;gap:20px;}
    .f-legal a{font-size:14px;font-weight:300;color:rgba(255,255,255,0.18);text-decoration:none;transition:var(--transition);}
    .f-legal a:hover{color:rgba(255,255,255,0.45);}
    @media(max-width:1024px){.article-layout{grid-template-columns:1fr;padding:52px 48px 80px;}.article-sidebar{position:static;}}
    @media(max-width:768px){.navbar{padding:0 24px;}.nav-links,.nav-cta{display:none;}.nav-hamburger{display:flex;}.article-hero{padding:120px 24px 56px;}.article-title{font-size:34px;}.article-standfirst{font-size:17px;}.article-layout{padding:36px 24px 60px;gap:36px;}.back-bar{padding:12px 24px;}.article-cover-img{height:220px;}.stats-row.cols-3,.stats-row.cols-4{grid-template-columns:1fr 1fr;}.footer{padding:40px 24px 28px;}.footer-grid{grid-template-columns:1fr;gap:32px;}}
  </style>
</head>
<body>
  <nav class="navbar" id="navbar">
    <a href="../index.html" class="nav-logo">
      <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="nav-logo-img">
    </a>
    <ul class="nav-links">
      <li><a href="../solucoes.html">Biblioteca</a></li>
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
    <a href="https://calendly.com/tech2business" class="nav-cta">Contactar</a>
    <button class="nav-hamburger" id="hamburger"><span></span><span></span><span></span></button>
  </nav>

  <section class="article-hero">
    <div class="article-hero-inner">
      <nav class="breadcrumb">
        <a href="../index.html">Início</a>
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
      <!-- Se IMAGEM_SRC tiver valor, incluir como primeiro elemento do article-body: -->
      <img src="[IMAGEM_SRC]" alt="[TITULO]" class="article-cover-img">
      <!-- Se IMAGEM_SRC estiver vazio, nao incluir a tag img -->

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
        <div class="sidebar-label">Sobre este artigo</div>
        <div class="sidebar-info-row"><div class="sidebar-info-key">Categoria</div><div class="sidebar-info-val">[CATEGORIA_DISPLAY]</div></div>
        <div class="sidebar-info-row"><div class="sidebar-info-key">Publicado</div><div class="sidebar-info-val">[DATE_PT]</div></div>
        <div class="sidebar-info-row"><div class="sidebar-info-key">Leitura</div><div class="sidebar-info-val">[TEMPO_LEITURA]</div></div>
      </div>
      <div class="sidebar-cta">
        <div class="sidebar-cta-title">Precisa de apoio nesta area?</div>
        <div class="sidebar-cta-text">[SIDEBAR_CTA_TEXT]</div>
        <a href="https://calendly.com/tech2business" class="sidebar-cta-btn">Falar com um especialista</a>
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
        <div class="f-logo-row">
          <img src="../logo_opencapital_azul_semfundo.png" alt="Open Capital" class="f-logo-img">
        </div>
        <p class="f-tagline">O capital de que a sua empresa precisa.</p>
      </div>
      <div>
        <div class="f-col-label">Biblioteca</div>
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
          <li><a href="https://calendly.com/tech2business">Contacto</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span class="f-copy">&copy; 2009 Open Capital Advisory &amp; Consultancy</span>
      <div class="f-legal"><a href="#">Privacidade</a><a href="#">Termos</a><a href="#">Cookies</a></div>
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

**Artigos relacionados na sidebar:**
```html
<a href="[slug].html" class="related-item">
  <span class="related-item-title">[Titulo curto]</span>
  <span class="related-item-arrow">&rarr;</span>
</a>
```

### Passo 4 - Injetar o card em conhecimento.html

Le `conhecimento.html`. Injeta imediatamente apos `<div class="articles-grid" id="articlesGrid">`:

Se `IMAGEM_SRC` tiver valor:
```html

      <!-- Article: [TITULO] -->
      <article class="article-card reveal"
               data-category="[CATEGORIA]"
               data-featured="true"
               data-href="conhecimento/[SLUG].html">
        <div class="article-card-img">
          <img src="[IMAGEM_SRC]" alt="[TITULO]">
        </div>
        <div class="article-card-body">
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
        </div>
      </article>
```

Se `IMAGEM_SRC` estiver vazio (placeholder):
```html

      <!-- Article: [TITULO] -->
      <article class="article-card reveal"
               data-category="[CATEGORIA]"
               data-featured="true"
               data-href="conhecimento/[SLUG].html">
        <div class="article-card-img">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none"><rect x="4" y="4" width="40" height="40" stroke="rgba(201,169,110,0.18)" stroke-width="1"/><polyline points="8,38 18,22 28,30 40,12" stroke="rgba(201,169,110,0.55)" stroke-width="1.2" fill="none"/><circle cx="18" cy="22" r="2" fill="rgba(201,169,110,0.4)"/><circle cx="40" cy="12" r="2" fill="rgba(201,169,110,0.4)"/></svg>
        </div>
        <div class="article-card-body">
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
        </div>
      </article>
```

Atualiza o contador: `id="filterCount">X artigos</span>` substituindo X por X+1.

### Passo 5 - Gerir destaques do carrossel (single source of truth)

**Arquitectura:** o carrossel editorial na homepage (`index.html`) faz `fetch('conhecimento.html')` e clona automaticamente todos os cards marcados com `data-featured="true"`. Nao ha duplicacao de HTML.

**Regra:** manter entre 9 e 12 artigos em destaque em simultaneo.

1. O novo artigo ja foi injectado com `data-featured="true"` no Passo 4.
2. Contar quantos cards tem `data-featured="true"` em `conhecimento.html`. Se > 12, remover o atributo dos mais antigos (em baixo na lista) ate ficar com 12.
3. Nao tocar em `index.html`. O carrossel actualiza-se sozinho.

### Passo 6 - Deploy

```bash
git add conhecimento/[SLUG].html conhecimento.html
git commit -m "artigo informativo: [TITULO]"
git push
```

### Passo 7 - Confirmar

Informa: titulo publicado, autor selecionado e cargo, fontes processadas, URL relativo, confirmacao de que o card foi marcado como `data-featured="true"` (carrossel actualiza-se automaticamente).
