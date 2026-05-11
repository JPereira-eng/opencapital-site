#!/usr/bin/env python3
"""
cross_portal_recovery.py - One-shot recovery: PAAs em watchlist com
correspondência em portais regionais sao promovidos para queue.json
com URL/codigo regional (regulamento real).

Esta é a versão "one-shot" do PASSO 2.7 do monitor (v4.11), aplicada de
uma vez ao backlog atual (132 PAAs em watchlist).

Uso:
  python cross_portal_recovery.py --dry-run
  python cross_portal_recovery.py
"""
import json
import sys
import subprocess
import re
import html as html_lib
from datetime import datetime, date
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = '--dry-run' in sys.argv
TODAY = date.today()

sys.path.insert(0, str(ROOT))
from recompute_scores import compute_score, FAMILIA_PT2030

# Mapeamento programa -> portal regional
PROGRAM_TO_PORTAL = {
    'COMPETE':    'compete-2030',
    'PESSOAS':    'pessoas-2030',
    'NORTE':      'norte-2030',
    'CENTRO':     'centro-2030',
    'LISBOA':     'lisboa-2030',
    'ALENTEJO':   'alentejo-2030',
    'ALGARVE':    'algarve-2030',
    'ACORES':     'acores-2030',
    'MADEIRA':    'madeira-2030',
    'MAR':        'mar-2030',
    'SUSTENTAVEL':'sustentavel-2030',
    'PAT':        'pat-2030',
}

# Portais com API confirmada (do mapping anterior)
PORTAL_APIS = {
    'pessoas-2030':     'https://pessoas2030.gov.pt/wp-json/wp/v2/aviso-2024',
    'sustentavel-2030': 'https://sustentavel2030.gov.pt/wp-json/wp/v2/aviso',
    'centro-2030':      'https://centro2030.pt/wp-json/wp/v2/aviso-2024',
    'lisboa-2030':      'https://lisboa.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'alentejo-2030':    'https://alentejo.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'algarve-2030':     'https://algarve.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'acores-2030':      'https://acores.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'madeira-2030':     'https://madeira.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'pat-2030':         'https://pat.portugal2030.pt/wp-json/wp/v2/aviso-2024',
}

SIMILARITY_THRESHOLD = 0.85


