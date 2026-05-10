#!/usr/bin/env python3
"""
Atualiza o back-link em todos os artigos de conhecimento/:
1. Substitui o href estatico de '../conhecimento.html' para '../conhecimento/atualidade.html'
   (default seguro, e refinado em runtime pelo back-link.js)
2. Adiciona <script src="../assets/js/back-link.js"></script> antes de </body>,
   se ainda nao estiver presente
"""
import os, re

BASE = 'conhecimento'
SCRIPT_TAG = '<script src="../assets/js/back-link.js" defer></script>'

modified = 0
skipped = 0
for fn in sorted(os.listdir(BASE)):
    if not fn.endswith('.html'):
        continue
    fp = os.path.join(BASE, fn)
    with open(fp, encoding='utf-8') as f:
        text = f.read()
    original = text

    # 1) Update back-link href
    text = re.sub(
        r'<a href="\.\./conhecimento\.html" class="back-link">[^<]*</a>',
        '<a href="../conhecimento/atualidade.html" class="back-link">&larr; Voltar ao Conhecimento</a>',
        text,
    )

    # 2) Inject script tag before </body> if not already there
    if 'back-link.js' not in text:
        text = re.sub(r'</body>', SCRIPT_TAG + '\n</body>', text, count=1)

    if text != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(text)
        modified += 1
    else:
        skipped += 1

print(f'Modified: {modified}')
print(f'Skipped:  {skipped}')
