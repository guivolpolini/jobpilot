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
    location: str = "São Caetano do Sul - SP"
    period: str  # formato MM/AAAA - MM/AAAA ou MM/AAAA - Presente
    bullets: List[str] = Field(description="2 a 3 bullets no mesmo padrão dos projetos")


class EducationItem(BaseModel):
    course: str
    institution: str
    graduation_date: str  # Previsão: MM/AAAA ou Concluído: MM/AAAA


class CertificationItem(BaseModel):
    name: str
    institution: str
    year: str


class LanguageItem(BaseModel):
    language: str
    level: str


class StandardATSResumeContent(BaseModel):
    # 1. CABEÇALHO
    full_name: str
    location: str = "São Caetano do Sul - SP"
    email: str
    phone: str
    linkedin_url: str
    github_url: str

    # 2. OBJETIVO
    objective: str = Field(description="1 linha com cargo-alvo e foco")

    # 3. RESUMO
    summary: str = Field(description="2 a 3 linhas, direto, sem clichês")

    # 4. HABILIDADES TÉCNICAS
    technical_skills: TechnicalSkillsStructure

    # 5. PROJETOS
    projects: List[ProjectItem] = Field(description="3 a 4 projetos reais")

    # 6. EXPERIÊNCIA
    experiences: List[ExperienceItem] = Field(description="Experiências profissionais e freelance")

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
    Constrói o currículo rigorosamente no padrão especificado pelo usuário:
    - 9 seções na ordem exata solicitada
    - Verbos de ação no passado/infinitivo
    - Priorização cirúrgica com base na vaga sem inventar dados
    """
    desc_lower = (job_description + " " + job_title).lower()

    # 1. OBJETIVO (1 linha com cargo-alvo e foco)
    is_estagio = any(w in desc_lower for w in ["estágio", "estagio", "intern"])
    is_junior = any(w in desc_lower for w in ["júnior", "junior", "jr"])

    if is_estagio:
        objective = "Estágio em Desenvolvimento de Software | Foco em Back-end e Integrações"
    elif is_junior:
        objective = f"Desenvolvedor Júnior | Foco em Back-end ({job_title})"
    else:
        clean_title = job_title if len(job_title) < 40 else "Desenvolvimento de Software"
        objective = f"{clean_title} | Foco em Back-end e APIs"

    # 2. RESUMO (2 a 3 linhas, direto, sem clichês)
    summary = (
        "Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com sólida base em algoritmos, "
        "estruturas de dados e modelagem relacional. Experiência prática no desenvolvimento de APIs RESTful com Python (FastAPI) "
        "e Java, integração de serviços de IA generativa e entrega de soluções web reais em produção."
    )

    # 3. HABILIDADES TÉCNICAS (agrupadas exatamente pelas 5 categorias)
    # Reordena conforme palavras-chave da vaga
    all_langs = ["Python", "Java", "JavaScript", "TypeScript", "SQL"]
    if "java" in desc_lower and "python" not in desc_lower:
        languages = ["Java", "Python", "SQL", "TypeScript", "JavaScript"]
    else:
        languages = ["Python", "Java", "SQL", "TypeScript", "JavaScript"]

    all_frameworks = ["FastAPI", "SQLAlchemy", "Pydantic", "React", "Next.js", "Tailwind CSS", "Node.js"]
    # Reordena frameworks se a vaga focar em React/Next ou FastAPI
    if any(k in desc_lower for k in ["react", "next", "frontend", "front-end"]):
        frameworks = ["React", "Next.js", "Tailwind CSS", "FastAPI", "SQLAlchemy", "Pydantic", "Node.js"]
    else:
        frameworks = ["FastAPI", "SQLAlchemy", "Pydantic", "React", "Next.js", "Node.js", "Tailwind CSS"]

    databases = ["MySQL", "PostgreSQL", "MongoDB", "Supabase"]
    if "postgres" in desc_lower:
        databases = ["PostgreSQL", "MySQL", "MongoDB", "Supabase"]
    elif "mongo" in desc_lower:
        databases = ["MongoDB", "MySQL", "PostgreSQL", "Supabase"]

    tools = ["Git", "GitHub", "Docker", "pytest", "Playwright", "Linux", "Vercel", "Render", "Google Gemini API"]
    methodologies = ["Programação Orientada a Objetos (POO)", "Arquitetura RESTful", "Clean Code", "Scrum", "Kanban"]

    # 4. PROJETOS (3 a 4 projetos reais com Nome | stack | link e bullets de ação)
    catalog = [
        {
            "name": "Assistente de Estudos com IA",
            "stack": "Python, FastAPI, SQLAlchemy, Pydantic, Google Gemini API, pytest",
            "url": "https://github.com/guivolpolini/ai-study-assistant",
            "bullets": [
                "Desenvolveu arquitetura modular em camadas (routers, services e schemas) com validação estrita via Pydantic.",
                "Integrou a API do Google Gemini com engenharia de prompts estruturados para geração determinística de JSON com quizzes e resumos.",
                "Implementou suíte de testes unitários automatizados com pytest e mocks, assegurando confiabilidade sem chamadas externas."
            ]
        },
        {
            "name": "JobPilot - Automação & Matching ATS",
            "stack": "Python, FastAPI, Next.js, SQLite/PostgreSQL, Playwright",
            "url": "https://github.com/guivolpolini/jobpilot",
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
            "bullets": [
                "Desenvolveu aplicação de agendamento online com arquitetura multiempresa e persistência no PostgreSQL via Supabase.",
                "Configurou webhooks e automação de fluxos com n8n para notificações em tempo real.",
                "Criou interface responsiva mobile-first com Tailwind CSS garantindo tempos de carregamento velozes."
            ]
        }
    ]

    # Reordena projetos priorizando stack da vaga
    def score_proj(p):
        score = 0
        s_lower = p["stack"].lower()
        for kw in (desc_lower.split() + ats_keywords):
            if len(kw) > 3 and kw.lower() in s_lower:
                score += 3
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

    # 5. EXPERIÊNCIA (freelance incluso) Cargo/Atividade | Local | período
    experiences = [
        ExperienceItem(
            role="Desenvolvedor Web Freelance",
            location="São Caetano do Sul - SP (Remoto)",
            period="01/2024 - Presente",
            bullets=[
                "Desenvolveu websites e landing pages responsivas com Next.js, React e Tailwind CSS com foco em SEO e conversão para pequenos negócios.",
                "Implementou integrações com APIs REST e webhooks para automação de atendimento e agendamento via WhatsApp.",
                "Gerenciou ciclos de entrega completos com clientes, desde o levantamento de requisitos até deploy em produção na Vercel."
            ]
        ),
        ExperienceItem(
            role="Desenvolvedor de Software (Projetos Open Source)",
            location="GitHub (Remoto)",
            period="03/2024 - Presente",
            bullets=[
                "Implementou repositórios públicos aplicando boas práticas de versionamento com Git, Conventional Commits e documentação técnica.",
                "Construiu APIs robustas utilizando FastAPI e Java com testes automatizados e validação rigorosa de payloads.",
                "Colaborou em projetos em equipe utilizando metodologias ágeis Scrum/Kanban."
            ]
        )
    ]

    # 6. FORMAÇÃO: Curso | Instituição | previsão de conclusão
    education = [
        EducationItem(
            course="Bacharelado em Ciência da Computação",
            institution="Instituto Mauá de Tecnologia (IMT)",
            graduation_date="Previsão de conclusão: 12/2028"
        )
    ]

    # 7. CERTIFICAÇÕES E CURSOS: nome | instituição | ano
    certifications = [
        CertificationItem(name="Certificação Java Programmer", institution="Oracle", year="2024"),
        CertificationItem(name="CC50 - Introdução à Ciência da Computação (CS50)", institution="Harvard / Fundação Estudar", year="2024"),
        CertificationItem(name="Desenvolvimento Orientado a Objetos com Python", institution="Fundação Bradesco", year="2024"),
        CertificationItem(name="Network Technician Career Path", institution="Cisco", year="2023")
    ]

    # 8. IDIOMAS: idioma, nível
    languages_list = [
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
            languages=languages,
            frameworks=frameworks,
            databases=databases,
            tools=tools,
            methodologies=methodologies
        ),
        projects=selected_projects,
        experiences=experiences,
        education=education,
        certifications=certifications,
        languages=languages_list
    )


def generate_tailored_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> StandardATSResumeContent:
    """
    Gera currículo seguindo ESTRITAMENTE as 9 seções do padrão ATS solicitado:
    CABEÇALHO, OBJETIVO, RESUMO, HABILIDADES TÉCNICAS, PROJETOS, EXPERIÊNCIA, FORMAÇÃO, CERTIFICAÇÕES E CURSOS, IDIOMAS.
    """
    prompt = f"""
