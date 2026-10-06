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


class TailoredResumeContent(BaseModel):
    full_name: str
    email: str
    phone: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    professional_summary: str = Field(description="Resumo profissional de alto impacto alinhado com a vaga")
    highlighted_skills: List[str] = Field(description="Competências técnicas reais ordenadas por relevância para a vaga")
    experiences: List[Dict[str, Any]] = Field(description="Experiências profissionais e realizações destacadas")
    projects: List[Dict[str, Any]] = Field(default_factory=list, description="Projetos reais do GitHub com links e tecnologias")
    education: List[Dict[str, Any]] = Field(description="Formação acadêmica e certificações")


def _generate_curated_fallback(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> TailoredResumeContent:
    """
    Gera um currículo de alta qualidade cirúrgico baseado no perfil real do GitHub e LinkedIn,
    mesmo quando o serviço de LLM externo não estiver disponível localmente.
    """
    desc_lower = (job_description + " " + job_title).lower()

    # Identifica tecnologias da vaga presentes no perfil real de Guilherme
    all_known_skills = [
        "Python", "FastAPI", "Java", "SQLAlchemy", "Pydantic", "APIs REST",
        "MySQL", "PostgreSQL", "MongoDB", "Docker", "Git", "GitHub", "pytest",
        "React", "Next.js", "TypeScript", "JavaScript", "Tailwind CSS",
        "Google Gemini API", "Inteligência Artificial", "Linux", "POO", "Supabase"
    ]

    matched_skills = []
    other_skills = []
    for skill in all_known_skills:
        if skill.lower() in desc_lower:
            matched_skills.append(skill)
        else:
            other_skills.append(skill)

    # Ordena com as tecnologias mais relevantes para a vaga primeiro
    prioritized_skills = matched_skills + other_skills[:max(0, 14 - len(matched_skills))]
    if not prioritized_skills:
        prioritized_skills = base_profile.get("skills", ["Python", "FastAPI", "Git", "SQL"])

    # Adaptar o Resumo Profissional focado na vaga específica
    is_estagio_or_jr = any(k in desc_lower for k in ["estágio", "estagio", "júnior", "junior", "trainee", "início"])
    role_target = "Estágio em Desenvolvimento de Software" if is_estagio_or_jr else f"Desenvolvimento de Software ({job_title})"

    summary = (
        f"Estudante de Ciência da Computação no Instituto Mauá de Tecnologia (IMT) com foco em {role_target}. "
        f"Experiência prática na construção de APIs RESTful resilientes, microsserviços e integração com modelos de Inteligência Artificial generativa. "
        f"Desenvolvedor web freelancer com projetos reais em produção (VolpoTech), aplicando boas práticas de código limpo, arquitetura desacoplada e modelagem de bancos relacionais e NoSQL."
    )

    # Filtrar e priorizar projetos do GitHub que têm conexão direta com os requisitos da vaga
    catalog_projects = [
        {
            "name": "Assistente de Estudos com IA",
            "technologies": "Python, FastAPI, SQLAlchemy, Google Gemini API, pytest",
            "url": "https://github.com/guivolpolini/ai-study-assistant",
            "description": "Plataforma web que transforma PDFs em resumos, quizzes e chat inteligente. Backend modular em FastAPI com Pydantic, prompts estruturados para IA generativa e testes unitários automatizados com pytest (mocks)."
        },
        {
            "name": "JobPilot - Automação & Matching ATS",
            "technologies": "Python, FastAPI, Next.js, Celery, Redis, Playwright",
            "url": "https://github.com/guivolpolini/jobpilot",
            "description": "Plataforma de automação de monitoramento de oportunidades com análise semântica de compatibilidade, geração dinâmica de currículos otimizados para ATS e pipeline assíncrono de mensageria."
        },
        {
            "name": "E-Commerce Full Stack & API REST",
            "technologies": "FastAPI, MySQL, SQLAlchemy, JWT, React, Next.js",
            "url": "https://github.com/guivolpolini/ecommerce-api",
            "description": "Sistema completo de comércio eletrônico com autenticação segura JWT, controle de rotas protegidas, catálogo de produtos e integração com checkout de pagamentos MercadoPago."
        },
        {
            "name": "SaaS Barbearia & Agendamento Digital",
            "technologies": "React, Vite, TypeScript, Tailwind CSS, Supabase, n8n",
            "url": "https://github.com/guivolpolini/saas-barbearia",
            "description": "MVP de agendamento online com arquitetura multiempresa, persistência em Postgres via Supabase e automações em tempo real com webhooks."
        },
        {
            "name": "DigestiveQuest - Jogo Educativo em Java",
            "technologies": "Java, Programação Orientada a Objetos (POO)",
            "url": "https://github.com/guivolpolini/DigestiveQuest",
            "description": "Projeto desenvolvido em equipe aplicando conceitos avançados de POO, lógica de programação e modelagem de entidades para apoiar a aprendizagem de 50 estudantes do Colégio Piaget."
        }
    ]

    # Ordena projetos trazendo para o topo os que casam com o stack da vaga
    def score_proj(p):
        score = 0
        techs = p["technologies"].lower()
        for s in prioritized_skills[:6]:
            if s.lower() in techs:
                score += 2
        return score

    catalog_projects.sort(key=score_proj, reverse=True)
    selected_projects = catalog_projects[:3]

    # Experiências reais
    experiences = [
        {
            "role": "Desenvolvedor Web Freelance",
            "company": "VolpoTech / Autônomo",
            "period": "2024 - Presente",
            "achievements": [
                "Criação e implantação de plataformas web responsivas focadas em alta conversão e presença digital de comércios locais.",
                "Implementação de fluxos automatizados com webhooks, APIs REST e integrações via WhatsApp e n8n.",
                "Entrega de projetos com React, Next.js, TypeScript e persistência em bancos relacionais."
            ]
        },
        {
            "role": "Desenvolvedor de Software (Projetos & Portfólio Open Source)",
            "company": "GitHub: github.com/guivolpolini",
            "period": "2024 - Presente",
            "achievements": [
                f"Construção de aplicações completas destacando {', '.join(prioritized_skills[:4])}, respeitando princípios SOLID e separação de camadas.",
                "Criação de pipelines de dados, tratamento de payloads JSON com Pydantic e persistência eficiente com SQLAlchemy/Postgres/MySQL.",
                "Desenvolvimento com cobertura de testes unitários (pytest) e práticas modernas de Git / GitHub Actions."
            ]
        }
    ]

    education = [
        {
            "degree": "Bacharelado em Ciência da Computação",
            "institution": "Instituto Mauá de Tecnologia (IMT)",
            "year": "Previsão de conclusão: Dez/2028"
        },
        {
            "degree": "Certificação Java Programmer (Oracle) & CC50 (Harvard / Fundação Estudar)",
            "institution": "Oracle / Harvard CC50 / Fundação Bradesco",
            "year": "2024 - 2025"
        }
    ]

    return TailoredResumeContent(
        full_name=base_profile.get("full_name") or "Guilherme Volpolini",
        email=base_profile.get("email") or "guilherme.volpolini@gmail.com",
        phone=base_profile.get("phone") or "(11) 98765-4321",
        linkedin_url=base_profile.get("linkedin_url") or "https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
        github_url=base_profile.get("github_url") or "https://github.com/guivolpolini",
        portfolio_url=base_profile.get("portfolio_url") or "https://github.com/guivolpolini",
        professional_summary=summary,
        highlighted_skills=prioritized_skills,
        experiences=experiences,
        projects=selected_projects,
        education=education
    )


def generate_tailored_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> TailoredResumeContent:
    """
    Gera currículo cirurgicamente adaptado para a vaga alvo
    incorporando informações do perfil, GitHub e LinkedIn.
    """
    prompt = f"""
Você é um especialista sênior em Recrutamento Técnico e otimização para sistemas ATS.
Sua missão é customizar o currículo do candidato para a vaga alvo com base nas informações REAIS do seu GitHub e LinkedIn.

=== REGRA DE OURO (SEM ALUCINAÇÕES) ===
- NUNCA invente empresas fictícias ou diplomas falsos.
- Use exclusivamente o histórico do candidato (estudante de Ciência da Computação no Instituto Mauá de Tecnologia, desenvolvedor de projetos no GitHub e freelancer na VolpoTech).
- Destaque os projetos reais do GitHub que mais se conectam com a vaga ({job_title}).

=== PERFIL ORIGINAL ===
{json.dumps(base_profile, ensure_ascii=False, indent=2)}

=== VAGA ALVO ===
Cargo: {job_title}
Descrição:
{job_description}

=== KEYWORDS ATS ===
{json.dumps(ats_keywords, ensure_ascii=False)}

=== SCHEMA JSON DE RESPOSTA ===
{{
  "full_name": "{base_profile.get('full_name', 'Guilherme Volpolini')}",
  "email": "{base_profile.get('email', 'guilherme.volpolini@gmail.com')}",
  "phone": "{base_profile.get('phone', '(11) 98765-4321')}",
  "linkedin_url": "{base_profile.get('linkedin_url', 'https://www.linkedin.com/in/guilherme-volpolini-a60961312/')}",
  "github_url": "{base_profile.get('github_url', 'https://github.com/guivolpolini')}",
  "portfolio_url": "{base_profile.get('portfolio_url', 'https://github.com/guivolpolini')}",
  "professional_summary": "Resumo de 3 a 4 linhas focado no cargo...",
  "highlighted_skills": ["Python", "FastAPI", "Java", "SQL"],
  "experiences": [
    {{
      "role": "Desenvolvedor Web Freelance",
      "company": "VolpoTech / Autônomo",
      "period": "2024 - Presente",
      "achievements": ["..."]
    }}
  ],
  "projects": [
    {{
      "name": "Nome do Projeto no GitHub",
      "technologies": "Stack utilizada",
      "url": "https://github.com/guivolpolini/...",
      "description": "O que faz e realizações técnicas alcançadas"
    }}
  ],
  "education": [
    {{
      "degree": "Bacharelado em Ciência da Computação",
      "institution": "Instituto Mauá de Tecnologia (IMT)",
      "year": "Previsão de conclusão: Dez/2028"
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente de carreira especializado em ATS que responde exclusivamente com JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return TailoredResumeContent(**data)
    except Exception as e:
        logger.info(f"LLM indisponível ou offline ({e}). Aplicando gerador de currículo inteligente baseado no GitHub e LinkedIn.")
        return _generate_curated_fallback(base_profile, job_title, job_description, ats_keywords)
