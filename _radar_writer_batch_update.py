"""
Helper para o radar-writer: atualiza catalogo + queue + shard + lookup + integrity + index
para cada artigo do batch e cria commit individual.
Apos correr: deve fazer git push manualmente.
"""
import json, os, hashlib, subprocess, sys
from datetime import date

REPO = r"C:/Users/jmcpe/Desktop/opencapital-site"
TODAY = date.today().isoformat()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest(), os.path.getsize(path)


def remove_from_queue(queue_path, slug):
    data = load_json(queue_path)
    queue = data.get("queue", [])
    new_queue = [i for i in queue if i.get("id") != slug]
    removed = len(queue) - len(new_queue)
    data["queue"] = new_queue
    data["updated"] = TODAY
    save_json(queue_path, data)
    return removed


def add_to_catalog(catalog_path, entry):
    cat = load_json(catalog_path)
    instruments = cat.get("instruments", [])
    # Remove duplicates first
    instruments = [i for i in instruments if i.get("id") != entry["id"]]
    instruments.append(entry)
    cat["instruments"] = instruments
    save_json(catalog_path, cat)


def add_to_shard(shard_path, slug, source_id, state, file_path):
    data = load_json(shard_path)
    items = data.get("items", [])
    items = [i for i in items if i.get("id") != slug]
    items.append({
        "id": slug,
        "file": file_path,
        "source": source_id,
        "state": state,
        "last_check": TODAY
    })
    data["items"] = items
    # Bump counters
    if "count" in data and isinstance(data["count"], int):
        data["count"] += 1
    else:
        data["count"] = data.get("count", 0) + 1
    if "published" in data:
        data["published"] = data.get("published", 0) + 1
    else:
        data["published"] = 1
    if state == "aberto":
        data["open"] = data.get("open", 0) + 1
    elif state == "fechado":
        data["closed"] = data.get("closed", 0) + 1
    elif state == "previsto":
        data["planned"] = data.get("planned", 0) + 1
    save_json(shard_path, data)


def add_to_lookup(lookup_path, slug, aviso_codigo=None):
    data = load_json(lookup_path)
    by_id = data.get("by_id", {})
    by_id[slug] = True
    data["by_id"] = by_id
    if aviso_codigo:
        by_av = data.get("by_aviso_codigo", {})
        by_av[aviso_codigo] = slug
        data["by_aviso_codigo"] = by_av
    data["updated"] = TODAY
    save_json(lookup_path, data)


def add_to_integrity(integrity_path, slug, source_id, regulation_path):
    if not os.path.exists(regulation_path):
        return False
    sha1, sz = sha1_file(regulation_path)
    data = load_json(integrity_path)
    fname = os.path.basename(regulation_path)
    if "entries" in data:
        target = data["entries"]
    else:
        target = data
    target[slug] = {
        "sha1": sha1,
        "checked": TODAY,
        "size": sz,
        "source_dir": source_id,
        "file": fname,
    }
    save_json(integrity_path, data)
    return True


def update_index(index_path, state, shard):
    idx = load_json(index_path)
    totals = idx.get("totals", {})
    totals["published"] = totals.get("published", 0) + 1
    totals["in_queue"] = max(0, totals.get("in_queue", 0) - 1)
    if state == "aberto":
        totals["open"] = totals.get("open", 0) + 1
    elif state == "fechado":
        totals["closed"] = totals.get("closed", 0) + 1
    elif state == "previsto":
        totals["planned"] = totals.get("planned", 0) + 1
    idx["totals"] = totals
    # shard counters mirror
    shards = idx.get("shards", {})
    sh = shards.get(shard, {})
    sh["count"] = sh.get("count", 0) + 1
    sh["published"] = sh.get("published", 0) + 1
    if state == "aberto":
        sh["open"] = sh.get("open", 0) + 1
    elif state == "fechado":
        sh["closed"] = sh.get("closed", 0) + 1
    elif state == "previsto":
        sh["planned"] = sh.get("planned", 0) + 1
    sh["updated"] = TODAY
    shards[shard] = sh
    idx["shards"] = shards
    if "_meta" in idx:
        idx["_meta"]["updated"] = TODAY
    idx["last_writer_run"] = TODAY
    save_json(index_path, idx)


def commit_article(slug, instrument_name):
    """git add the slug folder + catalog + registry, then commit."""
    paths = [
        f"instrumentos/{slug}/index.html",
        "instruments-catalog.json",
        "registry/queue.json",
        "registry/lookup.json",
        "registry/integrity.json",
        "registry/index.json",
    ]
    # Find shard files (any modified)
    paths.append("registry/shards/")
    cmd = ["git", "-C", REPO, "add"] + paths
    subprocess.run(cmd, check=True)
    msg = f"instrumento: {instrument_name}"
    subprocess.run(
        ["git", "-C", REPO, "commit", "-m", msg],
        check=True
    )


