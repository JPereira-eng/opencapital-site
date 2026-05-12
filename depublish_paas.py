#!/usr/bin/env python3
"""
depublish_paas.py - Remove 9 PAAs publicados indevidamente em 15/abril.

Para cada PAA:
  1. Remove folder instrumentos/<slug>/
  2. Remove entry de instruments-catalog.json
  3. Remove entry do shard correspondente
  4. Adiciona à queue-plano-anual.json (watchlist) para que o monitor
     detecte quando o regulamento real for publicado.

Uso:
  python depublish_paas.py --dry-run
  python depublish_paas.py
"""
import json
import sys
import shutil
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv
TODAY = date.today().isoformat()

# Os 9 PAAs com FA code central, sem .txt, criados em 15/abril
PAA_TARGETS = [
    ('FA0036/2025', 'protecao-civil-e-gestao-integrada-de-riscos-prevencao-e-mitigacao-de-r', 'aberto'),
    ('FA0287/2025', 'tratamento-em-estacoes-de-tratamento-de-aguas-residuais-etar-para-prod', 'previsto'),
    ('FA0280/2025', 'acoes-para-mitigacao-da-situacao-de-escassez-hidrica-e-assegurar-a-res', 'aberto'),
    ('FA0271/2025', 'aguas-residuais-em-alta', 'aberto'),
    ('FA0156/2025', 'programa-de-seguranca-ferroviaria-supressao-de-pns', 'aberto'),
    ('FA0269/2025', 'abastecimento-de-agua-em-alta', 'aberto'),
    ('FA0682/2024', 'linha-norte-estacao-do-oriente-terminal-tecnico', 'previsto'),
    ('FA0165/2025', 'ampliacao-e-modernizacao-do-aeroporto-das-lajes', 'previsto'),
    ('FA0098/2025', 'cursos-profissionais-entidades-privadas', 'previsto'),
]


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(p, data):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    print(f'depublish_paas.py (DRY_RUN={DRY_RUN})\n')

    # 1) Localizar folders exatos (o slug pode estar truncado)
    actions = []
    for fa_code, slug_hint, estado in PAA_TARGETS:
        # Find folder
        folder = ROOT / 'instrumentos' / slug_hint
        if not folder.exists():
            # Try variations / find by prefix
            candidates = list((ROOT / 'instrumentos').glob(f'{slug_hint[:50]}*'))
            if not candidates:
                print(f'  AVISO: folder não encontrado para {fa_code} ({slug_hint[:50]})')
                continue
            folder = candidates[0]
        slug_final = folder.name

        # Find in catalog
        with open(ROOT / 'instruments-catalog.json', encoding='utf-8') as f:
            cat = json.load(f)
        cat_entry = next((i for i in cat['instruments'] if i.get('id') == slug_final), None)

        # Find in shards
        shard_hit = None
        shards_dir = ROOT / 'registry' / 'shards'
        for sf in shards_dir.glob('pt2030-*.json'):
            sh = load(sf)
            if any(it.get('id') == slug_final for it in sh.get('items', [])):
                shard_hit = sf.name
                break

        actions.append({
            'fa_code': fa_code,
            'slug': slug_final,
            'estado': estado,
            'folder': folder,
            'has_catalog_entry': bool(cat_entry),
            'shard': shard_hit,
            'cat_entry': cat_entry,
        })

    print(f'=== Plano: remover {len(actions)} PAAs ===\n')
    for a in actions:
        print(f'  {a["fa_code"]:15} {a["slug"][:55]:55} cat={a["has_catalog_entry"]} shard={a["shard"]}')

    if DRY_RUN:
        print('\n*** Dry run. Re-correr sem --dry-run para aplicar. ***')
        return 0

    # 2) Executar
    # Load all state files
    cat_path = ROOT / 'instruments-catalog.json'
    watchlist_path = ROOT / 'registry' / 'queue-plano-anual.json'

    with open(cat_path, encoding='utf-8') as f:
        cat = json.load(f)
    with open(watchlist_path, encoding='utf-8') as f:
        watchlist = json.load(f)
    wl_items = watchlist.get('queue', [])
    wl_ids = {i.get('id', '') for i in wl_items}

    removed_count = 0
    for a in actions:
        slug = a['slug']
        fa = a['fa_code']

        # a) Remove folder
        if a['folder'].exists():
            shutil.rmtree(a['folder'])
            print(f'  [-folder] {slug}')

        # b) Remove from catalog
        before = len(cat['instruments'])
        cat['instruments'] = [i for i in cat['instruments'] if i.get('id') != slug]
        if len(cat['instruments']) < before:
            print(f'  [-cat   ] {slug}')

        # c) Remove from shard
        if a['shard']:
            sf = ROOT / 'registry' / 'shards' / a['shard']
            sh = load(sf)
            before = len(sh.get('items', []))
            sh['items'] = [it for it in sh.get('items', []) if it.get('id') != slug]
            after = len(sh['items'])
            if after < before:
                sh['count'] = after
                # Update aggregates
                opens = sum(1 for it in sh['items'] if it.get('state') == 'aberto')
                closeds = sum(1 for it in sh['items'] if it.get('state') == 'fechado')
                planneds = sum(1 for it in sh['items'] if it.get('state') == 'previsto')
                sh['open'] = opens
                sh['closed'] = closeds
                sh['planned'] = planneds
                sh['published'] = sh.get('published', after) - 1
                save(sf, sh)
                print(f'  [-shard ] {slug} from {a["shard"]}')

        # d) Add to watchlist
        if slug not in wl_ids:
            wl_items.append({
                'id': slug,
                'name': (a['cat_entry'].get('title', '') if a['cat_entry'] else fa) + f' (FA: {fa})',
                'codigo': fa,
                'aviso_codigo': fa,
                'source_id': 'portugal-2030',
                'shard': a['shard'] or 'pt2030-central',
                'detected_date': TODAY,
                'status': 'plano_anual',
                'priority_score': 500,
                'plano_anual_checks': 0,
                'notes': f'Re-adicionado à watchlist em {TODAY} após depublicação por suspeita PAA (sem regulamento técnico real). Aguarda detecção de regulamento real pelo monitor (PASSO 2.6 ou 2.7).',
            })
            print(f'  [+watchl] {slug}')

        removed_count += 1

    # Persistir
    watchlist['queue'] = wl_items
    save(cat_path, cat)
    save(watchlist_path, watchlist)

    print(f'\nConcluído: {removed_count} PAAs removidos do site e re-adicionados à watchlist.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
