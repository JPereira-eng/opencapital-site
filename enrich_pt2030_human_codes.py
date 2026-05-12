#!/usr/bin/env python3
"""
enrich_pt2030_human_codes.py - Enriquecimento retroativo.

Para cada artigo PT2030 já publicado, tenta extrair o human_code
(ACORES2030-YYYY-NN, PACS-YYYY-NN, etc.) do regulamento .txt e do HTML
do artigo. Atualiza:
  - lookup.by_human_code (NOVO mapping)
  - shard items (adiciona campo human_code)
  - instruments-catalog.json (adiciona human_code ao entry)

Uso:
  python enrich_pt2030_human_codes.py --dry-run
  python enrich_pt2030_human_codes.py
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv

PT2030_FONTES = {
    'portugal-2030', 'compete-2030', 'norte-2030', 'centro-2030',
    'lisboa-2030', 'alentejo-2030', 'algarve-2030', 'pessoas-2030',
    'sustentavel-2030', 'madeira-2030', 'acores-2030', 'mar-2030', 'pat-2030',
}

PROGRAMA_PATTERNS = (
    'ACORES2030', 'ALENTEJO2030', 'ALGARVE2030', 'CENTRO2030',
    'COMPETE2030', 'LISBOA2030', 'MADEIRA2030', 'NORTE2030',
    'PESSOAS2030', 'SUSTENTAVEL2030', 'MAR2030', 'PAT2030',
    'PACS',  # sustentavel usa PACS-YYYY-NN
)

# Regex para extrair human_code do texto
HUMAN_RE = re.compile(
    r'(?i)(?:c[oó]digo\s+do\s+aviso\s*:?\s*)?'
    r'\b('
    r'(?:ACORES|A[ÇC]ORES|ALENTEJO|ALGARVE|CENTRO|COMPETE|LISBOA|MADEIRA|NORTE|PESSOAS|SUSTENTAVEL|MAR|PAT)\s*-?\s*2030\s*-?\s*\d{4}\s*-?\s*\d+'
    r'|PACS\s*-?\s*\d{4}\s*-?\s*\d+'
    r')\b'
)


def normalize_human(code: str) -> str:
    """Normalizar para forma canónica."""
    code = unicodedata.normalize('NFKD', code).encode('ascii', 'ignore').decode()
    code = code.upper().replace(' ', '').strip()
    # PROGRAMA-YYYY-NN
    m = re.match(r'^([A-Z]+?)2030-?(\d{4})-?(\d+)$', code)
    if m:
        return f'{m.group(1)}2030-{m.group(2)}-{m.group(3)}'
    m = re.match(r'^PACS-?(\d{4})-?(\d+)$', code)
    if m:
        return f'PACS-{m.group(1)}-{m.group(2)}'
    return code  # fallback


def derive_programa(human_code: str) -> str:
    """ACORES2030-2026-12 → ACORES2030. PACS-2026-14 → SUSTENTAVEL2030."""
    if human_code.startswith('PACS'):
        return 'SUSTENTAVEL2030'
    m = re.match(r'^([A-Z]+2030)-', human_code)
    return m.group(1) if m else None


def extract_human_from_text(text: str, expected_source: str = None) -> str | None:
    """Procurar human_code no texto. Devolve forma normalizada ou None.

    Se expected_source dado, validar que programa do match corresponde.
    """
    if not text:
        return None
    matches = HUMAN_RE.findall(text[:50000])
    if not matches:
        return None

    # Mapping source -> programa esperado
    SOURCE_TO_PROGRAMA = {
        'acores-2030': 'ACORES2030',
        'alentejo-2030': 'ALENTEJO2030',
        'algarve-2030': 'ALGARVE2030',
        'centro-2030': 'CENTRO2030',
        'compete-2030': 'COMPETE2030',
        'lisboa-2030': 'LISBOA2030',
        'madeira-2030': 'MADEIRA2030',
        'norte-2030': 'NORTE2030',
        'pessoas-2030': 'PESSOAS2030',
        'sustentavel-2030': 'SUSTENTAVEL2030',  # mapeia para PACS na prática
        'mar-2030': 'MAR2030',
        'pat-2030': 'PAT2030',
    }
    expected = SOURCE_TO_PROGRAMA.get(expected_source)

    # Preferir match cujo programa coincide com o source
    candidates = [normalize_human(m) for m in matches]
    if expected:
        for c in candidates:
            prog = derive_programa(c)
            # Aceitar match exato OU PACS (sustentavel usa PACS)
            if prog == expected or (expected == 'SUSTENTAVEL2030' and prog == 'SUSTENTAVEL2030'):
                return c
        # Se sustentavel mas só temos PACS, validar
        if expected == 'SUSTENTAVEL2030':
            for c in candidates:
                if c.startswith('PACS-'):
                    return c
        # Nenhum match com programa esperado → descartar (provável falso positivo)
        return None

    # Sem expected: aceitar primeiro
    return candidates[0]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'enrich_pt2030_human_codes.py (DRY_RUN={DRY_RUN})\n')

    # Carregar estado
    with open('instruments-catalog.json', encoding='utf-8') as f:
        cat = json.load(f)
    with open('registry/lookup.json', encoding='utf-8') as f:
        lookup = json.load(f)
    lookup.setdefault('by_human_code', {})

    # Iterar todos os PT2030 publicados
    pt2030 = [i for i in cat['instruments'] if i.get('fonte','').lower() in {'pt2030'} | PT2030_FONTES]
    print(f'PT2030 publicados a verificar: {len(pt2030)}')

    enriched = 0
    no_human = 0
    already_set = 0
    for it in pt2030:
        slug = it['id']
        # Já tem human_code?
        if it.get('human_code'):
            already_set += 1
            continue

        # Procurar em regulamento .txt
        text = ''
        for txt_file in Path('regulamentos').rglob(f'{slug}.txt'):
            try:
                text = txt_file.read_text(encoding='utf-8', errors='ignore')
                break
            except Exception:
                pass

        # Identificar source/shard expected
        expected_source = None
        # Procurar nos shards
        for sf in Path('registry/shards').glob('pt2030-*.json'):
            try:
                sh = json.load(open(sf, encoding='utf-8'))
                for sit in sh.get('items', []):
                    if sit.get('id') == slug:
                        expected_source = sit.get('source')
                        break
                if expected_source: break
            except: pass

        # Fallback: HTML do artigo
        if not text or not extract_human_from_text(text, expected_source):
            html_file = Path(f'instrumentos/{slug}/index.html')
            if html_file.exists():
                text += '\n' + html_file.read_text(encoding='utf-8', errors='ignore')

        human = extract_human_from_text(text, expected_source)
        if not human:
            no_human += 1
            continue

        programa = derive_programa(human)
        print(f'  {slug[:50]:50} → {human} (programa: {programa})')

        if not DRY_RUN:
            # Atualizar catálogo
            it['human_code'] = human
            it['programa_code'] = programa
            # Atualizar lookup
            lookup['by_human_code'][human] = slug
        enriched += 1

    print(f'\n=== RESULTADO ===')
    print(f'  Enriquecidos: {enriched}')
    print(f'  Sem human_code detectável: {no_human}')
    print(f'  Já tinham human_code: {already_set}')

    if DRY_RUN:
        print('\n*** Dry run. Re-correr sem --dry-run para aplicar. ***')
        return 0

    # Persistir
    with open('instruments-catalog.json', 'w', encoding='utf-8') as f:
        json.dump(cat, f, ensure_ascii=False, indent=2); f.write('\n')
    with open('registry/lookup.json', 'w', encoding='utf-8') as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2); f.write('\n')

    # Atualizar shards também (campo human_code)
    shards_updated = 0
    for sf in (ROOT / 'registry' / 'shards').glob('pt2030-*.json'):
        with open(sf, encoding='utf-8') as f:
            sh = json.load(f)
        changed = False
        for item in sh.get('items', []):
            iid = item.get('id', '')
            cat_entry = next((c for c in cat['instruments'] if c['id'] == iid), None)
            if cat_entry and cat_entry.get('human_code') and not item.get('human_code'):
                item['human_code'] = cat_entry['human_code']
                item['programa_code'] = cat_entry.get('programa_code')
                changed = True
        if changed:
            with open(sf, 'w', encoding='utf-8') as f:
                json.dump(sh, f, ensure_ascii=False, indent=2); f.write('\n')
            shards_updated += 1

    print(f'\nShards PT2030 atualizados: {shards_updated}')
    print(f'lookup.by_human_code: {len(lookup["by_human_code"])} entries')
    return 0


if __name__ == '__main__':
    sys.exit(main())
