#!/usr/bin/env python3
"""
migrate_urls.py - Migra todas as paginas .html para estrutura folder/index.html.

Estrutura final:
  biblioteca.html                       -> biblioteca/index.html
  conhecimento/atualidade.html          -> conhecimento/atualidade/index.html
  instrumentos/portugal-2030.html       -> instrumentos/portugal-2030/index.html

Mantem-se inalterado:
  index.html (raiz)
  opencapital-design-system (exemplo).html
  _partials/* (geridos pelo build_navbar/build_footer)
  assets/*
  node_modules/*
  registry/*

Elimina:
  solucoes.html (apenas redirect, sem valor)

Uso:
  python migrate_urls.py --dry-run   # apenas mostra o que mudaria
  python migrate_urls.py             # executa a migracao
"""
import os
import re
import sys
import json
import shutil
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent

ROOT_KEEPERS = {
    'index.html',
    'opencapital-design-system (exemplo).html',
}
ROOT_DELETE = {'solucoes.html'}

DRY_RUN = '--dry-run' in sys.argv


def log(msg: str) -> None:
    print(msg)


# ---------------------------------------------------------------------------
# 1. Descobrir paginas a migrar
# ---------------------------------------------------------------------------
def find_pages_to_migrate() -> list[tuple[Path, Path]]:
    """Retorna [(old_abs, new_abs), ...]."""
    pages: list[tuple[Path, Path]] = []
    # Raiz
    for p in sorted(ROOT.glob('*.html')):
        if p.name in ROOT_KEEPERS or p.name in ROOT_DELETE:
            continue
        slug = p.stem
        pages.append((p, ROOT / slug / 'index.html'))
    # conhecimento/
    for p in sorted((ROOT / 'conhecimento').glob('*.html')):
        slug = p.stem
        pages.append((p, ROOT / 'conhecimento' / slug / 'index.html'))
    # instrumentos/
    for p in sorted((ROOT / 'instrumentos').glob('*.html')):
        slug = p.stem
        pages.append((p, ROOT / 'instrumentos' / slug / 'index.html'))
    return pages


PAGES = find_pages_to_migrate()
# Set de paths relativos POSIX a ROOT, da pagina ORIGINAL (com .html).
OLD_RELS = {str(old.relative_to(ROOT)).replace('\\', '/') for old, _ in PAGES}


def to_posix(p: Path | str) -> str:
    return str(p).replace('\\', '/')


# ---------------------------------------------------------------------------
# 2. Reescrita de referencias href/src/fetch
# ---------------------------------------------------------------------------
EXTERNAL_PREFIXES = ('http://', 'https://', '//', 'mailto:', 'tel:', '#', 'data:', 'javascript:')


def is_external(ref: str) -> bool:
    return ref.startswith(EXTERNAL_PREFIXES) or ref.startswith('/')


def split_suffix(ref: str) -> tuple[str, str]:
    """Devolve (base, suffix) onde suffix e o ?... ou #..."""
    for sep in ('?', '#'):
        if sep in ref:
            i = ref.index(sep)
            return ref[:i], ref[i:]
    return ref, ''


def posix_normpath(p: str) -> str:
    """Normaliza um caminho relativo POSIX (resolve . e ..). Devolve '' para root."""
    parts: list[str] = []
    for part in p.split('/'):
        if part == '' or part == '.':
            continue
        if part == '..':
            if parts and parts[-1] != '..':
                parts.pop()
            else:
                parts.append('..')
        else:
            parts.append(part)
    return '/'.join(parts)


def posix_relpath(target: str, start: str) -> str:
    """Devolve target relativo a start (ambos posix, relativos a ROOT)."""
    target_parts = target.split('/') if target else []
    start_parts = start.split('/') if start else []
    # Encontrar prefixo comum
    i = 0
    while i < len(target_parts) and i < len(start_parts) and target_parts[i] == start_parts[i]:
        i += 1
    up = ['..'] * (len(start_parts) - i)
    down = target_parts[i:]
    rel = '/'.join(up + down)
    return rel if rel else '.'


