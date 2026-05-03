"""
Correcoes manuais a tagging de instrumentos estrategicos onde a heuristica
errou. Cada correcao e justificada e referenciada ao instrumento concreto.

Aplicar com sed/JSON modification em vez de regex pattern matching, porque
sao casos especificos identificados manualmente.
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
CATALOG = ROOT / "instruments-catalog.json"

# Correcoes manuais. Formato: id -> (necessidades_corretas, justificacao)
CORRECTIONS = {
    "sifide-2026": (
        ["id-ciencia"],
        "SIFIDE e exclusivamente deducao fiscal de despesas I&D. Nao e investimento produtivo (e RFAI) nem credito.",
    ),
    "eic-transition-2026": (
        ["id-ciencia", "arranque-validacao"],
        "EIC Transition apoia maturacao de tecnologia (prova de conceito a producto), tem componente I&D forte.",
    ),
    "norte2030-siid-vinnovate": (
        ["id-ciencia", "investimento-produtivo"],
        "SIID = Sistema Incentivos I&D. Nucleo e I&D, com componente de investimento em demonstradores.",
    ),
    "eit-health-innovation-validation-2026": (
        ["id-ciencia", "arranque-validacao"],
        "EIT Health Innovation Validation transita prova-de-conceito academica para mercado.",
    ),
    "eit-urban-mobility-strategic-innovation-2026": (
        ["id-ciencia", "sustentabilidade-energia-clima", "arranque-validacao"],
        "EIT KIC programs financiam scale-up de startups; componente arranque essencial.",
    ),
    "horizon-eic-2026-bas-01-ecosystem": (
        ["id-ciencia", "premios-visibilidade"],
        "EIC ecosystem support nao e investimento produtivo, e infraestrutura de inovacao.",
    ),
    "eit-food-fan-2026": (
        ["arranque-validacao", "id-ciencia"],
        "EIT Food FAN e programa de aceleracao de startups agroalimentares; remover premios-visibilidade que nao e o core.",
    ),
    "eit-jumpstarter-2026": (
        ["arranque-validacao", "id-ciencia"],
        "EIT Jumpstarter foca em ideacao + I&D; remover premios-visibilidade (e secundario).",
    ),
    "eit-urban-mobility-financial-support-startups-2026": (
        ["arranque-validacao", "capitalizacao-crescimento"],
        "Financial support a startups inclui capitalizacao, nao so arranque.",
    ),
    "scaleup-promotion-initiative-eit-2026": (
        ["arranque-validacao", "capitalizacao-crescimento", "internacionalizacao"],
        "Scale-up promotion europeia inclui acesso a mercados internacionais.",
    ),
    "horizon-eic-2026-bas-02-scaleup": (
        ["arranque-validacao", "capitalizacao-crescimento", "id-ciencia"],
        "Scale-up requer capitalizacao, nao apenas digitalizacao.",
    ),
    "venture-incubation-program-eit-2026": (
        ["arranque-validacao", "id-ciencia"],
        "Programa de incubacao foca arranque e I&D; remover premios-visibilidade e digitalizacao genericos.",
    ),
    "horizon-eic-2026-pathfinderopen": (
        ["id-ciencia", "arranque-validacao"],
        "Pathfinder e exploratorio early-stage; tem componente arranque alem de I&D.",
    ),
    "eic-pathfinder-2026": (
        ["id-ciencia", "arranque-validacao"],
        "Pathfinder consolidar como I&D + arranque (remover digitalizacao-ia que e dimensao secundaria).",
    ),
    "eit-health-htds-2026": (
        ["id-ciencia", "arranque-validacao"],
        "Health Technology Days Showcase: I&D em saude com escala startup.",
    ),
    "horizon-eic-2026-accelerator-01": (
        ["arranque-validacao", "id-ciencia", "capitalizacao-crescimento"],
        "EIC Accelerator equivalente: 3 tags core. Remover digitalizacao-ia que e tematica especifica do call.",
    ),
    "horizon-eic-2026-bas-02": (
        ["arranque-validacao", "id-ciencia", "capitalizacao-crescimento"],
        "Business Acceleration Service scale-up: 3 tags core. Digitalizacao-ia e tematica, nao tag necessidade.",
    ),
    "new-models-deliver-healthcare-eit-2026": (
        ["id-ciencia", "impacto-social-inclusao", "arranque-validacao"],
        "Modelos de healthcare delivery exigem inovacao + impacto social + componente startup (EIT KIC).",
    ),
}


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["instruments"]
    by_id = {i["id"]: i for i in items}

    applied = []
    not_found = []

    for fix_id, (new_tags, why) in CORRECTIONS.items():
        if fix_id not in by_id:
            not_found.append(fix_id)
            continue
        item = by_id[fix_id]
        old_tags = item.get("necessidades", [])
        if old_tags == new_tags:
            continue
        item["necessidades"] = new_tags
        applied.append({
            "id": fix_id,
            "old": old_tags,
            "new": new_tags,
            "why": why,
        })

    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{len(applied)} correcoes aplicadas:\n")
    for a in applied:
        print(f"  {a['id']}")
        print(f"    {a['old']}")
        print(f"    -> {a['new']}")
        print(f"    why: {a['why']}")
        print()

    if not_found:
        print(f"NAO encontrados ({len(not_found)}): {not_found}")

    # Distribuicao final
    tag_counter = Counter()
    for item in items:
        for t in item.get("necessidades", []):
            tag_counter[t] += 1
    print("\nDistribuicao final:")
    for tag, count in tag_counter.most_common():
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
