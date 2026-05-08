"""Atualiza catálogo, queues, shards, lookup e index após o batch radar-writer."""
import json
from pathlib import Path

REPO = Path("C:/Users/jmcpe/Desktop/opencapital-site")
TODAY = "2026-05-06"

# 5 artigos criados neste batch
new_entries = [
    {
        "id": "edf-2026-ls-da-sme-nt",
        "category": "nr",
        "category_label": "Nao Reembolsavel",
        "estado": "aberto",
        "status_text": "Aberto ate 29 setembro 2026",
        "status_class": "status-open",
        "fonte": "ue",
        "beneficiario": "empresa",
        "setores": ["industria", "tecnologia-digital"],
        "necessidades": ["id-ciencia", "investimento-produtivo"],
        "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
        "title": "EDF-2026-LS-DA-SME-NT: Acoes de desenvolvimento nao tematicas para PME",
        "tagline": "Topico do Fundo Europeu de Defesa que aloca 30 milhoes de euros a consorcios liderados por PME para amadurecer produtos e tecnologias de defesa em qualquer area de interesse, com gestao da Agencia Europeia de Defesa.",
        "highlight0": "30 ME em lump sum, ate 6 ME por proposta",
        "highlight1": "PME europeias coordenadoras com tecnologia em TRL 4+",
        "highlight2": "Estados-Membros UE e paises associados ao EDF",
        "href": "instrumentos/edf-2026-ls-da-sme-nt.html",
        "featured": False,
        "shard": "eu-other",
        "source": "eu-funding-tenders",
        "aviso_codigo": "EDF-2026-LS-DA-SME-NT",
    },
    {
        "id": "edf-2026-ra-air-a4r",
        "category": "nr",
        "category_label": "Nao Reembolsavel",
        "estado": "aberto",
        "status_text": "Aberto ate 29 setembro 2026",
        "status_class": "status-open",
        "fonte": "ue",
        "beneficiario": "empresa,ensino-investigacao",
        "setores": ["tecnologia-digital", "mobilidade-transportes"],
        "necessidades": ["id-ciencia", "digitalizacao-ia"],
        "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
        "title": "EDF-2026-RA-AIR-A4R: Reabastecimento aereo autonomo e automatico",
        "tagline": "Topico de investigacao do Fundo Europeu de Defesa que aloca 20 milhoes de euros para desenvolver sensores, fusao de dados e algoritmos que permitam reabastecimento ar-ar sem intervencao humana, incluindo aeronaves nao tripuladas.",
        "highlight0": "20 ME em research action a custo real",
        "highlight1": "Primes aeroespaciais, centros de investigacao, empresas de IA aplicada",
        "highlight2": "Estados-Membros UE e paises associados ao EDF",
        "href": "instrumentos/edf-2026-ra-air-a4r.html",
        "featured": False,
        "shard": "eu-other",
        "source": "eu-funding-tenders",
        "aviso_codigo": "EDF-2026-RA-AIR-A4R",
    },
    {
        "id": "edf-2026-ls-dis-nt",
        "category": "nr",
        "category_label": "Nao Reembolsavel",
        "estado": "aberto",
        "status_text": "Aberto ate 29 setembro 2026",
        "status_class": "status-open",
        "fonte": "ue",
        "beneficiario": "empresa,ensino-investigacao",
        "setores": ["tecnologia-digital", "industria", "energia-ambiente", "saude-ciencias-vida"],
        "necessidades": ["id-ciencia", "capitalizacao-crescimento"],
        "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
        "title": "EDF-2026-LS-DIS-NT: Tecnologias disruptivas nao tematicas para defesa",
        "tagline": "Topico do Fundo Europeu de Defesa que aloca 27 milhoes de euros a tecnologias disruptivas em qualquer area de interesse para defesa, com tetos de 3 milhoes por proposta e duracao tipica de 12 a 24 meses.",
        "highlight0": "27 ME em lump sum 100%, ate 3 ME por proposta",
        "highlight1": "Empresas e centros com tecnologia disruptiva (TRL 4+)",
        "highlight2": "Estados-Membros UE e paises associados ao EDF",
        "href": "instrumentos/edf-2026-ls-dis-nt.html",
        "featured": False,
        "shard": "eu-other",
        "source": "eu-funding-tenders",
        "aviso_codigo": "EDF-2026-LS-DIS-NT",
    },
    {
        "id": "edf-2026-ls-dis-ra-smero-nt",
        "category": "nr",
        "category_label": "Nao Reembolsavel",
        "estado": "aberto",
        "status_text": "Aberto ate 29 setembro 2026",
        "status_class": "status-open",
        "fonte": "ue",
        "beneficiario": "empresa,ensino-investigacao",
        "setores": ["tecnologia-digital", "industria", "energia-ambiente", "saude-ciencias-vida"],
        "necessidades": ["id-ciencia", "arranque-validacao", "capitalizacao-crescimento"],
        "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
        "title": "EDF-2026-LS-DIS-RA-SMERO-NT: Investigacao disruptiva conduzida por PME e centros de investigacao",
        "tagline": "Topico EDF de 35 milhoes de euros para PME (coordenador) e organizacoes de investigacao que conduzem investigacao em tecnologias disruptivas para defesa, com lump sum a 100% e business coaching incluido.",
        "highlight0": "35 ME em lump sum 100%, business coaching incluido",
        "highlight1": "PME tecnologicas coordenadoras + centros de investigacao",
        "highlight2": "Estados-Membros UE e paises associados ao EDF",
        "href": "instrumentos/edf-2026-ls-dis-ra-smero-nt.html",
        "featured": False,
        "shard": "eu-other",
        "source": "eu-funding-tenders",
        "aviso_codigo": "EDF-2026-LS-DIS-RA-SMERO-NT",
    },
    {
        "id": "kibo-ventures",
        "category": "priv",
        "category_label": "Investimento Privado",
        "estado": "aberto",
        "status_text": "Ativo",
        "status_class": "status-cont",
        "fonte": "pventures",
        "beneficiario": "empresa,empreendedor",
        "setores": ["tecnologia-digital"],
        "necessidades": ["arranque-validacao", "capitalizacao-crescimento"],
        "regiao": "norte,centro,lisboa,alentejo,algarve,acores,madeira",
        "title": "Kibo Ventures",
        "tagline": "Plataforma espanhola de venture capital fundada em 2012 com mais de 500 milhoes de euros sob gestao em 6 fundos, 81 empresas investidas e 22 saidas, focada em tech europeu de seed a Series B.",
        "highlight0": "AUM > 500 ME, 81 investimentos, 22 exits (incl. IPO Nasdaq)",
        "highlight1": "Founders europeus em fintech, IA, deep tech, gaming, logistica",
        "highlight2": "Espanha e Europa",
        "href": "instrumentos/kibo-ventures.html",
        "featured": False,
        "shard": "catalogo-vc",
        "source": "kibo-ventures",
        "aviso_codigo": None,
        "from_catalogo": True,
    },
]

