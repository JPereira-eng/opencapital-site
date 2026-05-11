#!/usr/bin/env python3
"""
reconcile_pt2030.py - Recupera avisos PT2030 perdidos no pipeline.

Operacoes:
  1. Cruza API portugal-2030 com lookup, shards, queues
  2. Para cada aviso ABERTO ou PREVISTO no API:
     - Se publicado (ficheiro + shard ok) -> ignora
     - Se na queue ativa -> garante priority_score >= 500
     - Se apenas no lookup (fantasma) -> adiciona a queue.json
     - Se em registry-queue.json (legacy) -> migra para queue.json
  3. Recalcula priority_score com formula v4.11
  4. Reporta delta

Uso:
  python reconcile_pt2030.py --dry-run
  python reconcile_pt2030.py
"""
import json
import sys
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv
TODAY = date.today()

# Importar formula v4.11
sys.path.insert(0, str(ROOT))
from recompute_scores import compute_score, FAMILIA_PT2030


def load_json(path: str):
    fp = ROOT / path
    if not fp.exists():
        return None
    with open(fp, encoding='utf-8') as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    fp = ROOT / path
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def parse_date(s: str):
    if not s: return None
    s = str(s).strip()
    for fmt in ('%Y%m%d', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: pass
    return None


def slugify(s: str) -> str:
    """Slugify simples para nomes de aviso PT2030."""
    import unicodedata, re
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')[:80]


def derive_shard(programa_list) -> str:
    """Mapeia acf.programa[] para shard pt2030-*."""
    if not programa_list:
        return 'pt2030-central'
    if isinstance(programa_list, str):
        programa_list = [programa_list]
    progs = [str(p).upper() for p in programa_list]
    if len(progs) > 1:
        return 'pt2030-central'
    p = progs[0]
    if 'COMPETE' in p: return 'pt2030-compete'
    if 'PESSOAS' in p: return 'pt2030-pessoas'
    if 'NORTE' in p:   return 'pt2030-norte'
    if 'CENTRO' in p:  return 'pt2030-centro'
    if 'LISBOA' in p:  return 'pt2030-lisboa'
    if any(x in p for x in ('ALENTEJO', 'ALGARVE', 'ACORES', 'MADEIRA',
                            'MAR', 'SUSTENTAVEL', 'PAT')):
        return 'pt2030-other'
    return 'pt2030-central'


def main() -> int:
    print(f'reconcile_pt2030.py  (DRY_RUN={DRY_RUN})\n')

    # 1) API data ja descarregada
    api_items = []
    for p in [1, 2, 3]:
        fp = ROOT / f'_tmp_pt2030/p{p}.json'
        if not fp.exists():
            print(f'ERRO: {fp} nao existe. Correr curl para 3 paginas do API antes.')
            return 1
        with open(fp, encoding='utf-8') as f:
            api_items.extend(json.load(f))
    print(f'API portugal-2030: {len(api_items)} avisos descarregados')

    # 2) Estado do sistema
    lookup = load_json('registry/lookup.json') or {'by_id': {}, 'by_aviso_codigo': {}}
    by_codigo = lookup.get('by_aviso_codigo', {})
    by_id = lookup.get('by_id', {})

    queue = load_json('registry/queue.json') or {'queue': []}
    queue_items = queue.get('queue', [])
    queue_codes = {i.get('codigo', '') for i in queue_items if i.get('codigo')}
    queue_ids = {i.get('id', '') for i in queue_items}

    overflow = load_json('registry/queue-overflow.json') or {'queue': []}
    overflow_items = overflow.get('queue', overflow.get('items', []))
    overflow_codes = {i.get('codigo', '') for i in overflow_items if i.get('codigo')}

    plano_anual = load_json('registry/queue-plano-anual.json') or {'queue': []}
    plano_codes = {i.get('codigo', '') for i in plano_anual.get('queue', []) if i.get('codigo')}

    legacy = load_json('registry-queue.json') or {'queue': []}
    legacy_items = legacy.get('queue', [])

    # Indexar shards (id -> (shard_name, state))
    shard_index = {}
    for sf in (ROOT / 'registry/shards').glob('*.json'):
        try:
            with open(sf, encoding='utf-8') as f:
                sh = json.load(f)
            for it in sh.get('items', []):
                shard_index[it.get('id', '')] = (sf.stem, it.get('state', '?'))
        except Exception:
            pass

    # 3) Para cada aviso PT2030 aberto ou previsto, decidir acao
    actions = {
        'ja_publicado': [],
        'ja_na_queue': [],
        'bump_score': [],
        'migrar_legacy': [],
        'recuperar_fantasma': [],
        'manter_paa': [],
        'fechado_ignora': [],
    }

    legacy_by_code = {}
    for it in legacy_items:
        c = it.get('codigo') or it.get('aviso_codigo', '')
        if c:
            legacy_by_code[c] = it

    new_queue_items = []  # items a adicionar a queue.json
    items_to_remove_from_legacy = []

    for api_it in api_items:
        acf = api_it.get('acf', {}) or {}
        codigo = (acf.get('codigo') or '').strip()
        di = parse_date(acf.get('data_inicio'))
        df = parse_date(acf.get('data_fim'))
        title = api_it.get('title', {}).get('rendered', '') if isinstance(api_it.get('title'), dict) else api_it.get('title', '')
        # Decodificar HTML entities basicas
        import html as html_lib
        title = html_lib.unescape(title or '')

        # Skip fechados
        if df and df < TODAY:
            actions['fechado_ignora'].append(codigo)
            continue

        # Determinar estado
        if di and di > TODAY:
            estado = 'previsto'
        else:
            estado = 'aberto'

        nosso_slug = by_codigo.get(codigo)
        in_shard_published = False
        if nosso_slug and nosso_slug in shard_index:
            sh_name, sh_state = shard_index[nosso_slug]
            # Considerar publicado se esta no shard
            in_shard_published = True

        in_queue = codigo in queue_codes
        in_overflow = codigo in overflow_codes
        in_plano = codigo in plano_codes
        in_legacy = codigo in legacy_by_code

        # Logica de decisao
        if in_shard_published:
            actions['ja_publicado'].append(codigo)
            continue

        if in_plano:
            # Esta na watchlist PAA - deixar la, monitor promove quando abrir
            actions['manter_paa'].append(codigo)
            continue

        if in_queue:
            # Esta na queue ativa - apenas bump score (recompute fara isso)
            actions['ja_na_queue'].append(codigo)
            continue

        # Construir novo item
        new_id = nosso_slug or slugify(title) or f'pt2030-{codigo.replace("/","-").lower()}'
        # Determinar shard
        shard = derive_shard(acf.get('programa'))
        # Determinar source_id baseado no programa (refletindo regional)
        if shard == 'pt2030-norte':       source_id = 'norte-2030'
        elif shard == 'pt2030-centro':    source_id = 'centro-2030'
        elif shard == 'pt2030-lisboa':    source_id = 'lisboa-2030'
        elif shard == 'pt2030-pessoas':   source_id = 'pessoas-2030'
        elif shard == 'pt2030-compete':   source_id = 'compete-2030'
        elif shard == 'pt2030-other':
            # Mapear pelo programa especifico
            progs = [str(p).upper() for p in (acf.get('programa') or [])]
            if any('ALENTEJO' in p for p in progs):   source_id = 'alentejo-2030'
            elif any('ALGARVE' in p for p in progs):  source_id = 'algarve-2030'
            elif any('ACORES' in p for p in progs):   source_id = 'acores-2030'
            elif any('MADEIRA' in p for p in progs):  source_id = 'madeira-2030'
            elif any('SUSTENTAVEL' in p for p in progs): source_id = 'sustentavel-2030'
            else: source_id = 'portugal-2030'
        else:
            source_id = 'portugal-2030'

        # Construir dotacao
        dotacao_str = acf.get('df') or acf.get('orcamento') or ''
        # df parece ser numerico em centimos ou EUR direto
        budget_eur = 0
        if dotacao_str:
            try:
                budget_eur = float(str(dotacao_str).replace('.', '').replace(',', '.'))
            except Exception:
                pass

        # PDF / regulation_url
        pdf = acf.get('pdf') or ''
        link = api_it.get('link', '')

        new_item = {
            'id': new_id,
            'name': title[:200],
            'codigo': codigo,
            'aviso_codigo': codigo,
            'source_id': source_id,
            'shard': shard,
            'detected_date': TODAY.isoformat(),
            'data_inicio': di.isoformat() if di else None,
            'data_fim': df.isoformat() if df else None,
            'deadline': df.isoformat() if df else None,
            'budget_eur': budget_eur,
            'regulation_url': pdf or link,
            'pdf_url': pdf if pdf else None,
            'regulation_local': None,
            'status': 'pending',
            'state': estado,
            'fail_count': 0,
            'priority_score': 0,  # recompute_scores ira recalcular
        }

        # Se ja existe item legacy: aproveitar dados (regulation_local, status, etc.)
        if in_legacy:
            legacy_it = legacy_by_code[codigo]
            for fld in ('regulation_local', 'status', 'pdf_url', 'fail_count', 'notes'):
                if legacy_it.get(fld) is not None:
                    new_item[fld] = legacy_it[fld]
            new_item['id'] = legacy_it.get('id', new_item['id'])
            actions['migrar_legacy'].append(codigo)
            items_to_remove_from_legacy.append(codigo)
        else:
            actions['recuperar_fantasma'].append(codigo)

        # Recalcular score
        score, _ = compute_score(new_item)
        new_item['priority_score'] = score
        # Adicionar ao lookup se nao estiver
        if codigo and codigo not in by_codigo:
            by_codigo[codigo] = new_item['id']
        if new_item['id'] not in by_id:
            by_id[new_item['id']] = True

        new_queue_items.append(new_item)

    # 4) Relatorio
    print('\n=== DECISOES ===')
    for k, v in actions.items():
        print(f'  {k:25}: {len(v)}')

    print(f'\n=== ITEMS A ADICIONAR A queue.json: {len(new_queue_items)} ===')
    for it in sorted(new_queue_items, key=lambda x: x['priority_score'], reverse=True)[:10]:
        print(f'  [{it["priority_score"]:4}] {it["source_id"]:18} {it["codigo"]:18} {it["name"][:50]}')

    if DRY_RUN:
        print('\n*** Dry run. Re-correr sem --dry-run para aplicar. ***')
        return 0

    # 5) Escrita
    # Adicionar a queue.json
    queue_items.extend(new_queue_items)
    queue['queue'] = queue_items
    save_json('registry/queue.json', queue)

    # Remover dos legacy
    legacy['queue'] = [it for it in legacy_items
                       if (it.get('codigo') or it.get('aviso_codigo', '')) not in items_to_remove_from_legacy]
    save_json('registry-queue.json', legacy)

    # Atualizar lookup
    lookup['by_id'] = by_id
    lookup['by_aviso_codigo'] = by_codigo
    save_json('registry/lookup.json', lookup)

    # Atualizar index.json totals
    index = load_json('registry/index.json') or {}
    if 'totals' in index:
        index['totals']['in_queue'] = len(queue_items)
        index['_meta']['last_pt2030_reconcile'] = TODAY.isoformat()
        save_json('registry/index.json', index)

    print(f'\nFicheiros atualizados.')
    print(f'  queue.json: {len(queue_items)} items')
    print(f'  registry-queue.json (legacy): {len(legacy["queue"])} items restantes')
    print(f'  lookup.json: atualizado')

    return 0


if __name__ == '__main__':
    sys.exit(main())
