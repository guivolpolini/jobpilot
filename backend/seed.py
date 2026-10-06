import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.entities import CandidateProfile, Job, JobMatch
from app.services.llm_matcher import analyze_job_match
from app.services.resume_optimizer import generate_tailored_resume
from app.services.pdf_generator import generate_and_save_tailored_pdf


async def seed_database():
    print("[OK] Criando tabelas no banco de dados...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Verifica ou cria Perfil Base do Candidato
        res_profile = await session.execute(select(CandidateProfile).where(CandidateProfile.email == "guilherme.dev@exemplo.com"))
        candidate = res_profile.scalar_one_or_none()

        if not candidate:
            print("[OK] Criando perfil base do candidato...")
            candidate = CandidateProfile(
                full_name="Guilherme Volpolini",
                email="guilherme.dev@exemplo.com",
                phone="(11) 98765-4321",
                linkedin_url="https://linkedin.com/in/guilherme",
                github_url="https://github.com/guivolpolini",
                portfolio_url="https://github.com/guivolpolini/jobpilot",
                summary="Desenvolvedor Backend com foco em Python, FastAPI, microsserviços, mensageria com Redis/Celery e modelagem de bancos de dados relacionais.",
                skills=[
                    "Python", "FastAPI", "PostgreSQL", "SQLAlchemy", 
                    "Redis", "Celery", "Docker", "Git", "Playwright", "RESTful APIs"
                ],
                experiences=[
                    {
                        "role": "Desenvolvedor Backend (Projetos & Freelance)",
                        "company": "Projetos Pessoais & Open Source",
                        "period": "2023 - Presente",
                        "achievements": [
                            "Desenvolveu arquitetura completa da plataforma JobPilot integrando FastAPI, Celery e PostgreSQL.",
                            "Implementou pipeline assíncrono de mensageria com Redis para processamento de background jobs.",
                            "Construiu APIs RESTful estruturadas com Pydantic v2 e validação rigorosa de dados."
                        ]
                    }
                ],
                education=[
                    {
                        "degree": "Análise e Desenvolvimento de Sistemas / Ciência da Computação",
                        "institution": "Universidade",
                        "year": "2025"
                    }
                ],
                languages=[{"language": "Português", "level": "Nativo"}, {"language": "Inglês", "level": "Intermediário/Técnico"}]
            )
            session.add(candidate)
            await session.commit()
            await session.refresh(candidate)

        # 2. Vagas de Exemplo Realistas
        sample_jobs = [
            {
                "title": "Desenvolvedor Python Backend Júnior",
                "company": "Fintech Horizon",
                "location": "São Paulo, SP",
                "workplace_type": "Remoto",
                "job_url": "https://exemplo.com/vagas/fintech-horizon-python-jr",
                "salary": "R$ 4.500 - R$ 6.000",
                "source": "Greenhouse",
                "raw_description": (
                    "Procuramos Desenvolvedor Python Júnior para nosso time de pagamentos. "
                    "Requisitos essenciais: Python 3, vivência com FastAPI ou Flask, bancos relacionais (PostgreSQL), "
                    "boas práticas de versionamento com Git e familiaridade com APIs REST. "
                    "Desejável: Docker, Redis ou mensageria assíncrona."
                )
            },
            {
                "title": "Junior Data & Backend Developer",
                "company": "DataCorp Analytics",
                "location": "Belo Horizonte, MG",
                "workplace_type": "Remoto",
                "job_url": "https://exemplo.com/vagas/datacorp-dev",
                "salary": "R$ 4.800",
                "source": "Manual",
                "raw_description": "Experiência com pipelines de dados, Python, SQL avançado, noções de AWS e familiaridade com LLMs."
            },
            {
                "title": "Estágio em Desenvolvimento Backend (Python)",
                "company": "NextGen Software",
                "location": "São Paulo, SP",
                "workplace_type": "Remoto",
                "job_url": "https://exemplo.com/vagas/nextgen-estagio-python",
                "salary": "R$ 2.500 + Benefícios",
                "source": "Gupy",
                "raw_description": "Vaga de Estágio para estudantes de TI. Atuará com Python, FastAPI, testes unitários, consumo de APIs e Git. Ambiente focado em aprendizado acelerado."
            },
            {
                "title": "Estágio em Engenharia de Software",
                "company": "Inovare Labs",
                "location": "Florianópolis, SC",
                "workplace_type": "Híbrido",
                "job_url": "https://exemplo.com/vagas/inovare-estagio-eng",
                "salary": "R$ 2.200",
                "source": "Gupy",
                "raw_description": "Oportunidade de estágio técnico. Requisitos: lógica de programação sólida, Python ou JavaScript, bancos SQL e vontade de aprender microsserviços."
            }
        ]

        for j_data in sample_jobs:
            res_job = await session.execute(select(Job).where(Job.job_url == j_data["job_url"]))
            job = res_job.scalar_one_or_none()

            if not job:
                print(f"[OK] Cadastrando vaga: {j_data['title']} ({j_data['company']})...")
                job = Job(**j_data)
                session.add(job)
                await session.commit()
                await session.refresh(job)

                # Cria Match inicial para demonstração
                match = JobMatch(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    score=88 if "Horizon" in job.company else 82,
                    summary_fit="Excelente compatibilidade técnica com a stack requerida (Python, FastAPI, PostgreSQL e Filas).",
                    matching_skills=["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Git", "Redis"],
                    missing_skills=["Vivência prévia em pagamentos", "Docker em produção"],
                    recommendations=[
                        "Destaque o projeto JobPilot no topo do currículo.",
                        "Enfatize os testes de integração e o uso do Celery."
                    ],
                    tailored_resume_url=f"/uploads/curriculo_job_{job.id}_cand_{candidate.id}.pdf"
                )
                session.add(match)
                await session.commit()

        print("[OK] Banco de dados populado com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed_database())
