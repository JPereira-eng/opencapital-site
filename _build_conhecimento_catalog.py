#!/usr/bin/env python3
"""Backfill conhecimento-catalog.json from existing 43 articles."""
import os, re, json

MAP = {
    # ATUALIDADE (15)
    'backlash-data-centers-custo-infraestrutura-digital': ('atualidade', None, None),
    'bolha-ia-o-que-os-mercados-dizem': ('atualidade', None, None),
    'china-taiwan-fratura-cadeias-valor': ('atualidade', None, None),
    'construcao-escassez-mao-de-obra': ('atualidade', None, None),
    'defesa-aco-nova-politica-industrial-europeia': ('atualidade', None, None),
    'europa-eua-fim-otan': ('atualidade', None, None),
    'fragmentacao-global-fim-globalizacao-eficiente': ('atualidade', None, None),
    'portugal-gnl-russo-renovaveis-pressao-bruxelas': ('atualidade', None, None),
    'portugal-trabalha-mais-ganha-menos-paradoxo-laboral': ('atualidade', None, None),
    'rearmamento-europeu-prioridade-ue': ('atualidade', None, None),
    'recuo-esg-ue-competitividade': ('atualidade', None, None),
    'salarios-portugal-2025-acima-inflacao': ('atualidade', None, None),
    'tarifas-trump-impacto-empresas-portuguesas': ('atualidade', None, None),
    'venda-novobanco-bpce-banca-portuguesa': ('atualidade', None, None),
    'zona-euro-contracao-abril-impacto-medio-oriente': ('atualidade', None, None),
    # OPINIAO (4)
    'carga-fiscal-pais-rico-estado-pais-pobre': ('opiniao', None, None),
    'contratos-publicos-tribunal-contas-ninguem-despedido': ('opiniao', None, None),
    'pme-portuguesas-credito-mais-capital-menos': ('opiniao', None, None),
    'produtividade-portuguesa-problema-da-gestao': ('opiniao', None, None),
    # ESTRATEGIA (11)
    'automacao-vs-digitalizacao': ('estrategia', 'inovacao-tecnologia', None),
    'contratar-para-crescer-ou-tapar-falhas': ('estrategia', 'pessoas-equipas', None),
    'expandir-capacidade-procura-sustenta-investimento': ('estrategia', 'crescimento-mercados', None),
    'identificar-gargalos-operacao-industrial': ('estrategia', 'operacoes-produtividade', None),
    'identificar-gargalos-operacao-servicos': ('estrategia', 'operacoes-produtividade', None),
    'kpis-pme-quais-fazem-sentido': ('estrategia', 'operacoes-produtividade', None),
    'medir-antes-automatizar-operacao': ('estrategia', 'operacoes-produtividade', None),
    'mercado-externo-oportunidade-real-ou-hipotese': ('estrategia', 'crescimento-mercados', None),
    'preparar-ronda-investimento-startup': ('estrategia', 'capital-financiamento', None),
    'tipos-de-inovacao': ('estrategia', 'inovacao-tecnologia', None),
    'esg-o-que-importa-para-pme': ('estrategia', 'sustentabilidade-esg', None),
    # REGULAMENTOS (13)
    'ai-act-o-que-muda-para-empresas': ('regulamentos', None, 'regulamentos-leis'),
    'capacidade-instalada-o-que-e': ('regulamentos', None, 'conceitos-metricas'),
    'como-funciona-horizonte-europa': ('regulamentos', None, 'programas-instrumentos'),
    'como-funcionam-beneficios-fiscais-investimento': ('regulamentos', None, 'conceitos-metricas'),
    'como-interpretar-taxas-apoio': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'contratos-publicos-guia-para-empresas': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'erros-comuns-candidatura-incentivos': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'fundos-europeus-auditorias-irregularidades': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'metodos-pagamento-portugal-2030': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'o-que-e-um-projeto-id': ('regulamentos', None, 'conceitos-metricas'),
    'regime-de-minimis': ('regulamentos', None, 'regulamentos-leis'),
    'regras-comunicacao-fundos-europeus-placas-cartazes-websites': ('regulamentos', None, 'procedimentos-boas-praticas'),
    'rgpd-o-que-as-empresas-precisam-saber': ('regulamentos', None, 'regulamentos-leis'),
}

AUTOR_FOTO = {
    'Jorge Pereira': 'retrato_jorgepereira.png',
    'Mariana Costa': 'retrato_marianacosta.png',
    'Sofia Costa': 'retrato_sofiacosta.png',
    'Luís Gomes': 'retrato_luísgomes.png',
    'Pedro Nunes': 'retrato_pedronunes.png',
    'André Carvalho': 'retrato_andrecarvalho.png',
    'Mara Ferreira': 'retrato_maraferreira.png',
    'Johnson Semedo': 'retrato_Johnson Semedo.png',
    'Carla Sousa': 'retrato_carlasousa.png',
    'Inês Teixeira': 'retrato_inêsteixeira.png',
    'João Silva': 'retrato_joaosilva.png',
    'Miguel Santos': 'retrato_miguelsantos.png',
    'Rita Ferreira': 'retrato_ritaferreira.png',
}

