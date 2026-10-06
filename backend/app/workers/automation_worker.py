import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.entities import Application, ApplicationStatus, Job, CandidateProfile
from app.automation.adapters.generic_adapter import GenericATSAdapter

logger = logging.getLogger(__name__)

sync_engine = create_engine(settings.DATABASE_SYNC_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


@celery_app.task(name="tasks.execute_application_automation", bind=True, max_retries=2)
def execute_application_automation(self, application_id: int):
    """
    Worker Celery que executa o preenchimento da candidatura no navegador.
    """
    session = SyncSessionLocal()
    try:
        app_record = session.query(Application).filter(Application.id == application_id).first()
        if not app_record:
            logger.error(f"Application ID={application_id} não encontrada")
            return

        job = session.query(Job).filter(Job.id == app_record.job_id).first()
        candidate = session.query(CandidateProfile).filter(CandidateProfile.id == app_record.candidate_id).first()

        candidate_data = {
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "linkedin_url": candidate.linkedin_url,
            "github_url": candidate.github_url,
        }

        adapter = GenericATSAdapter(target_url=job.job_url)
        preview = adapter.generate_fill_preview(
            candidate_data=candidate_data,
            resume_path=f"./uploads/curriculo_job_{job.id}_cand_{candidate.id}.pdf"
        )

        # Executa automação
        result = asyncio.run(adapter.execute_form_submission(preview, headless=True))

        # Registra log e atualiza status
        logs = app_record.automation_logs or []
        logs.append(result)
        app_record.automation_logs = logs

        if result.get("success"):
            app_record.status = ApplicationStatus.APPLIED
        else:
            app_record.status = ApplicationStatus.TO_APPLY

        session.commit()
        return result
    except Exception as exc:
        session.rollback()
        logger.error(f"Falha na task de automação: {exc}")
        raise self.retry(exc=exc, countdown=30)
    finally:
        session.close()
