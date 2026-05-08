# -*- coding: utf-8 -*-
"""Adiciona entradas em queue.json (deadline-driven) e queue-catalogo.json (ongoing) para os itens do radar 06.05.2026."""
import json

TODAY = "2026-05-08"

# === DEADLINE-DRIVEN ITEMS (queue.json) ===
queue_items = [
    # MAY 2026 - HIGH URGENCY
    {
        "id": "mastercard-fintechs-2026",
        "name": "Mastercard For Fintechs 2026",
        "source_id": "mastercard-fintechs",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-11",
        "budget": "100.000 EUR (vencedor final, marketing support)",
        "regulation_url": "https://www.mastercard.com/europe/en/innovation/partner-with-us/mastercardforfintechs.html",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 115,
        "status": "ready",
        "notes": "3a edicao. Aberto a fintechs (pre-seed, seed, Series A) com solucoes operacionais em PT, ES, IT, FR, BE ou NL. Vencedor recebe 100K EUR em marketing support + acesso preferencial ao Start Path. Categorias: IA/Agent, Cripto, Pagamentos, Embedded Finance, SME B2B, Banking & Lending, Loyalty, HR Tech, Insurance."
    },
    {
        "id": "abanca-innova-vc-2026",
        "name": "ABANCA Innova - Venture Client Program (12a edicao)",
        "source_id": "abanca-innova",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-12",
        "budget": "Acesso a PoC com banco (sem financiamento direto)",
        "regulation_url": "https://abancainnova.com/programa-para-startups/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 110,
        "status": "ready",
        "notes": "12a edicao. Foco em IA, criptoativos e tokenizacao para o setor financeiro. Bootcamp 26.05-16.06. Aberto a startups com produto no mercado e equipa formada. Inclui workshops com equipas internas ABANCA + bootcamp para definir piloto."
    },
    {
        "id": "chips-venture-forum-2026",
        "name": "Chips Venture Forum 2026",
        "source_id": "chips-ju",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-12",
        "budget": "Acesso a 70+ jurados/investidores; expor no SEMICON Europa Munich (10-13 Nov 2026)",
        "regulation_url": "https://www.chips-ju.europa.eu/Events/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 110,
        "status": "ready",
        "notes": "Organizado por BLUMORPHO + EIC + aCCCess. Aberto a startups deep-tech de semicondutores. Candidatura via Chips Competence Centre local. 2 fases: Bordeaux (NPHO Venture Summit 21-22 Out) + Munich (SEMICON Europa Nov)."
    },
    {
        "id": "amcc-testbed-mediacall-2026",
        "name": "AMCC Test Bed - Open Media Call 2026",
        "source_id": "amcc-testbed",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-15",
        "budget": "Pilots no consortio AMCC + mentoria + aceleracao",
        "regulation_url": "https://testbed.a-mcc.eu/openmediacall/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 105,
        "status": "ready",
        "notes": "Test Bed AMCC (PCI + NOS + UA + Google) lanca Media Open Call para pilotagem e aceleracao de solucoes tecnologicas para o setor media. Aberto a startups e SMEs."
    },
    {
        "id": "aveiro-smart-connected-spaces-2026",
        "name": "Aveiro Smart Connected Spaces Test Bed - Open Call 2026",
        "source_id": "pci-aveiro",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-15",
        "budget": "Pilots no consortio (sem valor monetario direto - acesso a infraestrutura)",
        "regulation_url": "https://www.alticelabs.com/innovation/rdi-projects/testbed-aveiro-smart-connected-spaces/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 105,
        "status": "ready",
        "notes": "Consortio: PCI, Altice Labs, Porto de Aveiro, UA, IT, TICE, Ocean Forum. 59 pilotos previstos ate Set 2025. Foco em comunicacoes, sensing, IA. Aberto a SMEs e startups."
    },
    {
        "id": "tasmu-accelerator-2026",
        "name": "TASMU Accelerator Program 2026 (Qatar)",
        "source_id": "tasmu-qatar",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-15",
        "budget": "Top startups: 200.000 QAR (~55.000 USD) + acesso a 45+ VCs",
        "regulation_url": "https://accelerator.tasmu.gov.qa/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 105,
        "status": "ready",
        "notes": "Programa do Ministerio MCIT do Qatar. Foco em Health, Environment, Smart Cities, Transportation & Logistics. Zero equity. Portfolio total >4 mil milhoes QAR. Suportou 75 startups de 78 paises desde a fundacao."
    },
    {
        "id": "premio-cotec-internacionalizacao-2026",
        "name": "Premio Inovacao na Internacionalizacao 2026 (3a edicao) - COTEC/Santander",
        "source_id": "cotec-portugal",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-15",
        "budget": "Premio: experiencia F1 Tag Heuer Gran Premio de Espana 2026 (Madrid) + reconhecimento",
        "regulation_url": "https://pii.cotec.pt/",
        "pdf_url": "https://cotecportugal.pt/wp-content/uploads/2025/04/Regulamento-PII_25.pdf",
        "regulation_local": None,
        "priority_score": 105,
        "status": "ready",
        "notes": "3a edicao com novo modelo de avaliacao. Categorias por dimensao (Pequena, Media, MidCap) e geografia (Europa, Global). 3 finalistas por categoria. Indicadores: intensidade exportadora, crescimento internacional, I&D, produtividade, rentabilidade."
    },
    {
        "id": "eit-um-startup-creation-2026",
        "name": "EIT Urban Mobility - Startup Creation Program 2026",
        "source_id": "eit-urban-mobility",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-15",
        "budget": "10.000 EUR (top 2 equipas) + mentoria + Demo Day",
        "regulation_url": "https://www.bgi.pt/eit-urban-mobility/urban-mobility-startup-creation",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 105,
        "status": "ready",
        "notes": "Programa BGI co-financiado pela EIT Urban Mobility. Fase concept/prototype, equipas pre-incorporacao. Topicos: Urban Logistics, Electrification, Public Transport, Mobility Data, Health and Mobility. 100% online, gratuito."
    },
    {
        "id": "mentor-me-28digital-2026",
        "name": "Mentor Me Program 2026 - 28DIGITAL/EIT Digital",
        "source_id": "28digital",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-20",
        "budget": "33.000 EUR ou 3% equity (mentoria estruturada)",
        "regulation_url": "https://28digital.eu/mentor-me/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 100,
        "status": "ready",
        "notes": "Programa de mentoria 28DIGITAL/EIT Digital. Para startups angel/pre-seed digital e deep-tech com MVP. Tracks: Team dynamics, Product-market fit, Funding readiness, Sales & marketing. Junho batch deadline 20.05.2026."
    },
    {
        "id": "infineon-startup-challenge-2026",
        "name": "Infineon Startup Challenge 2026 - Humanoid Robotics",
        "source_id": "infineon-startup",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-27",
        "budget": "Acesso Silicon Saxony Days + coaching tecnico Infineon + Demo Day Graz + Munich pitch night",
        "regulation_url": "https://silicon-saxony.de/sisax-events/infineon-startup-challenge-2026-humanoid-robotics/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 95,
        "status": "ready",
        "notes": "Foco em 5 areas: Digital Twins, Artificial Skin & Hand, Environmental sensing (radar/laser), Visual feedback, Motor control. 24 startups pre-selecionadas para pitch publico (Silicon Saxony Days Dresden 17 Jun). Top 12 selecionadas para o programa. Demo day Graz 6 Out, pitch night Munich 22 Out."
    },
    {
        "id": "premio-maria-sousa-2026",
        "name": "Premio Maria de Sousa 2026 (6a edicao)",
        "source_id": "bial-fundacao",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-31",
        "budget": "Ate 5 premios de 30.000 EUR cada (total 150.000 EUR)",
        "regulation_url": "https://www.fundacaobial.com/pt-PT/premios/premio-maria-de-sousa",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 90,
        "status": "ready",
        "notes": "Promovido pela Fundacao BIAL e Ordem dos Medicos. Para investigadores portugueses ate 35 anos em ciencias da saude. Inclui estagio obrigatorio em centro internacional de excelencia. Candidatos podem residir em Portugal ou no estrangeiro."
    },
    {
        "id": "scale-her-2026",
        "name": "SCALE'HER 2026 - Acelerador EU para mulheres em deep tech",
        "source_id": "scale-her",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-31",
        "budget": "Programa 6 meses + 3 meses mentoria 1:1 (sem equity, online)",
        "regulation_url": "https://scale-her-project.eu/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 90,
        "status": "ready",
        "notes": "Programa EU para 60 startups lideradas por mulheres em digital e deep tech. 100% online. Workshops, panels, capital strategy. Cohort 2026."
    },
    # JUNE 2026
    {
        "id": "jarvis-open-call-2-2026",
        "name": "JARVIS Open Call 2 - Track 1 Co-development",
        "source_id": "jarvis-eu",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-01",
        "budget": "Track 1: ate 100.000 EUR/projeto (co-dev). Track 2: ate 130.000 EUR/projeto (external pilots, deadline 10.07).",
        "regulation_url": "https://jarvis-project.eu/open-calls/open-call-2/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 88,
        "status": "ready",
        "notes": "Cascade funding Horizon Europe. Foco: Human-Robot Interaction industrial. Track 1 (co-dev em testbeds JARVIS) deadline 01.06.2026; Track 2 (5 pilotos externos 10 meses) deadline 10.07.2026. Setores: aeronautica, automotive, decommissioning nuclear, offshore inspection, agile production."
    },
    {
        "id": "jewel-eurocluster-nzt-2026",
        "name": "JEWEL Eurocluster Open Call 1 - Net-Zero Tech Demo Projects",
        "source_id": "jewel-eurocluster",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-01",
        "budget": "Ate 54.000 EUR/projeto (max 90% intensidade). Total call: 540.000 EUR (~10 projetos).",
        "regulation_url": "https://www.clustercollaboration.eu/content/jewel-eurocluster-open-call-1-nzt-demo-projects",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 88,
        "status": "ready",
        "notes": "Eurocluster JEWEL para demo de tecnologias net-zero. Areas: baterias, hidrogenio (eletrolisadores, fuel cells), smart grid, renovaveis para industria. Ecossistemas: automotive, aeroespacial, defesa, energy-intensive. Consortio: 2+ SMEs de 2 regioes EU NUTS2. Duracao 9 meses."
    },
    {
        "id": "aiod-platform-oc-2026",
        "name": "AI on Demand Platform (AIoD) Open Call 1",
        "source_id": "aiod-platform",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-08",
        "budget": "AI Providers: ate 60.000 EUR (lump sum). AI Adopters: ate 15.000 EUR.",
        "regulation_url": "https://www.aiodp.ai/open_calls/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 80,
        "status": "ready",
        "notes": "Cascade funding Digital Europe. Aberto a SMEs e organizacoes de investigacao com produtos IA TRL 7+ em formato containerizado (Docker). 3 fases: Stage 1 (50 providers pitch), Stage 2 (20 integracao), Stage 3 (10 deployment). Programa: Set 2026 - Abr 2027."
    },
    {
        "id": "prize-energy-communities-governance-2026",
        "name": "Prize for Governance Innovations in Energy Communities 2026",
        "source_id": "horizonte-europa",
        "shard": "eu-horizon",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-25",
        "budget": "1.000.000 EUR total (ate 10 comunidades premiadas)",
        "regulation_url": "https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/prizes/prize-governance-innovations-energy-communities_en",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 70,
        "status": "ready",
        "notes": "Premio CE para reconhecer comunidades de energia (Renewable energy community ou Citizens energy community sob definicoes UE). Max 10.000 membros a 01.01.2026. Submissao via Funding & Tenders Portal. Periodo: 20 Jan - 25 Jun 2026."
    },
    {
        "id": "eawards-portugal-2026",
        "name": "eAwards Portugal 2026 - Fundacao NTT Data",
        "source_id": "nttdata-fundacao",
        "shard": "catalogo-premios",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-30",
        "budget": "Vencedor PT: 10.000 EUR + acesso a programa de aceleracao. Final internacional: 100.000 EUR.",
        "regulation_url": "https://globaleawards.com/pt/portugal/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 68,
        "status": "ready",
        "notes": "Final internacional realizada em Lisboa em Nov 2026. Areas: Saude, Educacao, Energia, Ambiente, Banca, Industria, Seguros, Seguranca. Para startups e projetos em fase avancada de prototipagem. Parceria com Unicorn Factory Lisboa."
    },
    {
        "id": "loreal-unesco-women-science-2027",
        "name": "Premios Internacionais L'Oreal-UNESCO For Women in Science 2027 (29a edicao)",
        "source_id": "loreal-unesco",
        "shard": "catalogo-premios",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-06-30",
        "budget": "5 premios x 100.000 EUR (Fisica, Matematica/Informatica, Quimica, Ciencias da Terra/Ambiente)",
        "regulation_url": "https://www.forwomeninscience.com/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 68,
        "status": "ready",
        "notes": "29a edicao. Processo por nomeacao - propostas submetidas digitalmente por cientistas eminentes (PhD min). Cerimonia: UNESCO Paris, Junho 2027. Selecao final: Dezembro 2026."
    },
    # LATER 2026
    {
        "id": "horizon-hop-on-facility-2026",
        "name": "Horizon Europe - Hop-On Facility 2026",
        "source_id": "horizonte-europa",
        "shard": "eu-horizon",
        "aviso_codigo": "HORIZON-WIDERA-2026-ACCESS-04",
        "detected_date": TODAY,
        "deadline": "2026-09-24",
        "budget": "30.000.000 EUR (orcamento indicativo total)",
        "regulation_url": "https://rea.ec.europa.eu/funding-and-grants/horizon-europe-widening-participation-and-spreading-excellence/hop-facility_en",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Permite a instituicoes de paises Widening (Portugal incluido) integrarem-se em projetos ja em curso sob Pilar 2 ou EIC Pathfinder. Top-up de tarefas/work packages. Aberto desde 13.01.2026."
    },
    {
        "id": "i3-instrument-strand1-2a-2026",
        "name": "I3 Instrument 2026 - Strand 1 & 2a (Investment calls)",
        "source_id": "eu-funding-tenders",
        "shard": "eu-other",
        "aviso_codigo": "I3-2026-INV1, I3-2026-INV2a",
        "detected_date": TODAY,
        "deadline": "2026-11-12",
        "budget": "Programa 2025-2027 total: 176.000.000 EUR (FEDER)",
        "regulation_url": "https://eismea.ec.europa.eu/programmes/interregional-innovation-investments-i3-instrument_en",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 40,
        "status": "ready",
        "notes": "I3 Instrument sob FEDER. Strand 1 e 2a (Investment): 13.05.2026 - 12.11.2026. Para projetos interregionais de inovacao em fase scale-up e comercializacao. Smart specialisation areas. Strand 2a inclui regioes menos desenvolvidas."
    },
    {
        "id": "euipo-sme-fund-2026",
        "name": "EUIPO SME Fund 2026 - Vouchers IP",
        "source_id": "euipo-sme-fund",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-12-04",
        "budget": "Voucher 1 (IP Scan): ate 1.260 EUR (90%). Voucher 2 (TM/Designs): ate 700 EUR (75%/50%). Voucher 3 (Patentes): ate 1.000 EUR nacional / 2.500 EUR EU. Voucher 4 (Plant Varieties).",
        "regulation_url": "https://www.euipo.europa.eu/en/sme-corner/sme-fund/2026",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 35,
        "status": "ready",
        "notes": "Programa EUIPO 2 Fev - 4 Dez 2026. Vouchers 1 e 2 ja esgotados (alta procura). Vouchers 3 (patentes) e 4 (plant varieties) ainda disponiveis. Reembolso ate 75% custos IP."
    },
    {
        "id": "linha-fomento-ific-mais-2026",
        "name": "Linha Fomento IFIC Mais - BPF",
        "source_id": "banco-fomento",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-12-31",
        "budget": "1.500.000.000 EUR (1,5 mil milhoes)",
        "regulation_url": "https://www.bpfomento.pt/pt/catalogo/linha-fomento-ific-mais/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 30,
        "status": "ready",
        "notes": "Linha do Banco Portugues de Fomento para financiamento de capitais alheios em projetos IFIC, PT2030 ou PRR. Cobre ate 50% capital alheio dos projetos. IFIC IA nas PME: ate 25% investimento. Outros: ate 50%."
    },
    # TEF-Health (deadline ongoing OC #2)
    {
        "id": "tef-health-oc-2026",
        "name": "TEF-Health - Open Call #2 (Subsidized Testing & Validation)",
        "source_id": "tef-health",
        "shard": "eu-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": "2026-05-29",
        "budget": "Servicos subsidiados de testes/validacao/certificacao (sem grant direto)",
        "regulation_url": "https://tefhealth.eu/call",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 95,
        "status": "ready",
        "notes": "Projeto Digital Europe Programme (5 anos desde 2023). Open Call #2 lancada Abril 2025. Acesso a centros de investigacao, universidades, hospitais europeus. Para SMEs em IA e robotica de saude. Evento: 9 Jun 2026 Berlim."
    },
]

