# JobPilot — Plataforma de Inteligência e Automação de Candidaturas

O **JobPilot** é uma plataforma que analisa descrições de vagas de emprego, calcula a compatibilidade real (Score 0-100%) com o perfil do candidato via IA, destaca gaps de habilidades e prepara currículos otimizados para ATS.

---

## 🏗️ Arquitetura do Sistema

```
[Fontes de Vagas] ──► [FastAPI Backend] ──► [PostgreSQL & Redis]
                             │
                             ▼
                   [Celery Workers]
                    ├── LLM Matcher (Structured Pydantic Output)
                    ├── ATS Resume Generator (PDF)
                    └── One-Click Trigger & Google Sheets Sync
```

* **Backend**: Python 3.12+ com FastAPI e Pydantic v2.
* **ORM & Banco**: SQLAlchemy 2.0 (Async) + PostgreSQL.
* **Filas & Tarefas Assíncronas**: Redis + Celery.
* **Storage Modular**: Interface desacoplada (`LocalStorageService` para dev, `S3StorageService` para produção/AWS).
* **LLM Engine**: OpenAI API-compatible (FreeLLMAPI em `http://localhost:3001/v1` ou OpenAI).
* **Frontend**: Next.js 14 + Tailwind CSS (em desenvolvimento).

---

## 🚀 Como Executar

### 1. Subir Infraestrutura (Docker)
```bash
docker compose up -d
```
Isso iniciará:
* **PostgreSQL**: porta `5432`
* **Redis**: porta `6379`
* **MinIO (S3 compatível)**: porta `9000` (Console Web em `http://localhost:9001`)

### 2. Configurar o Backend
Crie e ative um ambiente virtual:
```bash
cd backend
python -m venv venv
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

Copie as variáveis de ambiente:
```bash
cp ../.env.example .env
```

### 3. Executar o Servidor FastAPI
```bash
uvicorn app.main:app --reload --port 8000
```
Documentação interativa Swagger disponível em: `http://localhost:8000/api/v1/docs`

### 4. Executar o Worker Celery
Em outro terminal:
```bash
celery -A app.core.celery_app worker --loglevel=info
```

---

## 📌 Principais Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/profiles` | Cadastra perfil profissional estruturado |
| `POST` | `/api/v1/jobs` | Cadastra nova vaga (dispara match assíncrono) |
| `POST` | `/api/v1/jobs/{id}/match/{candidate_id}` | Dispara análise de match via LLM |
| `GET` | `/api/v1/jobs/{id}/matches` | Retorna score, skills atendidas e faltantes |
| `GET` | `/api/v1/apply/{job_id}` | **Link de 1 Clique**: registra intenção e enfileira automação |
