"""
Backfill heuristico de necessidades[] para instruments-catalog.json.
Aplica regras de keywords (titulo + tagline) + defaults por fonte/categoria.
Output: JSON atualizado + relatorio backfill-review.md com casos de baixa confianca.
"""
import json
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
CATALOG = ROOT / "instruments-catalog.json"
REVIEW = ROOT / "scripts" / "backfill-review.md"

VALID_TAGS = [
    "arranque-validacao", "contratacao-rh", "formacao-qualificacao",
    "id-ciencia", "digitalizacao-ia", "investimento-produtivo",
    "capitalizacao-crescimento", "tesouraria-credito-garantias",
    "internacionalizacao", "sustentabilidade-energia-clima",
    "impacto-social-inclusao", "premios-visibilidade",
]

# IDs que ja foram etiquetados manualmente (pilotos) - nunca sobrescrever.
PILOT_IDS = {
    "sifide-ii-candidaturas-2025",
    "iefp-estagios-iniciar-2026",
    "eic-accelerator-2026",
}

# Cada regra produz (tag, weight). Sem trailing \b para apanhar plurais e variantes.
# Usar substring matching simples (lowercased text).
KEYWORD_RULES = [
    # arranque-validacao
    (r"\b(startup|start[- ]?up|spin[- ]?off|incuba|born from|prova de conceito|proof of concept|pre[- ]?seed|seed funding|transition 2026|eic transition|scaling[- ]?up|scale[- ]?up)", "arranque-validacao", 2),
    (r"\b(empreendedor|valida(c|ç)(a|ã)o de neg|cria(c|ç)(a|ã)o de empresa|early[- ]stage|early stage|aceleradora|accelerator program|spin out|make it with space|euspa|space entrepreneur)", "arranque-validacao", 2),
    # contratacao-rh
    (r"\b(est(a|á)gio|contrata(c|ç)(a|ã)o|emprego|posto[s]? de trabalho|labour market|employment|jovem[s]? t(e|é)cnico|recursos humanos|inser(c|ç)(a|ã)o (no )?mercado|primeiro emprego|cria(c|ç)(a|ã)o de emprego|job creation)", "contratacao-rh", 2),
    # formacao-qualificacao
    (r"\b(forma(c|ç)(a|ã)o|qualifica(c|ç)(a|ã)o|capacita(c|ç)(a|ã)o|upskilling|reskilling|training|aprendizagem|compet(e|ê)ncia|curso[s]?|skills development|formandos|estudante|aluno|escola[s]? profissional|tesp|t(e|é)cnicos superiores profissionais|mestrado|doutoramento|interpreta(c|ç)(a|ã)o de conferencias|erasmus|european youth|corpo europeu de solidariedade)", "formacao-qualificacao", 2),
    (r"\b(certifica(c|ç)(a|ã)o profissional|forma(c|ç)(a|ã)o profissional|aprendizagem ao longo|lifelong learning|cursos profissionais|cursos t(e|é)cnicos|ep linc|EP-LINC)", "formacao-qualificacao", 3),
    # id-ciencia
    (r"\b(I&D|I&D&I|investiga(c|ç)(a|ã)o|research|ci(e|ê)ncia|cient(i|í)fic|inova(c|ç)(a|ã)o|innovation|RTD|R&D|horizon|horizonte europa|HORIZON|eit health|htds|biotech|bioagrifood|efsa|modelos de dinamica populacional|population dynamic|biological model)", "id-ciencia", 2),
    (r"\b(SIFIDE|laborator|projeto[s]? de I&D|p(o|ó)s-doutoramento|doutoramento|bolsa[s]? de investiga|FCT|EIC pathfinder|breakthrough|disruptive technology|space programme|space program|euspa)", "id-ciencia", 3),
    # digitalizacao-ia
    (r"\b(digital|TIC|software|automa(c|ç)(a|ã)o|intelig(e|ê)ncia artificial|artificial intelligence| AI |IA aplicada|cybersec|cibersegur|cloud|big data|data[- ]driven|industry 4|ind(u|ú)stria 4)", "digitalizacao-ia", 2),
    (r"\b(transforma(c|ç)(a|ã)o digital|digital transformation|tecnologia[s]? digital|deep tech|deep-tech|tech2business|industria 4\.0|ind(u|ú)stria 4\.0)", "digitalizacao-ia", 3),
    # investimento-produtivo
    (r"\b(equipamento|instala(c|ç)(a|ã)o|instala(c|ç)(o|õ)es|infraestrutura|capacidade produtiva|produ(c|ç)(a|ã)o industrial|f(a|á)brica|unidade industrial|moderniza(c|ç)(a|ã)o|maquinaria|incentivo[s]? de base territorial|sistema de incentivos|aquisi(c|ç)(a|ã)o de equipamento|porturi|portuari|ferrovi|aeroport|estrada|rodoviari|ponte|terminal|pesca|aquicultura|porto[s]? de pesca|lota[s]?|abrigo[s]? de pesca|agricultur|agrari|agroindustri|pepac|defesa militar|uav|sistema de armas|naval|tanque)", "investimento-produtivo", 2),
    (r"\b(RFAI|inova(c|ç)(a|ã)o produtiva|investimento produtivo|ativos fixos|capex|sibt|iti cim|it cim|cim ave|cim douro|cim oeste|cim terras|reabilita(c|ç)(a|ã)o|mar2030|mar 2030|edf 2026|european defence fund|fundo europeu de defesa)", "investimento-produtivo", 3),
    # capitalizacao-crescimento
    (r"\b(equity|venture capital| VC |private equity| PE |business angel|angel|capital de risco|growth capital|scale[- ]?up|scaleup|capital semente|capitaliza(c|ç)(a|ã)o|reforco de capital|capitais pr(o|ó)prios|crowdfunding|investimento privado)", "capitalizacao-crescimento", 2),
    # tesouraria-credito-garantias
    (r"\b(linha de cr(e|é)dito|cr(e|é)dito|empr(e|é)stimo|garantia|garantia m(u|ú)tua|tesouraria|liquidez|working capital|capital de giro|fundo de maneio|guarantee|loan|financiamento corrente|InvestEU)", "tesouraria-credito-garantias", 2),
    # internacionalizacao
    (r"\b(internacionaliza(c|ç)(a|ã)o|exporta(c|ç)(a|ã)o|export|mercado[s]? externo|international cooperation|global market|miss(a|ã)o[s]? empresarial|feira[s]? internaciona|europeaid|africa partnership|cooperation framework|diaspora|euaf|eutf|external action|developing countries|paises terceiros|parceria global|trade promotion|agrip|promo(c|ç)(a|ã)o de produtos agricolas|sme market expansion|expansion 2026)", "internacionalizacao", 2),
    # sustentabilidade-energia-clima
    (r"\b(sustent|energia|renov(a|á)v|efici(e|ê)ncia energ(e|é)tica|descarboniza|carbon|net[- ]zero|verde|green deal|clima|climate|economia circular|circular economy|residuo|waste|biodiversid|emissoes|hidrog(e|é)nio|hydrogen|fotovoltaic|e(o|ó)lic|solar|ambiente|environmental|polui(c|ç)(a|ã)o|gas natural|gases|tratamento de aguas|saneamento|litoral|adaptacao climatica|escassez hidrica|aguas residuais|ciclo urbano|natureza|conservacao)", "sustentabilidade-energia-clima", 2),
    (r"\b(transi(c|ç)(a|ã)o energ(e|é)tica|transi(c|ç)(a|ã)o ecol(o|ó)gica|just transition|pacs|sustentavel 2030|sustentável 2030|life 2026|life programme|governanca ambiental|life sap)", "sustentabilidade-energia-clima", 3),
    # impacto-social-inclusao
    (r"\b(inclus(a|ã)o|inclusion|economia social|social economy|comunidad|vulner(a|á)v|igualdade|gender|sociedade civil|civil society|migrant|refugiado|refugee|direito[s]? humano|human rights|pobreza|poverty|sa(u|ú)de mental|doen(c|ç)a mental|cuidados continuad|rncci|habita(c|ç)(a|ã)o|saude|cuidados de saude|healthcare|integra(c|ç)(a|ã)o social|terceira idade|envelhe|igualdade de g(e|é)nero|deficiencia|deficiência|cidadania|democracia|memoria europeia|dialogo social|socpl|cerv|gemela(c|ç)(a|ã)o|participa(c|ç)(a|ã)o cidad|redes de municipios|protec(c|ç)(a|ã)o de dados|cultural|cultura|criativ|creative europe|europa criativa|festival|cinema|audiovisual|filme|tv e online|media[- ]program|crea media|crea cult|enredor|diaspora|new models to deliver healthcare|youth participation|cooperacao territorial|urbact|poctep|protec(c|ç)(a|ã)o civil|civil protection|ucpm|prevencao e preparacao|preparedness|emergency response|adr e entidades|acoes representativas|consumer protection|smp cons|kapp ex|kapp pvpp)", "impacto-social-inclusao", 2),
    # premios-visibilidade
    (r"\b(pr(e|é)mio|prize|award|reconhecimento|distin(c|ç)(a|ã)o|honorific|concurso de m(e|é)rito)", "premios-visibilidade", 3),
]