# === ONGOING ITEMS (queue-catalogo.json) ===
catalogo_items = [
    # Recognition / Status
    {
        "id": "selo-id-ani-ongoing",
        "name": "Selo ID - Reconhecimento de Idoneidade I&D (ANI)",
        "source_id": "ani",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Reconhecimento (sem valor monetario direto). Habilita acesso a SIFIDE - recuperacao ate 82,5% do investimento I&D.",
        "regulation_url": "https://ani.pt/selo-id-reconhecimento-de-idoneidade-na-pratica-de-atividades-de-id/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 60,
        "status": "ready",
        "notes": "Selo emitido pela ANI, valido 12 anos. Submissao continua via plataforma SIFIDE. Atualizacao 2025: simplificacao para startups incubadas, reconhecimento condicional para empresas novas, eliminacao de revisoes externas."
    },
    {
        "id": "estatuto-startup-scaleup-portugal",
        "name": "Reconhecimento Estatuto de Startup e Scaleup (Lei 21/2023)",
        "source_id": "startup-portugal",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Reconhecimento (gratuito, valido 3 anos com renovacao automatica)",
        "regulation_url": "https://startupportugal.com/pt/estatuto-startup/",
        "pdf_url": "https://startupportugal.com/wp-content/uploads/2024/02/Manual-de-Procedimentos-Reconhecimento-do-Estatuto-de-Startup-e-Scale-Up.pdf",
        "regulation_local": None,
        "priority_score": 60,
        "status": "ready",
        "notes": "Lei 21/2023 + Portaria 401/2023. Decisao em 5 dias uteis. Beneficios: empreendedorismo, inovacao. Requisitos startup: <10 anos, <50M volume negocios, reconhecimento Tech Sector ou ANI, ronda VC ou investimento BPF. Scaleup: criterios de Tech Visa."
    },
    # Maturidade Digital INCM
    {
        "id": "selos-maturidade-digital-incm",
        "name": "Selos de Maturidade Digital (INCM)",
        "source_id": "incm-selos-digital",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "30.000.000 EUR (PRR componente 16) - certificacao de 15.000 entidades",
        "regulation_url": "https://selosmaturidadedigital.incm.pt/",
        "pdf_url": "https://files.incm.pt/SMD/PDF/RegulamentoMarca_SelosMaturidadeDigital.INCM.pdf",
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "Plano de Acao Transicao Digital (RCM 30/2020). Certificacao bronze/prata/ouro em 4 dimensoes: Sustentabilidade, Ciberseguranca, Privacidade, Acessibilidade. Financiado PRR Investimento TD-C16-i03."
    },
    # CTT 1520
    {
        "id": "ctt-1520-startup-program",
        "name": "CTT 1520 Startup Program",
        "source_id": "ctt-1520",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Open innovation (sem valor monetario direto, parcerias comerciais com CTT)",
        "regulation_url": "https://www.ctt.pt/grupo-ctt/a-empresa/inovacao-e-startups/1520-startup-program/index",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Programa de inovacao aberta dos CTT. Submissao continua via formulario online. Analise alinhamento com objetivos CTT, reunioes face-to-face. Parceria com Portugal Ventures (perks para startups participadas)."
    },
    # AWS Startup Loft
    {
        "id": "aws-startup-loft-emea",
        "name": "AWS Startup Loft Accelerator EMEA",
        "source_id": "aws-startup-loft",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "AWS Activate: ate 25.000 USD em creditos AWS + 5K Business Support + 80 self-paced labs",
        "regulation_url": "https://aws-startup-lofts.com/emea/program/accelerator",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Programa AWS de 10 semanas, equity-free, sem deadline (rolling). 4 pilares: Technology, Product, Go-to-market, Funding. Para startups EMEA early-stage com prototipo/PoC."
    },
    # CCC-Centro Cybersecurity
    {
        "id": "ccc-centro-ciberseguranca",
        "name": "Apoio em Ciberseguranca - CCC-Centro",
        "source_id": "ccc-centro",
        "shard": "pt-other",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Servicos gratuitos. Investimento aprovado: 1.146.872 EUR.",
        "regulation_url": "https://www.ccc-centro.pt/sobre-o-centro/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Centro de Competencias em Ciberseguranca da regiao Centro (NUT-II). Lidera UA + Politecnicos (Castelo Branco, Leiria, Tomar) + IT + TICE.PT + UBI. Apoia 387+ entidades regionais. Servicos gratuitos. Periodo: 01.03.2024 - 31.03.2026."
    },
    # VCs (Catalogo VC)
    {
        "id": "armilar-venture-partners-catalogo",
        "name": "Armilar Venture Partners",
        "source_id": "armilar-ventures",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets seed/early-stage. AUM 260M EUR. Latest fund: 120M EUR.",
        "regulation_url": "https://www.armilar.com/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "VC portuguesa fundada em 2000. Deep-tech, early-stage. Portfolio inclui OutSystems, Feedzai, Sword Health (3 unicornios, 1 IPO, 14 aquisicoes). Foco Iberia para seed; expandido para Europa/EUA em Series A+."
    },
    {
        "id": "fundo-nos-5g-armilar",
        "name": "Fundo NOS 5G (gerido pela Armilar)",
        "source_id": "armilar-ventures",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "10.000.000 EUR (fundo total)",
        "regulation_url": "https://www.nos.pt/pt/institucional/5g/fundo-nos-5g",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Lancado fim 2019 pela NOS, gerido pela Armilar Venture Partners. Areas: 5G, IoT, Data & Analytics, Cloud, VR/AR, Ciberseguranca. Portfolio ja inclui Coreflux, Reckon.ai, KIT-AR e outras."
    },
    {
        "id": "c2-capital-partners-catalogo",
        "name": "C2 Capital Partners",
        "source_id": "c2-capital",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets 0,5M-5M EUR. AUM 430M EUR.",
        "regulation_url": "https://c2capital.pt/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "PE/VC portuguesa desde 2009 (ex-Capital Criativo). Registada CMVM. Duas areas: Expansion Capital + Alternative Investments. Foco SMEs familiares + clean/renewable energy. Portfolio: Everbio, BRAINR, TUU."
    },
    {
        "id": "perseo-iberdrola-catalogo",
        "name": "PERSEO - Iberdrola International Startup Programme",
        "source_id": "perseo-iberdrola",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": ">200.000.000 EUR investidos no portfolio. PoCs/pilots + GET TechSeed Fund + Andromeda SustainableTech Fund.",
        "regulation_url": "https://www.iberdrola.com/about-us/our-innovation-model/international-startup-program-perseo",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Programa CVC Iberdrola desde 2008. Foco: energia, IA, digitalizacao, automacao, smart energy efficiency, EV charging, solar. IPOs: Wallbox e Stem (2021). Mais recente investimento: Barbara (Network Mgmt SW, Fev 2026)."
    },
    {
        "id": "sogrape-ventures-beta-capital",
        "name": "Sogrape Ventures (gerido por Beta Capital)",
        "source_id": "sogrape-ventures",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "5.000.000 EUR (CVC fund)",
        "regulation_url": "https://ventures.sogrape.com/pt",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "CVC Sogrape lancado fim 2023, gerido pela Beta Capital. Foco: precision viticulture, low-alcohol alternative beverages, tracability/authenticity, packaging, beverage AI/ML. Primeiro investimento: Candam Tech (1,1M EUR)."
    },
    {
        "id": "transatlantic-highway-ventures-catalogo",
        "name": "Transatlantic Highway Ventures",
        "source_id": "transatlantic-highway",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets 50.000-200.000 EUR (pre-seed)",
        "regulation_url": "https://www.thv.vc/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "Fundo VC para early-stage startups portuguesas a escalar para os EUA. Foco: agentic AI, AI infrastructure, B2B, vertical SaaS. Inclui apoio go-to-market e fundraising."
    },
    {
        "id": "trind-ventures-catalogo",
        "name": "Trind Ventures - Seed Stage Venture Fund",
        "source_id": "trind-ventures",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets 100.000 EUR-1M (seed). Follow-on ate 5M. Fund total: 55M EUR.",
        "regulation_url": "https://trind.vc/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "VC baseado em Tallinn (com escritorios Helsinki, Munich). Seed stage focado em startups europeias. Foco: B2C, C2C, marketplaces, ecommerce, consumer-component B2B PLG. Portfolio inclui Fractory, Ready Player Me."
    },
    {
        "id": "indico-founders-program-catalogo",
        "name": "Indico Founders Program (Indico Capital Partners)",
        "source_id": "indico-capital",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "100.000 EUR (investimento por startup, fund 125M)",
        "regulation_url": "https://www.indicocapital.com/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "Programa pre-seed de 12 meses (6 meses presencial Indico + Google for Startups). Tech, sustainability, ocean. Powered by Google for Startups. Setores Indico: Web3, SaaS, AI, IoT, Fintech, Cybersecurity (Pre-Seed a Series C)."
    },
    {
        "id": "lince-capital-catalogo",
        "name": "Lince Capital",
        "source_id": "lince-capital",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets 250.000 EUR-5M+ (Seed/late seed)",
        "regulation_url": "https://lince-capital.com/en/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "VC portuguesa desde 2016. Registada CMVM PT.135.267. Foco: digital health, healthtech, scalable software com expansao europeia. Portfolio: Sword Health, Feedzai, Bling (2 unicornios, 1 IPO). 52 investimentos."
    },
    {
        "id": "shilling-vc-catalogo",
        "name": "Shilling VC (Founders Fund + Opportunity Fund)",
        "source_id": "shilling-vc",
        "shard": "catalogo-vc",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Tickets 100.000 EUR-1M (Founders Fund pre-seed/seed). Opportunity Fund 50M EUR (Series A+). AUM 52M EUR.",
        "regulation_url": "https://www.shilling.vc/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 55,
        "status": "ready",
        "notes": "VC portuguesa desde 2011. Setores: fintech, healthcare, IA, consumer, biotech, commerce. Portfolio: Sword Health, Unbabel, Bizay, Uniplaces, Talka. 84 investimentos (11 nos ultimos 12 meses, Jan 2026)."
    },
    {
        "id": "daskapital-catalogo",
        "name": "Daskapital - Crowdfunding Platform",
        "source_id": "daskapital",
        "shard": "catalogo-crowdfunding",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Crowdlending (medio prazo, ativos fixos) + Crowdfactoring (curto prazo, faturas)",
        "regulation_url": "https://daskapital.eu/",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 45,
        "status": "ready",
        "notes": "Plataforma portuguesa de crowdfunding. Modelos: Equity, Debt, Tokenized. Produtos: Daslending (medio prazo) e Dasfactoring (curto prazo via creditos a receber)."
    },
    {
        "id": "produtech-dih-factor",
        "name": "DIH-squared / DIH2 Factor (PRODUTECH DIH Platform)",
        "source_id": "produtech-dih",
        "shard": "catalogo-aceleradores",
        "aviso_codigo": None,
        "detected_date": TODAY,
        "deadline": None,
        "budget": "Acesso a VCs investors + apoio teste/validacao em fabrica",
        "regulation_url": "https://dih-squared.eu/content/dih%C2%B2-factor",
        "pdf_url": None,
        "regulation_local": None,
        "priority_score": 50,
        "status": "ready",
        "notes": "DIH portugues PRODUTECH integrado no consortio DIH-squared. Apoia startups e scale-ups (seed-Series A) em robotica e fabrico agil. Pitch event anual com VCs. PRODUTECH integra EUHubs4Data."
    },
]

