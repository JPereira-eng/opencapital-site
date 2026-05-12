#!/usr/bin/env python3
"""
add_data_status.py - Backfill do campo `data_status` no schema.

Adiciona campo `data_status: "forecast" | "verified"` a todos os items
em queue.json, queue-plano-anual.json, queue-overflow.json, shards/*.json
e instruments-catalog.json.

Lógica:
  - Item publicado em shard (com .html no disco): verified
  - Item com regulation_local apontando para .txt que NÃO é PAA: verified
  - Item com regulation_local apontando para .txt que É PAA: forecast
  - Item com source_id = 'portugal-2030' (central API): forecast (default safer)
  - Item com source_id = 'sustentavel-2030' (Tipo A com aviso field): verified se tem .txt
  - Restantes regional Tipo B: forecast (default - PDF da API é PAA placeholder)
  - Items na watchlist (queue-plano-anual): sempre forecast (TESTE A confirmou PAA)
  - Items de famílias não-PT2030: data_status não aplica (n/a)

Uso:
  python add_data_status.py --dry-run
  python add_data_status.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv

FAMILIA_PT2030 = {
    'portugal-2030', 'compete-2030', 'norte-2030', 'centro-2030',
    'lisboa-2030', 'alentejo-2030', 'algarve-2030', 'pessoas-2030',
    'sustentavel-2030', 'madeira-2030', 'acores-2030', 'mar-2030', 'pat-2030',
}

# Regulamento Tipo A: portais que expõem regulamento real na API
TIPO_A = {'sustentavel-2030'}

PAA_MARKERS = [
    'plano anual de avisos',
    'resumo de aviso do plano',
    'paa2026', 'paa202',
    'aviso a publicar em:',
    'previsao aproximada',
    'previsão aproximada',
]


def is_paa_content(text: str) -> bool:
    """Verifica se conteúdo tem marcadores PAA."""
    if not text:
        return False
    lower = text[:2000].lower()
    return any(m in lower for m in PAA_MARKERS)


def derive_data_status(item: dict, in_shard_published: bool = False) -> str:
    """Devolve 'verified' | 'forecast' | 'n/a' baseado em sinais existentes."""
    source = item.get('source_id', '') or item.get('source', '')

    # Famílias não-PT2030 não usam data_status
    if source not in FAMILIA_PT2030:
        return 'n/a'

    # Items publicados em shard com ficheiro HTML: verified
    slug = item.get('id', '')
    if in_shard_published or (slug and Path(f'instrumentos/{slug}/index.html').exists()):
        return 'verified'

    # Items na watchlist (status=plano_anual): forecast (TESTE A confirmou PAA)
    if item.get('status') == 'plano_anual':
        return 'forecast'

    # Items com regulation_local: verificar conteúdo
    reg = item.get('regulation_local')
    if reg and Path(reg).exists():
        try:
            text = Path(reg).read_text(encoding='utf-8', errors='ignore')[:5000]
            return 'forecast' if is_paa_content(text) else 'verified'
        except Exception:
            pass

    # Procurar em regulamentos/ pelo slug
    if slug:
        for txt in Path('regulamentos').rglob(f'{slug}.txt'):
            try:
                text = txt.read_text(encoding='utf-8', errors='ignore')[:5000]
                return 'forecast' if is_paa_content(text) else 'verified'
            except Exception:
                pass

    # Items de portais Tipo A (sustentavel) com regulation_url HTTP válida:
    # provavelmente verified (mas confirmar só com .txt)
    # Por default, sem .txt: forecast
    reg_url = item.get('regulation_url', '')
    if not isinstance(reg_url, str): reg_url = str(reg_url) if reg_url else ''
    if source in TIPO_A and reg_url.startswith('http'):
        return 'forecast'  # ainda não confirmado por .txt

    # Default safer: forecast
    return 'forecast'


def process_file(path: str, key: str = 'queue'):
    fp = ROOT / path
    if not fp.exists():
        return 0, 0
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)
    items = data.get(key, data.get('items', []))
    if not isinstance(items, list):
        return 0, 0

    changed = 0
    n_a = 0
    forecast = 0
    verified = 0

    for item in items:
        if 'data_status' in item:
            # Já tem campo, skip (não sobre-escrever)
            cur = item['data_status']
            if cur == 'verified': verified += 1
            elif cur == 'forecast': forecast += 1
            else: n_a += 1
            continue
        new_status = derive_data_status(item)
        item['data_status'] = new_status
        if new_status == 'verified': verified += 1
        elif new_status == 'forecast': forecast += 1
        else: n_a += 1
        changed += 1

    if changed and not DRY_RUN:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')

    return changed, (verified, forecast, n_a)


def process_shard(sf):
    with open(sf, encoding='utf-8') as f:
        sh = json.load(f)
    items = sh.get('items', [])
    changed = 0
    for it in items:
        if 'data_status' in it: continue
        # Items em shard estão publicados → verified
        slug = it.get('id', '')
        is_published = bool(slug) and Path(f'instrumentos/{slug}/index.html').exists()
        source = it.get('source', '')
        if source not in FAMILIA_PT2030:
            it['data_status'] = 'n/a'
        else:
            it['data_status'] = 'verified' if is_published else 'forecast'
        changed += 1
    if changed and not DRY_RUN:
        with open(sf, 'w', encoding='utf-8') as f:
            json.dump(sh, f, ensure_ascii=False, indent=2); f.write('\n')
    return changed


def process_catalog():
    fp = ROOT / 'instruments-catalog.json'
    with open(fp, encoding='utf-8') as f:
        cat = json.load(f)
    changed = 0
    for it in cat['instruments']:
        if 'data_status' in it: continue
        fonte = (it.get('fonte', '') or '').lower()
        slug = it.get('id', '')
        if fonte != 'pt2030':
            it['data_status'] = 'n/a'
        else:
            # Items publicados (têm ficheiro): verified
            if slug and Path(f'instrumentos/{slug}/index.html').exists():
                it['data_status'] = 'verified'
            else:
                it['data_status'] = 'forecast'
        changed += 1
    if changed and not DRY_RUN:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2); f.write('\n')
    return changed


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'add_data_status.py (DRY_RUN={DRY_RUN})\n')

    total_changed = 0
    print('=== Queues ===')
    for path in ['registry/queue.json', 'registry/queue-plano-anual.json',
                 'registry/queue-overflow.json', 'registry/queue-catalogo.json']:
        c, stats = process_file(path)
        if isinstance(stats, tuple):
            v, f, n = stats
            print(f'  {path}: +{c} novos campos | total: verified={v} forecast={f} n/a={n}')
        else:
            print(f'  {path}: +{c}')
        total_changed += c

    print('\n=== Shards ===')
    shards_dir = ROOT / 'registry' / 'shards'
    for sf in sorted(shards_dir.glob('*.json')):
        c = process_shard(sf)
        if c > 0:
            print(f'  {sf.name}: +{c}')
        total_changed += c

    print('\n=== Catalog ===')
    c = process_catalog()
    print(f'  instruments-catalog.json: +{c}')
    total_changed += c

    print(f'\nTotal items atualizados: {total_changed}')
    if DRY_RUN:
        print('\n*** Dry run. Re-correr sem --dry-run para aplicar. ***')


if __name__ == '__main__':
    main()
