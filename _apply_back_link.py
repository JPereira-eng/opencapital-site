#!/usr/bin/env python3
"""
Atualiza o back-link em todos os artigos de conhecimento/<slug>/index.html:
1. Substitui o href estatico para '../atualidade/' (default seguro, refinado em
   runtime pelo back-link.js)
2. Adiciona <script src="../../assets/js/back-link.js"></script> antes de </body>,
   se ainda nao estiver presente.

Estrutura clean URLs: artigos vivem em conhecimento/<slug>/index.html (depth 2).
"""
import re
from pathlib import Path

BASE = Path('conhecimento')
SCRIPT_TAG = '<script src="../../assets/js/back-link.js" defer></script>'
HUBS = {'atualidade', 'opiniao', 'estrategia', 'regulamentos'}

modified = 0
skipped = 0
for sub in sorted(BASE.iterdir()):
    if not sub.is_dir():
        continue
    if sub.name in HUBS:
        continue  # hubs nao tem back-link
    fp = sub / 'index.html'
    if not fp.exists():
        continue
    text = fp.read_text(encoding='utf-8')
    original = text

    # 1) Update back-link href (qualquer variante antiga ou nova)
    text = re.sub(
        r'<a href="[^"]*" class="back-link">[^<]*</a>',
        '<a href="../atualidade/" class="back-link">&larr; Voltar ao Conhecimento</a>',
        text,
    )

    # 2) Inject script tag before </body> if not already there
    if 'back-link.js' not in text:
        text = re.sub(r'</body>', SCRIPT_TAG + '\n</body>', text, count=1)

    if text != original:
        fp.write_text(text, encoding='utf-8')
        modified += 1
    else:
        skipped += 1

print(f'Modified: {modified}')
print(f'Skipped:  {skipped}')
