#!/usr/bin/env python
"""Gera sitemap.xml com todas as paginas indexaveis do site."""
import os
import glob
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://opencapital.pt'


def priority(rel: str) -> str:
    if rel == 'index.html':
        return '1.0'
    if rel in ('biblioteca.html', 'solucoes.html', 'conhecimento.html', 'sobre-nos.html'):
        return '0.9'
    if rel in ('parceiros.html', 'carreiras.html', 'capital-simulator.html', 'tech2business.html'):
        return '0.8'
    if rel in ('privacidade.html', 'termos.html'):
        return '0.3'
    if rel.startswith('instrumentos/') or rel.startswith('conhecimento/'):
        return '0.7'
    return '0.5'


def changefreq(rel: str) -> str:
    if rel == 'index.html':
        return 'weekly'
    return 'monthly'


def main() -> None:
    patterns = ['*.html', 'instrumentos/*.html', 'conhecimento/*.html']
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(ROOT, p)))

    excluded = ('node_modules', '_partials', 'snippets', 'design-system', 'exemplo')
    files = [f for f in files if not any(x in f.lower() for x in excluded)]

    sep = os.sep
    urls = []
    for fp in sorted(files):
        rel = os.path.relpath(fp, ROOT).replace(sep, '/')
        loc = f'{BASE}/' if rel == 'index.html' else f'{BASE}/{rel}'
        mtime = datetime.date.fromtimestamp(os.path.getmtime(fp)).isoformat()
        urls.append(
            '  <url>\n'
            f'    <loc>{loc}</loc>\n'
            f'    <lastmod>{mtime}</lastmod>\n'
            f'    <changefreq>{changefreq(rel)}</changefreq>\n'
            f'    <priority>{priority(rel)}</priority>\n'
            '  </url>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(urls)
        + '\n</urlset>\n'
    )

    out = os.path.join(ROOT, 'sitemap.xml')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(xml)
    print(f'sitemap.xml gerado com {len(urls)} URLs em {out}')


if __name__ == '__main__':
    main()