def process_one(article):
    slug = article["slug"]
    print(f"\n=== {slug} ===")
    # 1. Catalog entry
    add_to_catalog(REPO + "/instruments-catalog.json", article["catalog"])
    print(f"  + catalog entry")
    # 2. Remove from queue
    removed = remove_from_queue(REPO + "/registry/queue.json", slug)
    print(f"  - queue ({removed} removed)")
    # 3. Add to shard
    shard_path = REPO + f"/registry/shards/{article['shard']}.json"
    add_to_shard(shard_path, slug, article["source_id"], article["state"], f"instrumentos/{slug}/index.html")
    print(f"  + shard {article['shard']}")
    # 4. Add to lookup
    add_to_lookup(REPO + "/registry/lookup.json", slug, article.get("aviso_codigo"))
    print(f"  + lookup")
    # 5. Add to integrity if regulation exists
    reg_path = article.get("regulation_path")
    if reg_path and os.path.exists(reg_path):
        ok = add_to_integrity(REPO + "/registry/integrity.json", slug, article["source_id"], reg_path)
        print(f"  + integrity (sha1 ok)" if ok else f"  ! integrity skipped")
    else:
        print(f"  ~ integrity skipped (no regulation)")
    # 6. Update index
    update_index(REPO + "/registry/index.json", article["state"], article["shard"])
    print(f"  + index totals + shard counters")
    # 7. Commit
    commit_article(slug, article["instrument_name"])
    print(f"  [OK] committed")


