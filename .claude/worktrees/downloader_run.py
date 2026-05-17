"""Radar downloader run - 2026-05-16
Processes top-10 pending items from queue.json: searches portal API by title/codigo,
resolves real wordpress_id and acf.pdf, downloads PDF, validates with TESTE A (PAA)
and TESTE B (size), updates queue.json + queue-plano-anual.json.
"""
import json
import urllib.request
import urllib.parse
import re
import os
import subprocess
import io
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = r'C:/Users/jmcpe/Desktop/opencapital-site'
TODAY = '2026-05-16'

PORTAL_API = {
    'centro-2030': 'https://centro2030.pt/wp-json/wp/v2/aviso-2024',
    'acores-2030': 'https://acores.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'madeira-2030': 'https://madeira.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'alentejo-2030': 'https://alentejo.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'algarve-2030': 'https://algarve.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'lisboa-2030': 'https://lisboa.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'pat-2030': 'https://pat.portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'portugal-2030': 'https://portugal2030.pt/wp-json/wp/v2/aviso-2024',
    'sustentavel-2030': 'https://sustentavel2030.gov.pt/wp-json/wp/v2/aviso',
    'pessoas-2030': 'https://pessoas2030.gov.pt/wp-json/wp/v2/aviso-2024',
}

PORTAL_MEDIA = {
    'centro-2030': 'https://centro2030.pt/wp-json/wp/v2/media',
    'acores-2030': 'https://acores.portugal2030.pt/wp-json/wp/v2/media',
    'madeira-2030': 'https://madeira.portugal2030.pt/wp-json/wp/v2/media',
    'alentejo-2030': 'https://alentejo.portugal2030.pt/wp-json/wp/v2/media',
    'algarve-2030': 'https://algarve.portugal2030.pt/wp-json/wp/v2/media',
    'lisboa-2030': 'https://lisboa.portugal2030.pt/wp-json/wp/v2/media',
    'pat-2030': 'https://pat.portugal2030.pt/wp-json/wp/v2/media',
    'portugal-2030': 'https://portugal2030.pt/wp-json/wp/v2/media',
    'sustentavel-2030': 'https://sustentavel2030.gov.pt/wp-json/wp/v2/media',
    'pessoas-2030': 'https://pessoas2030.gov.pt/wp-json/wp/v2/media',
}


def fetch_url(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception:
        return None


def download_binary(url, dest, timeout=45):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        return len(data)
    except Exception:
        return None


def normalize_title(t):
    t = t.lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-z0-9]+', ' ', t).strip()
    return t


def title_similarity(a, b):
    sa = set(normalize_title(a).split())
    sb = set(normalize_title(b).split())
    if not sa or not sb:
        return 0
    common = sa & sb
    return len(common) / max(len(sa), len(sb))


COMMON_STOP = {'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'e', 'em', 'para', 'com',
               'pela', 'pelo', 'na', 'no', 'as', 'os', 'um', 'uma'}