# Defaults por fonte (fallback quando keywords nao decidem)
FONTE_DEFAULTS = {
    "iefp": ["contratacao-rh", "formacao-qualificacao"],
    "fct": ["id-ciencia"],
    "ani": ["id-ciencia"],
    "pventures": ["arranque-validacao", "capitalizacao-crescimento"],
    "aicep": ["internacionalizacao"],
    "erc": ["id-ciencia"],
    "uptec-porto": ["arranque-validacao"],
    "instituto-pedro-nunes": ["arranque-validacao"],
    "ppl-crowdfunding": ["arranque-validacao", "capitalizacao-crescimento"],
    "pessoas-2030": ["contratacao-rh", "formacao-qualificacao"],
    "turismo-portugal": ["investimento-produtivo"],
    "turismo": ["investimento-produtivo"],
    "eit": ["arranque-validacao", "id-ciencia"],
    "compete": ["id-ciencia", "investimento-produtivo"],
    "norte-2030": ["investimento-produtivo"],
    "prr": ["investimento-produtivo"],
    "bfomento": ["tesouraria-credito-garantias"],
    "banco-fomento": ["tesouraria-credito-garantias"],
    "privado": ["capitalizacao-crescimento"],
    "priv": ["capitalizacao-crescimento"],
    "eu-funding-tenders": ["id-ciencia"],
}

