#!/usr/bin/env python3
"""
recompute_scores.py - Recalcula priority_score de todos os items nas queues
usando a fórmula v4.11 (2026-05-11): 3 eixos equilibrados + handicap PT2030.

Fontes a recalcular:
  - registry/queue.json
  - registry/queue-overflow.json
  - registry/queue-plano-anual.json
  - registry/queue-catalogo.json

Uso:
  python recompute_scores.py --dry-run   # mostra antes/depois sem escrever
  python recompute_scores.py             # aplica
"""
import json
import sys
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv
TODAY = date.today()

# ---------------------------------------------------------------------------
# Listas de fontes (v4.11)
# IMPORTANTE: NAO usar o campo `priority` do sources-scan.json para isto.
# ---------------------------------------------------------------------------
FAMILIA_PT2030 = {
    'portugal-2030', 'compete-2030', 'norte-2030', 'centro-2030',
    'lisboa-2030', 'alentejo-2030', 'algarve-2030', 'pessoas-2030',
    'sustentavel-2030', 'madeira-2030', 'acores-2030',
}
HORIZON = {'eu-horizon'}
NACIONAIS_ESTRATEGICOS = {
    'banco-fomento', 'ani', 'iapmei', 'iefp', 'prr', 'aicep', 'fct',
}
EU_OUTROS = {
    'eu-funding-tenders', 'eic', 'eea-grants', 'cef', 'crea', 'cerv',
    'interreg', 'eu-other',
}


