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
    professional_summary: str = Field(description="Resumo profissional alinhado com o cargo, sem mentiras")
    highlighted_skills: List[str] = Field(description="Competências técnicas reais ordenadas por relevância para a vaga")
    experiences: List[Dict[str, Any]] = Field(description="Experiências com bullet points ajustados destacando keywords da vaga")
    education: List[Dict[str, Any]] = Field(description="Formação acadêmica")


def generate_tailored_resume(
    base_profile: Dict[str, Any],
    job_title: str,
    job_description: str,
    ats_keywords: List[str]
) -> TailoredResumeContent:
    """
    Adapta cirurgicamente o currículo para passar pelo filtro ATS da vaga:
    - NÃO inventa empresas nem cargos fictícios (regra rígida anti-alucinação).
    - Realça realizações e termos técnicos existentes que conectam com os requisitos.
    """
    prompt = f"""
Você é um especialista em otimização de currículos para sistemas ATS (Applicant Tracking Systems) e RH.
Sua missão é customizar o currículo do candidato especificamente para a vaga informada.

=== REGRA DE OURO (NUNCA INVENTAR DADOS) ===
- NUNCA invente empregos, empresas, datas, certificações ou tecnologias que o candidato NUNCA usou.
- Apenas REFORMULE, REORDENE e ENFATIZE as experiências reais com verbos de ação fortes e palavras-chave que o robô de ATS busca.

=== PERFIL ORIGINAL DO CANDIDATO ===
{json.dumps(base_profile, ensure_ascii=False, indent=2)}

=== VAGA ALVO ===
Cargo: {job_title}
Descrição:
{job_description}

=== PALAVRAS-CHAVE ATS PRIORITÁRIAS ===
{json.dumps(ats_keywords, ensure_ascii=False)}

=== FORMATO DE RESPOSTA ===
Responda ESTRITAMENTE em formato JSON com o schema abaixo:
{{
  "full_name": "{base_profile.get('full_name', '')}",
  "email": "{base_profile.get('email', '')}",
  "phone": "{base_profile.get('phone', '')}",
  "linkedin_url": "{base_profile.get('linkedin_url', '')}",
  "github_url": "{base_profile.get('github_url', '')}",
  "portfolio_url": "{base_profile.get('portfolio_url', '')}",
  "professional_summary": "Resumo conciso de 3 a 4 linhas direcionado para as necessidades do cargo...",
  "highlighted_skills": ["Python", "FastAPI", "SQL", "Docker", "Git"],
  "experiences": [
    {{
      "role": "Desenvolvedor Backend",
      "company": "Nome da Empresa",
      "period": "2023 - Presente",
      "achievements": [
        "Desenvolveu APIs RESTful de alta performance...",
        "Reduziu tempo de resposta de endpoints..."
      ]
    }}
  ],
  "education": [
    {{
      "degree": "Ciência da Computação",
      "institution": "Universidade X",
      "year": "2024"
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente de carreira focado em ATS que responde exclusivamente com JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return TailoredResumeContent(**data)
    except Exception as e:
        logger.error(f"Erro ao otimizar currículo via LLM: {e}")
        # Fallback seguro com perfil original
        return TailoredResumeContent(
            full_name=base_profile.get("full_name", ""),
            email=base_profile.get("email", ""),
            phone=base_profile.get("phone", "") or "",
            linkedin_url=base_profile.get("linkedin_url", "") or "",
            github_url=base_profile.get("github_url", "") or "",
            portfolio_url=base_profile.get("portfolio_url", "") or "",
            professional_summary=base_profile.get("summary", "") or "Profissional dedicado de TI.",
            highlighted_skills=base_profile.get("skills", []),
            experiences=base_profile.get("experiences", []),
            education=base_profile.get("education", [])
        )
