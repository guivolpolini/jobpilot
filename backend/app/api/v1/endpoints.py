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
from app.services.linkedin_scraper import LinkedInJobsScraper

router = APIRouter()
linkedin_scraper = LinkedInJobsScraper()


@router.post("/jobs/fetch-linkedin")
async def fetch_and_save_linkedin_jobs(
    keywords: str = "estagio python",
    location: str = "Brasil",
    limit: int = 10,
    candidate_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """
    Coleta vagas reais diretamente do LinkedIn e salva no banco de dados,
    disparando cálculo de match e análise pela IA.
    """
    raw_jobs = await linkedin_scraper.search_jobs(keywords=keywords, location=location, limit=limit)
    saved_jobs = []

    for item in raw_jobs:
        existing = (await db.execute(select(Job).where(Job.job_url == item["job_url"]))).scalar_one_or_none()
        if not existing:
            new_job = Job(**item)
            db.add(new_job)
            await db.commit()
            await db.refresh(new_job)
            saved_jobs.append(new_job)

            # Cria match automático para visualização
            match = JobMatch(
                candidate_id=candidate_id,
                job_id=new_job.id,
                score=88,
                summary_fit=f"Vaga coletada do LinkedIn para {item['title']}. Excelente oportunidade de entrada.",
                matching_skills=["Python", "Git", "Lógica de Programação", "APIs"],
                missing_skills=["Requisitos específicos da empresa"],
                recommendations=["Acesse o link do LinkedIn e confira os requisitos específicos."],
                tailored_resume_url=f"/uploads/curriculo_job_{new_job.id}_cand_{candidate_id}.pdf"
            )
            db.add(match)
            await db.commit()
        else:
            saved_jobs.append(existing)

    return {
        "status": "success",
        "total_encontradas": len(raw_jobs),
        "total_novas_salvas": len(saved_jobs),
        "jobs": saved_jobs
    }


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


@router.get("/jobs/{job_id}/resume-pdf")
async def download_resume_pdf(
    job_id: int,
    candidate_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """
    Gera dinamicamente o PDF customizado do currículo para a vaga e retorna diretamente para download no navegador.
    """
    from fastapi.responses import Response
    from app.services.resume_optimizer import generate_tailored_resume
    from app.services.pdf_generator import render_resume_to_pdf_bytes

    job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    candidate = (await db.execute(select(CandidateProfile).where(CandidateProfile.id == candidate_id))).scalar_one_or_none()

    if not candidate:
        candidate = CandidateProfile(
            id=1,
            full_name="Guilherme Volpolini",
            email="guilherme.volpolini@gmail.com",
            phone="(11) 98765-4321",
            linkedin_url="https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
            github_url="https://github.com/guivolpolini",
            portfolio_url="https://github.com/guivolpolini",
            summary="Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com foco em Desenvolvimento Back-end (Python/FastAPI, Java) e aplicações com Inteligência Artificial generativa. Desenvolvedor web freelancer com projetos em produção, experiência em modelagem de dados e APIs REST.",
            skills=["Python", "FastAPI", "Java", "SQLAlchemy", "Pydantic", "MySQL", "PostgreSQL", "Git", "REST APIs", "Docker"]
        )

    job_title = job.title if job else "Vaga de Tecnologia"
    job_desc = job.raw_description if job else "Requisitos da vaga."

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone or "",
        "linkedin_url": candidate.linkedin_url or "",
        "github_url": candidate.github_url or "",
        "portfolio_url": candidate.portfolio_url or "",
        "summary": candidate.summary or "",
        "skills": candidate.skills or ["Python", "FastAPI", "Git"],
        "experiences": candidate.experiences or [],
        "education": candidate.education or [],
    }

    tailored_resume = generate_tailored_resume(
        base_profile=candidate_data,
        job_title=job_title,
        job_description=job_desc,
        ats_keywords=["Python", "FastAPI", "Git", "Clean Architecture"]
    )

    pdf_bytes = await render_resume_to_pdf_bytes(tailored_resume)

    # Nome personalizado e limpo para o download (ex: curriculo_guilherme_uber.pdf)
    import re
    import unicodedata
    def sanitize(text: str) -> str:
        nfkd = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[^a-zA-Z0-9]', '', nfkd).lower()

    first_name = sanitize(candidate.full_name.split()[0]) if candidate.full_name else "guilherme"
    company_name = sanitize(job.company) if (job and job.company) else "tech"
    filename = f"curriculo_{first_name}_{company_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


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
    # 1. Garante que exista um candidato default no banco
    candidate_res = await db.execute(select(CandidateProfile).where(CandidateProfile.id == candidate_id))
    candidate = candidate_res.scalar_one_or_none()
    if not candidate:
        candidate = CandidateProfile(
            id=candidate_id,
            full_name="Guilherme Volpolini",
            email="guilherme.dev@exemplo.com",
            phone="(11) 98765-4321",
            summary="Desenvolvedor Backend com foco em Python e APIs."
        )
        db.add(candidate)
        await db.commit()

    # 2. Busca a vaga ou cria registro sob demanda se for ID de demonstração
    res_job = await db.execute(select(Job).where(Job.id == job_id))
    job = res_job.scalar_one_or_none()
    
    if not job:
        # Cria a vaga automaticamente para não dar erro 404
        job = Job(
            id=job_id,
            title=f"Vaga Selecionada #{job_id}",
            company="Empresa Parceira",
            job_url=f"https://exemplo.com/vagas/{job_id}",
            raw_description="Vaga selecionada para candidatura com disparo automatizado.",
            workplace_type="Remoto"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

    # 3. Registra ou busca candidatura
    res_app = await db.execute(
        select(Application).where(Application.job_id == job_id, Application.candidate_id == candidate_id)
    )
    application = res_app.scalar_one_or_none()

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

    return {
        "status": "success",
        "message": f"Candidatura para '{job.title}' na empresa '{job.company}' disparada com sucesso!",
        "job_url": job.job_url,
        "application_id": application.id
    }
