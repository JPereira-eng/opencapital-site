#!/usr/bin/env python3
"""Add setores field to each instrument in instruments-catalog.json.

Maps each instrument id to one or more sector codes based on beneficiary→sector logic.
Sectors: agroalimentar, comercio, economia-criativa, energia-ambiente, industria,
mar-pescas, mobilidade-transportes, saude-ciencias-vida, tecnologia-digital, turismo.
Plus special value: todos (transversal instruments that match any sector filter).
"""
import json
import sys
from pathlib import Path

# Mapping: instrument id -> list of sector codes
SETORES_MAP = {
    "step-inovacao-produtiva-digital-biotecnologia": ["tecnologia-digital", "saude-ciencias-vida"],
    "step-inovacao-produtiva-energia": ["energia-ambiente", "industria"],
    "step-idi-empresarial-energia": ["energia-ambiente"],
    "step-idi-empresarial-digital-biotecnologia": ["tecnologia-digital", "saude-ciencias-vida"],
    "eic-accelerator-2026": ["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"],
    "step-scale-up-eic": ["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"],
    "siac-digitalizacao-transformacao-digital": ["todos"],
    "sitce-descarbonizacao-eficiencia-energetica": ["industria", "energia-ambiente"],
    "siac-acoes-coletivas-internacionalizacao": ["todos"],
    "eic-pathfinder-2026": ["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"],
    "eic-transition-2026": ["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"],
    "sice-internacionalizacao-pme": ["todos"],
    "siid-internacionalizacao-id-horizonte-europa": ["tecnologia-digital", "saude-ciencias-vida", "energia-ambiente"],
    "norte2030-siid-vinnovate": ["industria", "tecnologia-digital"],
    "horizon-cl4-2026-data-ai": ["tecnologia-digital"],
    "horizon-hlth-2026-healthcare": ["saude-ciencias-vida"],
    "cef-digital-2026-cabo-submarino": ["tecnologia-digital"],
    "horizon-cl6-2026-02": ["agroalimentar", "energia-ambiente"],
    "lisboa2030-2026-step-fase2": ["tecnologia-digital", "saude-ciencias-vida"],
    "centro2030-2026-5-step": ["tecnologia-digital"],
    "norte2030-2026-2-ferrovia-linha-vouga": ["mobilidade-transportes"],
    "horizon-widera-twinning-2026": ["todos"],
    "horizon-cl4-2026-espaco": ["tecnologia-digital"],
    "norte2030-infraestruturas-acolhimento-empresarial": ["todos"],
    "linha-garantia-bpf-investeu-pme": ["todos"],
    "turismo-acolhe-2026": ["turismo"],
    "iefp-estagios-iniciar-2026": ["todos"],
    "iefp-estagios-mais-talento-2026": ["todos"],
    "programa-consolidar-bpf": ["todos"],
    "horizon-cl4-2026-01-materiais-producao": ["industria"],
    "horizon-raise-2026-01-ia-ciencia": ["tecnologia-digital"],
    "prima-2026-seccao-2": ["agroalimentar", "energia-ambiente"],
    "sifide-ii-candidaturas-2025": ["todos"],
    "sustentavel-2030-pacs-2026-04": ["mobilidade-transportes"],
    "sustentavel-2030-pacs-2026-03": ["mobilidade-transportes"],
    "sustentavel-2030-pacs-2025-16": ["mobilidade-transportes"],
    "apoio-organizacoes-sociedade-civil-migrantes-pessoas2030": ["todos"],
    "estagios-alma-pessoas2030": ["todos"],
    "sustentavel-2030-pacs-2025-15": ["mobilidade-transportes"],
    "madeira2030-2026-13-internacionalizacao-pme": ["todos"],
    "mar2030-2026-10-madeira-custos-suplementares": ["mar-pescas"],
    "sustentavel-2030-pacs-2026-06": ["mobilidade-transportes"],
    "sustentavel-2030-pacs-2026-05": ["mobilidade-transportes", "energia-ambiente"],
    "sustentavel-2030-pacs-2025-10": ["mobilidade-transportes"],
    "sustentavel-2030-pacs-2026-02": ["energia-ambiente"],
    "cef-dig-2026-smart-cables": ["tecnologia-digital"],
    "horizon-cl6-2026-01-zeropollution": ["mar-pescas", "energia-ambiente"],
    "deep2start-ani-2025-01": ["tecnologia-digital"],
    "sustentavel-2030-pacs-2026-07": ["energia-ambiente"],
    "sustentavel-2030-pacs-2026-8": ["energia-ambiente"],
    "urbact-iv-action-networks-2026": ["todos"],
    "alentejo2030-ciclo-urbano-agua-2026": ["energia-ambiente"],
    "rede-fornecedores-inovadores": ["todos"],
    "horizon-cid-2026-01-clean-industrial-deal": ["industria", "energia-ambiente"],
    "digital-2026-bestuse-10": ["tecnologia-digital", "saude-ciencias-vida"],
    "sustentavel-2030-pacs-2025-14": ["energia-ambiente"],
    "prr-doenca-mental-rncci-2026": ["saude-ciencias-vida"],
    "prr-habitacao-c02-i01-2026": ["todos"],
    "prr-flexibilidade-rede-2026": ["energia-ambiente"],
    "eit-food-fan-2026": ["agroalimentar"],
    "open-horizons-call-3-startups-mulheres": ["tecnologia-digital"],
    "inclusao-pela-cultura-juntas-freguesia-alentejo": ["economia-criativa"],
    "apoio-capacitacao-entidades-emprego-alentejo": ["todos"],
    "respostas-sociais-proximidade-2-aviso-acores": ["todos"],
    "cursos-profissionais-2-aviso-acores": ["todos"],
    "eurostars-call-11-setembro-2026": ["todos"],
    "emfaf-2026-pia-msp": ["mar-pescas"],
    "innovation-fund-2025-net-zero": ["energia-ambiente", "industria", "mobilidade-transportes"],
    "eit-health-innovation-validation-2026": ["saude-ciencias-vida"],
    "eit-urban-mobility-strategic-innovation-2026": ["mobilidade-transportes"],
    "eit-urban-mobility-financial-support-startups-2026": ["mobilidade-transportes"],
    "climatelaunchpad-2026": ["energia-ambiente"],
    "esa-bic-centro-plus-2026": ["tecnologia-digital"],
    "esa-bic-tagus-plus-2026": ["tecnologia-digital"],
    "gulbenkian-apoio-internacionalizacao-2026": ["economia-criativa"],
    "infraestruturas-e-equipamentos-tecnologicos-step": ["tecnologia-digital", "saude-ciencias-vida"],
    "formacao-continua-de-docentes-formadores-e-outros-agentes-de-educacao-": ["todos"],
    "sistema-de-incentivos-de-base-territorial-iti-cim-regiao-do-oeste-indu": ["industria"],
    "sistema-de-incentivos-de-base-territorial-it-cim-terras-de-tras-os-mon": ["todos"],
    "sistema-de-incentivos-de-base-territorial-it-cim-ave": ["todos"],
    "step-i-d-i-empresarial-energia": ["energia-ambiente"],
    "programa-apoio-crescer-com-o-turismo": ["turismo"],
    "protecao-civil-e-gestao-integrada-de-riscos-prevencao-e-mitigacao-de-r": ["energia-ambiente"],
    "tratamento-em-estacoes-de-tratamento-de-aguas-residuais-etar-para-prod": ["energia-ambiente"],
    "acoes-para-mitigacao-da-situacao-de-escassez-hidrica-e-assegurar-a-res": ["energia-ambiente"],
    "aguas-residuais-em-alta": ["energia-ambiente"],
    "programa-de-seguranca-ferroviaria-supressao-de-pns": ["mobilidade-transportes"],
    "abastecimento-de-agua-em-alta": ["energia-ambiente"],
    "linha-norte-estacao-do-oriente-terminal-tecnico": ["mobilidade-transportes"],
    "ampliacao-e-modernizacao-do-aeroporto-das-lajes": ["mobilidade-transportes"],
    "infraestrutura-ferroviaria-rte-programa-de-sinalizacao-e-implementacao": ["mobilidade-transportes"],
    "infraestrutura-portuaria-rte-porto-de-lisboa-3-aviso-navegabilidade-do": ["mobilidade-transportes"],
    "aquisicao-de-equipamentos-e-intervencao-em-infraestruturas-portuarias-": ["mobilidade-transportes"],
    "estagios-profissionais": ["todos"],
    "cursos-profissionais-entidades-privadas": ["todos"],
    "linha-apoio-qualificacao-oferta-2026": ["turismo"],
    "linha-bpf-investeu-mobilidade-urbana-sustentavel": ["mobilidade-transportes"],
    "linha-bpf-investeu-id-digitalizacao": ["todos"],
    "linha-bpf-invest-export": ["todos"],
    "ewa-advance-programme-2026": ["agroalimentar"],
    "risingfoodstars-2026": ["agroalimentar"],
    "new-models-deliver-healthcare-eit-2026": ["saude-ciencias-vida"],
    "ignite-neb-open-call-hosts-2026": ["economia-criativa"],
    "eit-jumpstarter-2026": ["todos"],
    "neb-mentors-open-call-2026": ["economia-criativa"],
    "fct-computacao-avancada-a0-a1-lote-d-2026": ["tecnologia-digital"],
    "fct-computacao-avancada-a2-a3-lote-d-2026": ["tecnologia-digital"],
    "scaleup-promotion-initiative-eit-2026": ["mobilidade-transportes"],
    "portugal-events-2026-2028": ["turismo"],
}


def main():
    catalog_path = Path(__file__).parent.parent / "instruments-catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    instruments = data["instruments"]
    missing = []
    updated = 0
    for item in instruments:
        iid = item["id"]
        if iid not in SETORES_MAP:
            missing.append(iid)
            continue
        item["setores"] = SETORES_MAP[iid]
        updated += 1

    if missing:
        print(f"ERRO: ids sem mapeamento ({len(missing)}):", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)

    # Count sectors
    counts = {}
    for item in instruments:
        for s in item.get("setores", []):
            counts[s] = counts.get(s, 0) + 1

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"OK: {updated}/{len(instruments)} instrumentos atualizados.")
    print("Distribuicao por setor:")
    for s in sorted(counts.keys()):
        print(f"  {s}: {counts[s]}")


if __name__ == "__main__":
    main()
