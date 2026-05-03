"""
Refinamento da tag id-ciencia: remove tag em instrumentos onde "inovacao"
foi capturada retoricamente mas o instrumento e claramente de outra natureza
(formacao, cidadania, cultura, acao social, cooperacao territorial).

Regras de remocao:
1. id-ciencia so e removida se o instrumento tem >= 1 outra tag (nunca deixar instrumento sem tags)
2. Programas claramente NAO-I&D (lista RHETORICAL_PROGRAMS abaixo) perdem id-ciencia
3. Instrumentos cujo titulo NAO contem keywords I&D fortes mas tem id-ciencia + 2+ outras tags fortes - remover id-ciencia (sinal de that ela foi adicionada por "inova" rhetorico)
"""
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
CATALOG = ROOT / "instruments-catalog.json"

PILOT_IDS = {
    "sifide-ii-candidaturas-2025",
    "iefp-estagios-iniciar-2026",
    "eic-accelerator-2026",
}

# Programas onde "inovacao" e retorico, NAO I&D
# Match no slug (id) do instrumento.
RHETORICAL_SLUG_PATTERNS = [
    r"^erasmus[- ]",         # Erasmus mobility/training
    r"^cerv[- ]",             # Citizenship, Equality, Rights, Values
    r"^crea[- ]media",        # Creative Europe MEDIA (audiovisual)
    r"^crea[- ]cult",         # Creative Europe Culture
    r"^esc[- ]",              # European Solidarity Corps
    r"^socpl[- ]",            # Social Policy
    r"^urbact[- ]",           # Urban cooperation
    r"^poctep[- ]",           # Territorial cooperation
    r"^ucpm[- ]",             # Civil Protection
    r"^smp[- ]cons",          # Single Market Programme - Consumers
    r"^smp[- ]stand",         # Standardisation
    r"^agrip[- ]",            # Agri promotion
    r"^pepac[- ]",            # CAP (agriculture)
    r"^mar2030[- ]",          # Mar 2030 (fisheries compensation/infra)
    r"^estagios[- ]",         # IEFP/Pessoas estagios
    r"^cursos[- ]",           # Cursos profissionais
    r"^euaf[- ]",             # EU Anti-Fraud
    r"^eutf[- ]",             # EU Trust Funds
    r"^europeaid",            # EuropeAid programs
    r"^ep[- ]linc",           # EP-LINC training
    r"^pessoas2030[- ]",      # PT2030 social fund
    r"^pessoas[- ]2030",
    r"^aviso[- ]pessoas",
    r"^apoio[- ]organizacoes",
    r"^apoio[- ]capacitacao",
    r"^cef[- ]",              # CEF Connecting Europe (infrastructure)
    r"^edf[- ]",              # European Defence Fund (military, but I&D component varies)
    r"^life[- ]",             # LIFE programme (environment)
    r"^sustentavel[- ]2030",  # PT2030 environmental
    r"^aguas[- ]",
    r"^abastecimento[- ]",
    r"^acoes[- ]para[- ]minimizar",
    r"^acoes[- ]para[- ]mitigacao",
    r"^ampliacao[- ]e[- ]modernizacao",
    r"^aquisicao[- ]de[- ]equipamentos",
    r"^programa[- ]seguranca[- ]ferroviaria",
    r"^sibt[- ]",             # SIBT (territorial investment)
    r"^iti[- ]cim",
    r"^sistema[- ]de[- ]incentivos[- ]de[- ]base[- ]territorial",
]

# Keywords no titulo que indicam I&D GENUINO
# Se o titulo tem alguma destas, a tag id-ciencia FICA mesmo que o slug seja rhetorical
GENUINE_RD_KEYWORDS = [
    r"\b(I&D|I&D&I|R&D|RTD)\b",
    r"\binvestiga(c|ç)(a|ã)o\b",
    r"\bresearch\b",
    r"\bSIFIDE\b",
    r"\beic[- ](pathfinder|accelerator|transition|scale)",
    r"\bdoutoramento\b",
    r"\bp(o|ó)s[- ]doc",
    r"\blaborator",
    r"\bbreakthrough\b",
    r"\bdisruptive\b",
    r"\bdeep[- ]?tech",
    r"\beurostars\b",
    r"\bhorizon[- ]europe\b",
    r"\bhorizonte europa\b",
    r"\bhorizon[- ]hlth",
    r"\bhorizon[- ]cl",
    r"\bclinical trial",
    r"\bpiloting\b",
    r"\bproof of concept\b",
    r"\bbiotechnology\b",
    r"\bbiotec",
    r"\bquantum\b",
    r"\bquantic",
]


def is_rhetorical_program(slug):
    for pattern in RHETORICAL_SLUG_PATTERNS:
        if re.search(pattern, slug, flags=re.IGNORECASE):
            return True
    return False


def has_genuine_rd_signal(title, tagline):
    text = f"{title} {tagline}".lower()
    for pattern in GENUINE_RD_KEYWORDS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["instruments"]
    stats = Counter()
    removed_examples = []

    for item in items:
        if item.get("id") in PILOT_IDS:
            stats["pilot_skipped"] += 1
            continue

        tags = item.get("necessidades", [])
        if "id-ciencia" not in tags:
            stats["no_id_ciencia"] += 1
            continue

        # Se id-ciencia e a unica tag, manter sempre
        if len(tags) == 1:
            stats["kept_only_tag"] += 1
            continue

        slug = item.get("id", "")
        title = item.get("title", "")
        tagline = item.get("tagline", "")

        is_rhetoric = is_rhetorical_program(slug)
        has_real_rd = has_genuine_rd_signal(title, tagline)

        # Remover se: programa retorico E sem sinal genuino de I&D
        if is_rhetoric and not has_real_rd:
            new_tags = [t for t in tags if t != "id-ciencia"]
            item["necessidades"] = new_tags
            stats["removed"] += 1
            if len(removed_examples) < 15:
                removed_examples.append({
                    "id": slug,
                    "title": title[:70],
                    "old_tags": tags,
                    "new_tags": new_tags,
                })
        else:
            stats["kept"] += 1

    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nStats:", dict(stats))
    print("\nExemplos de remocao:")
    for ex in removed_examples:
        print(f"  {ex['id']}")
        print(f"    {ex['title']}")
        print(f"    {ex['old_tags']} -> {ex['new_tags']}")

    # Tag distribution apos refino
    tag_counter = Counter()
    for item in items:
        for t in item.get("necessidades", []):
            tag_counter[t] += 1
    print("\nDistribuicao apos refino:")
    for tag, count in tag_counter.most_common():
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
