import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, Enum, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    SAVED = "Salva"
    TO_APPLY = "Aplicar"
    APPLIED = "Aplicada"
    INTERVIEW = "Entrevista"
    OFFER = "Oferta"
    REJECTED = "Rejeitada"


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Perfil estruturado para comparação de IA
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    experiences: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    education: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    languages: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    matches: Mapped[List["JobMatch"]] = relationship("JobMatch", back_populates="candidate")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="candidate")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    workplace_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Remoto, Híbrido, Presencial
    job_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), default="manual") # gupy, greenhouse, indeed, etc.
    salary: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Extração de requisitos processada por IA
    extracted_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    extracted_requirements: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    matches: Mapped[List["JobMatch"]] = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="job")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Scores & Análise da IA
    score: Mapped[int] = mapped_column(Integer, nullable=False) # 0 a 100%
    summary_fit: Mapped[str] = mapped_column(Text, nullable=False)
    matching_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # PDF Otimizado para ATS
    tailored_resume_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    candidate: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="matches")
    job: Mapped["Job"] = relationship("Job", back_populates="matches")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.TO_APPLY,
        nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Histórico de automação
    automation_logs: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    candidate: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