# ---------------------------------------------------------------------------
# Parsing de campos do item
# ---------------------------------------------------------------------------
def parse_deadline(item: dict):
    """Devolve date ou None. Tenta vários campos."""
    for field in ('data_fim', 'deadline', 'data_fim_aviso', 'end_date'):
        v = item.get(field)
        if not v:
            continue
        s = str(v).strip()
        for fmt in ('%Y%m%d', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
    return None


def parse_budget_eur(item: dict) -> float:
    """Tenta extrair dotação em EUR. Devolve 0 se desconhecida."""
    for field in ('budget', 'dotacao', 'budget_eur', 'envelope'):
        v = item.get(field)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip().upper().replace('.', '').replace(' ', '')
            # Remover sufixos
            mult = 1.0
            if 'M' in s and 'EUR' in s:
                mult = 1_000_000
                s = s.replace('M', '').replace('EUR', '')
            elif 'M' in s:
                mult = 1_000_000
                s = s.replace('M', '')
            elif 'K' in s:
                mult = 1_000
                s = s.replace('K', '')
            s = s.replace('EUR', '').replace(',', '.').strip()
            try:
                return float(s) * mult
            except ValueError:
                pass
    return 0.0


# ---------------------------------------------------------------------------
# Fórmula v4.11
# ---------------------------------------------------------------------------
def source_bonus(source_id: str) -> int:
    if source_id in FAMILIA_PT2030:
        return 500
    if source_id in HORIZON:
        return 30
    if source_id in NACIONAIS_ESTRATEGICOS:
        return 25
    if source_id in EU_OUTROS:
        return 20
    return 10  # catálogos e restantes


def dotacao_bonus(budget_eur: float) -> int:
    if budget_eur > 10_000_000:
        return 30
    if budget_eur > 1_000_000:
        return 10
    return 0


def prazo_bonus(deadline) -> int:
    if not deadline:
        return 0
    delta = (deadline - TODAY).days
    if delta < 30:
        return 30
    if delta < 60:
        return 20
    if delta < 90:
        return 10
    return 0


def compute_score(item: dict) -> tuple[int, dict]:
    src = item.get('source_id', '')
    budget = parse_budget_eur(item)
    deadline = parse_deadline(item)
    s_bonus = source_bonus(src)
    d_bonus = dotacao_bonus(budget)
    p_bonus = prazo_bonus(deadline)
    total = s_bonus + d_bonus + p_bonus
    detail = {
        'source': s_bonus,
        'dotacao': d_bonus,
        'prazo': p_bonus,
        'deadline': str(deadline) if deadline else None,
        'budget_eur': budget,
    }
    return total, detail


# ---------------------------------------------------------------------------
# Processar ficheiros
# ---------------------------------------------------------------------------
FILES = [
    'registry/queue.json',
    'registry/queue-overflow.json',
    'registry/queue-plano-anual.json',
    'registry/queue-catalogo.json',
]


def process_file(path: str) -> dict:
    fp = ROOT / path
    if not fp.exists():
        return {'file': path, 'skipped': True}
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('queue', data.get('items', []))
    if not isinstance(items, list):
        return {'file': path, 'skipped': True, 'reason': 'no list'}

    stats = {
        'file': path,
        'total': len(items),
        'changed': 0,
        'pt2030': 0,
        'horizon': 0,
        'nacional': 0,
        'eu_outros': 0,
        'catalogo': 0,
        'min_before': None,
        'max_before': None,
        'min_after': None,
        'max_after': None,
        'samples_top': [],
    }

    before_scores = [i.get('priority_score', 0) for i in items]
    if before_scores:
        stats['min_before'] = min(before_scores)
        stats['max_before'] = max(before_scores)

    for item in items:
        old = item.get('priority_score', 0)
        new, detail = compute_score(item)
        item['priority_score'] = new
        item['_score_detail'] = detail  # opcional: deixar trace
        if new != old:
            stats['changed'] += 1
        src = item.get('source_id', '')
        if src in FAMILIA_PT2030:
            stats['pt2030'] += 1
        elif src in HORIZON:
            stats['horizon'] += 1
        elif src in NACIONAIS_ESTRATEGICOS:
            stats['nacional'] += 1
        elif src in EU_OUTROS:
            stats['eu_outros'] += 1
        else:
            stats['catalogo'] += 1

    after_scores = [i.get('priority_score', 0) for i in items]
    if after_scores:
        stats['min_after'] = min(after_scores)
        stats['max_after'] = max(after_scores)

    # Top 5 amostra
    items_sorted = sorted(items, key=lambda x: x.get('priority_score', 0), reverse=True)
    for it in items_sorted[:5]:
        stats['samples_top'].append({
            'score': it.get('priority_score') or 0,
            'source': it.get('source_id') or '-',
            'codigo': it.get('codigo') or it.get('aviso_codigo') or '-',
            'name': (it.get('name') or it.get('title') or '')[:50],
        })

    if not DRY_RUN:
        # Limpar _score_detail antes de escrever (era apenas trace)
        for it in items:
            it.pop('_score_detail', None)
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

    return stats


def main() -> int:
    print(f'recompute_scores.py — v4.11')
    print(f'DRY_RUN: {DRY_RUN}\n')
    all_stats = []
    for path in FILES:
        stats = process_file(path)
        all_stats.append(stats)
        if stats.get('skipped'):
            print(f'[SKIP] {path}')
            continue
        print(f'=== {path} ===')
        print(f'  Total items: {stats["total"]}')
        print(f'  Alterados: {stats["changed"]}')
        print(f'  Por fonte: PT2030={stats["pt2030"]} Horizon={stats["horizon"]} '
              f'Nacional={stats["nacional"]} EU_outros={stats["eu_outros"]} '
              f'Catalogo={stats["catalogo"]}')
        print(f'  Score range: {stats["min_before"]}-{stats["max_before"]} -> '
              f'{stats["min_after"]}-{stats["max_after"]}')
        print(f'  Top 5 apos recalculo:')
        for s in stats['samples_top']:
            print(f'    [{s["score"]:4}] {s["source"]:22} {s["codigo"]:20} {s["name"]}')
        print()
    if DRY_RUN:
        print('*** Dry run — nenhum ficheiro alterado. Re-correr sem --dry-run para aplicar. ***')
    else:
        print('Ficheiros atualizados.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
