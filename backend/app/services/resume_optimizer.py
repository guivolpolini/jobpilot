import re
import json
import logging
import unicodedata
from typing import Dict, Any, List
from openai import OpenAI
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=settings.OPENAI_BASE_URL,
    api_key=settings.OPENAI_API_KEY
)


class TechnicalSkillsStructure(BaseModel):
    languages: List[str] = Field(default_factory=list, description="Linguagens de programação")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks e Bibliotecas")
    databases: List[str] = Field(default_factory=list, description="Bancos de dados")
    tools: List[str] = Field(default_factory=list, description="Cloud, DevOps e Ferramentas")
    methodologies: List[str] = Field(default_factory=list, description="Metodologias e práticas")


class ProjectItem(BaseModel):
    name: str
    stack: str
    url: str
    bullets: List[str] = Field(description="2 a 3 bullets: verbo de ação + o que foi feito + tecnologia + resultado/impacto")


class ExperienceItem(BaseModel):
    role: str
    location: str = "São Caetano do Sul - SP (Remoto)"
    period: str
    bullets: List[str] = Field(description="2 a 3 bullets no mesmo padrão dos projetos")


class EducationItem(BaseModel):
    course: str
    institution: str
    graduation_date: str


class CertificationItem(BaseModel):
    name: str
    institution: str
    year: str


class LanguageItem(BaseModel):
    language: str
    level: str


class StandardATSResumeContent(BaseModel):
    full_name: str = "Guilherme Volpolini"
    location: str = "São Caetano do Sul - SP"
    email: str = "guilherme.volpolini@gmail.com"
    phone: str = "(11) 98765-4321"
    linkedin_url: str = "https://www.linkedin.com/in/guilherme-volpolini-a60961312/"
    github_url: str = "https://github.com/guivolpolini"
    objective: str
    summary: str
    technical_skills: TechnicalSkillsStructure
    projects: List[ProjectItem]
    experiences: List[ExperienceItem]
    education: List[EducationItem]
    certifications: List[CertificationItem]
    languages: List[LanguageItem]


def _normalize(text: str) -> str:
    if not text:
        return ""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').lower()