def search_terms(name):
    words = re.findall(r'[a-zA-ZÀ-ÿ]+', name)
    keywords = [w for w in words if len(w) > 3 and w.lower() not in COMMON_STOP][:3]
    return keywords


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    queue_data = load_json(f'{REPO}/registry/queue.json')
    items = queue_data['queue']
    pending = [i for i in items if i.get('regulation_local') is None
               and i.get('status') in ('pending', None)
               and i.get('regulation_url')
               and i.get('fail_count', 0) < 3]
    pending.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    to_process = pending[:10]
    print(f"Will process {len(to_process)} items")

    paa_data = load_json(f'{REPO}/registry/queue-plano-anual.json')

    results = {'ready': [], 'paa_moved': [], 'failed': [], 'skipped': []}

    for idx, item in enumerate(to_process):
        item_id = item['id']
        source_id = item['source_id']
        name = item['name']
        codigo = item.get('codigo', '')
        print(f"\n[{idx+1}/{len(to_process)}] {item_id[:50]} | {source_id}")
        print(f"  Name: {name[:80]}")

        if source_id not in PORTAL_API:
            print(f"  SKIP: Unknown source {source_id}")
            results['skipped'].append({'id': item_id, 'reason': 'unknown source'})
            continue

        api = PORTAL_API[source_id]
        media_api = PORTAL_MEDIA[source_id]

        found_post = None
        search_attempts = []

        if codigo:
            cod_variants = [codigo, codigo.replace('/', '-'), codigo.replace('/', ''), codigo.split('/')[0]]
            for cv in cod_variants:
                search_attempts.append(cv)
                url = f"{api}?per_page=10&search={urllib.parse.quote(cv)}"
                resp = fetch_url(url)
                if resp:
                    try:
                        data = json.loads(resp)
                        if isinstance(data, list) and data:
                            for post in data:
                                acf = post.get('acf', {})
                                post_cod = (acf.get('codigo') or '').strip()
                                if post_cod == codigo or post_cod.replace('/', '') == codigo.replace('/', ''):
                                    found_post = post
                                    break
                            if found_post:
                                break
                            if len(data) == 1:
                                found_post = data[0]
                                break
                    except Exception:
                        pass
                if found_post:
                    break

        if not found_post:
            terms = search_terms(name)
            if terms:
                qstr = ' '.join(terms)
                search_attempts.append(qstr)
                url = f"{api}?per_page=20&search={urllib.parse.quote(qstr)}"
                resp = fetch_url(url)
                if resp:
                    try:
                        data = json.loads(resp)
                        if isinstance(data, list) and data:
                            best = None
                            best_score = 0
                            for post in data:
                                ptitle = post.get('title', {}).get('rendered', '')
                                score = title_similarity(name, ptitle)
                                acf = post.get('acf', {})
                                if codigo and (acf.get('codigo') or '').strip() == codigo:
                                    score += 1.0
                                if score > best_score:
                                    best_score = score
                                    best = post
                            if best and best_score >= 0.3:
                                found_post = best
                    except Exception:
                        pass

        if not found_post:
            print(f"  FAIL: post not found via search. Tried: {search_attempts}")
            item['fail_count'] = item.get('fail_count', 0) + 1
            item['download_error'] = f"Search failed: codigo {codigo} not on portal {source_id}"
            item['last_fail_date'] = TODAY
            ft = item.get('fallback_tried', [])
            if '2b-acf-all' not in ft:
                ft.append('2b-acf-all')
            item['fallback_tried'] = ft
            results['failed'].append({'id': item_id, 'reason': 'post not found via API search'})
            continue

        acf = found_post.get('acf', {})
        real_wp_id = found_post.get('id')
        real_slug = found_post.get('slug')
        print(f"  Found post: wp_id={real_wp_id} slug={real_slug[:50]}")
        print(f"  acf.codigo={acf.get('codigo')}")

        pdf_url_candidates = []
        for field in ['pdf', 'aviso', 'regulamento', 'ficha_tecnica', 'documento', 'aviso_documento']:
            val = acf.get(field)
            if not val:
                continue
            if isinstance(val, str) and val.startswith('http'):
                pdf_url_candidates.append(('direct', val, field))
            elif isinstance(val, int) and val > 0:
                murl = f"{media_api}/{val}"
                mresp = fetch_url(murl)
                if mresp:
                    try:
                        mdata = json.loads(mresp)
                        src = mdata.get('source_url')
                        if src:
                            pdf_url_candidates.append(('media_resolved', src, field))
                    except Exception:
                        pass
            elif isinstance(val, str) and val.isdigit():
                murl = f"{media_api}/{val}"
                mresp = fetch_url(murl)
                if mresp:
                    try:
                        mdata = json.loads(mresp)
                        src = mdata.get('source_url')
                        if src:
                            pdf_url_candidates.append(('media_resolved', src, field))
                    except Exception:
                        pass

        if not pdf_url_candidates:
            print(f"  FAIL: no PDF in ACF. Fields: {list(acf.keys())[:20]}")
            item['fail_count'] = item.get('fail_count', 0) + 1
            item['download_error'] = f"No PDF in ACF for wp_id {real_wp_id}"
            item['last_fail_date'] = TODAY
            ft = item.get('fallback_tried', [])
            if '2b-acf-all' not in ft:
                ft.append('2b-acf-all')
            item['fallback_tried'] = ft
            item['wordpress_id'] = real_wp_id
            results['failed'].append({'id': item_id, 'reason': 'no PDF in ACF'})
            continue

        pdf_origin, pdf_url, pdf_field = pdf_url_candidates[0]
        print(f"  PDF URL ({pdf_field}, {pdf_origin}): {pdf_url[:100]}")

        os.makedirs(f'{REPO}/regulamentos/{source_id}', exist_ok=True)
        pdf_path = f'{REPO}/regulamentos/{source_id}/{item_id}.pdf'
        txt_path = f'{REPO}/regulamentos/{source_id}/{item_id}.txt'

        size = download_binary(pdf_url, pdf_path)
        if not size or size < 5000:
            print(f"  FAIL: download too small ({size} bytes)")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            item['fail_count'] = item.get('fail_count', 0) + 1
            item['download_error'] = f"PDF download failed or too small ({size})"
            item['last_fail_date'] = TODAY
            ft = item.get('fallback_tried', [])
            if '2b-acf-all' not in ft:
                ft.append('2b-acf-all')
            item['fallback_tried'] = ft
            item['wordpress_id'] = real_wp_id
            results['failed'].append({'id': item_id, 'reason': f'download failed ({size})'})
            continue

        print(f"  Downloaded: {size} bytes")

        try:
            subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf_path, txt_path],
                          check=True, capture_output=True, timeout=30)
        except Exception as e:
            print(f"  FAIL: pdftotext error: {e}")
            for p in (pdf_path, txt_path):
                if os.path.exists(p):
                    os.remove(p)
            item['fail_count'] = item.get('fail_count', 0) + 1
            item['download_error'] = "pdftotext failed"
            item['last_fail_date'] = TODAY
            ft = item.get('fallback_tried', [])
            if '2b-acf-all' not in ft:
                ft.append('2b-acf-all')
            item['fallback_tried'] = ft
            item['wordpress_id'] = real_wp_id
            results['failed'].append({'id': item_id, 'reason': 'pdftotext failed'})
            continue

        with open(txt_path, encoding='utf-8', errors='replace') as f:
            text = f.read()

        word_count = len(text.split())
        text_lower = text.lower()

        paa_markers = [
            'plano anual de avisos',
            'resumo de aviso do plano',
            'paa2026', 'paa2025', 'paa2024',
            'aviso a publicar em:',
            'previsao aproximada', 'previsão aproximada',
            'aviso que ira ser lancado', 'aviso que irá ser lançado',
        ]
        is_paa = any(m in text_lower for m in paa_markers)

        if is_paa:
            print(f"  PAA detected (words={word_count}). Moving to watchlist.")
            os.remove(pdf_path)
            os.remove(txt_path)
            item_paa = dict(item)
            item_paa['status'] = 'plano_anual'
            item_paa['download_error'] = 'Plano Anual - nao e aviso publicado, apenas previsao'
            item_paa['plano_anual_detected_date'] = TODAY
            item_paa['plano_anual_checks'] = 1
            item_paa['wordpress_id'] = real_wp_id
            existing = [p for p in paa_data['queue'] if p.get('id') == item_id]
            if existing:
                existing[0]['plano_anual_checks'] = existing[0].get('plano_anual_checks', 0) + 1
                existing[0]['plano_anual_last_check'] = TODAY
            else:
                paa_data['queue'].append(item_paa)
            results['paa_moved'].append(item_id)
            item['_REMOVE'] = True
            continue

        crit_markers = ['despesas elegíveis', 'despesas elegiveis',
                       'criterios de seleção', 'critérios de seleção',
                       'criterios de selecao']
        has_crit = any(m in text_lower for m in crit_markers)

        if word_count < 800 and not has_crit:
            print(f"  FAIL TESTE B: insufficient content (words={word_count})")
            os.remove(pdf_path)
            os.remove(txt_path)
            item['fail_count'] = item.get('fail_count', 0) + 1
            item['download_error'] = f"Resumo sem regulamento completo (words={word_count})"
            item['last_fail_date'] = TODAY
            ft = item.get('fallback_tried', [])
            if '2b-acf-all' not in ft:
                ft.append('2b-acf-all')
            item['fallback_tried'] = ft
            item['wordpress_id'] = real_wp_id
            results['failed'].append({'id': item_id, 'reason': f'TESTE B failed (words={word_count})'})
            continue

        item['regulation_local'] = f'regulamentos/{source_id}/{item_id}.txt'
        item['status'] = 'ready'
        item['fail_count'] = 0
        item['data_status'] = 'verified'
        item['wordpress_id'] = real_wp_id
        item['regulation_url'] = pdf_url
        item['pdf_url'] = pdf_url
        for k in ('download_error', 'last_fail_date'):
            if k in item:
                del item[k]
        ft = item.get('fallback_tried', [])
        if '2b-acf-all' not in ft:
            ft.append('2b-acf-all')
        item['fallback_tried'] = ft
        print(f"  SUCCESS: words={word_count}")
        results['ready'].append(item_id)

    queue_data['queue'] = [i for i in items if not i.get('_REMOVE')]
    save_json(f'{REPO}/registry/queue.json', queue_data)
    save_json(f'{REPO}/registry/queue-plano-anual.json', paa_data)

    print("\n\n=== SUMMARY ===")
    print(f"Ready:    {len(results['ready'])}")
    for r in results['ready']:
        print(f"  + {r}")
    print(f"PAA moved: {len(results['paa_moved'])}")
    for r in results['paa_moved']:
        print(f"  ~ {r}")
    print(f"Failed:   {len(results['failed'])}")
    for r in results['failed']:
        print(f"  - {r['id'][:60]}: {r['reason']}")
    print(f"Skipped:  {len(results['skipped'])}")


if __name__ == '__main__':
    main()
