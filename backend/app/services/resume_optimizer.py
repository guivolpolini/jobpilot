import re
import json
import logging
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
    period: str  # formato MM/AAAA - MM/AAAA ou MM/AAAA - Presente
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
    # 1. CABEÇALHO
    full_name: str = "Guilherme Volpolini"
    location: str = "São Caetano do Sul - SP"
    email: str = "guilherme.volpolini@gmail.com"
    phone: str = "(11) 98765-4321"
    linkedin_url: str = "https://www.linkedin.com/in/guilherme-volpolini-a60961312/"
    github_url: str = "https://github.com/guivolpolini"

    # 2. OBJETIVO
    objective: str

    # 3. RESUMO
    summary: str

    # 4. HABILIDADES TÉCNICAS
    technical_skills: TechnicalSkillsStructure

    # 5. PROJETOS
    projects: List[ProjectItem]

    # 6. EXPERIÊNCIA
    experiences: List[ExperienceItem]

    # 7. FORMAÇÃO
    education: List[EducationItem]

    # 8. CERTIFICAÇÕES E CURSOS
    certifications: List[CertificationItem]

    # 9. IDIOMAS
    languages: List[LanguageItem]


def _build_standard_curated_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> StandardATSResumeContent:
    """
    Adapta cirurgicamente o currículo para a vaga alvo:
    - OBJETIVO espelha exatamente o cargo e foco da vaga.
    - RESUMO destaca o alinhamento acadêmico e técnico específico da vaga.
    - HABILIDADES TÉCNICAS são reordenadas trazendo para a frente os requisitos da vaga.
    - PROJETOS e BULLETS são priorizados para comprovar a stack exigida.
    """
    raw_text = (job_title + " " + job_description + " " + " ".join(ats_keywords)).lower()
    text_context = raw_text

    # Detectores de perfil da vaga
    has_python = any(k in text_context for k in ["python", "fastapi", "django", "flask"])
    has_java = any(k in text_context for k in ["java", "spring", "jvm", "poo"])
    has_frontend = any(k in text_context for k in ["react", "next", "frontend", "front-end", "javascript", "typescript", "tailwind", "css", "html"])
    has_data_ai = any(k in text_context for k in ["ia", "ai", "dados", "gemini", "llm", "inteligência artificial", "inteligencia artificial", "nlp"])
    has_fullstack = (has_python or has_java) and has_frontend or "fullstack" in text_context or "full stack" in text_context
    is_estagio = any(w in text_context for w in ["estágio", "estagio", "estagiário", "estagiario", "intern", "estag"])
    is_junior = any(w in text_context for w in ["júnior", "junior", "jr", "iniciante", "trainee"])

    # 1. OBJETIVO (1 linha adaptada com cargo-alvo e foco)
    clean_role = job_title.strip()
    if is_estagio:
        if has_frontend and not has_python:
            objective = "Estágio em Desenvolvimento Web / Front-end | Foco em React, TypeScript e Next.js"
        elif has_java and not has_python:
            objective = "Estágio em Desenvolvimento de Software | Foco em Java e Back-end"
        elif has_data_ai:
            objective = "Estágio em Desenvolvimento de Software | Foco em Python e Aplicações com IA"
        else:
            objective = f"Estágio em Desenvolvimento de Software | Foco em {clean_role if len(clean_role) < 35 else 'Back-end e APIs'}"
    elif is_junior:
        if has_frontend and not has_python:
            objective = f"Desenvolvedor Front-end Júnior | Foco em React e TypeScript ({clean_role})"
        elif has_java and not has_python:
            objective = f"Desenvolvedor Java Júnior | Foco em Back-end e Microsserviços"
        else:
            objective = f"Desenvolvedor Júnior | Foco em {clean_role if len(clean_role) < 35 else 'Back-end e APIs'}"
    else:
        objective = f"{clean_role} | Foco em Arquitetura de Software e APIs"

    # 2. RESUMO (2 a 3 linhas adaptadas cirurgicamente aos requisitos da vaga)
    if has_java and not has_python:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com sólida base em POO e Java. "
            f"Experiência prática no desenvolvimento de sistemas orientados a objetos, estruturas de dados e modelagem de bancos relacionais. "
            f"Vivência em projetos colaborativos com versionamento Git e aplicação de Clean Code para o cargo de {clean_role}."
        )
    elif has_frontend and not has_python:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com atuação prática como Desenvolvedor Web Freelance (VolpoTech). "
            f"Experiência na construção de aplicações web responsivas e performáticas com React, Next.js, TypeScript e Tailwind CSS. "
            f"Foco em consumo de APIs REST, interfaces de alta conversão e deploy contínuo direcionado para {clean_role}."
        )
    elif has_data_ai:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com ênfase em Python e IA generativa. "
            f"Desenvolvedor de soluções que integram LLMs (Google Gemini API) a pipelines robustos em FastAPI e validação com Pydantic. "
            f"Forte fundamentação matemática, testes unitários com pytest e foco prático na oportunidade de {clean_role}."
        )
    else:
        summary = (
            f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com sólida base em algoritmos e modelagem relacional. "
            f"Experiência no desenvolvimento de APIs RESTful com Python (FastAPI), automação de processos e integração de microsserviços. "
            f"Projetos reais em produção e práticas de Clean Code alinhados aos requisitos de {clean_role}."
        )

    # 3. HABILIDADES TÉCNICAS (reordenadas dinamicamente trazendo as exigências da vaga para a frente)
    languages_pool = ["Python", "Java", "SQL", "TypeScript", "JavaScript"]
    if has_java and not has_python:
        languages_order = ["Java", "SQL", "Python", "TypeScript", "JavaScript"]
    elif has_frontend:
        languages_order = ["TypeScript", "JavaScript", "Python", "SQL", "Java"]
    else:
        languages_order = ["Python", "SQL", "Java", "TypeScript", "JavaScript"]

    frameworks_pool = ["FastAPI", "SQLAlchemy", "Pydantic", "React", "Next.js", "Tailwind CSS", "Node.js"]
    if has_frontend:
        frameworks_order = ["React", "Next.js", "Tailwind CSS", "FastAPI", "SQLAlchemy", "Pydantic", "Node.js"]
    else:
        frameworks_order = ["FastAPI", "SQLAlchemy", "Pydantic", "Node.js", "React", "Next.js", "Tailwind CSS"]

    databases_pool = ["MySQL", "PostgreSQL", "MongoDB", "Supabase"]
    if "postgres" in text_context:
        databases_order = ["PostgreSQL", "MySQL", "MongoDB", "Supabase"]
    elif "mongo" in text_context:
        databases_order = ["MongoDB", "MySQL", "PostgreSQL", "Supabase"]
    else:
        databases_order = ["MySQL", "PostgreSQL", "MongoDB", "Supabase"]

    tools_pool = ["Git", "GitHub", "Docker", "pytest", "Playwright", "Linux", "Vercel", "Render", "Google Gemini API"]
    if "docker" in text_context:
        tools_order = ["Docker", "Git", "GitHub", "pytest", "Linux", "Playwright", "Vercel", "Render", "Google Gemini API"]
    elif "test" in text_context or "pytest" in text_context:
        tools_order = ["pytest", "Git", "GitHub", "Docker", "Playwright", "Linux", "Vercel", "Render", "Google Gemini API"]
    else:
        tools_order = ["Git", "GitHub", "Docker", "pytest", "Playwright", "Linux", "Vercel", "Render", "Google Gemini API"]

    methodologies = ["Programação Orientada a Objetos (POO)", "Arquitetura RESTful", "Clean Code", "Scrum", "Kanban"]

    # 4. PROJETOS (seleção e priorização dos 3 projetos que melhor comprovam a vaga)
    catalog = [
        {
            "name": "Assistente de Estudos com IA",
            "stack": "Python, FastAPI, SQLAlchemy, Pydantic, Google Gemini API, pytest",
            "url": "https://github.com/guivolpolini/ai-study-assistant",
            "tags": ["python", "fastapi", "ia", "ai", "gemini", "pytest", "backend"],
            "bullets": [
                "Desenvolveu arquitetura modular em camadas (routers, services e schemas) com validação estrita via Pydantic.",
                "Integrou a API do Google Gemini com prompts estruturados para geração determinística de JSON com quizzes e resumos.",
                "Implementou suíte de testes unitários automatizados com pytest e mocks, assegurando confiabilidade sem chamadas externas."
            ]
        },
        {
            "name": "JobPilot - Automação & Matching ATS",
            "stack": "Python, FastAPI, Next.js, SQLite/PostgreSQL, Playwright",
            "url": "https://github.com/guivolpolini/jobpilot",
            "tags": ["python", "fastapi", "automação", "playwright", "next.js", "fullstack", "backend"],
            "bullets": [
                "Construiu sistema de monitoramento de oportunidades com análise semântica de aderência a requisitos de vagas.",
                "Implementou pipeline de compilação dinâmica de currículos aderentes a ATS utilizando Playwright headless.",
                "Estruturou APIs assíncronas com FastAPI e documentação OpenAPI interativa."
            ]
        },
        {
            "name": "E-Commerce Full Stack & API REST",
            "stack": "FastAPI, MySQL, SQLAlchemy, JWT, React, Next.js",
            "url": "https://github.com/guivolpolini/ecommerce-api",
            "tags": ["fastapi", "mysql", "sql", "jwt", "react", "next.js", "fullstack", "backend"],
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
            "tags": ["java", "poo", "orientação a objetos", "desktop"],
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
            "tags": ["react", "typescript", "tailwind", "frontend", "supabase", "postgres", "n8n"],
            "bullets": [
                "Desenvolveu aplicação de agendamento online com arquitetura multiempresa e persistência no PostgreSQL via Supabase.",
                "Configurou webhooks e automação de fluxos com n8n para notificações em tempo real.",
                "Criou interface responsiva mobile-first com Tailwind CSS garantindo tempos de carregamento velozes."
            ]
        }
    ]

    # Pontuação por afinidade com as exigências da vaga
    def score_project(p):
        score = 0
        for tag in p["tags"]:
            if tag in text_context:
                score += 5
        for kw in ats_keywords:
            if kw.lower() in p["stack"].lower():
                score += 3
        return score

    catalog.sort(key=score_project, reverse=True)
    selected_projects = [
        ProjectItem(
            name=p["name"],
            stack=p["stack"],
            url=p["url"],
            bullets=p["bullets"]
        )
        for p in catalog[:3]
    ]

    # 5. EXPERIÊNCIA (bullets adaptados para a vaga)
    exp_web_bullets = [
        "Desenvolveu websites e landing pages responsivas com Next.js, React e Tailwind CSS com foco em SEO e conversão para pequenos negócios.",
        "Implementou integrações com APIs REST e webhooks para automação de atendimento e agendamento via WhatsApp.",
        "Gerenciou ciclos de entrega completos com clientes, desde o levantamento de requisitos até deploy em produção na Vercel."
    ]

    exp_opensource_bullets = [
        "Implementou repositórios públicos aplicando boas práticas de versionamento com Git, Conventional Commits e documentação técnica.",
        f"Construiu APIs robustas utilizando {'Java' if has_java and not has_python else 'FastAPI'} com testes automatizados e validação rigorosa de payloads.",
        "Colaborou em projetos em equipe utilizando metodologias ágeis Scrum/Kanban."
    ]

    experiences = [
        ExperienceItem(
            role="Desenvolvedor Web Freelance",
            location="São Caetano do Sul - SP (Remoto)",
            period="01/2024 - Presente",
            bullets=exp_web_bullets
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