def _build_standard_curated_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> StandardATSResumeContent:
    """
    Constrói adaptação única e cirúrgica para CADA vaga:
    - Identifica a área específica (Dados, Front-end, Python/Backend, Java, Automação/DevOps).
    - Modela OBJETIVO, RESUMO, HABILIDADES e PROJETOS exatamente para os requisitos da oportunidade.
    """
    clean_role = job_title.strip() if job_title else "Desenvolvedor de Software"
    t_norm = _normalize(job_title)
    d_norm = _normalize(job_description)
    k_norm = " ".join([_normalize(k) for k in (ats_keywords or [])])
    full_norm = f"{t_norm} {d_norm} {k_norm}"

    def has_any_word(words: List[str], text: str) -> bool:
        for w in words:
            pattern = r'\b' + re.escape(w) + r'\b'
            if re.search(pattern, text):
                return True
        return False

    is_estagio = has_any_word(["estagio", "estagiario", "intern", "estagiaria", "estagio de ti"], full_norm)
    is_junior = has_any_word(["junior", "jr", "iniciante", "trainee", "entry"], full_norm)

    # 2. Área técnica da vaga (com verificação rigorosa de limites de palavra)
    is_data = has_any_word(["dados", "data", "analytics", "bi", "sql", "analise de dados", "analise", "etl"], full_norm)
    is_frontend = has_any_word(["frontend", "front-end", "react", "next", "nextjs", "typescript", "javascript", "tailwind", "ui", "ux", "css", "html", "web design"], full_norm)
    is_java = has_any_word(["java", "spring", "poo", "orientacao a objetos"], full_norm)
    is_python = has_any_word(["python", "fastapi", "django", "flask", "microsservicos", "pagamentos"], full_norm)
    is_automation = has_any_word(["automacao", "playwright", "scraping", "crawler", "selenium", "mensageria", "celery", "redis"], full_norm)

    # --- 1. OBJETIVO CUSTOMIZADO ---
    if is_estagio:
        if is_data and not (is_frontend and not ("analise" in full_norm or "dados" in full_norm)):
            objective = f"Estágio em Análise de Dados | Foco em SQL, Python e Modelagem Relacional"
        elif is_frontend and not is_python:
            objective = f"Estágio em Desenvolvimento Web / Front-end | Foco em React, TypeScript e Next.js"
        elif is_java:
            objective = f"Estágio em Desenvolvimento de Software | Foco em Java e POO"
        elif is_python:
            objective = f"Estágio em Desenvolvimento Backend | Foco em Python, FastAPI e APIs REST"
        else:
            objective = f"Estágio em Tecnologia | Foco em Desenvolvimento de Software e Resolução de Problemas"
    elif is_junior:
        if is_data and not is_frontend:
            objective = f"Desenvolvedor de Dados Júnior | Foco em Python, SQL e ETL"
        elif is_frontend and not is_python:
            objective = f"Desenvolvedor Front-end Júnior | Foco em React, Next.js e TypeScript"
        elif is_java:
            objective = f"Desenvolvedor Java Júnior | Foco em Back-end e Microsserviços"
        elif is_python:
            objective = f"Desenvolvedor Python Backend Júnior | Foco em FastAPI e APIs RESTful"
        else:
            objective = f"Desenvolvedor de Software Júnior | Foco em Back-end e Integrações"
    else:
        objective = f"{clean_role} | Foco em Arquitetura de Software e APIs"

    # --- 2. RESUMO PERSONALIZADO ---
    if is_data and not is_frontend:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com sólida base em modelagem relacional, SQL e algoritmos. "
            f"Experiência prática na manipulação e estruturação de dados com Python (FastAPI/SQLAlchemy), MySQL e PostgreSQL. "
            f"Habilidade no consumo de fontes de dados, tratamento de regras de negócio e entrega de projetos com código limpo para {clean_role}."
        )
    elif is_frontend and not is_python:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com atuação prática como Desenvolvedor Web Freelance (VolpoTech). "
            f"Experiência comprovada na criação de aplicações web responsivas e modernas com React, Next.js, TypeScript e Tailwind CSS. "
            f"Foco em usabilidade, integração com APIs REST e deploy contínuo na Vercel para a oportunidade de {clean_role}."
        )
    elif is_java:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com sólida base em Programação Orientada a Objetos e Java. "
            f"Certificação Java Programmer pela Oracle, com domínio de arquitetura em camadas, herança, polimorfismo e modelagem relacional. "
            f"Vivência em desenvolvimento colaborativo com Git, testes e Clean Code alinhados ao cargo de {clean_role}."
        )
    elif is_automation or "celery" in full_norm or "playwright" in full_norm:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com foco em desenvolvimento backend e automação de processos. "
            f"Experiência prática com Python, FastAPI, mensageria assíncrona (Redis/Celery) e automação de fluxos com Playwright headless. "
            f"Forte orientação a testes automatizados com pytest e microsserviços escaláveis para a oportunidade de {clean_role}."
        )
    else:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com foco em desenvolvimento de software e APIs RESTful. "
            f"Experiência na construção de aplicações escaláveis com Python (FastAPI), validação de esquemas via Pydantic e persistência relacional. "
            f"Projetos reais entregues em produção, versionamento avançado com Git e foco em resultados para {clean_role}."
        )

    # --- 3. HABILIDADES TÉCNICAS REORDENADAS ---
    if is_data and not is_frontend:
        languages_order = ["SQL", "Python", "Java", "TypeScript", "JavaScript"]
        frameworks_order = ["SQLAlchemy", "FastAPI", "Pydantic", "Node.js", "React", "Next.js", "Tailwind CSS"]
        databases_order = ["MySQL", "PostgreSQL", "MongoDB", "Supabase"]
        tools_order = ["Git", "GitHub", "pytest", "Docker", "Linux", "Playwright", "Google Gemini API", "Vercel"]
    elif is_frontend and not is_python:
        languages_order = ["TypeScript", "JavaScript", "HTML/CSS", "Python", "SQL", "Java"]
        frameworks_order = ["React", "Next.js", "Tailwind CSS", "Vite", "FastAPI", "Node.js", "SQLAlchemy"]
        databases_order = ["Supabase", "PostgreSQL", "MySQL", "MongoDB"]
        tools_order = ["Vercel", "Git", "GitHub", "Docker", "Linux", "pytest", "Playwright", "Google Gemini API"]
    elif is_java:
        languages_order = ["Java", "SQL", "Python", "TypeScript", "JavaScript"]
        frameworks_order = ["FastAPI", "SQLAlchemy", "Pydantic", "Node.js", "React", "Next.js", "Tailwind CSS"]
        databases_order = ["MySQL", "PostgreSQL", "MongoDB", "Supabase"]
        tools_order = ["Git", "GitHub", "Docker", "Linux", "pytest", "Playwright", "Vercel", "Google Gemini API"]
    elif is_automation:
        languages_order = ["Python", "SQL", "TypeScript", "JavaScript", "Java"]
        frameworks_order = ["FastAPI", "SQLAlchemy", "Pydantic", "Next.js", "React", "Tailwind CSS", "Node.js"]
        databases_order = ["PostgreSQL", "MySQL", "MongoDB", "Supabase"]
        tools_order = ["Playwright", "Docker", "Git", "GitHub", "pytest", "Linux", "Vercel", "Google Gemini API"]
    else:
        languages_order = ["Python", "SQL", "Java", "TypeScript", "JavaScript"]
        frameworks_order = ["FastAPI", "SQLAlchemy", "Pydantic", "React", "Next.js", "Tailwind CSS", "Node.js"]
        databases_order = ["PostgreSQL", "MySQL", "MongoDB", "Supabase"]
        tools_order = ["Docker", "Git", "GitHub", "pytest", "Linux", "Playwright", "Vercel", "Google Gemini API"]

    methodologies = ["Programação Orientada a Objetos (POO)", "Arquitetura RESTful", "Clean Code", "Scrum", "Kanban"]

    # --- 4. CATÁLOGO DE PROJETOS E SELEÇÃO ESPECÍFICA ---
    catalog = [
        {
            "name": "JobPilot - Automação & Matching ATS",
            "stack": "Python, FastAPI, Next.js, PostgreSQL/SQLite, Playwright",
            "url": "https://github.com/guivolpolini/jobpilot",
            "affinity": ["automacao", "playwright", "python", "fastapi", "apis", "integracoes", "crawler", "scraping", "estagio", "junior"],
            "bullets": [
                "Construiu sistema de monitoramento de oportunidades com análise semântica de aderência a requisitos de vagas.",
                "Implementou pipeline de compilação dinâmica de currículos aderentes a ATS utilizando Playwright headless.",
                "Estruturou APIs assíncronas com FastAPI e documentação OpenAPI interativa."
            ]
        },
        {
            "name": "Assistente de Estudos com IA",
            "stack": "Python, FastAPI, SQLAlchemy, Pydantic, Google Gemini API, pytest",
            "url": "https://github.com/guivolpolini/ai-study-assistant",
            "affinity": ["python", "fastapi", "ia", "ai", "dados", "data", "gemini", "pytest", "backend", "sql"],
            "bullets": [
                "Desenvolveu arquitetura modular em camadas (routers, services e schemas) com validação estrita via Pydantic.",
                "Integrou a API do Google Gemini com prompts estruturados para geração determinística de JSON com quizzes e resumos.",
                "Implementou suíte de testes unitários automatizados com pytest e mocks, assegurando confiabilidade sem chamadas externas."
            ]
        },
        {
            "name": "E-Commerce Full Stack & API REST",
            "stack": "FastAPI, MySQL, SQLAlchemy, JWT, React, Next.js",
            "url": "https://github.com/guivolpolini/ecommerce-api",
            "affinity": ["mysql", "sql", "dados", "pagamentos", "jwt", "fastapi", "backend", "fullstack", "ecommerce"],
            "bullets": [
                "Projetou API RESTful completa para comércio eletrônico com autenticação segura baseada em JWT e senhas com hash criptográfico.",
                "Modelou banco relacional MySQL com SQLAlchemy contemplando relacionamentos 1:N e N:N para produtos, pedidos e categorias.",
                "Integrou fluxo de pagamentos com a API do MercadoPago e construiu painel administrativo no front-end."
            ]
        },
        {
            "name": "DigestiveQuest - Jogo Educativo em Java",
            "stack": "Java, POO, Swing",
            "url": "https://github.com/guivolpolini/DigestiveQuest",
            "affinity": ["java", "poo", "orientacao a objetos", "desktop", "jogos", "equipe"],
            "bullets": [
                "Desenvolveu jogo interativo em equipe aplicando herança, polimorfismo, encapsulamento e tratamento de exceções em Java.",
                "Estruturou lógica de gameplay e progressão pedagógica para o Colégio Piaget.",
                "Validou impacto direto na prática, apoiando o aprendizado de 50 estudantes em ambiente escolar."
            ]
        },
        {
            "name": "SaaS Barbearia & Agendamento Digital",
            "stack": "React, Vite, TypeScript, Tailwind CSS, Supabase, n8n",
            "url": "https://github.com/guivolpolini/saas-barbearia",
            "affinity": ["frontend", "front-end", "react", "typescript", "tailwind", "web", "ui", "ux", "supabase"],
            "bullets": [
                "Desenvolveu aplicação de agendamento online com arquitetura multiempresa e persistência no PostgreSQL via Supabase.",
                "Configurou webhooks e automação de fluxos com n8n para notificações em tempo real.",
                "Criou interface responsiva mobile-first com Tailwind CSS garantindo tempos de carregamento velozes."
            ]
        }
    ]

    def score_proj(p):
        score = 0
        p_stack = _normalize(p["stack"])
        for aff in p["affinity"]:
            if aff in full_norm:
                score += 4
        for kw in ats_keywords:
            if _normalize(kw) in p_stack:
                score += 5
        return score

    catalog.sort(key=score_proj, reverse=True)
    selected_projects = [
        ProjectItem(
            name=p["name"],
            stack=p["stack"],
            url=p["url"],
            bullets=p["bullets"]
        )
        for p in catalog[:3]
    ]

    # --- 5. EXPERIÊNCIA COM BULLETS ALINHADOS ---
    if is_data and not is_frontend:
        exp_freelance_bullets = [
            "Estruturou persistência e consultas relacionais para plataformas web de pequenos negócios garantindo integridade de dados.",
            "Implementou automação de fluxos com webhooks e integrações via WhatsApp facilitando a captação de leads.",
            "Gerenciou ciclos de entrega completos com clientes, desde o levantamento de regras até deploy em produção."
        ]
        exp_opensource_bullets = [
            "Modelou bancos relacionais (MySQL/PostgreSQL) aplicando normalização e relacionamentos estruturados com SQLAlchemy.",
            "Construiu pipelines de processamento de dados e validação estrita com Pydantic e testes automatizados (pytest).",
            "Manteve repositórios públicos documentados seguindo boas práticas de Git e Conventional Commits."
        ]
    elif is_frontend and not is_python:
        exp_freelance_bullets = [
            "Desenvolveu websites e landing pages responsivas com Next.js, React e Tailwind CSS com foco em SEO e alta conversão.",
            "Implementou interfaces modernas com foco em experiência do usuário (UX/UI) e compatibilidade cross-browser.",
            "Gerenciou ciclos de entrega completos com clientes, desde a prototipação até deploy na Vercel."
        ]
        exp_opensource_bullets = [
            "Construiu aplicações web com TypeScript e React aplicando componentização desacoplada e padrões modernos.",
            "Consumiu APIs RESTful estruturando estados globais e fluxos de dados reativos.",
            "Colaborou em projetos em equipe utilizando metodologias ágeis Scrum/Kanban e versionamento Git."
        ]
    else:
        exp_freelance_bullets = [
            "Desenvolveu websites e plataformas web responsivas com Next.js, React e Tailwind CSS com foco em SEO e conversão.",
            "Implementou integrações com APIs REST e webhooks para automação de atendimento e agendamento via WhatsApp.",
            "Gerenciou ciclos de entrega completos com clientes, desde o levantamento de requisitos até deploy em produção."
        ]
        exp_opensource_bullets = [
            f"Construiu APIs robustas utilizando {'Java' if is_java else 'FastAPI'} com validação rigorosa de payloads e testes automatizados.",
            "Modelou bancos de dados relacionais e implementou regras de negócio modulares e manuteníveis.",
            "Colaborou em projetos aplicando boas práticas de versionamento Git e Conventional Commits."
        ]

    experiences = [
        ExperienceItem(
            role="Desenvolvedor Web Freelance",
            location="São Caetano do Sul - SP (Remoto)",
            period="01/2024 - Presente",
            bullets=exp_freelance_bullets
        ),
        ExperienceItem(
            role="Desenvolvedor de Software (Projetos Open Source)",
            location="GitHub (Remoto)",
            period="03/2024 - Presente",
            bullets=exp_opensource_bullets
        )
    ]

    education = [
        EducationItem(
            course="Bacharelado em Ciência da Computação",
            institution="Instituto Mauá de Tecnologia (IMT)",
            graduation_date="Previsão de conclusão: 12/2028"
        )
    ]

    certifications = [
        CertificationItem(name="Certificação Java Programmer", institution="Oracle", year="2024"),
        CertificationItem(name="CC50 - Introdução à Ciência da Computação (CS50)", institution="Harvard / Fundação Estudar", year="2024"),
        CertificationItem(name="Desenvolvimento Orientado a Objetos com Python", institution="Fundação Bradesco", year="2024"),
        CertificationItem(name="Network Technician Career Path", institution="Cisco", year="2023")
    ]

    languages = [
        LanguageItem(language="Português", level="Nativo"),
        LanguageItem(language="Inglês", level="Avançado"),
        LanguageItem(language="Espanhol", level="Intermediário")
    ]

    return StandardATSResumeContent(
        full_name="Guilherme Volpolini",
        location="São Caetano do Sul - SP",
        email=base_profile.get("email") or "guilherme.volpolini@gmail.com",
        phone=base_profile.get("phone") or "(11) 98765-4321",
        linkedin_url="https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
        github_url="https://github.com/guivolpolini",
        objective=objective,
        summary=summary,
        technical_skills=TechnicalSkillsStructure(
            languages=languages_order,
            frameworks=frameworks_order,
            databases=databases_order,
            tools=tools_order,
            methodologies=methodologies
        ),
        projects=selected_projects,
        experiences=experiences,
        education=education,
        certifications=certifications,
        languages=languages
    )