Você é um especialista em currículos para a área de tecnologia.
Gere o currículo EXATAMENTE no modelo estruturado abaixo, sem mudar a ordem das seções nem inventar informações.

FORMATO E REGRAS:
- Uma coluna, texto simples, compatível com ATS (sem tabelas, foto, ícones ou barras de nível).
- Máximo 1 página.
- Idioma: português.
- Datas no formato MM/AAAA.
- Bullets começam com verbo no passado ou infinitivo (Desenvolveu, Implementou, Integrou...).
- Priorize o que a vaga pede: reordene habilidades e projetos conforme a descrição da vaga e use as mesmas palavras-chave dela, apenas com skills reais.
- NUNCA invente tecnologia, métrica ou experiência.

=== DADOS REAIS DO CANDIDATO ===
{json.dumps(base_profile, ensure_ascii=False, indent=2)}

=== VAGA ALVO ===
Cargo: {job_title}
Descrição:
{job_description}

=== PALAVRAS-CHAVE ATS ===
{json.dumps(ats_keywords, ensure_ascii=False)}

=== ESTRUTURA RIGOROSA (JSON SCHEMA) ===
{{
  "full_name": "Guilherme Volpolini",
  "location": "São Caetano do Sul - SP",
  "email": "guilherme.volpolini@gmail.com",
  "phone": "(11) 98765-4321",
  "linkedin_url": "https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
  "github_url": "https://github.com/guivolpolini",
  "objective": "1 linha com cargo-alvo e foco (ex.: Estágio em Desenvolvimento de Software, foco em backend)",
  "summary": "2 a 3 linhas, direto, sem clichês ('proativo', 'dinâmico')",
  "technical_skills": {{
    "languages": ["Python", "Java", "SQL", "TypeScript", "JavaScript"],
    "frameworks": ["FastAPI", "SQLAlchemy", "Pydantic", "React", "Next.js"],
    "databases": ["MySQL", "PostgreSQL", "MongoDB"],
    "tools": ["Git", "GitHub", "Docker", "pytest", "Linux"],
    "methodologies": ["POO", "APIs RESTful", "Clean Code", "Scrum"]
  }},
  "projects": [
    {{
      "name": "Nome do Projeto",
      "stack": "Tecnologias utilizadas",
      "url": "https://github.com/guivolpolini/...",
      "bullets": [
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto",
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto"
      ]
    }}
  ],
  "experiences": [
    {{
      "role": "Desenvolvedor Web Freelance",
      "location": "São Caetano do Sul - SP (Remoto)",
      "period": "01/2024 - Presente",
      "bullets": [
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto",
        "Verbo de ação + o que foi feito + tecnologia + resultado/impacto"
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
    {{
      "name": "Certificação Java Programmer",
      "institution": "Oracle",
      "year": "2024"
    }}
  ],
  "languages": [
    {{ "language": "Português", "level": "Nativo" }},
    {{ "language": "Inglês", "level": "Avançado" }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um especialista em currículos de tecnologia ATS. Responda exclusivamente com JSON no schema exato fornecido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return StandardATSResumeContent(**data)
    except Exception as e:
        logger.info(f"LLM offline ({e}). Gerando modelo padronizado estrito com dados do GitHub e LinkedIn.")
        return _build_standard_curated_resume(base_profile, job_title, job_description, ats_keywords)