def transform_ref(ref: str, file_old_parent: str, file_new_parent: str) -> str:
    """
    Transforma uma referencia relativa.

    file_old_parent: dir do ficheiro ANTES da migracao (posix relativo a ROOT; '' = raiz)
    file_new_parent: dir do ficheiro DEPOIS  (posix relativo a ROOT)
    """
    if not ref:
        return ref
    if is_external(ref):
        return ref
    base, suffix = split_suffix(ref)
    if not base or base == '.' or base == './':
        return ref

    # Resolver alvo (POSIX, relativo a ROOT) com base no LOCAL ORIGINAL.
    if file_old_parent:
        target = posix_normpath(file_old_parent + '/' + base)
    else:
        target = posix_normpath(base)

    # Decidir novo alvo
    rewritten_to_folder = False
    if target in OLD_RELS:
        # Era pagina migrada -> agora e folder/
        new_target = target[:-5]  # strip .html
        rewritten_to_folder = True
    elif target == 'index.html':
        # Root index -> referencia ao root
        new_target = ''
        rewritten_to_folder = True
    else:
        # Asset, recurso nao migrado -> mantem
        new_target = target

    # Recalcular caminho relativo do FICHEIRO NOVO ate ao NOVO alvo
    if new_target == '':
        # Root (apos converter index.html). Emitir caminho ate raiz.
        if file_new_parent == '':
            rel = './'
        else:
            depth = file_new_parent.count('/') + 1
            rel = '../' * depth
    else:
        rel = posix_relpath(new_target, file_new_parent)
        if rewritten_to_folder and not rel.endswith('/'):
            rel += '/'

    return rel + suffix


# Regex que apanha atributos href/src e fetch() com string literal.
ATTR_RE = re.compile(r'''(\b(?:href|src)\s*=\s*)(["'])([^"']*)\2''', re.IGNORECASE)
FETCH_RE = re.compile(r'''(\bfetch\s*\(\s*)(["'])([^"']*)\2''')
# data-href (cards click handlers)
DATA_HREF_RE = re.compile(r'''(\bdata-href\s*=\s*)(["'])([^"']*)\2''', re.IGNORECASE)
# window.location.href = "..."
WINDOW_LOC_RE = re.compile(r'''(window\.location(?:\.href)?\s*=\s*)(["'])([^"']*)\2''')


def rewrite_paths_in_text(text: str, file_old_parent: str, file_new_parent: str) -> str:
    def repl(m: re.Match) -> str:
        prefix, quote, val = m.group(1), m.group(2), m.group(3)
        new_val = transform_ref(val, file_old_parent, file_new_parent)
        return f'{prefix}{quote}{new_val}{quote}'

    text = ATTR_RE.sub(repl, text)
    text = FETCH_RE.sub(repl, text)
    text = DATA_HREF_RE.sub(repl, text)
    text = WINDOW_LOC_RE.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# 3. Migrar paginas (move + rewrite)
# ---------------------------------------------------------------------------
def migrate_pages() -> None:
    log(f'\n=== A migrar {len(PAGES)} paginas ===')
    for old_abs, new_abs in PAGES:
        old_rel = to_posix(old_abs.relative_to(ROOT))
        new_rel = to_posix(new_abs.relative_to(ROOT))
        old_parent = to_posix(old_abs.parent.relative_to(ROOT)) if old_abs.parent != ROOT else ''
        new_parent = to_posix(new_abs.parent.relative_to(ROOT))

        text = old_abs.read_text(encoding='utf-8')
        new_text = rewrite_paths_in_text(text, old_parent, new_parent)

        if DRY_RUN:
            if new_text != text:
                # Mostrar primeiras 3 diferencas
                diffs = [(a, b) for a, b in zip(text.splitlines(), new_text.splitlines()) if a != b][:3]
                log(f'  [DRY] {old_rel} -> {new_rel}')
                for a, b in diffs:
                    log(f'        - {a[:120]}')
                    log(f'        + {b[:120]}')
            else:
                log(f'  [DRY] {old_rel} -> {new_rel} (sem alteracoes de path)')
            continue

        new_abs.parent.mkdir(parents=True, exist_ok=True)
        new_abs.write_text(new_text, encoding='utf-8')
        old_abs.unlink()
        log(f'  {old_rel} -> {new_rel}')


