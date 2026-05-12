#!/usr/bin/env python3
"""Radar Downloader v4.1 - single execution.

Processes up to 10 items from queue.json (aviso) and queue-catalogo.json
(catalogo), priority-sorted. PT2030 family items use API + media resolve
(2b-pdf). Applies TESTE A (PAA) and TESTE B (size) bloqueantes.
PAAs are moved to queue-plano-anual.json.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("C:/Users/jmcpe/Desktop/opencapital-site")
QUEUE_AVISO = REPO / "registry" / "queue.json"
QUEUE_CATALOGO = REPO / "registry" / "queue-catalogo.json"
QUEUE_PAA = REPO / "registry" / "queue-plano-anual.json"
SOURCES_SCAN = REPO / "sources-scan.json"
REG_DIR = REPO / "regulamentos"
TODAY = "2026-05-13"
MAX_DOWNLOADS = 10

PT2030_FAMILY = {
    "portugal-2030", "compete-2030", "pessoas-2030", "sustentavel-2030",
    "norte-2030", "centro-2030", "lisboa-2030", "alentejo-2030",
    "algarve-2030", "acores-2030", "madeira-2030", "pat-2030",
}

PAA_PATTERNS = [
    "plano anual de avisos",
    "resumo de aviso do plano",
    "paa2026", "paa2027", "paa2025",
    "aviso a publicar em",
    "previsao aproximada", "previsão aproximada",
    "aviso que ira ser lancado", "aviso que irá ser lançado",
    "ficha que aqui pode consultar e apenas uma previsao",
    "ficha que aqui pode consultar é apenas uma previsão",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_sources_api() -> dict[str, str]:
    s = load_json(SOURCES_SCAN)
    return {src["id"]: src["api_url"] for src in s.get("sources", []) if src.get("api_url")}


def curl_get(url: str, timeout: int = 30) -> tuple[int, bytes]:
    try:
        r = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0", "-w", "\n__HTTP_CODE__:%{http_code}", url],
            capture_output=True, timeout=timeout,
        )
        body = r.stdout
        m = re.search(rb"\n__HTTP_CODE__:(\d+)$", body)
        code = int(m.group(1)) if m else 0
        if m:
            body = body[: m.start()]
        return code, body
    except subprocess.TimeoutExpired:
        return 0, b""
    except Exception:
        return 0, b""


def curl_download(url: str, out: Path, timeout: int = 60) -> tuple[int, int]:
    """Download to file. Returns (http_code, bytes_downloaded)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0",
             "-w", "%{http_code} %{size_download}",
             "-o", str(out), url],
            capture_output=True, timeout=timeout,
        )
        parts = r.stdout.decode("ascii", errors="ignore").strip().split()
        code = int(parts[0]) if parts else 0
        size = int(parts[1]) if len(parts) > 1 else 0
        return code, size
    except Exception:
        return 0, 0


def pdftotext(pdf_path: Path, txt_path: Path) -> bool:
    try:
        r = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(pdf_path), str(txt_path)],
            capture_output=True, timeout=60,
        )
        return r.returncode == 0 and txt_path.exists()
    except Exception:
        return False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def is_paa(text: str) -> bool:
    lo = text.lower()
    return any(p in lo for p in PAA_PATTERNS)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


_PORTAL_INDEX_CACHE: dict[str, list[dict]] = {}


def fetch_portal_avisos(src_id: str, api_base: str) -> list[dict]:
    if src_id in _PORTAL_INDEX_CACHE:
        return _PORTAL_INDEX_CACHE[src_id]
    all_posts: list[dict] = []
    page = 1
    while page <= 10:
        url = f"{api_base}?per_page=100&page={page}"
        code, body = curl_get(url, timeout=30)
        if code != 200 or not body:
            break
        try:
            posts = json.loads(body.decode("utf-8", errors="ignore"))
        except Exception:
            break
        if not isinstance(posts, list) or not posts:
            break
        all_posts.extend(posts)
        if len(posts) < 100:
            break
        page += 1
    _PORTAL_INDEX_CACHE[src_id] = all_posts
    return all_posts


