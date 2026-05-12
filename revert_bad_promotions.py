#!/usr/bin/env python3
"""
revert_bad_promotions.py - Reverter promoções erróneas do monitor.

Problema: monitor PASSO 2.7 promoveu 12 items com:
  - human_code populado com FA code (deveria ser ACORES2030-YYYY-NN etc.)
  - cross_portal_match.matched_portal = 'portugal-2030' (central, não Tipo A)
  - regulation_url = '-' (não descarregável)

Reverter:
  1. Remover items da queue (se vieram só do cross-portal match)
  2. Voltar para watchlist (se já não estiverem)
  3. Limpar human_code de FA codes
  4. Limpar lookup.by_human_code de entries com FA codes

Uso:
  python revert_bad_promotions.py --dry-run
  python revert_bad_promotions.py
"""
import json
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv
TODAY = date.today().isoformat()

FA_PATTERN = re.compile(r'^FA\d{4}/\d{4}$')
HUMAN_VALID = re.compile(r'^([A-Z]+2030-\d{4}-\d+|PACS-\d{4}-\d+)$')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'revert_bad_promotions.py (DRY_RUN={DRY_RUN})\n')

    with open('registry/queue.json', encoding='utf-8') as f:
        q_data = json.load(f)
    with open('registry/queue-plano-anual.json', encoding='utf-8') as f:
        w_data = json.load(f)
    with open('registry/lookup.json', encoding='utf-8') as f:
        lookup = json.load(f)

    queue = q_data.get('queue', [])
    watchlist = w_data.get('queue', [])
    wl_ids = {i.get('id', '') for i in watchlist}

    # Identificar items na queue que vieram de cross-portal match bogus
    to_revert = []
    for it in queue:
        cpm = it.get('cross_portal_match')
        if not cpm or not isinstance(cpm, dict):
            continue
        method = cpm.get('match_method', '')
        matched_portal = cpm.get('matched_portal', '')
        # Critérios de reversão:
        # 1. Match foi feito no central (portugal-2030)
        # 2. OU human_code é FA code (não formato humano canónico)
        # 3. OU regulation_url está vazio/inválido
        hc = it.get('human_code', '') or ''
        url = it.get('regulation_url', '')
        url_invalid = not url or url == '-' or not (isinstance(url, str) and url.startswith('http'))
        hc_invalid = bool(hc and FA_PATTERN.match(hc))

        # Critério estrito: SÓ reverter promoções do monitor recente
        # (matched_portal=portugal-2030 indica match no central, sem valor real)
        if matched_portal == 'portugal-2030':
            to_revert.append({
                'item': it,
                'reasons': {
                    'matched_in_central': True,
                    'human_code_is_fa': hc_invalid,
                    'no_valid_url': url_invalid,
                }
            })

    print(f'Items a reverter: {len(to_revert)}\n')
    for r in to_revert[:15]:
        it = r['item']
        print(f'  {it.get("codigo","-"):18} {it.get("id","-")[:50]}')
        print(f'    razões: {r["reasons"]}')

    if DRY_RUN:
        print(f'\n*** Dry run. Re-correr sem --dry-run para aplicar. ***')
        return 0

    # Executar reversão
    revert_ids = {r['item'].get('id', '') for r in to_revert}

    # 1. Remover da queue
    new_queue = [it for it in queue if it.get('id', '') not in revert_ids]
    removed_count = len(queue) - len(new_queue)

    # 2. Adicionar à watchlist (se não estiverem)
    added_to_wl = 0
    for r in to_revert:
        it = r['item']
        if it.get('id', '') in wl_ids:
            continue
        # Limpar campos errados antes de adicionar a watchlist
        wl_item = {**it}
        hc = wl_item.get('human_code', '')
        if hc and FA_PATTERN.match(hc):
            wl_item.pop('human_code', None)
        wl_item.pop('cross_portal_match', None)  # limpar marker erróneo
        wl_item['status'] = 'plano_anual'
        wl_item['plano_anual_last_check'] = TODAY
        wl_item.setdefault('plano_anual_checks', 0)
        wl_item['notes'] = (wl_item.get('notes', '') + f' | Revertido de promoção errónea em {TODAY}: cross-portal match no central não constituía evidência de regulamento real.')[:500]
        watchlist.append(wl_item)
        added_to_wl += 1

    # 3. Limpar lookup.by_human_code de FA codes
    by_human = lookup.get('by_human_code', {})
    bad_keys = [k for k in by_human if FA_PATTERN.match(k)]
    for k in bad_keys:
        del by_human[k]

    # Persistir
    q_data['queue'] = new_queue
    w_data['queue'] = watchlist
    lookup['by_human_code'] = by_human

    with open('registry/queue.json', 'w', encoding='utf-8') as f:
        json.dump(q_data, f, ensure_ascii=False, indent=2); f.write('\n')
    with open('registry/queue-plano-anual.json', 'w', encoding='utf-8') as f:
        json.dump(w_data, f, ensure_ascii=False, indent=2); f.write('\n')
    with open('registry/lookup.json', 'w', encoding='utf-8') as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2); f.write('\n')

    print(f'\n=== APLICADO ===')
    print(f'  Queue: -{removed_count} items ({len(new_queue)} restantes)')
    print(f'  Watchlist: +{added_to_wl} items ({len(watchlist)} totais)')
    print(f'  lookup.by_human_code: -{len(bad_keys)} entries FA inválidas')
    return 0


if __name__ == '__main__':
    sys.exit(main())