# ---------------------------------------------------------------------------
# 4. Atualizar ficheiros NAO migrados (index.html, partials, assets/js)
# ---------------------------------------------------------------------------
def rewrite_non_migrated() -> None:
    log('\n=== A atualizar ficheiros nao migrados ===')
    # index.html (raiz)
    targets = [ROOT / 'index.html']
    # partials
    for p in (ROOT / '_partials').glob('*.html'):
        targets.append(p)
    # JS files NAO sao processados automaticamente — paths la sao relativos
    # a' pagina que os carrega, nao a propria localizacao do JS. Updates manuais.

    for tgt in targets:
        if not tgt.exists():
            continue
        text = tgt.read_text(encoding='utf-8')
        rel_to_root = tgt.relative_to(ROOT)
        parent = to_posix(rel_to_root.parent) if rel_to_root.parent != Path('.') else ''
        # Para partials, [[PREFIX]] e usado para representar profundidade variavel.
        # Aqui ATAMOS o parent ao do partial em si (raiz), porque os links serao
        # depois injetados em paginas com diferentes profundidades pelo build_navbar.
        # MAS: os hrefs em partials sao do tipo [[PREFIX]]xxx.html — temos de mudar
        # apenas o sufixo .html para /.
        new_text = text
        if tgt.name in ('navbar.html', 'footer.html'):
            # Transformacao especial: [[PREFIX]]xxx.html -> [[PREFIX]]xxx/
            def repl_prefix(m: re.Match) -> str:
                prefix_attr, quote, val = m.group(1), m.group(2), m.group(3)
                # Apenas se for um path com [[PREFIX]] ou comecar por algo conhecido
                if not val.startswith('[[PREFIX]]'):
                    return m.group(0)
                # remover prefixo, processar, recolocar
                inner = val[len('[[PREFIX]]'):]
                base, suffix = split_suffix(inner)
                if base.endswith('.html') and base != 'index.html':
                    base = base[:-5] + '/'
                elif base == 'index.html':
                    base = ''
                return f'{prefix_attr}{quote}[[PREFIX]]{base}{suffix}{quote}'
            new_text = ATTR_RE.sub(repl_prefix, new_text)
        else:
            new_text = rewrite_paths_in_text(text, parent, parent)

        if new_text != text:
            if DRY_RUN:
                log(f'  [DRY] {tgt.relative_to(ROOT)}: alteracoes detetadas')
            else:
                tgt.write_text(new_text, encoding='utf-8')
                log(f'  {tgt.relative_to(ROOT)}')


# ---------------------------------------------------------------------------
# 5. Atualizar catalogos JSON
# ---------------------------------------------------------------------------
def update_catalogs() -> None:
    log('\n=== A atualizar catalogos JSON ===')
    for fname in ('conhecimento-catalog.json', 'instruments-catalog.json'):
        fp = ROOT / fname
        if not fp.exists():
            continue
        data = json.loads(fp.read_text(encoding='utf-8'))
        changed = 0

        def fix_href(h: str) -> str:
            nonlocal changed
            if not isinstance(h, str):
                return h
            base, suffix = split_suffix(h)
            if base in OLD_RELS:
                changed += 1
                return base[:-5] + '/' + suffix
            return h

        # Estruturas: 'articles' (conhecimento) ou 'instruments'
        for key in ('articles', 'instruments'):
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if 'href' in item:
                        item['href'] = fix_href(item['href'])

        if DRY_RUN:
            log(f'  [DRY] {fname}: {changed} hrefs alterariam')
        else:
            fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            log(f'  {fname}: {changed} hrefs atualizados')


# ---------------------------------------------------------------------------
# 6. Eliminar solucoes.html
# ---------------------------------------------------------------------------
def delete_solucoes() -> None:
    fp = ROOT / 'solucoes.html'
    if fp.exists():
        if DRY_RUN:
            log(f'\n[DRY] Eliminaria {fp.name}')
        else:
            fp.unlink()
            log(f'\nEliminado: {fp.name}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    if DRY_RUN:
        log('*** DRY RUN — nenhum ficheiro sera alterado ***')
    log(f'\nPaginas a migrar: {len(PAGES)}')
    log(f'  Raiz: {sum(1 for o,_ in PAGES if o.parent == ROOT)}')
    log(f'  conhecimento/: {sum(1 for o,_ in PAGES if o.parent.name == "conhecimento")}')
    log(f'  instrumentos/: {sum(1 for o,_ in PAGES if o.parent.name == "instrumentos")}')

    migrate_pages()
    rewrite_non_migrated()
    update_catalogs()
    delete_solucoes()

    log('\n=== Concluido ===')
    if DRY_RUN:
        log('Para executar a serio: python migrate_urls.py')
    else:
        log('Proximos passos:')
        log('  1. python build_navbar.py    (re-aplicar navbar com profundidades novas)')
        log('  2. python build_footer.py    (re-aplicar footer)')
        log('  3. python scripts/build_sitemap.py  (regenerar sitemap)')
        log('  4. git add -A && git commit && git push')
    return 0


if __name__ == '__main__':
    sys.exit(main())
