#!/usr/bin/env python3
"""
build_navbar.py — Sincroniza a navbar em todas as paginas HTML do site.

Fonte unica: _partials/navbar.html (usa [[PREFIX]] como placeholder de paths).
Insere conteudo entre marcadores <!-- NAVBAR:START --> e <!-- NAVBAR:END -->.
Em ficheiros sem marcadores, deteta o bloco existente
<nav class="navbar"...>...</nav> (e o <div class="nav-mobile-menu"...>...</div>
imediatamente a seguir, se existir) e substitui-o pelos marcadores na primeira
corrida (migracao).

Uso:
  python build_navbar.py                # processa todo o repo
  python build_navbar.py FILE [FILE...] # processa ficheiros especificos
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTIAL = ROOT / "_partials" / "navbar.html"
START = "<!-- NAVBAR:START -->"
END = "<!-- NAVBAR:END -->"

# Pastas a varrer quando nao sao passados ficheiros explicitos.
SCAN_DIRS = [ROOT, ROOT / "instrumentos", ROOT / "conhecimento"]

# Padrao para detetar navbar legada + mobile menu opcional logo a seguir.
# Apanha a tag <nav class="navbar"...>...</nav> e, se existir, o
# <div class="nav-mobile-menu"...>...</div> que vem depois (com whitespace
# entre eles permitido).
LEGACY_NAVBAR_RE = re.compile(
    r'<nav class="navbar"[^>]*>.*?</nav>'
    r'(?:\s*<div class="nav-mobile-menu"[^>]*>.*?</div>)?',
    re.DOTALL,
)
# Marcadores + conteudo (usado em ficheiros ja migrados).
MARKER_BLOCK_RE = re.compile(
    re.escape(START) + r".*?" + re.escape(END), re.DOTALL
)


def render(prefix: str) -> str:
    """Renderiza o partial com o prefixo de path adequado."""
    template = PARTIAL.read_text(encoding="utf-8").rstrip("\n")
    return template.replace("[[PREFIX]]", prefix)


def prefix_for(file_path: Path) -> str:
    """Devolve '../' x n consoante a profundidade relativa a raiz."""
    rel = file_path.resolve().relative_to(ROOT)
    depth = len(rel.parts) - 1  # parts inclui o nome do ficheiro
    return "../" * depth


def process(file_path: Path) -> str:
    """Processa um ficheiro. Devolve 'updated' | 'migrated' | 'skip' | 'noop'."""
    text = file_path.read_text(encoding="utf-8")
    prefix = prefix_for(file_path)
    rendered = render(prefix)
    block = f"{START}\n{rendered}\n{END}"

    if START in text and END in text:
        new_text = MARKER_BLOCK_RE.sub(block, text, count=1)
        status = "updated"
    elif LEGACY_NAVBAR_RE.search(text):
        new_text = LEGACY_NAVBAR_RE.sub(block, text, count=1)
        status = "migrated"
    else:
        return "skip"

    if new_text == text:
        return "noop"
    file_path.write_text(new_text, encoding="utf-8")
    return status


def collect_files(args: list[str]) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args]
    files = []
    # Estrutura clean URLs: paginas vivem em pasta/index.html.
    # Procurar todos os index.html sob ROOT (excluindo node_modules, .git, etc.)
    EXCLUDE_PARTS = {"node_modules", ".git", ".claude", "_partials", "assets", "registry"}
    for p in sorted(ROOT.rglob("*.html")):
        if any(part in EXCLUDE_PARTS for part in p.relative_to(ROOT).parts):
            continue
        files.append(p)
    return files


def main() -> int:
    if not PARTIAL.exists():
        print(f"ERRO: partial nao encontrado em {PARTIAL}", file=sys.stderr)
        return 1
    files = collect_files(sys.argv[1:])
    counts = {"updated": 0, "migrated": 0, "skip": 0, "noop": 0}
    for f in files:
        status = process(f)
        counts[status] += 1
        if status in ("updated", "migrated"):
            print(f"  {status:8} {f.relative_to(ROOT)}")
    print(
        f"\n{counts['updated']} actualizado(s), "
        f"{counts['migrated']} migrado(s), "
        f"{counts['noop']} sem mudancas, "
        f"{counts['skip']} ignorado(s) (sem navbar)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
