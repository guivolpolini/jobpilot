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
                email="guilherme.volpolini@gmail.com",
                phone="(11) 98765-4321",
                linkedin_url="https://www.linkedin.com/in/guilherme-volpolini-a60961312/",
                github_url="https://github.com/guivolpolini",
                portfolio_url="https://github.com/guivolpolini",
                summary="Estudante de Ciência da Computação no Instituto Mauá de Tecnologia com foco em Desenvolvimento Back-end (Python/FastAPI, Java) e aplicações com Inteligência Artificial generativa. Desenvolvedor web freelancer com projetos em produção, experiência em modelagem de dados e APIs REST.",
                skills=[
                    "Python", "FastAPI", "Java", "SQLAlchemy", "Pydantic",
                    "MySQL", "PostgreSQL", "MongoDB", "APIs REST", "Docker",
                    "JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS",
                    "Git", "GitHub", "pytest", "Google Gemini API", "Linux"
                ],
                experiences=[
                    {
                        "role": "Desenvolvedor Web Freelance",
                        "company": "VolpoTech / Autônomo",
                        "period": "2024 - Presente",
                        "achievements": [
                            "Desenvolve websites e aplicações web responsivas de alta conversão para pequenos negócios e comércio local.",
                            "Implementa integrações de APIs REST, webhooks e automação de agendamentos (WhatsApp/n8n).",
                            "Desenvolveu sistemas como SaaS Barbearia (React, Vite, Supabase, n8n) e QR Avalia para automação de reviews no Google."
                        ]
                    },
                    {
                        "role": "Desenvolvedor de Software (Projetos & Portfólio)",
                        "company": "GitHub Open Source / Projetos Pessoais",
                        "period": "2024 - Presente",
                        "achievements": [
                            "Assistente de Estudos com IA: Arquitetura backend em FastAPI + SQLAlchemy + Pydantic com integração da API Google Gemini, extração de texto de PDFs e testes com pytest.",
                            "JobPilot: Plataforma completa de automação de vagas e matching ATS usando FastAPI, Celery, Redis e Playwright headless.",
                            "E-Commerce Full Stack: API REST completa com FastAPI, MySQL, autenticação JWT e integração com MercadoPago.",
                            "DigestiveQuest: Jogo educativo em Java com POO e lógica de programação em equipe apoiando o aprendizado de 50 alunos do Colégio Piaget."
                        ]
                    }
                ],
                education=[
                    {
                        "degree": "Bacharelado em Ciência da Computação",
                        "institution": "Instituto Mauá de Tecnologia (IMT)",
                        "year": "Previsão de conclusão: Dez/2028"
                    },
                    {
                        "degree": "Certificação Java Programmer & CC50 Harvard",
                        "institution": "Oracle / Fundação Estudar",
                        "year": "2024 - 2025"
                    }
                ],
                languages=[{"language": "Português", "level": "Nativo"}, {"language": "Inglês", "level": "Avançado"}]
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
                "job_url": "https://www.linkedin.com/jobs/search/?keywords=Desenvolvedor+Python+Backend+Junior+Fintech+Horizon",
                "salary": "R$ 4.500 - R$ 6.000",
                "source": "LinkedIn",
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
                "job_url": "https://www.linkedin.com/jobs/search/?keywords=Junior+Data+Backend+Developer+DataCorp+Analytics",
                "salary": "R$ 4.800",
                "source": "LinkedIn",
                "raw_description": "Experiência com pipelines de dados, Python, SQL avançado, noções de AWS e familiaridade com LLMs."
            },
            {
                "title": "Estágio em Desenvolvimento Backend (Python)",
                "company": "NextGen Software",
                "location": "São Paulo, SP",
                "workplace_type": "Remoto",
                "job_url": "https://www.linkedin.com/jobs/search/?keywords=Estagio+em+Desenvolvimento+Backend+Python+NextGen+Software",
                "salary": "R$ 2.500 + Benefícios",
                "source": "LinkedIn",
                "raw_description": "Vaga de Estágio para estudantes de TI. Atuará com Python, FastAPI, testes unitários, consumo de APIs e Git. Ambiente focado em aprendizado acelerado."
            },
            {
                "title": "Estágio em Engenharia de Software",
                "company": "Inovare Labs",
                "location": "Florianópolis, SC",
                "workplace_type": "Híbrido",
                "job_url": "https://www.linkedin.com/jobs/search/?keywords=Estagio+em+Engenharia+de+Software+Inovare+Labs",
                "salary": "R$ 2.200",
                "source": "LinkedIn",
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
