"use client";

import React, { useState } from "react";
import { 
  Briefcase, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  ExternalLink, 
  Send, 
  FileText, 
  TrendingUp,
  Search,
  Building,
  MapPin,
  X
} from "lucide-react";
import { Job, JobMatch } from "@/types";

// Dados para inicialização e demonstração da interface visual
const INITIAL_JOBS: Job[] = [
  {
    id: 1,
    title: "Desenvolvedor Python Backend Júnior",
    company: "Fintech Horizon",
    location: "São Paulo, SP",
    workplace_type: "Remoto",
    job_url: "https://exemplo.com/vagas/python-jr",
    salary: "R$ 4.500 - R$ 6.000",
    raw_description: "Requisitos: Python, FastAPI, SQLAlchemy, PostgreSQL, Docker, testes automatizados e boa comunicação.",
    created_at: "Hoje"
  },
  {
    id: 2,
    title: "Software Engineer Jr (APIs & Microserviços)",
    company: "CloudScale Tech",
    location: "Curitiba, PR",
    workplace_type: "Híbrido",
    job_url: "https://exemplo.com/vagas/cloudscale-jr",
    salary: "R$ 5.200",
    raw_description: "Buscamos pessoa desenvolvedora com vivência em Python ou Node, filas assíncronas (Redis/RabbitMQ), e foco em Clean Code.",
    created_at: "Ontem"
  },
  {
    id: 3,
    title: "Junior Data & Backend Developer",
    company: "DataCorp Analytics",
    location: "Belo Horizonte, MG",
    workplace_type: "Remoto",
    job_url: "https://exemplo.com/vagas/datacorp-dev",
    salary: "R$ 4.800",
    raw_description: "Experiência com pipelines de dados, Python, SQL avançado, noções de AWS e familiaridade com LLMs.",
    created_at: "Há 2 dias"
  }
];

const INITIAL_MATCHES: Record<number, JobMatch> = {
  1: {
    id: 101,
    candidate_id: 1,
    job_id: 1,
    score: 88,
    summary_fit: "Forte compatibilidade técnica. Seu domínio em FastAPI, PostgreSQL e modelagem relacional atende diretamente o core da vaga.",
    matching_skills: ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Git"],
    missing_skills: ["Testes automatizados com Pytest", "Docker Compose avançado"],
    recommendations: [
      "Destaque no resumo os endpoints que você construiu com Celery",
      "Evidencie boas práticas de migrations e arquitetura modular"
    ],
    tailored_resume_url: "/uploads/curriculo_horizon_ats.pdf",
    created_at: "Hoje"
  },
  2: {
    id: 102,
    candidate_id: 1,
    job_id: 2,
    score: 82,
    summary_fit: "Boa sinergia com a arquitetura assíncrona do projeto, especialmente pelo seu uso de Redis e mensageria.",
    matching_skills: ["Python", "Redis", "APIs REST", "Arquitetura Assíncrona"],
    missing_skills: ["Node.js / TypeScript", "RabbitMQ"],
    recommendations: [
      "Saliente sua habilidade de transitar entre Python e conceitos de backend resiliente"
    ],
    tailored_resume_url: "/uploads/curriculo_cloudscale_ats.pdf",
    created_at: "Ontem"
  }
};