def _slugify(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s


def find_post_by_item(item: dict, posts: list[dict]) -> dict | None:
    target_id = (item.get("id") or "").lower()
    target_slug = _slugify(item.get("name", ""))
    target_codigo = (item.get("codigo") or item.get("aviso_codigo") or "").upper()
    target_tokens = set(target_id.split("-")) | set(target_slug.split("-"))
    target_tokens.discard("")

    best = None
    best_score = 0
    for p in posts:
        slug = p.get("slug") or ""
        title_raw = (p.get("title") or {}).get("rendered") or ""
        acf = p.get("acf") or {}
        codigo = (acf.get("codigo") or "").upper()

        # Exact codigo match wins outright
        if target_codigo and codigo and (target_codigo == codigo or target_codigo.replace("/", "-") == codigo.replace("/", "-")):
            return p

        slug_tokens = set(slug.split("-"))
        title_slug_tokens = set(_slugify(title_raw).split("-"))
        cand_tokens = slug_tokens | title_slug_tokens
        cand_tokens.discard("")

        if not target_tokens or not cand_tokens:
            continue
        inter = target_tokens & cand_tokens
        # Jaccard similarity-ish
        denom = len(target_tokens | cand_tokens)
        score = len(inter) / denom if denom else 0
        if score > best_score:
            best_score = score
            best = p

    if best and best_score >= 0.5:
        return best
    return None


def process_pt2030_item(item: dict, api_base: str) -> tuple[str, str, dict]:
    """Process a PT2030 family item.

    Returns (outcome, message, mutations) where outcome is one of:
      'ready', 'paa', 'fail', 'skip'.
    Mutations dict contains updates to merge into the item.
    """
    src_id = item["source_id"]
    item_id = item["id"]
    fallback_tried = list(item.get("fallback_tried", []))

    # Strategy: fetch full portal index, match by slug/codigo to get real WP post.
    # (The integer in regulation_url is garbled by the scanner, not a real WP id.)
    posts = fetch_portal_avisos(src_id, api_base)
    if not posts:
        return "fail", f"portal index vazio ({src_id})", {
            "download_error": f"portal index vazio para {src_id}",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    post = find_post_by_item(item, posts)
    fallback_tried.append("2b-pdf")
    if not post:
        return "fail", f"slug match nao encontrado em {src_id}", {
            "download_error": "slug match nao encontrado na API",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    acf = post.get("acf") or {}

    # Collect all candidate media IDs from ACF fields
    candidates_media: list[tuple[str, int]] = []
    primary_fields = ["pdf", "regulamento", "ficha_tecnica", "aviso_documento",
                      "documento_oficial", "programa_documento", "aviso"]
    for fname in primary_fields:
        v = acf.get(fname)
        if isinstance(v, int) and v > 0:
            candidates_media.append((fname, v))
        elif isinstance(v, str) and v.isdigit() and int(v) > 0:
            candidates_media.append((fname, int(v)))
        elif isinstance(v, str) and v.lower().endswith(".pdf") and v.startswith("http"):
            candidates_media.append((fname + ":url", -1))  # direct URL, handle below
            # store URL in a side-channel
            globals().setdefault("_DIRECT_URLS", {})[(item_id, fname)] = v

    # Array fields
    for fname in ["anexos", "documentos"]:
        v = acf.get(fname)
        if isinstance(v, list):
            for j, entry in enumerate(v):
                if isinstance(entry, int) and entry > 0:
                    candidates_media.append((f"{fname}[{j}]", entry))
                elif isinstance(entry, dict):
                    eid = entry.get("ID") or entry.get("id")
                    if isinstance(eid, int) and eid > 0:
                        candidates_media.append((f"{fname}[{j}]", eid))

    if not candidates_media:
        fallback_tried.append("2b-acf-all")
        return "fail", "ACF sem media candidates", {
            "download_error": "ACF sem pdf/anexos",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    # Resolve API base for media
    media_base = api_base.rsplit("/", 1)[0] + "/media"
    pdf_dir = REG_DIR / src_id
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"{item_id}.pdf"
    txt_path = pdf_dir / f"{item_id}.txt"

    last_error = ""
    best_text = ""
    best_field = ""
    best_url = ""

    for fname, media_id in candidates_media:
        if media_id == -1:
            # Direct URL
            direct = globals().get("_DIRECT_URLS", {}).get((item_id, fname.split(":")[0]))
            if not direct:
                continue
            pdf_url = direct
        else:
            mcode, mbody = curl_get(f"{media_base}/{media_id}")
            if mcode != 200 or not mbody:
                last_error = f"media {media_id} HTTP {mcode}"
                continue
            try:
                media = json.loads(mbody.decode("utf-8", errors="ignore"))
            except Exception:
                last_error = f"media {media_id} JSON parse"
                continue
            pdf_url = media.get("source_url") or ""
            if not pdf_url:
                last_error = f"media {media_id} sem source_url"
                continue

        dcode, dsize = curl_download(pdf_url, pdf_path)
        if dcode != 200 or dsize < 1000:
            last_error = f"download {pdf_url} HTTP {dcode} size={dsize}"
            continue

        if not pdftotext(pdf_path, txt_path):
            last_error = f"pdftotext falhou em {pdf_url}"
            continue

        text = read_text(txt_path)
        if not text.strip():
            last_error = "txt vazio apos pdftotext"
            continue

        # Pick the candidate with the most words (heuristic: real regulamento > resumo)
        wc = word_count(text)
        if wc > word_count(best_text):
            best_text = text
            best_field = fname
            best_url = pdf_url
            # Keep this pdf/txt as winner
            # Save copies to disk under canonical name (already there)

    if not best_text:
        fallback_tried.append("2b-acf-all")
        if pdf_path.exists():
            pdf_path.unlink(missing_ok=True)
        if txt_path.exists():
            txt_path.unlink(missing_ok=True)
        return "fail", last_error or "todos candidates falharam", {
            "download_error": last_error or "ACF candidates falharam",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    # We need to make sure the saved pdf/txt corresponds to best candidate.
    # Re-download winner to be safe (only if we have URL):
    if best_url:
        curl_download(best_url, pdf_path)
        pdftotext(pdf_path, txt_path)

    text = read_text(txt_path)

    # TESTE A: PAA check
    if is_paa(text):
        pdf_path.unlink(missing_ok=True)
        txt_path.unlink(missing_ok=True)
        fallback_tried.append("2b-pdf")
        return "paa", f"PAA detected (campo={best_field})", {
            "fallback_tried": fallback_tried,
            "fallback_field": best_field,
        }

    wc = word_count(text)

    # TESTE B: size + keywords
    has_kw = ("despesas eleg" in text.lower()) or ("criterios de selec" in text.lower()) or ("critérios de selec" in text.lower())
    if wc < 800 and not has_kw:
        pdf_path.unlink(missing_ok=True)
        txt_path.unlink(missing_ok=True)
        return "fail", f"conteudo insuficiente ({wc} palavras, sem keywords)", {
            "download_error": "Resumo sem regulamento completo",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
            "fallback_field": best_field,
        }

    # SUCCESS - mark verified
    return "ready", f"ok ({wc} palavras, campo={best_field})", {
        "regulation_local": f"regulamentos/{src_id}/{item_id}.txt",
        "status": "ready",
        "fail_count": 0,
        "download_error": None,
        "fallback_tried": fallback_tried,
        "fallback_field": best_field,
        "data_status": "verified",
    }


def process_horizon_item(item: dict) -> tuple[str, str, dict]:
    """Horizon Europe via eu-funding-tenders topicDetails JSON API."""
    src_id = item["source_id"]
    item_id = item["id"]
    fallback_tried = list(item.get("fallback_tried", []))
    aviso_codigo = item.get("aviso_codigo") or item.get("codigo") or item_id

    topic = aviso_codigo.lower().replace("/", "-")
    api_url = f"https://ec.europa.eu/info/funding-tenders/opportunities/data/topicDetails/{topic}.json"
    fallback_tried.append("2b-horizon")

    code, body = curl_get(api_url, timeout=45)
    if code != 200 or not body:
        return "fail", f"horizon API HTTP {code}", {
            "download_error": f"horizon API HTTP {code}",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }
    try:
        data = json.loads(body.decode("utf-8", errors="ignore"))
    except Exception:
        return "fail", "horizon JSON parse error", {
            "download_error": "horizon JSON parse",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    # Topic data is nested
    td = data.get("TopicDetails") or data
    fields = []
    for k in ("title", "callIdentifier", "topicTitle", "topicIdentifier"):
        v = td.get(k)
        if v:
            fields.append(f"{k}: {v}")

    desc = td.get("description") or td.get("descriptionByte") or ""
    if isinstance(desc, dict):
        desc = desc.get("html", "") or desc.get("text", "") or ""
    if isinstance(desc, str):
        # Strip HTML tags
        plain = re.sub(r"<[^>]+>", " ", desc)
        plain = re.sub(r"\s+", " ", plain).strip()
        fields.append(f"description:\n{plain}")

    for k in ("conditions", "keywords", "actions", "budgetOverviewInEur",
              "deadlineDate", "deadlineModelText"):
        v = td.get(k)
        if v:
            if isinstance(v, (dict, list)):
                fields.append(f"{k}: {json.dumps(v, ensure_ascii=False)[:800]}")
            else:
                fields.append(f"{k}: {v}")

    txt = "\n\n".join(fields).strip()
    if word_count(txt) < 300:
        return "fail", f"horizon conteudo curto ({word_count(txt)})", {
            "download_error": "horizon JSON com pouco conteudo",
            "fail_count": item.get("fail_count", 0) + 1,
            "last_fail_date": TODAY,
            "fallback_tried": fallback_tried,
        }

    pdf_dir = REG_DIR / src_id
    pdf_dir.mkdir(parents=True, exist_ok=True)
    txt_path = pdf_dir / f"{item_id}.txt"
    txt_path.write_text(txt, encoding="utf-8")

    # Horizon Europe is not PAA. TESTE A irrelevant in practice; we still check.
    if is_paa(txt):
        txt_path.unlink(missing_ok=True)
        return "paa", "horizon flagged PAA (improbable)", {"fallback_tried": fallback_tried}

    return "ready", f"horizon ok ({word_count(txt)} palavras)", {
        "regulation_local": f"regulamentos/{src_id}/{item_id}.txt",
        "status": "ready",
        "fail_count": 0,
        "download_error": None,
        "fallback_tried": fallback_tried,
        "data_status": "verified",
    }


def move_to_paa_watchlist(item: dict) -> None:
    paa = load_json(QUEUE_PAA)
    paa_q = paa.setdefault("queue", [])
    item_id = item["id"]

    # Find existing
    existing = None
    for it in paa_q:
        if it.get("id") == item_id:
            existing = it
            break

    if existing:
        existing["plano_anual_checks"] = int(existing.get("plano_anual_checks", 0)) + 1
        existing["plano_anual_last_check"] = TODAY
    else:
        new_item = dict(item)
        new_item["status"] = "plano_anual"
        new_item["download_error"] = "Plano Anual - não e aviso publicado, apenas previsao"
        new_item["plano_anual_detected_date"] = TODAY
        new_item["plano_anual_checks"] = 1
        paa_q.append(new_item)

    paa["_updated"] = TODAY
    save_json(QUEUE_PAA, paa)


def main() -> int:
    sources_api = load_sources_api()
    aviso = load_json(QUEUE_AVISO)
    catalogo = load_json(QUEUE_CATALOGO)

    # Build pool
    pool: list[tuple[str, dict]] = []
    for it in aviso.get("queue", []):
        if it.get("regulation_local"):
            continue
        if it.get("status") in ("ready", "abandoned"):
            continue
        if not it.get("regulation_url"):
            continue
        if it.get("fail_count", 0) >= 3:
            continue
        pool.append(("aviso", it))
    for it in catalogo.get("queue", []):
        if it.get("regulation_local"):
            continue
        if it.get("status") in ("ready", "abandoned"):
            continue
        if not it.get("regulation_url"):
            continue
        if it.get("fail_count", 0) >= 3:
            continue
        pool.append(("catalogo", it))

    pool.sort(key=lambda x: x[1].get("priority_score", 0), reverse=True)
    pool = pool[:MAX_DOWNLOADS]

    print(f"Pool size: {len(pool)}")
    counters = {"ready": 0, "paa": 0, "fail": 0, "skip": 0}
    aviso_ready = 0
    catalogo_ready = 0
    paa_moved = 0
    abandoned = 0

    aviso_by_id = {it["id"]: it for it in aviso.get("queue", [])}
    catalogo_by_id = {it["id"]: it for it in catalogo.get("queue", [])}

    items_to_remove_from_aviso: list[str] = []

    for origin, item in pool:
        src_id = item["source_id"]
        item_id = item["id"]
        print(f"\n=== [{origin}] {item_id} (src={src_id}, score={item.get('priority_score',0)}) ===")

        if origin == "aviso" and src_id in PT2030_FAMILY:
            api_base = sources_api.get(src_id)
            if not api_base:
                print(f"  SKIP: sem api_url para {src_id}")
                counters["skip"] += 1
                continue
            outcome, msg, mut = process_pt2030_item(item, api_base)
        elif origin == "aviso" and src_id == "eu-funding-tenders":
            outcome, msg, mut = process_horizon_item(item)
        else:
            print(f"  SKIP: fluxo nao implementado nesta run (src={src_id})")
            counters["skip"] += 1
            continue

        print(f"  -> {outcome}: {msg}")
        counters[outcome] = counters.get(outcome, 0) + 1

        # Apply mutations
        target = aviso_by_id if origin == "aviso" else catalogo_by_id
        if item_id in target:
            for k, v in mut.items():
                if v is None and k in target[item_id]:
                    target[item_id].pop(k, None)
                else:
                    target[item_id][k] = v

        if outcome == "paa":
            # Move to watchlist + remove from aviso queue
            move_to_paa_watchlist(target[item_id])
            items_to_remove_from_aviso.append(item_id)
            paa_moved += 1
        elif outcome == "ready":
            if origin == "aviso":
                aviso_ready += 1
            else:
                catalogo_ready += 1

        # Check if reached fail_count >= 3 (mark abandoned only after webSearch fallback,
        # which we don't perform here. We just leave at fail_count=3+, future run will handle.)

    # Remove PAA items from aviso queue
    if items_to_remove_from_aviso:
        aviso["queue"] = [it for it in aviso["queue"] if it["id"] not in items_to_remove_from_aviso]

    # Persist
    aviso["_updated"] = TODAY
    catalogo["_updated"] = TODAY
    save_json(QUEUE_AVISO, aviso)
    save_json(QUEUE_CATALOGO, catalogo)

    print("\n=== RESUMO ===")
    print(f"Aviso ready:    {aviso_ready}")
    print(f"Catálogo ready: {catalogo_ready}")
    print(f"PAA watchlisted:{paa_moved}")
    print(f"Falhas:         {counters.get('fail',0)}")
    print(f"Skipped:        {counters.get('skip',0)}")
    print(f"Abandoned:      {abandoned}")

    # For commit message
    print(f"\nCOMMIT_MSG=downloader: {aviso_ready} aviso ready, {catalogo_ready} catálogo ready, {paa_moved} PAAs watchlisted, {counters.get('fail',0)} falhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