MESES = {'janeiro':1,'fevereiro':2,'março':3,'marco':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}


def extract(slug):
    fp = f'conhecimento/{slug}.html'
    with open(fp, encoding='utf-8') as f:
        h = f.read()
    t = re.search(r'<title>([^<]+)</title>', h)
    title = t.group(1).replace(' | Open Capital', '').strip() if t else slug
    md = re.search(r'<meta name="description" content="([^"]+)"', h)
    desc = md.group(1).strip() if md else ''
    tg = re.search(r'class="article-standfirst"[^>]*>([^<]+)<', h) or re.search(r'class="hero-tagline"[^>]*>([^<]+)<', h)
    tagline = tg.group(1).strip() if tg else desc[:200]
    autor = None
    for pat in [r'sidebar-author-name"[^>]*>([^<]+)<', r'meta-tag">Autor\s*<span>([^<]+)</span>', r'class="author-name"[^>]*>([^<]+)<']:
        m = re.search(pat, h)
        if m:
            autor = m.group(1).strip(); break
    data_pub = None
    dm = re.search(r'meta-tag">Data\s*<span>([^<]+)</span>', h)
    if dm:
        raw = dm.group(1).strip()
        m2 = re.match(r'(\w+)\s+(20\d{2})', raw)
        if m2:
            mes, ano = m2.group(1).lower(), m2.group(2)
            mnum = MESES.get(mes)
            if mnum:
                data_pub = f'{ano}-{mnum:02d}'
        if not data_pub:
            data_pub = raw
    return {'title': title, 'desc_meta': desc, 'tagline': tagline, 'autor': autor, 'data_pub': data_pub}


articles = []
for slug, (sub, subtema, subgrupo) in MAP.items():
    fp = f'conhecimento/{slug}.html'
    if not os.path.exists(fp):
        print(f'MISSING: {slug}')
        continue
    info = extract(slug)
    entry = {
        'slug': slug,
        'title': info['title'],
        'tagline': info['tagline'],
        'subseccao': sub,
        'autor': info['autor'],
        'autor_foto': AUTOR_FOTO.get(info['autor']),
        'data_publicacao': info['data_pub'],
        'href': f'conhecimento/{slug}.html',
        'meta_description': info['desc_meta'],
    }
    if subtema:
        entry['subtema'] = subtema
    if subgrupo:
        entry['subgrupo'] = subgrupo
    articles.append(entry)

articles.sort(key=lambda x: (x.get('data_publicacao') or '0', x['slug']), reverse=True)

out = {
    '_meta': {
        'description': 'Catalogo central de artigos da seccao Conhecimento. Lido pelos hubs (atualidade, opiniao, estrategia, regulamentos) para renderizar listagens.',
        'version': '1.0',
        'last_update': '2026-05-09',
        'subseccoes': ['atualidade', 'opiniao', 'estrategia', 'regulamentos'],
        'subtemas_estrategia': [
            'estrategia-decisao', 'operacoes-produtividade', 'crescimento-mercados',
            'pessoas-equipas', 'capital-financiamento', 'inovacao-tecnologia', 'sustentabilidade-esg'
        ],
        'subtemas_estrategia_labels': {
            'estrategia-decisao': 'Estratégia e decisão',
            'operacoes-produtividade': 'Operações e produtividade',
            'crescimento-mercados': 'Crescimento e mercados',
            'pessoas-equipas': 'Pessoas e equipas',
            'capital-financiamento': 'Capital e financiamento',
            'inovacao-tecnologia': 'Inovação e transformação tecnológica',
            'sustentabilidade-esg': 'Sustentabilidade e ESG',
        },
        'subgrupos_regulamentos': [
            'regulamentos-leis', 'programas-instrumentos', 'conceitos-metricas', 'procedimentos-boas-praticas'
        ],
        'subgrupos_regulamentos_labels': {
            'regulamentos-leis': 'Regulamentos e Leis',
            'programas-instrumentos': 'Programas e Instrumentos Explicados',
            'conceitos-metricas': 'Conceitos e Métricas',
            'procedimentos-boas-praticas': 'Procedimentos e Boas Práticas',
        },
    },
    'articles': articles,
}
with open('conhecimento-catalog.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

from collections import Counter
print(f'Total: {len(articles)} artigos')
print('Por subseccao:', dict(Counter(a['subseccao'] for a in articles)))
print('Por subtema (estrategia):', dict(Counter(a.get('subtema') for a in articles if a['subseccao']=='estrategia')))
print('Por subgrupo (regulamentos):', dict(Counter(a.get('subgrupo') for a in articles if a['subseccao']=='regulamentos')))
no_autor = [a['slug'] for a in articles if not a.get('autor')]
no_data = [a['slug'] for a in articles if not a.get('data_publicacao')]
print(f'Sem autor: {len(no_autor)}', no_autor[:5] if no_autor else '')
print(f'Sem data: {len(no_data)}', no_data[:5] if no_data else '')