# Defaults por categoria (ultimo recurso)
CATEGORY_DEFAULTS = {
    "priv": ["capitalizacao-crescimento"],
    "div": ["tesouraria-credito-garantias"],
    "fiscal": ["id-ciencia"],  # SIFIDE-like default
    "hib": ["arranque-validacao", "capitalizacao-crescimento"],
    "inv": ["investimento-produtivo"],
}


def score_tags(text):
    """Aplica todas as regras de keywords e devolve dict {tag: score}.
    Normaliza hifenes e underscores para espacos antes de aplicar regras."""
    normalized = text.lower().replace("-", " ").replace("_", " ")
    scores = Counter()
    for pattern, tag, weight in KEYWORD_RULES:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            scores[tag] += weight
    return scores


def decide_tags(item):
    """Devolve (tags, confidence, reason)."""
    text = f"{item.get('title','')} {item.get('tagline','')} {item.get('id','')}"
    scores = score_tags(text)
    fonte = item.get("fonte", "")
    category = item.get("category", "")

    # Top tags com score >= 2 (ja vem do peso minimo das regras)
    strong = [(tag, s) for tag, s in scores.most_common() if s >= 2]

    if len(strong) >= 1:
        # Pegar ate 3 tags fortes (com score >=2)
        tags = [t for t, _ in strong[:3]]
        # Confianca alta se 1-3 tags claras com top score >= 3 ou >= 2 tags strong
        top_score = strong[0][1]
        if top_score >= 3 or len(strong) >= 2:
            return tags, "high", f"keywords (top scores: {dict(strong[:3])})"
        else:
            return tags, "medium", f"keywords (single weak match: {dict(strong[:3])})"

    # Sem keywords claras -> fallback fonte
    if fonte in FONTE_DEFAULTS:
        return FONTE_DEFAULTS[fonte], "medium", f"fonte default ({fonte})"

    # Fallback categoria
    if category in CATEGORY_DEFAULTS:
        return CATEGORY_DEFAULTS[category], "low", f"categoria default ({category})"

    # Sem sinal -> review obrigatorio. Default conservador: capitalizacao-crescimento
    return ["capitalizacao-crescimento"], "low", "sem sinal claro (default conservador)"


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["instruments"]
    review_rows = []
    stats = Counter()

    for item in items:
        # Pilots: nunca sobrescrever
        if item.get("id") in PILOT_IDS:
            stats["pilot_kept"] += 1
            continue

        tags, confidence, reason = decide_tags(item)
        # Validate tags
        for t in tags:
            assert t in VALID_TAGS, f"Invalid tag: {t}"
        item["necessidades"] = tags
        stats[f"conf_{confidence}"] += 1

        if confidence != "high":
            review_rows.append({
                "id": item["id"],
                "title": item["title"],
                "fonte": item.get("fonte", ""),
                "category": item.get("category", ""),
                "tags": tags,
                "confidence": confidence,
                "reason": reason,
            })

    # Escrever JSON atualizado
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Escrever relatorio de revisao
    review_rows.sort(key=lambda r: (r["confidence"], r["fonte"]))
    with open(REVIEW, "w", encoding="utf-8") as f:
        f.write(f"# Backfill review report\n\n")
        f.write(f"Casos com confianca medium/low ({len(review_rows)} de {len(items)}):\n\n")
        f.write("| ID | Title | Fonte | Cat | Tags propostas | Confianca | Razao |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in review_rows:
            tags_str = ", ".join(r["tags"])
            f.write(f"| `{r['id']}` | {r['title'][:60]} | {r['fonte']} | {r['category']} | {tags_str} | **{r['confidence']}** | {r['reason']} |\n")

    print(f"\nStats: {dict(stats)}")
    print(f"Review report: {REVIEW}")
    print(f"Catalog updated: {CATALOG}")
    print(f"Tag distribution:")
    tag_counter = Counter()
    for item in items:
        for t in item.get("necessidades", []):
            tag_counter[t] += 1
    for tag, count in tag_counter.most_common():
        print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