export default function Dashboard() {
  const [jobs] = useState<Job[]>(INITIAL_JOBS);
  const [matches] = useState<Record<number, JobMatch>>(INITIAL_MATCHES);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [search, setSearch] = useState("");

  const filteredJobs = jobs.filter(
    (j) =>
      j.title.toLowerCase().includes(search.toLowerCase()) ||
      j.company.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-[#0c1222]/60 p-6 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 shadow-lg shadow-blue-500/25">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white tracking-wide text-lg">JobPilot</h1>
            <p className="text-xs text-slate-400">ATS Engine & Automação</p>
          </div>
        </div>

        <nav className="mt-8 space-y-1.5">
          <button className="flex w-full items-center gap-3 rounded-lg bg-blue-600/15 px-3 py-2.5 text-sm font-medium text-blue-400 transition hover:bg-blue-600/20">
            <Briefcase className="h-4 w-4" />
            Vagas & Análises
          </button>
          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-slate-800/60 hover:text-white">
            <TrendingUp className="h-4 w-4" />
            Métricas & Candidaturas
          </button>
          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-slate-800/60 hover:text-white">
            <FileText className="h-4 w-4" />
            Currículos ATS
          </button>
        </nav>

        <div className="mt-auto pt-48">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3.5 text-xs">
            <div className="flex items-center gap-2 font-medium text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Sync com Planilha Ativo
            </div>
            <p className="mt-1.5 text-slate-400">
              Disparo de 1 clique habilitado no Google Sheets.
            </p>
          </div>
        </div>
      </aside>

      {/* Conteúdo Principal */}
      <main className="flex-1 p-8 overflow-y-auto">
        {/* Header com KPIs */}
        <header>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-white">Vagas Monitoradas</h2>
              <p className="text-sm text-slate-400 mt-1">
                Análise em tempo real de compatibilidade e currículos adaptados para passar pelo ATS.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Buscar cargo ou empresa..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-9 w-64 rounded-lg border border-slate-800 bg-slate-900/80 pl-9 pr-4 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Cards de Métricas */}
          <div className="mt-6 grid grid-cols-4 gap-4">
            <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-4">
              <p className="text-xs font-medium text-slate-400">Total de Vagas</p>
              <p className="mt-2 text-2xl font-bold text-white">{jobs.length}</p>
            </div>
            <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-4">
              <p className="text-xs font-medium text-slate-400">Alto Match (&gt;80%)</p>
              <p className="mt-2 text-2xl font-bold text-emerald-400">2 vagas</p>
            </div>
            <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-4">
              <p className="text-xs font-medium text-slate-400">Currículos Gerados</p>
              <p className="mt-2 text-2xl font-bold text-blue-400">2 PDFs</p>
            </div>
            <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-4">
              <p className="text-xs font-medium text-slate-400">Score Médio</p>
              <p className="mt-2 text-2xl font-bold text-purple-400">85%</p>
            </div>
          </div>
        </header>

        {/* Lista de Vagas */}
        <section className="mt-8 space-y-3">
          {filteredJobs.map((job) => {
            const match = matches[job.id];
            return (
              <div
                key={job.id}
                className="group flex items-center justify-between rounded-xl border border-slate-800/80 bg-[#0e1629]/40 p-5 transition hover:border-slate-700 hover:bg-[#0e1629]/80"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-white text-base group-hover:text-blue-400 transition">
                      {job.title}
                    </h3>
                    <span className="rounded-md border border-slate-700/60 bg-slate-800/40 px-2 py-0.5 text-xs text-slate-300">
                      {job.workplace_type}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-400">
                    <span className="flex items-center gap-1.5">
                      <Building className="h-3.5 w-3.5 text-slate-500" />
                      {job.company}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5 text-slate-500" />
                      {job.location}
                    </span>
                    {job.salary && (
                      <span className="text-slate-300 font-medium">
                        💰 {job.salary}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-5">
                  {match ? (
                    <div className="text-right">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-400">Match ATS:</span>
                        <span className={`text-base font-bold ${
                          match.score >= 80 ? "text-emerald-400" : "text-amber-400"
                        }`}>
                          {match.score}%
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500">
                        {match.matching_skills.length} skills atendidas
                      </span>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-500 italic">Pendente análise</span>
                  )}

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedJob(job)}
                      className="rounded-lg border border-slate-700 bg-slate-800/80 px-3.5 py-2 text-xs font-medium text-white transition hover:bg-slate-700"
                    >
                      Ver Detalhes
                    </button>
                    <a
                      href={`http://localhost:8000/api/v1/apply/${job.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-medium text-white shadow-md shadow-blue-500/20 transition hover:bg-blue-500"
                    >
                      <Send className="h-3.5 w-3.5" />
                      1 Clique
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </section>
      </main>

      {/* Drawer Lateral de Detalhes da Vaga e Análise do Match */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
          <div className="w-[520px] h-full border-l border-slate-800 bg-[#0c1222] p-6 shadow-2xl flex flex-col overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="font-bold text-lg text-white">{selectedJob.title}</h3>
                <p className="text-xs text-slate-400">{selectedJob.company} • {selectedJob.location}</p>
              </div>
              <button 
                onClick={() => setSelectedJob(null)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {matches[selectedJob.id] && (
              <div className="mt-6 space-y-6">
                {/* Score & Resumo */}
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/10 p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                      Score de Compatibilidade
                    </span>
                    <span className="text-2xl font-black text-blue-400">
                      {matches[selectedJob.id].score}%
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-300 leading-relaxed">
                    {matches[selectedJob.id].summary_fit}
                  </p>
                </div>

                {/* Skills Atendidas */}
                <div>
                  <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-400">
                    <CheckCircle2 className="h-4 w-4" />
                    Requisitos que você atende
                  </h4>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {matches[selectedJob.id].matching_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300 font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Gaps / O que está faltando */}
                <div>
                  <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-rose-400">
                    <XCircle className="h-4 w-4" />
                    Gaps identificados pela IA
                  </h4>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {matches[selectedJob.id].missing_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="rounded-md border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-300 font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Recomendações */}
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    💡 Recomendações para a Candidatura
                  </h4>
                  <ul className="mt-2 space-y-1.5 text-xs text-slate-300">
                    {matches[selectedJob.id].recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Currículo Gerado */}
                {matches[selectedJob.id].tailored_resume_url && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                    <p className="text-xs font-semibold text-slate-300">Currículo Customizado para ATS</p>
                    <p className="text-xs text-slate-500 mt-1">Keywords enfatizadas sem alucinação.</p>
                    <a
                      href={matches[selectedJob.id].tailored_resume_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-2 rounded-lg bg-slate-800 px-3 py-2 text-xs font-medium text-white hover:bg-slate-700 transition"
                    >
                      <FileText className="h-4 w-4 text-blue-400" />
                      Baixar PDF Otimizado
                    </a>
                  </div>
                )}
              </div>
            )}

            <div className="mt-auto pt-6 border-t border-slate-800 flex gap-3">
              <a
                href={selectedJob.job_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-xs font-medium text-white hover:bg-slate-700 transition"
              >
                <ExternalLink className="h-4 w-4" />
                Abrir Vaga Original
              </a>
              <a
                href={`http://localhost:8000/api/v1/apply/${selectedJob.id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-medium text-white hover:bg-blue-500 shadow-lg shadow-blue-500/20 transition"
              >
                <Send className="h-4 w-4" />
                Disparo 1 Clique
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
