import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.entities import Job, CandidateProfile, JobMatch
from app.services.llm_matcher import analyze_job_match

logger = logging.getLogger(__name__)

# Engine síncrona para workers Celery
sync_engine = create_engine(settings.DATABASE_SYNC_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


@celery_app.task(name="tasks.process_job_matching", bind=True, max_retries=3)
def process_job_matching(self, job_id: int, candidate_id: int):
    """
    Worker Celery assíncrono:
    1. Busca vaga e perfil do candidato no banco.
    2. Roda a análise de compatibilidade via LLM.
    3. Persiste o score e gaps em JobMatch.
    """
    logger.info(f"Iniciando match para Job ID={job_id} e Candidato ID={candidate_id}")
    session = SyncSessionLocal()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        candidate = session.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()

        if not job or not candidate:
            logger.error(f"Job ou Candidato não encontrado (job_id={job_id}, candidate_id={candidate_id})")
            return

        candidate_data = {
            "full_name": candidate.full_name,
            "summary": candidate.summary,
            "skills": candidate.skills,
            "experiences": candidate.experiences,
            "education": candidate.education,
        }

        # Chamada ao LLM Matcher
        analysis = analyze_job_match(
            candidate_profile=candidate_data,
            job_title=job.title,
            job_description=job.raw_description
        )

        # Atualiza ou cria JobMatch
        job_match = session.query(JobMatch).filter(
            JobMatch.job_id == job_id,
            JobMatch.candidate_id == candidate_id
        ).first()

        if not job_match:
            job_match = JobMatch(
                job_id=job_id,
                candidate_id=candidate_id,
                score=analysis.score,
                summary_fit=analysis.summary_fit,
                matching_skills=analysis.matching_skills,
                missing_skills=analysis.missing_skills,
                recommendations=analysis.recommendations
            )
            session.add(job_match)
        else:
            job_match.score = analysis.score
            job_match.summary_fit = analysis.summary_fit
            job_match.matching_skills = analysis.matching_skills
            job_match.missing_skills = analysis.missing_skills
            job_match.recommendations = analysis.recommendations

        session.commit()
        logger.info(f"Match concluído: Job ID={job_id} Score={analysis.score}%")
        return {"job_id": job_id, "score": analysis.score}

    except Exception as exc:
        session.rollback()
        logger.error(f"Erro ao processar match: {exc}")
        raise self.retry(exc=exc, countdown=10)
    finally:
        session.close()