# Load and update queue.json
with open('registry/queue.json', encoding='utf-8') as f:
    qd = json.load(f)
existing_q_ids = {it.get('id') for it in qd['queue']}
new_q_count = 0
for it in queue_items:
    if it['id'] not in existing_q_ids:
        qd['queue'].append(it)
        new_q_count += 1
qd['updated'] = TODAY
with open('registry/queue.json', 'w', encoding='utf-8') as f:
    json.dump(qd, f, indent=2, ensure_ascii=False)
print(f'queue.json: +{new_q_count} novos itens (total agora: {len(qd["queue"])})')

# Load and update queue-catalogo.json
with open('registry/queue-catalogo.json', encoding='utf-8') as f:
    cd = json.load(f)
if 'queue' not in cd:
    cd['queue'] = []
existing_c_ids = {it.get('id') for it in cd['queue']}
new_c_count = 0
for it in catalogo_items:
    if it['id'] not in existing_c_ids:
        cd['queue'].append(it)
        new_c_count += 1
cd['updated'] = TODAY
with open('registry/queue-catalogo.json', 'w', encoding='utf-8') as f:
    json.dump(cd, f, indent=2, ensure_ascii=False)
print(f'queue-catalogo.json: +{new_c_count} novos itens (total agora: {len(cd["queue"])})')

# Update registry/index.json totals
with open('registry/index.json', encoding='utf-8') as f:
    idx = json.load(f)
idx['totals']['in_queue'] = len(qd['queue'])
idx['totals']['in_catalogo'] = len(cd['queue'])
with open('registry/index.json', 'w', encoding='utf-8') as f:
    json.dump(idx, f, indent=2, ensure_ascii=False)
print(f'registry/index.json: in_queue={idx["totals"]["in_queue"]}, in_catalogo={idx["totals"]["in_catalogo"]}')
