"""Single-article registry update helper for radar-writer batch."""
import json, os, sys
from datetime import date

REPO = r"C:/Users/jmcpe/Desktop/opencapital-site"
TODAY = date.today().isoformat()

def load(p):
    with open(os.path.join(REPO, p), 'r', encoding='utf-8') as f:
        return json.load(f)

def save(p, data):
    with open(os.path.join(REPO, p), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_for_article(slug, aviso_codigo, shard_name, source_id, estado, queue_file='registry/queue.json'):
    """Update shard, lookup, index, and remove from queue."""
    # 1. Shard
    shard_path = f'registry/shards/{shard_name}.json'
    sh = load(shard_path)
    new_item = {
        "id": slug,
        "file": f"instrumentos/{slug}/index.html",
        "source": source_id,
        "state": estado,
        "last_check": TODAY
    }
    sh['items'].append(new_item)
    sh['count'] = len(sh['items'])
    if estado == 'aberto':
        sh['open'] = sh.get('open', 0) + 1
    elif estado == 'fechado':
        sh['closed'] = sh.get('closed', 0) + 1
    elif estado == 'previsto':
        sh['planned'] = sh.get('planned', 0) + 1
    sh['published'] = sh.get('published', 0) + 1
    save(shard_path, sh)
    print(f'[shard {shard_name}] count={sh["count"]} planned={sh["planned"]} published={sh["published"]}')

    # 2. Lookup
    lk = load('registry/lookup.json')
    lk['by_id'][slug] = True
    if aviso_codigo:
        lk['by_aviso_codigo'][aviso_codigo] = slug
    save('registry/lookup.json', lk)
    print(f'[lookup] added by_id={slug}, by_aviso_codigo={aviso_codigo}')

    # 3. Index
    idx = load('registry/index.json')
    idx['totals']['published'] = idx['totals'].get('published', 0) + 1
    idx['totals']['in_queue'] = max(0, idx['totals'].get('in_queue', 0) - 1)
    if estado == 'aberto':
        idx['totals']['open'] = idx['totals'].get('open', 0) + 1
    elif estado == 'fechado':
        idx['totals']['closed'] = idx['totals'].get('closed', 0) + 1
    elif estado == 'previsto':
        idx['totals']['planned'] = idx['totals'].get('planned', 0) + 1
    idx['shards'][shard_name] = {
        'count': sh['count'],
        'open': sh.get('open', 0),
        'closed': sh.get('closed', 0),
        'planned': sh.get('planned', 0),
        'published': sh.get('published', 0)
    }
    idx['_meta']['last_writer_run'] = TODAY
    save('registry/index.json', idx)
    print(f'[index] published={idx["totals"]["published"]}, in_queue={idx["totals"]["in_queue"]}, planned={idx["totals"]["planned"]}')

    # 4. Remove from queue
    qd = load(queue_file)
    queue_list = qd.get('queue', [])
    before = len(queue_list)
    qd['queue'] = [i for i in queue_list if i.get('id') != slug]
    after = len(qd['queue'])
    if 'updated' in qd:
        qd['updated'] = TODAY
    save(queue_file, qd)
    print(f'[queue {queue_file}] {before} -> {after}')

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage: _writer_helper.py <slug> <aviso_codigo> <shard> <source_id> <estado> [queue_file]')
        sys.exit(1)
    slug = sys.argv[1]
    aviso = sys.argv[2]
    shard = sys.argv[3]
    src = sys.argv[4]
    est = sys.argv[5]
    qf = sys.argv[6] if len(sys.argv) > 6 else 'registry/queue.json'
    update_for_article(slug, aviso, shard, src, est, qf)
