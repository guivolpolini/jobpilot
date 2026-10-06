from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.entities import Job, JobMatch, CandidateProfile, Application, ApplicationStatus
from app.schemas.job import (
    JobCreate, JobResponse, JobMatchResponse,
    CandidateProfileCreate, CandidateProfileResponse,
    ApplicationCreate, ApplicationResponse
)
from app.workers.match_worker import process_job_matching
from app.workers.automation_worker import execute_application_automation

router = APIRouter()


# --- Rotas de Perfil ---
@router.post("/profiles", response_model=CandidateProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate_profile(
    profile_in: CandidateProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    profile = CandidateProfile(**profile_in.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/profiles/{profile_id}", response_model=CandidateProfileResponse)
async def get_candidate_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).where(CandidateProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return profile


# --- Rotas de Vagas ---
@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_in: JobCreate,
    candidate_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    job = Job(**job_in.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Se informado candidate_id, dispara worker assíncrono para match imediato
    if candidate_id:
        process_job_matching.delay(job_id=job.id, candidate_id=candidate_id)

    return job


@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).order_by(desc(Job.created_at)).offset(skip).limit(limit))
    return result.scalars().all()


# --- Rotas de Análise / Match ---
@router.post("/jobs/{job_id}/match/{candidate_id}")
async def trigger_job_match(
    job_id: int,
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    candidate = (await db.execute(select(CandidateProfile).where(CandidateProfile.id == candidate_id))).scalar_one_or_none()
    
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Vaga ou perfil não encontrado")

    task = process_job_matching.delay(job_id=job_id, candidate_id=candidate_id)
    return {
        "message": "Processamento de match agendado com sucesso no Celery",
        "task_id": task.id
    }


@router.get("/jobs/{job_id}/matches", response_model=List[JobMatchResponse])
async def get_job_matches(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobMatch).where(JobMatch.job_id == job_id))
    return result.scalars().all()


# --- Endpoint de 1 Clique (One-Click Quick Apply Trigger) ---
@router.get("/apply/{job_id}")
async def quick_apply_trigger(
    job_id: int,
    candidate_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint acessado pelo link da planilha ou dashboard.
    Registra a intenção de candidatura e enfileira worker de automação.
    """
    job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    # Verifica se já existe candidatura
    res = await db.execute(
        select(Application).where(Application.job_id == job_id, Application.candidate_id == candidate_id)
    )
    application = res.scalar_one_or_none()

    if not application:
        application = Application(
            candidate_id=candidate_id,
            job_id=job_id,
            status=ApplicationStatus.TO_APPLY,
            notes="Disparado via One-Click Link"
        )
        db.add(application)
        await db.commit()
        await db.refresh(application)

    # Dispara worker assíncrono do Playwright
    execute_application_automation.delay(application_id=application.id)

    return {
        "status": "success",
        "message": f"Candidatura para '{job.title}' na empresa '{job.company}' enfileirada!",
        "job_url": job.job_url,
        "application_id": application.id
    }
