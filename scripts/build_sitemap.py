#!/usr/bin/env python
"""Gera sitemap.xml com URLs limpos (folder/) para todas as paginas."""
import os
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://opencapital.pt'

# Pastas a ignorar
EXCLUDE_PARTS = {'node_modules', '.git', '.claude', '_partials', 'assets', 'registry', 'scripts'}
EXCLUDE_NAME_FRAGMENTS = ('design-system', 'exemplo')


def url_for(rel_path: Path) -> str:
    """Converte caminho do ficheiro em URL limpa."""
    rel = rel_path.as_posix()
    # index.html da raiz -> root URL
    if rel == 'index.html':
        return f'{BASE}/'
    # folder/index.html -> /folder/
    if rel.endswith('/index.html'):
        return f'{BASE}/{rel[:-len("index.html")]}'
    # fallback: usar caminho como esta (nao deveria acontecer apos migracao)
    return f'{BASE}/{rel}'


def priority(rel: str) -> str:
    if rel == 'index.html':
        return '1.0'
    top_pages = {
        'biblioteca/index.html', 'conhecimento/index.html', 'sobre-nos/index.html',
    }
    if rel in top_pages:
        return '0.9'
    medium_pages = {
        'parceiros/index.html', 'carreiras/index.html',
        'capital-simulator/index.html', 'tech2business/index.html',
    }
    if rel in medium_pages:
        return '0.8'
    if rel.endswith('privacidade/index.html') or rel.endswith('termos/index.html'):
        return '0.3'
    if rel.startswith('instrumentos/') or rel.startswith('conhecimento/'):
        return '0.7'
    return '0.5'


def changefreq(rel: str) -> str:
    if rel == 'index.html':
        return 'weekly'
    return 'monthly'


def main() -> None:
    files = []
    for p in sorted(ROOT.rglob('*.html')):
        rel = p.relative_to(ROOT)
        # Excluir pastas
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        # Excluir por nome
        if any(frag in str(rel).lower() for frag in EXCLUDE_NAME_FRAGMENTS):
            continue
        files.append(p)

    urls = []
    for fp in files:
        rel = fp.relative_to(ROOT)
        rel_str = rel.as_posix()
        loc = url_for(rel)
        mtime = datetime.date.fromtimestamp(os.path.getmtime(fp)).isoformat()
        urls.append(
            '  <url>\n'
            f'    <loc>{loc}</loc>\n'
            f'    <lastmod>{mtime}</lastmod>\n'
            f'    <changefreq>{changefreq(rel_str)}</changefreq>\n'
            f'    <priority>{priority(rel_str)}</priority>\n'
            '  </url>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(urls)
        + '\n</urlset>\n'
    )

    out = ROOT / 'sitemap.xml'
    out.write_text(xml, encoding='utf-8', newline='\n')
    print(f'sitemap.xml gerado com {len(urls)} URLs em {out}')


if __name__ == '__main__':
    main()
