import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.core.config import settings
from app.schemas.job import JobMatchAnalysisResult

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=settings.OPENAI_BASE_URL,
    api_key=settings.OPENAI_API_KEY
)


def analyze_job_match(
    candidate_profile: Dict[str, Any],
    job_title: str,
    job_description: str
) -> JobMatchAnalysisResult:
    """
    Envia o perfil do candidato e a descrição da vaga para o LLM.
    Retorna análise estruturada com score (0-100), skills coincidentes, faltantes e recomendações.
    """
    prompt = f"""
Você é um especialista sênior em Recrutamento Técnico e sistemas ATS (Applicant Tracking System).
Sua missão é avaliar a compatibilidade real e honesta entre um candidato e uma vaga de emprego.

=== DADOS DO CANDIDATO ===
Nome: {candidate_profile.get('full_name')}
Resumo: {candidate_profile.get('summary')}
Habilidades: {json.dumps(candidate_profile.get('skills', []), ensure_ascii=False)}
Experiências: {json.dumps(candidate_profile.get('experiences', []), ensure_ascii=False)}
Educação: {json.dumps(candidate_profile.get('education', []), ensure_ascii=False)}

=== VAGA DE EMPREGO ===
Título: {job_title}
Descrição:
{job_description}

=== INSTRUÇÕES E REGRAS ===
1. Avalie de forma realista o score de 0 a 100%.
   - Não infle a nota.
   - 0-40%: Incompatível / Faltam fundamentos essenciais da vaga.
   - 41-70%: Compatibilidade moderada / Tem base mas faltam requisitos importantes.
   - 71-100%: Forte compatibilidade / Perfil preenche os requisitos principais.
2. Identifique exatamente quais competências o candidato possui e quais estão faltando.
3. Forneça palavras-chave cruciais (ATS keywords) presentes na vaga que o candidato deve enfatizar no currículo.
4. Responda ESTRITAMENTE em formato JSON compatível com o schema abaixo:

{{
  "score": 85,
  "summary_fit": "O candidato possui ótima base técnica em Python e bancos relacionais, mas precisa comprovar vivência em Docker.",
  "matching_skills": ["Python", "SQL", "FastAPI"],
  "missing_skills": ["Docker", "Kubernetes"],
  "recommendations": ["Destacar projetos pessoais com APIs no resumo", "Subir repositório no GitHub demonstrando testes"],
  "ats_keywords_to_highlight": ["FastAPI", "PostgreSQL", "Clean Architecture", "RESTful API"]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente técnico que avalia vagas e currículos retornando exclusivamente JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return JobMatchAnalysisResult(**data)
    except Exception as e:
        logger.error(f"Erro ao analisar match via LLM: {e}")
        # Fallback de segurança se LLM local estiver temporariamente fora
        return JobMatchAnalysisResult(
            score=50,
            summary_fit="Análise preliminar em modo de contingência.",
            matching_skills=[],
            missing_skills=[],
            recommendations=["Verifique a descrição completa da vaga."],
            ats_keywords_to_highlight=[]
        )