def generate_tailored_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> StandardATSResumeContent:
    """
    Gera currículo adaptado para cada vaga alvo específica respeitando
    o modelo estrito de 9 seções e personalizando palavras-chave e prioridades.
    """
    prompt = f"""
Você é um especialista em currículos para a área de tecnologia.
Adapte o currículo EXATAMENTE ao modelo especificado abaixo para a vaga informada.

REGRAS OBRIGATÓRIAS:
- Uma coluna, texto simples, compatível com ATS (sem tabelas, foto, ícones ou barras de nível).
- Máximo 1 página.
- Idioma: português.
- Datas no formato MM/AAAA.
- Bullets começam com verbo no passado ou infinitivo (Desenvolveu, Implementou, Integrou...).
- Priorize o que a vaga pede: reordene habilidades e projetos conforme a descrição da vaga e use as mesmas palavras-chave dela, apenas se o candidato realmente tiver a skill.
- Nunca invente tecnologia, métrica ou experiência.

=== DADOS REAIS DO CANDIDATO ===
{json.dumps(base_profile, ensure_ascii=False, indent=2)}

=== VAGA ALVO ===
Cargo: {job_title}
Descrição:
{job_description}

=== PALAVRAS-CHAVE ATS DA VAGA ===
{json.dumps(ats_keywords, ensure_ascii=False)}

=== FORMATO JSON REQUERIDO ===
{{
  "full_name": "Guilherme Volpolini",
  "location": "São Caetano do Sul - SP",
  "email": "guilherme.volpolini@gmail.com",
  "phone": "(11) 98765-4321",
  "linkedin_url": "https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
  "github_url": "https://github.com/guivolpolini",
  "objective": "1 linha adaptada com cargo-alvo e foco alinhado à vaga",
  "summary": "2 a 3 linhas adaptadas ao contexto da vaga, direto, sem clichês",
  "technical_skills": {{
    "languages": ["...reordenadas com as linguagens pedidas pela vaga no topo"],
    "frameworks": ["...reordenados com os frameworks pedidos pela vaga no topo"],
    "databases": ["...reordenados com os bancos pedidos pela vaga no topo"],
    "tools": ["...reordenadas com ferramentas pedidas pela vaga no topo"],
    "methodologies": ["POO", "Arquitetura RESTful", "Clean Code", "Scrum", "Kanban"]
  }},
  "projects": [
    {{
      "name": "Nome do Projeto (escolhido entre os repositórios reais do candidato que melhor combinam com a vaga)",
      "stack": "Stack do projeto",
      "url": "https://github.com/guivolpolini/...",
      "bullets": [
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto com foco nas keywords da vaga",
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto com foco nas keywords da vaga"
      ]
    }}
  ],
  "experiences": [
    {{
      "role": "Desenvolvedor Web Freelance",
      "location": "São Caetano do Sul - SP (Remoto)",
      "period": "01/2024 - Presente",
      "bullets": [
        "Bullets com verbos de ação valorizando competências que se conectam com a vaga",
        "Bullets com verbos de ação valorizando competências que se conectam com a vaga"
      ]
    }},
    {{
      "role": "Desenvolvedor de Software (Projetos Open Source)",
      "location": "GitHub (Remoto)",
      "period": "03/2024 - Presente",
      "bullets": [
        "Bullets com verbos de ação enfatizando o stack da vaga (FastAPI, Java, testes, etc.)",
        "Bullets com verbos de ação enfatizando o stack da vaga (FastAPI, Java, testes, etc.)"
      ]
    }}
  ],
  "education": [
    {{
      "course": "Bacharelado em Ciência da Computação",
      "institution": "Instituto Mauá de Tecnologia (IMT)",
      "graduation_date": "Previsão de conclusão: 12/2028"
    }}
  ],
  "certifications": [
    {{ "name": "Certificação Java Programmer", "institution": "Oracle", "year": "2024" }},
    {{ "name": "CC50 - Introdução à Ciência da Computação (CS50)", "institution": "Harvard / Fundação Estudar", "year": "2024" }},
    {{ "name": "Desenvolvimento Orientado a Objetos com Python", "institution": "Fundação Bradesco", "year": "2024" }},
    {{ "name": "Network Technician Career Path", "institution": "Cisco", "year": "2023" }}
  ],
  "languages": [
    {{ "language": "Português", "level": "Nativo" }},
    {{ "language": "Inglês", "level": "Avançado" }},
    {{ "language": "Espanhol", "level": "Intermediário" }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um especialista em currículos de tecnologia ATS. Responda exclusivamente com JSON no schema estrito."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return StandardATSResumeContent(**data)
    except Exception as e:
        logger.info(f"LLM indisponível ({e}). Gerando adaptação algorítmica cirúrgica para a vaga.")
        return _build_standard_curated_resume(base_profile, job_title, job_description, ats_keywords)
