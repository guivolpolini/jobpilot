import re
import unicodedata
from typing import Dict, Any, List


def normalize_str(s: str) -> str:
    if not s:
        return ""
    nfkd = unicodedata.normalize('NFD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn').lower()


def analyze_job_requirements(job_title: str, job_description: str, ats_keywords: List[str] = None):
    t_norm = normalize_str(job_title)
    d_norm = normalize_str(job_description)
    k_norm = " ".join([normalize_str(k) for k in (ats_keywords or [])])
    full_text = f"{t_norm} {d_norm} {k_norm}"

    # 1. Nível da vaga
    is_estagio = any(w in full_text for w in ["estagio", "estagiario", "intern", "estag"])
    is_junior = any(w in full_text for w in ["junior", "jr", "iniciante", "trainee", "entry"])
    
    # 2. Especialidade técnica predominante
    is_data = any(w in full_text for w in ["dados", "data", "analytics", "bi", "sql", "pandas", "analise de dados"])
    is_frontend = any(w in full_text for w in ["frontend", "react", "next", "typescript", "javascript", "tailwind", "css", "html", "web", "ux", "ui"])
    is_python_backend = any(w in full_text for w in ["python", "fastapi", "django", "flask", "microsservicos", "api"])
    is_java_backend = any(w in full_text for w in ["java", "spring", "poo", "orientacao a objetos"])
    is_fullstack = (is_frontend and (is_python_backend or is_java_backend)) or "fullstack" in full_text or "full stack" in full_text
    is_cloud_devops = any(w in full_text for w in ["docker", "devops", "cloud", "aws", "linux", "ci/cd"])

    return {
        "title": job_title,
        "is_estagio": is_estagio,
        "is_junior": is_junior,
        "is_data": is_data,
        "is_frontend": is_frontend,
        "is_python_backend": is_python_backend,
        "is_java_backend": is_java_backend,
        "is_fullstack": is_fullstack,
        "is_cloud_devops": is_cloud_devops,
        "full_text": full_text
    }