# 1. Atualizar instruments-catalog.json
catalog_path = REPO / "instruments-catalog.json"
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
existing_ids = {it["id"] for it in catalog["instruments"]}
for entry in new_entries:
    if entry["id"] in existing_ids:
        print(f"SKIP catalog (existe): {entry['id']}")
        continue
    catalog["instruments"].append({k: v for k, v in entry.items() if k not in ("shard", "source", "aviso_codigo", "from_catalogo")})
catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"catalog: {len(catalog['instruments'])} entries")

# 2. Remover dos queue files
queue_path = REPO / "registry" / "queue.json"
queue = json.loads(queue_path.read_text(encoding="utf-8"))
ids_aviso = {e["id"] for e in new_entries if not e.get("from_catalogo")}
queue["queue"] = [it for it in queue["queue"] if it.get("id") not in ids_aviso]
queue["updated"] = TODAY
queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"queue.json: {len(queue['queue'])} restantes")

queue_cat_path = REPO / "registry" / "queue-catalogo.json"
queue_cat = json.loads(queue_cat_path.read_text(encoding="utf-8"))
ids_cat = {e["id"] for e in new_entries if e.get("from_catalogo")}
queue_cat["queue"] = [it for it in queue_cat["queue"] if it.get("id") not in ids_cat]
queue_cat_path.write_text(json.dumps(queue_cat, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"queue-catalogo.json: {len(queue_cat['queue'])} restantes")

# 3. Adicionar aos shards
shards_dir = REPO / "registry" / "shards"
for entry in new_entries:
    shard_path = shards_dir / f"{entry['shard']}.json"
    shard = json.loads(shard_path.read_text(encoding="utf-8"))
    items = shard.get("items", [])
    if any(i.get("id") == entry["id"] for i in items):
        print(f"SKIP shard (existe): {entry['id']}")
        continue
    items.append({
        "id": entry["id"],
        "file": entry["href"],
        "source": entry["source"],
        "state": entry["estado"],
        "last_check": TODAY,
    })
    shard["items"] = items
    shard_path.write_text(json.dumps(shard, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"shard {entry['shard']}: +{entry['id']} ({len(items)} items)")

# 4. Atualizar lookup
lookup_path = REPO / "registry" / "lookup.json"
lookup = json.loads(lookup_path.read_text(encoding="utf-8"))
for entry in new_entries:
    lookup.setdefault("by_id", {})[entry["id"]] = True
    if entry.get("aviso_codigo"):
        lookup.setdefault("by_aviso_codigo", {})[entry["aviso_codigo"]] = entry["id"]
lookup_path.write_text(json.dumps(lookup, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"lookup: by_id={len(lookup['by_id'])}, by_aviso_codigo={len(lookup['by_aviso_codigo'])}")

# 5. Atualizar index
index_path = REPO / "registry" / "index.json"
index = json.loads(index_path.read_text(encoding="utf-8"))
n = len(new_entries)
n_aviso = sum(1 for e in new_entries if not e.get("from_catalogo"))
n_cat = n - n_aviso
n_open = sum(1 for e in new_entries if e["estado"] == "aberto")
index["totals"]["published"] = index["totals"].get("published", 0) + n
index["totals"]["in_queue"] = index["totals"].get("in_queue", 0) - n_aviso
index["totals"]["in_catalogo"] = max(0, index["totals"].get("in_catalogo", 0) - n_cat)
index["totals"]["open"] = index["totals"].get("open", 0) + n_open
index["last_writer_run"] = TODAY
index["_meta"]["last_writer_run"] = TODAY

# Bump shard counters
for entry in new_entries:
    sh = index["shards"].setdefault(entry["shard"], {})
    sh["count"] = sh.get("count", 0) + 1
    if entry["estado"] == "aberto":
        sh["open"] = sh.get("open", 0) + 1
    sh["published"] = sh.get("published", 0) + 1

index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"index: published={index['totals']['published']}, in_queue={index['totals']['in_queue']}, in_catalogo={index['totals']['in_catalogo']}")

print("DONE")
