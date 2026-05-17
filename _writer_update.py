"""Helper script to update catalog, shard, queue and index for a single article."""
import json
import sys
import os
from pathlib import Path

REPO = Path("C:/Users/jmcpe/Desktop/opencapital-site")
TODAY = "2026-05-17"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def add_catalog_entry(entry):
    cat_path = REPO / "instruments-catalog.json"
    cat = load(cat_path)
    cat["instruments"] = [i for i in cat["instruments"] if i.get("id") != entry["id"]]
    cat["instruments"].append(entry)
    save(cat_path, cat)


def add_shard_entry(shard, item, state):
    sp = REPO / "registry" / "shards" / f"{shard}.json"
    s = load(sp)
    s["items"] = [i for i in s["items"] if i.get("id") != item["id"]]
    s["items"].append(item)
    s["count"] = s.get("count", 0) + 1
    s["published"] = s.get("published", 0) + 1
    if state == "aberto":
        s["open"] = s.get("open", 0) + 1
    elif state == "fechado":
        s["closed"] = s.get("closed", 0) + 1
    elif state == "previsto":
        s["planned"] = s.get("planned", 0) + 1
    save(sp, s)


def ensure_lookup(slug, aviso_codigo):
    lp = REPO / "registry" / "lookup.json"
    l = load(lp)
    l.setdefault("by_id", {})[slug] = True
    if aviso_codigo:
        l.setdefault("by_aviso_codigo", {})[aviso_codigo] = slug
    save(lp, l)


def remove_from_queue(slug, queue_file="queue.json"):
    qp = REPO / "registry" / queue_file
    q = load(qp)
    before = len(q.get("queue", []))
    q["queue"] = [i for i in q.get("queue", []) if i.get("id") != slug]
    after = len(q["queue"])
    save(qp, q)
    return before - after


def update_index(shard, state):
    ip = REPO / "registry" / "index.json"
    idx = load(ip)
    idx["_meta"]["last_writer_run"] = TODAY
    idx["last_writer_run"] = TODAY
    t = idx["totals"]
    t["published"] = t.get("published", 0) + 1
    t["in_queue"] = max(0, t.get("in_queue", 0) - 1)
    if state == "aberto":
        t["open"] = t.get("open", 0) + 1
    elif state == "fechado":
        t["closed"] = t.get("closed", 0) + 1
    elif state == "previsto":
        t["planned"] = t.get("planned", 0) + 1
    save(ip, idx)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "process":
        # All-in-one for a single article
        slug = sys.argv[2]
        shard = sys.argv[3]
        state = sys.argv[4]
        aviso_codigo = sys.argv[5] if len(sys.argv) > 5 else ""
        queue_file = sys.argv[6] if len(sys.argv) > 6 else "queue.json"
        entry_json = sys.stdin.read()
        entry = json.loads(entry_json)

        add_catalog_entry(entry)
        item = {
            "id": slug,
            "file": f"instrumentos/{slug}/index.html",
            "source": entry.get("fonte_source", entry["fonte"]),
            "state": state,
            "last_check": TODAY,
        }
        if aviso_codigo:
            item["aviso_codigo"] = aviso_codigo
        add_shard_entry(shard, item, state)
        ensure_lookup(slug, aviso_codigo)
        removed = remove_from_queue(slug, queue_file)
        update_index(shard, state)
        print(f"OK: catalog+shard+lookup+index updated. Queue removed: {removed}")
