from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.entities import ApplicationStatus


# --- Schemas de Perfil do Candidato ---
class CandidateProfileBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experiences: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    languages: List[Dict[str, Any]] = []


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Schemas de Vaga ---
class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    workplace_type: Optional[str] = "Remoto"
    job_url: str
    source: Optional[str] = "manual"
    salary: Optional[str] = None
    raw_description: str


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    extracted_skills: List[str] = []
    extracted_requirements: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Schemas de Match e Análise da IA ---
class JobMatchAnalysisResult(BaseModel):
    """Estrutura esperada do retorno da IA (Structured Output via LLM)"""
    score: int = Field(ge=0, le=100, description="Score de compatibilidade de 0 a 100")
    summary_fit: str = Field(description="Resumo claro de por que o candidato combina ou não")
    matching_skills: List[str] = Field(default=[], description="Habilidades e requisitos que o candidato atende")
    missing_skills: List[str] = Field(default=[], description="Requisitos que o candidato não possui no perfil")
    recommendations: List[str] = Field(default=[], description="Como adaptar ou focar para essa vaga")
    ats_keywords_to_highlight: List[str] = Field(default=[], description="Palavras-chave vitais para passar pelo filtro ATS")


class JobMatchResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    score: int
    summary_fit: str
    matching_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
    tailored_resume_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Schemas de Candidatura (Application) ---
class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int
    status: Optional[ApplicationStatus] = ApplicationStatus.TO_APPLY
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    automation_logs: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