def normalize_title(s: str) -> str:
    s = html_lib.unescape(s or '')
    s = re.sub(r'\s+', ' ', s.lower().strip())
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def parse_date(s):
    if not s: return None
    for fmt in ('%Y%m%d', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S'):
        try: return datetime.strptime(str(s).strip(), fmt).date()
        except ValueError: pass
    return None


def fetch_api(url: str) -> list:
    """Fetch all pages of WP REST API."""
    items = []
    page = 1
    while page <= 5:  # safeguard
        try:
            r = subprocess.run(
                ['curl', '-sL', '-m', '30', f'{url}?per_page=100&page={page}'],
                capture_output=True, text=True, timeout=60,
            )
            data = json.loads(r.stdout)
            if not isinstance(data, list) or not data:
                break
            items.extend(data)
            if len(data) < 100:
                break
            page += 1
        except Exception:
            break
    return items


def derive_portal_candidates(programas):
    """Devolve list de portal_ids candidatos baseado em acf.programa."""
    candidatos = set()
    if not programas:
        return []
    if isinstance(programas, str):
        programas = [programas]
    for p in programas:
        p_upper = str(p).upper()
        for key, portal in PROGRAM_TO_PORTAL.items():
            if key in p_upper:
                candidatos.add(portal)
    # Filtrar apenas portais com API conhecida
    return [p for p in candidatos if p in PORTAL_APIS]


def main() -> int:
    print(f'cross_portal_recovery.py (DRY_RUN={DRY_RUN})\n')

    # 1) Carregar watchlist
    with open('registry/queue-plano-anual.json', encoding='utf-8') as f:
        watchlist_data = json.load(f)
    watchlist = watchlist_data.get('queue', [])
    print(f'Watchlist: {len(watchlist)} items totais')

    # 2) Filtrar elegíveis: TODOS os PT2030 (central ou regional) na watchlist
    #    com data_inicio passada ou desconhecida (presumido aberto)
    eligible = []
    for item in watchlist:
        sid = item.get('source_id', '')
        # Família PT2030 toda (central + regionais)
        if sid not in FAMILIA_PT2030:
            continue
        di_raw = item.get('data_inicio') or item.get('acf_data_inicio')
        di = parse_date(di_raw)
        if di and di > TODAY:
            continue  # ainda previsto, não tentar
        eligible.append(item)

    print(f'Elegíveis (família PT2030, data_inicio passada): {len(eligible)}\n')

    # 3) Pre-fetch APIs dos portais regionais (cache)
    print('A buscar avisos dos portais regionais...')
    regional_avisos = {}
    for portal_id, api_url in PORTAL_APIS.items():
        avisos = fetch_api(api_url)
        regional_avisos[portal_id] = avisos
        print(f'  {portal_id}: {len(avisos)} avisos')
    print()

    # 4) Para cada elegível, tentar match
    matches = []
    sem_match = []
    sem_candidatos = []

    for item in eligible:
        name = item.get('name', '')
        # Várias fontes possíveis para descobrir portais candidatos
        programas = item.get('programa') or item.get('acf_programa') or []
        if isinstance(programas, str):
            programas = [programas]
        portais_pre_calculados = item.get('regional_portals') or []
        source_atual = item.get('source_id', '')

        # 1) Candidatos: usar regional_portals se disponível
        portais_candidatos = list(portais_pre_calculados)
        # 2) Fallback: derivar de programa
        if not portais_candidatos:
            portais_candidatos = derive_portal_candidates(programas)
        # 3) Excluir o próprio source (não faz sentido procurar nele mesmo)
        portais_candidatos = [p for p in portais_candidatos
                               if p != source_atual and p in PORTAL_APIS]

        if not portais_candidatos:
            # 4) Último recurso: tentar TODOS os portais regionais com API
            #    (mais caro mas funciona quando programa não está mapeado)
            portais_candidatos = [p for p in PORTAL_APIS.keys() if p != source_atual]

        best_match = None
        best_score = 0.0
        best_portal = None
        for portal_id in portais_candidatos:
            for av in regional_avisos.get(portal_id, []):
                title_r = av.get('title', {})
                title_r = title_r.get('rendered', '') if isinstance(title_r, dict) else str(title_r)
                sim = title_similarity(name, title_r)
                if sim > best_score and sim >= SIMILARITY_THRESHOLD:
                    best_score = sim
                    best_match = av
                    best_portal = portal_id

        if best_match:
            matches.append({
                'item': item,
                'match': best_match,
                'portal': best_portal,
                'similarity': best_score,
            })
        else:
            sem_match.append(item)

    print(f'\n=== RESULTADO ===')
    print(f'Total elegíveis: {len(eligible)}')
    print(f'  Com match >= {SIMILARITY_THRESHOLD*100:.0f}%: {len(matches)}')
    print(f'  Sem match em portais candidatos: {len(sem_match)}')
    print(f'  Sem programa mapeável (sem candidatos): {len(sem_candidatos)}')

    if matches:
        print(f'\n=== TOP 10 MATCHES ===')
        for m in sorted(matches, key=lambda x: x['similarity'], reverse=True)[:10]:
            print(f'  {m["similarity"]*100:.0f}% | {m["item"].get("aviso_codigo","-"):15} -> {m["portal"]}/{m["match"].get("acf",{}).get("codigo","-")}')
            print(f'        central: {m["item"]["name"][:65]}')
            print(f'       regional: {html_lib.unescape(m["match"].get("title",{}).get("rendered","") if isinstance(m["match"].get("title"),dict) else str(m["match"].get("title","")))[:65]}')
            print()

    if DRY_RUN:
        print(f'\n*** Dry run. Re-correr sem --dry-run para promover {len(matches)} items para queue.json. ***')
        return 0

    # 5) Aplicar: promover matches para queue.json, remover da watchlist
    with open('registry/queue.json', encoding='utf-8') as f:
        queue_data = json.load(f)
    queue = queue_data.get('queue', [])

    promoted_ids = set()
    for m in matches:
        item = m['item']
        match = m['match']
        portal = m['portal']
        acf = match.get('acf', {}) or {}

        codigo_regional = acf.get('codigo', '') or ''
        pdf = acf.get('pdf', '')
        link = match.get('link', '')
        title = match.get('title', {})
        title = title.get('rendered', '') if isinstance(title, dict) else str(title)

        novo_item = dict(item)  # copia
        novo_item['source_id'] = portal
        novo_item['codigo'] = codigo_regional
        novo_item['aviso_codigo'] = codigo_regional
        novo_item['regulation_url'] = pdf or link
        novo_item['pdf_url'] = pdf if pdf else None
        novo_item['regulation_local'] = None
        novo_item['status'] = 'pending'
        novo_item['fail_count'] = 0
        novo_item['name'] = html_lib.unescape(title)
        novo_item['cross_portal_match'] = {
            'original_codigo': item.get('aviso_codigo'),
            'original_portal': 'portugal-2030',
            'matched_portal': portal,
            'matched_codigo': codigo_regional,
            'title_similarity': round(m['similarity'], 3),
            'matched_at': TODAY.isoformat(),
        }
        # Recalcular score com nova fonte
        score, _ = compute_score(novo_item)
        novo_item['priority_score'] = score
        queue.append(novo_item)
        promoted_ids.add(item['id'])

    # Remover da watchlist
    watchlist_new = [it for it in watchlist if it['id'] not in promoted_ids]
    watchlist_data['queue'] = watchlist_new
    queue_data['queue'] = queue

    # Ordem crítica: queue primeiro
    with open('registry/queue.json', 'w', encoding='utf-8') as f:
        json.dump(queue_data, f, ensure_ascii=False, indent=2); f.write('\n')
    with open('registry/queue-plano-anual.json', 'w', encoding='utf-8') as f:
        json.dump(watchlist_data, f, ensure_ascii=False, indent=2); f.write('\n')

    print(f'\nAplicado:')
    print(f'  queue.json: +{len(matches)} items (agora {len(queue)})')
    print(f'  queue-plano-anual.json: -{len(matches)} items (agora {len(watchlist_new)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