# ======= BATCH DEFINITION =======
ARTICLES = [
    {
        "slug": "capacitacao-para-a-inclusao-pessoas-2030",
        "instrument_name": "Capacitação para a Inclusão (PESSOAS 2030)",
        "shard": "pt2030-pessoas",
        "source_id": "pessoas-2030",
        "aviso_codigo": "FA0742/2024",
        "state": "fechado",
        "regulation_path": REPO + "/regulamentos/pessoas-2030/capacitacao-para-a-inclusao-pessoas-2030.txt",
        "catalog": {
            "id": "capacitacao-para-a-inclusao-pessoas-2030",
            "category": "nr",
            "category_label": "Não Reembolsável",
            "estado": "fechado",
            "status_text": "Fechado (30/04/2026)",
            "status_class": "status-closed",
            "fonte": "pt2030",
            "beneficiario": "entidade-pública,associacao",
            "setores": ["todos"],
            "necessidades": ["impacto-social-inclusao", "formação-qualificação"],
            "regiao": "norte,centro,alentejo",
            "title": "Capacitação para a Inclusão (PESSOAS 2030)",
            "tagline": "Concurso FSE+ do PESSOAS 2030 com 12,25M EUR a 85% para entidades públicas e privadas que capacitem grupos vulneráveis no Norte, Centro e Alentejo.",
            "highlight0": "12,25M EUR FSE+ a 85% de cofinanciamento",
            "highlight1": "Entidades públicas e privadas (modalidade individual)",
            "highlight2": "Norte, Centro, Alentejo",
            "href": "instrumentos/capacitacao-para-a-inclusao-pessoas-2030/",
            "featured": False,
        },
    },
    {
        "slug": "acoes-mercado-social-emprego-pessoas2030",
        "instrument_name": "Ações do Mercado Social de Emprego (PESSOAS 2030)",
        "shard": "pt2030-pessoas",
        "source_id": "pessoas-2030",
        "aviso_codigo": "FA0770/2024",
        "state": "fechado",
        "regulation_path": REPO + "/regulamentos/pessoas-2030/acoes-mercado-social-emprego-pessoas2030.txt",
        "catalog": {
            "id": "acoes-mercado-social-emprego-pessoas2030",
            "category": "nr",
            "category_label": "Não Reembolsável",
            "estado": "fechado",
            "status_text": "Fechado (30/04/2026)",
            "status_class": "status-closed",
            "fonte": "pt2030",
            "beneficiario": "entidade-pública",
            "setores": ["todos"],
            "necessidades": ["impacto-social-inclusao", "contratacao-rh"],
            "regiao": "norte,centro,alentejo",
            "title": "Ações do Mercado Social de Emprego (PESSOAS 2030)",
            "tagline": "Convite do PESSOAS 2030 com 31,45M EUR FSE+ a 85% para entidades públicas que ativam grupos vulneráveis no mercado de trabalho do Norte, Centro e Alentejo.",
            "highlight0": "31,45M EUR FSE+ a 85% (regime convite)",
            "highlight1": "Entidades públicas (modalidade individual)",
            "highlight2": "Norte, Centro, Alentejo",
            "href": "instrumentos/acoes-mercado-social-emprego-pessoas2030/",
            "featured": False,
        },
    },
    {
        "slug": "insercao-socioprofissional-cigana-pessoas2030",
        "instrument_name": "Inserção Socioprofissional da Comunidade Cigana (PESSOAS 2030)",
        "shard": "pt2030-pessoas",
        "source_id": "pessoas-2030",
        "aviso_codigo": "FA0453/2023",
        "state": "fechado",
        "regulation_path": REPO + "/regulamentos/pessoas-2030/insercao-socioprofissional-cigana-pessoas2030.txt",
        "catalog": {
            "id": "insercao-socioprofissional-cigana-pessoas2030",
            "category": "nr",
            "category_label": "Não Reembolsável",
            "estado": "fechado",
            "status_text": "Fechado (30/04/2026)",
            "status_class": "status-closed",
            "fonte": "pt2030",
            "beneficiario": "entidade-pública,associacao",
            "setores": ["todos"],
            "necessidades": ["impacto-social-inclusao", "contratacao-rh"],
            "regiao": "norte,centro,alentejo",
            "title": "Inserção Socioprofissional da Comunidade Cigana",
            "tagline": "Concurso FSE+ do PESSOAS 2030 com 3M EUR a 85% para integrar membros da comunidade cigana no mercado de trabalho do Norte, Centro e Alentejo.",
            "highlight0": "3M EUR FSE+ a 85% para integração socioprofissional",
            "highlight1": "Entidades públicas e privadas (modalidade individual)",
            "highlight2": "Norte, Centro, Alentejo",
            "href": "instrumentos/insercao-socioprofissional-cigana-pessoas2030/",
            "featured": False,
        },
    },
    {
        "slug": "acoes-plano-envelhecimento-ativo-saudavel-longevidade",
        "instrument_name": "Envelhecimento Ativo, Saudável e Longevidade (PESSOAS 2030)",
        "shard": "pt2030-pessoas",
        "source_id": "pessoas-2030",
        "aviso_codigo": "FA0441/2023",
        "state": "fechado",
        "regulation_path": REPO + "/regulamentos/pessoas-2030/acoes-plano-envelhecimento-ativo-saudavel-longevidade.txt",
        "catalog": {
            "id": "acoes-plano-envelhecimento-ativo-saudavel-longevidade",
            "category": "nr",
            "category_label": "Não Reembolsável",
            "estado": "fechado",
            "status_text": "Fechado (30/04/2026)",
            "status_class": "status-closed",
            "fonte": "pt2030",
            "beneficiario": "entidade-pública,associacao",
            "setores": ["saude-ciencias-vida"],
            "necessidades": ["impacto-social-inclusao"],
            "regiao": "norte,centro,alentejo",
            "title": "Envelhecimento Ativo, Saudável e Longevidade",
            "tagline": "Concurso FSE+ do PESSOAS 2030 com 7M EUR a 85% para entidades públicas e privadas que executem ações no quadro do Plano Nacional para o Envelhecimento Ativo.",
            "highlight0": "7M EUR FSE+ a 85% para envelhecimento ativo",
            "highlight1": "Entidades públicas e privadas (modalidade individual)",
            "highlight2": "Norte, Centro, Alentejo",
            "href": "instrumentos/acoes-plano-envelhecimento-ativo-saudavel-longevidade/",
            "featured": False,
        },
    },
    {
        "slug": "horizon-miss-2027-02",
        "instrument_name": "Horizonte Europa Missão Cancro: Investigação Clínica em CCI",
        "shard": "eu-horizon",
        "source_id": "eu-funding-tenders",
        "aviso_codigo": "HORIZON-MISS-2027-02-CANCER-02",
        "state": "previsto",
        "regulation_path": REPO + "/regulamentos/eu-funding-tenders/horizon-miss-2027-02.txt",
        "catalog": {
            "id": "horizon-miss-2027-02",
            "category": "nr",
            "category_label": "Não Reembolsável",
            "estado": "previsto",
            "status_text": "Previsto (call 2027)",
            "status_class": "status-planned",
            "fonte": "ue",
            "beneficiario": "ensino-investigação,entidade-pública",
            "setores": ["saude-ciencias-vida"],
            "necessidades": ["id-ciencia", "internacionalização"],
            "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
            "title": "Horizonte Europa Missão Cancro: Investigação Clínica em CCI",
            "tagline": "Tópico HORIZON-MISS-2027-02-CANCER-02 da Missão Cancro: lump sum grant para consórcios europeus que conduzam investigação clínica em cancro do pulmão, mama, próstata e colorretal.",
            "highlight0": "HORIZON Lump Sum Grant para consórcios multinacionais",
            "highlight1": "CCI europeias (mín. 4 países, 1 com CCI subdesenvolvida)",
            "highlight2": "União Europeia e países associados",
            "href": "instrumentos/horizon-miss-2027-02/",
            "featured": False,
        },
    },
]


def main():
    for article in ARTICLES:
        process_one(article)
    print("\n=== BATCH COMPLETO ===")


if __name__ == "__main__":
    main()
