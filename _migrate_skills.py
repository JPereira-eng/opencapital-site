#!/usr/bin/env python3
"""
_migrate_skills.py - Atualiza skills .claude/commands/*.md e gerar_artigo.py
para a nova estrutura clean URLs (folder/index.html).

Aplica a mesma logica de migrate_urls.py mas a templates que vivem dentro
de ficheiros .md / .py — sem mover ficheiros, apenas reescrevendo os paths
HTML neles.

Cada skill emite HTML para uma das pastas:
  - .claude/commands/trend.md       -> conhecimento/<slug>/index.html (depth 2)
  - .claude/commands/opiniao.md     -> conhecimento/<slug>/index.html (depth 2)
  - .claude/commands/estrategia.md  -> conhecimento/<slug>/index.html (depth 2)
  - .claude/commands/informativo.md -> conhecimento/<slug>/index.html (depth 2)
  - .claude/commands/youtube.md     -> conhecimento/<slug>/index.html (depth 2)
  - .claude/commands/instrumento.md / instrumento-template.md
  - .claude/commands/radar-writer.md -> instrumentos/<slug>/index.html (depth 2)
  - .claude/commands/radar-monitor.md -> ler estados, paths simples

Importa migrate_urls e usa a sua rewrite_paths_in_text.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate_urls import rewrite_paths_in_text, split_suffix, OLD_RELS  # noqa

ROOT = Path(__file__).resolve().parent

# Mapeamento skill -> (file_old_parent, file_new_parent)
# Aplica-se aos blocos HTML embutidos em cada skill.
SKILL_DEPTH = {
    'trend.md':                ('conhecimento', 'conhecimento/__slug__'),
    'opiniao.md':              ('conhecimento', 'conhecimento/__slug__'),
    'estrategia.md':           ('conhecimento', 'conhecimento/__slug__'),
    'informativo.md':          ('conhecimento', 'conhecimento/__slug__'),
    'youtube.md':              ('conhecimento', 'conhecimento/__slug__'),
    'instrumento.md':          ('instrumentos', 'instrumentos/__slug__'),
    'instrumento-template.md': ('instrumentos', 'instrumentos/__slug__'),
    'radar-writer.md':         ('instrumentos', 'instrumentos/__slug__'),
    'radar-monitor.md':        ('instrumentos', 'instrumentos/__slug__'),
}

# Tambem precisamos atualizar referencias a slugs/file:
# - "instrumentos/<slug>.html" -> "instrumentos/<slug>/index.html" (path do disco)
# - "conhecimento/<slug>.html" -> "conhecimento/<slug>/index.html" (path do disco)
# Estes apenas no texto literal das skills (instrucoes).


def update_skill_filepaths(text: str) -> str:
    """Atualiza referencias a paths no disco do tipo dir/slug.html -> dir/slug/index.html.

    Tem cuidado: nao toca em paths URL (que ja levam '/').
    """
    # Padroes comuns em backticks ou code fences
    patterns = [
        (r'(instrumentos/)([a-z0-9\-]+)\.html\b', r'\1\2/index.html'),
        (r'(conhecimento/)([a-z0-9\-]+)\.html\b', r'\1\2/index.html'),
        (r'(\[slug\])\.html\b', r'\1/index.html'),
        (r'(\[SLUG\])\.html\b', r'\1/index.html'),
        # placeholders [pasta]/[slug].html  ja apanhados acima
    ]
    for pat, repl in patterns:
        text = re.sub(pat, repl, text)
    return text


def process_skill(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    original = text

    name = path.name
    if name in SKILL_DEPTH:
        old_parent, new_parent = SKILL_DEPTH[name]
        # Aplicar rewrite de href/src nos blocos HTML dentro do .md
        text = rewrite_paths_in_text(text, old_parent, new_parent)

    # Atualizar paths de disco mencionados nas instrucoes
    text = update_skill_filepaths(text)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main() -> int:
    skills_dir = ROOT / '.claude' / 'commands'
    changed = 0
    skipped = 0
    for f in sorted(skills_dir.glob('*.md')):
        if process_skill(f):
            print(f'  updated {f.relative_to(ROOT)}')
            changed += 1
        else:
            skipped += 1
    # gerar_artigo.py
    gp = ROOT / 'gerar_artigo.py'
    if gp.exists():
        text = gp.read_text(encoding='utf-8')
        orig = text
        text = rewrite_paths_in_text(text, 'conhecimento', 'conhecimento/__slug__')
        text = update_skill_filepaths(text)
        if text != orig:
            gp.write_text(text, encoding='utf-8')
            print(f'  updated gerar_artigo.py')
            changed += 1
    print(f'\n{changed} actualizados, {skipped} sem mudancas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
