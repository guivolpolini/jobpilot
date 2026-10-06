import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.entities import Job, CandidateProfile, JobMatch
from app.services.llm_matcher import analyze_job_match
from app.services.resume_optimizer import generate_tailored_resume
from app.services.pdf_generator import generate_and_save_tailored_pdf
from app.services.sheets_sync import GoogleSheetsService

logger = logging.getLogger(__name__)

# Engine síncrona para workers Celery
sync_engine = create_engine(settings.DATABASE_SYNC_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

sheets_service = GoogleSheetsService()


@celery_app.task(name="tasks.process_job_matching", bind=True, max_retries=3)
def process_job_matching(self, job_id: int, candidate_id: int):
    """
    Pipeline Completo do Worker Celery:
    1. Busca vaga e perfil do candidato.
    2. Calcula Match Score (0-100%) e extrai ATS keywords via LLM.
    3. Se match >= 60%, otimiza o currículo cirurgicamente sem alucinação e gera PDF ATS.
    4. Sincroniza linha completa com o Google Sheets com o link de 1 clique.
    5. Persiste dados no PostgreSQL.
    """
    logger.info(f"Iniciando pipeline de processamento para Job ID={job_id} e Candidato ID={candidate_id}")
    session = SyncSessionLocal()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        candidate = session.query(CandidateProfile).filter(CandidateProfile.id == candidate_id).first()

        if not job or not candidate:
            logger.error(f"Job ou Candidato não encontrado (job_id={job_id}, candidate_id={candidate_id})")
            return

        candidate_data = {
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "linkedin_url": candidate.linkedin_url,
            "github_url": candidate.github_url,
            "portfolio_url": candidate.portfolio_url,
            "summary": candidate.summary,
            "skills": candidate.skills,
            "experiences": candidate.experiences,
            "education": candidate.education,
        }

        # 1. Matcher da IA
        analysis = analyze_job_match(
            candidate_profile=candidate_data,
            job_title=job.title,
            job_description=job.raw_description
        )

        tailored_pdf_url = None

        # 2. Se score for promissor (>= 60%), gera currículo customizado ATS em PDF
        if analysis.score >= 60:
            logger.info(f"Match alto ({analysis.score}%). Otimizando currículo para ATS...")
            tailored_resume = generate_tailored_resume(
                base_profile=candidate_data,
                job_title=job.title,
                job_description=job.raw_description,
                ats_keywords=analysis.ats_keywords_to_highlight
            )
            tailored_pdf_url = generate_and_save_tailored_pdf(
                resume_data=tailored_resume,
                job_id=job.id,
                candidate_id=candidate.id
            )
            logger.info(f"PDF ATS gerado com sucesso: {tailored_pdf_url}")

        # 3. Atualiza ou cria JobMatch no banco relacional
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
                recommendations=analysis.recommendations,
                tailored_resume_url=tailored_pdf_url
            )
            session.add(job_match)
        else:
            job_match.score = analysis.score
            job_match.summary_fit = analysis.summary_fit
            job_match.matching_skills = analysis.matching_skills
            job_match.missing_skills = analysis.missing_skills
            job_match.recommendations = analysis.recommendations
            if tailored_pdf_url:
                job_match.tailored_resume_url = tailored_pdf_url

        session.commit()

        # 4. Sincroniza linha no Google Sheets com link de 1 clique
        sheets_service.sync_job_row(
            job_id=job.id,
            company=job.company,
            role=job.title,
            match_score=analysis.score,
            job_url=job.job_url,
            resume_pdf_url=tailored_pdf_url or "N/A",
            status="Pronto para Envio"
        )

        logger.info(f"Pipeline finalizado com sucesso para Job ID={job_id}!")
        return {"job_id": job_id, "score": analysis.score, "pdf_url": tailored_pdf_url}

    except Exception as exc:
        session.rollback()
        logger.error(f"Erro no pipeline do worker: {exc}")
        raise self.retry(exc=exc, countdown=15)
    finally:
        session.close()
