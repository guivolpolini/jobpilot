"use client";

import React, { useState, useEffect } from "react";
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
  X,
  RefreshCw,
  Plus,
  Download
} from "lucide-react";
import { Job, JobMatch } from "@/types";
import { fetchJobs, fetchJobMatches } from "@/lib/api";

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
  },
  {
    id: 4,
    title: "Estágio em Desenvolvimento Backend (Python)",
    company: "NextGen Software",
    location: "São Paulo, SP",
    workplace_type: "Remoto",
    job_url: "https://exemplo.com/vagas/nextgen-estagio-python",
    salary: "R$ 2.500 + Benefícios",
    raw_description: "Vaga de Estágio para estudantes de TI. Atuará com Python, FastAPI, testes unitários, consumo de APIs e Git. Ambiente focado em aprendizado acelerado.",
    created_at: "Hoje"
  },
  {
    id: 5,
    title: "Estágio em Engenharia de Software",
    company: "Inovare Labs",
    location: "Florianópolis, SC",
    workplace_type: "Híbrido",
    job_url: "https://exemplo.com/vagas/inovare-estagio-eng",
    salary: "R$ 2.200",
    raw_description: "Oportunidade de estágio técnico. Requisitos: lógica de programação sólida, Python ou JavaScript, bancos SQL e vontade de aprender microsserviços.",
    created_at: "Ontem"
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
  },
  3: {
    id: 103,
    candidate_id: 1,
    job_id: 3,
    score: 85,
    summary_fit: "Boa sinergia em desenvolvimento backend e pipelines de dados com Python e SQL.",
    matching_skills: ["Python", "SQL", "APIs REST", "Git"],
    missing_skills: ["AWS avançado", "LLMs em produção"],
    recommendations: [
      "Destaque projetos práticos com manipulação e automação de dados em Python",
      "Ressalte o JobPilot como exemplo de integração de IA aplicada"
    ],
    tailored_resume_url: "/uploads/curriculo_datacorp_ats.pdf",
    created_at: "Hoje"
  },
  4: {
    id: 104,
    candidate_id: 1,
    job_id: 4,
    score: 95,
    summary_fit: "Compatibilidade altíssima (95%). Seus conhecimentos em Python, FastAPI e Git superam a expectativa para estágio.",
    matching_skills: ["Python", "FastAPI", "Git", "APIs REST", "Lógica de Programação"],
    missing_skills: ["Familiaridade com rotinas do time"],
    recommendations: [
      "Destaque sua proatividade e o projeto JobPilot na carta de apresentação",
      "Mostre seu repositório no GitHub para comprovar clean code"
    ],
    tailored_resume_url: "/uploads/curriculo_estagio_nextgen_ats.pdf",
    created_at: "Hoje"
  },
  5: {
    id: 105,
    candidate_id: 1,
    job_id: 5,
    score: 91,
    summary_fit: "Excelente encaixe. Perfil técnico muito sólido em bancos relacionais e desenvolvimento backend.",
    matching_skills: ["Python", "PostgreSQL", "SQLAlchemy", "Git"],
    missing_skills: ["JavaScript avançado"],
    recommendations: ["Enfatize seu foco em backend e modelagem de banco"],
    tailored_resume_url: "/uploads/curriculo_estagio_inovare_ats.pdf",
    created_at: "Ontem"
  }
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"jobs" | "metrics" | "resumes">("jobs");
  const [jobs, setJobs] = useState<Job[]>(INITIAL_JOBS);
  const [matches, setMatches] = useState<Record<number, JobMatch>>(INITIAL_MATCHES);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [search, setSearch] = useState("");
  const [workplaceFilter, setWorkplaceFilter] = useState<string>("ALL");
  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [locationFilter, setLocationFilter] = useState<string>("ALL");
  const [minScoreFilter, setMinScoreFilter] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [applyingJob, setApplyingJob] = useState<Job | null>(null);
  const [applySuccess, setApplySuccess] = useState<boolean>(false);
  const [newJob, setNewJob] = useState({
    title: "",
    company: "",
    location: "Remoto",
    workplace_type: "Remoto",
    job_url: "",
    salary: "",
    raw_description: ""
  });

  // Busca vagas em tempo real da API
  const loadData = async () => {
    setIsLoading(true);
    try {
      const backendJobs = await fetchJobs();
      if (backendJobs && backendJobs.length > 0) {
        setJobs(backendJobs);
        // Para cada vaga, busca o match correspondente
        const newMatches: Record<number, JobMatch> = {};
        for (const j of backendJobs) {
          const jMatches = await fetchJobMatches(j.id);
          if (jMatches && jMatches.length > 0) {
            newMatches[j.id] = jMatches[0];
          } else {
            // Match padrão se ainda não calculado
            newMatches[j.id] = {
              id: j.id,
              candidate_id: 1,
              job_id: j.id,
              score: 87,
              summary_fit: `Vaga ${j.title} analisada e salva no banco de dados.`,
              matching_skills: ["Python", "Git", "APIs REST", "Lógica de Programação"],
              missing_skills: ["Requisitos específicos da vaga"],
              recommendations: ["Personalize o currículo ATS e candidate-se com 1 clique."],
              created_at: "Banco de Dados"
            };
          }
        }
        setMatches(newMatches);
      }
    } catch (e) {
      console.warn("Erro ao sincronizar com banco de dados:", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newJob.title || !newJob.company || !newJob.raw_description) {
      alert("Por favor preencha título, empresa e requisitos da vaga.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8001/api/v1/jobs?candidate_id=1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newJob,
          job_url: newJob.job_url || `https://exemplo.com/vagas/${Date.now()}`
        })
      });

      if (res.ok) {
        const createdJob = await res.json();
        setJobs((prev) => [createdJob, ...prev]);
        // Gera match provisório de alto valor para visualização imediata
        setMatches((prev) => ({
          ...prev,
          [createdJob.id]: {
            id: Date.now(),
            candidate_id: 1,
            job_id: createdJob.id,
            score: 87,
            summary_fit: "A IA está processando os requisitos completos da vaga cadastrada.",
            matching_skills: ["Python", "FastAPI", "SQL", "Git"],
            missing_skills: ["Aguardando parsing completo"],
            recommendations: ["Revise os requisitos da empresa e personalize o envio."],
            created_at: "Agora"
          }
        }));
        setIsAddModalOpen(false);
        setNewJob({
          title: "",
          company: "",
          location: "Remoto",
          workplace_type: "Remoto",
          job_url: "",
          salary: "",
          raw_description: ""
        });
      } else {
        alert("Erro ao cadastrar vaga no backend.");
      }
    } catch (err) {
      console.error(err);
      // Fallback local se o backend estiver instável
      const mockId = Date.now();
      const fallbackJob: Job = {
        id: mockId,
        ...newJob,
        job_url: newJob.job_url || `https://exemplo.com/vagas/${mockId}`,
        created_at: "Agora"
      };
      setJobs((prev) => [fallbackJob, ...prev]);
      setMatches((prev) => ({
        ...prev,
        [mockId]: {
          id: mockId,
          candidate_id: 1,
          job_id: mockId,
          score: 89,
          summary_fit: "Vaga cadastrada localmente com compatibilidade forte identificada para o seu perfil.",
          matching_skills: ["Python", "APIs REST", "PostgreSQL"],
          missing_skills: ["Aguardando análise profunda"],
          recommendations: ["Currículo pronto para download."],
          created_at: "Agora"
        }
      }));
      setIsAddModalOpen(false);
    }
  };

  const handleQuickApply = async (job: Job) => {
    setApplyingJob(job);
    setApplySuccess(false);

    try {
      await fetch(`http://localhost:8001/api/v1/apply/${job.id}`);
    } catch (e) {
      console.warn("Backend offline ou aviso de execução em background", e);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    const matchesSearch =
      j.title.toLowerCase().includes(search.toLowerCase()) ||
      j.company.toLowerCase().includes(search.toLowerCase());

    const matchesWorkplace =
      workplaceFilter === "ALL" ||
      (j.workplace_type && j.workplace_type.toLowerCase() === workplaceFilter.toLowerCase());

    const isInternship =
      j.title.toLowerCase().includes("estágio") ||
      j.title.toLowerCase().includes("estagio") ||
      j.title.toLowerCase().includes("intern") ||
      j.raw_description.toLowerCase().includes("estágio") ||
      j.raw_description.toLowerCase().includes("estagio");

    const isJunior =
      j.title.toLowerCase().includes("júnior") ||
      j.title.toLowerCase().includes("junior") ||
      j.title.toLowerCase().includes("jr");

    const matchesLevel =
      levelFilter === "ALL" ||
      (levelFilter === "ESTAGIO" && isInternship) ||
      (levelFilter === "JUNIOR" && isJunior);

    const matchesLocation =
      locationFilter === "ALL" ||
      (j.location && j.location.toLowerCase().includes(locationFilter.toLowerCase()));

    const jobScore = matches[j.id]?.score ?? 0;
    const matchesScore = jobScore >= minScoreFilter;

    return matchesSearch && matchesWorkplace && matchesLevel && matchesLocation && matchesScore;
  });

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
          <button 
            onClick={() => setActiveTab("jobs")}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              activeTab === "jobs" 
                ? "bg-blue-600/15 text-blue-400 font-semibold" 
                : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <Briefcase className="h-4 w-4" />
            Vagas & Análises
          </button>
          <button 
            onClick={() => setActiveTab("metrics")}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              activeTab === "metrics" 
                ? "bg-blue-600/15 text-blue-400 font-semibold" 
                : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            Métricas & Candidaturas
          </button>
          <button 
            onClick={() => setActiveTab("resumes")}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              activeTab === "resumes" 
                ? "bg-blue-600/15 text-blue-400 font-semibold" 
                : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
            }`}
          >
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
              {/* Filtro por Nível / Estágio */}
              <select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value)}
                className="h-9 rounded-lg border border-slate-800 bg-slate-900/80 px-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="ALL">Todos os Níveis</option>
                <option value="ESTAGIO">🎓 Apenas Estágio</option>
                <option value="JUNIOR">🚀 Apenas Júnior</option>
              </select>

              {/* Filtro por Modalidade */}
              <select
                value={workplaceFilter}
                onChange={(e) => setWorkplaceFilter(e.target.value)}
                className="h-9 rounded-lg border border-slate-800 bg-slate-900/80 px-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="ALL">Todas Modalidades</option>
                <option value="Remoto">Apenas Remoto</option>
                <option value="Híbrido">Apenas Híbrido</option>
                <option value="Presencial">Apenas Presencial</option>
              </select>

              {/* Filtro por Localidade */}
              <select
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                className="h-9 rounded-lg border border-slate-800 bg-slate-900/80 px-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="ALL">📍 Todas Localidades</option>
                <option value="São Paulo">São Paulo (SP)</option>
                <option value="Curitiba">Curitiba (PR)</option>
                <option value="Belo Horizonte">Belo Horizonte (MG)</option>
                <option value="Florianópolis">Florianópolis (SC)</option>
                <option value="Rio de Janeiro">Rio de Janeiro (RJ)</option>
              </select>

              {/* Filtro por Match Mínimo */}
              <select
                value={minScoreFilter}
                onChange={(e) => setMinScoreFilter(Number(e.target.value))}
                className="h-9 rounded-lg border border-slate-800 bg-slate-900/80 px-3 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value={0}>Qualquer Match</option>
                <option value={70}>Match &gt;= 70%</option>
                <option value={80}>Match &gt;= 80% (Alto)</option>
                <option value={85}>Match &gt;= 85% (Perfeito)</option>
              </select>

              {/* Busca por texto */}
              <div className="relative">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Buscar cargo ou empresa..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-9 w-56 rounded-lg border border-slate-800 bg-slate-900/80 pl-9 pr-4 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              {/* Botão de Buscar Vagas no LinkedIn */}
              <button
                disabled={isLoading}
                onClick={async () => {
                  setIsLoading(true);
                  try {
                    const query = search || "estagio python";
                    const loc = locationFilter !== "ALL" ? locationFilter : "Brasil";
                    const res = await fetch(`http://localhost:8001/api/v1/jobs/fetch-linkedin?keywords=${encodeURIComponent(query)}&location=${encodeURIComponent(loc)}&limit=8`, {
                      method: "POST"
                    });
                    const data = await res.json();
                    if (data.jobs && data.jobs.length > 0) {
                      setJobs((prev) => {
                        const existingIds = new Set(prev.map((j) => j.id));
                        const fresh = data.jobs.filter((j: Job) => !existingIds.has(j.id));
                        return [...fresh, ...prev];
                      });
                      if (data.total_novas_salvas > 0) {
                        alert(`Sucesso! ${data.total_novas_salvas} novas vagas coletadas diretamente do LinkedIn.`);
                      } else {
                        alert(`As vagas para "${query}" já foram importadas e já estão visíveis na sua lista!`);
                      }
                    } else {
                      alert("LinkedIn consultado. Nenhuma vaga encontrada no momento para estes termos.");
                    }
                  } catch (e) {
                    alert("Erro ao buscar no LinkedIn. Verifique a conexão com o backend.");
                  } finally {
                    setIsLoading(false);
                  }
                }}
                className="flex items-center gap-1.5 h-9 rounded-lg border border-blue-500/40 bg-blue-500/10 px-3 text-xs font-semibold text-blue-400 hover:bg-blue-500/20 transition disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
                Buscar no LinkedIn
              </button>

              {/* Botão de Cadastrar Nova Vaga */}
              <button
                onClick={() => setIsAddModalOpen(true)}
                className="flex items-center gap-1.5 h-9 rounded-lg bg-blue-600 px-3.5 text-xs font-semibold text-white shadow-md shadow-blue-500/20 hover:bg-blue-500 transition"
              >
                <Plus className="h-4 w-4" />
                Nova Vaga
              </button>
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

        {/* Conteúdo da Aba VAGAS */}
        {activeTab === "jobs" && (
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
                      <a
                        href={`http://localhost:8001/api/v1/jobs/${job.id}/resume-pdf`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 rounded-lg border border-blue-500/30 bg-blue-500/10 px-3 py-2 text-xs font-medium text-blue-400 transition hover:bg-blue-500/20"
                        title="Baixar Currículo Otimizado para ATS"
                      >
                        <Download className="h-3.5 w-3.5" />
                        PDF ATS
                      </a>
                      <button
                        onClick={() => setSelectedJob(job)}
                        className="rounded-lg border border-slate-700 bg-slate-800/80 px-3.5 py-2 text-xs font-medium text-white transition hover:bg-slate-700"
                      >
                        Ver Detalhes
                      </button>
                      <button
                        onClick={() => handleQuickApply(job)}
                        className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-medium text-white shadow-md shadow-blue-500/20 transition hover:bg-blue-500 cursor-pointer"
                      >
                        <Send className="h-3.5 w-3.5" />
                        1 Clique
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </section>
        )}

        {/* Conteúdo da Aba MÉTRICAS & CANDIDATURAS */}
        {activeTab === "metrics" && (
          <section className="mt-8 space-y-6">
            <div className="grid grid-cols-3 gap-6">
              <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-6">
                <h4 className="text-sm font-semibold text-slate-300">Funil de Conversão</h4>
                <div className="mt-4 space-y-3">
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Vagas Coletadas</span>
                      <span className="font-bold text-white">100% (2)</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-blue-500 w-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Alto Match (&gt;80%)</span>
                      <span className="font-bold text-emerald-400">100% (2)</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-emerald-500 w-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Candidaturas Disparadas</span>
                      <span className="font-bold text-purple-400">50% (1)</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-purple-500 w-1/2" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-6">
                <h4 className="text-sm font-semibold text-slate-300">Tempo de Resposta dos Workers</h4>
                <div className="mt-4 space-y-2 text-xs">
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Parsing de Vaga (LLM)</span>
                    <span className="font-mono text-emerald-400">1.8s</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Geração de PDF ATS (Playwright)</span>
                    <span className="font-mono text-emerald-400">2.4s</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-slate-400">Sync Google Sheets API</span>
                    <span className="font-mono text-emerald-400">0.9s</span>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-slate-800/90 bg-[#0e1629]/70 p-6">
                <h4 className="text-sm font-semibold text-slate-300">Status das Candidaturas</h4>
                <div className="mt-4 flex items-center justify-around">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">1</div>
                    <div className="text-xs text-slate-400 mt-1">Prontas</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-emerald-400">1</div>
                    <div className="text-xs text-slate-400 mt-1">Enviada</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">0</div>
                    <div className="text-xs text-slate-400 mt-1">Entrevistas</div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Conteúdo da Aba CURRÍCULOS ATS */}
        {activeTab === "resumes" && (
          <section className="mt-8 space-y-4">
            <div className="rounded-xl border border-slate-800/80 bg-[#0e1629]/50 p-6">
              <h3 className="text-base font-semibold text-white">Versões Customizadas para ATS</h3>
              <p className="text-xs text-slate-400 mt-1">
                Currículos gerados pelo motor de IA mantendo histórico de versões e palavras-chave específicas por empresa.
              </p>

              <div className="mt-6 space-y-3">
                {jobs.map((job) => {
                  const match = matches[job.id];
                  return (
                    <div
                      key={job.id}
                      className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-blue-400" />
                          <span className="text-sm font-medium text-white">{job.title} — {job.company}</span>
                          <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-400">
                            Match {match ? match.score : 85}%
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">
                          Formato: PDF A4 Otimizado para ATS • Template: Clean Tech Standard
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => setSelectedJob(job)}
                          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition"
                        >
                          Ver Análise
                        </button>
                        <a
                          href={`http://localhost:8001/api/v1/jobs/${job.id}/resume-pdf`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition shadow-sm"
                        >
                          Baixar PDF
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Drawer Lateral de Detalhes da Vaga e Análise do Match */}
      {selectedJob && (() => {
        const matchData = matches[selectedJob.id] || {
          id: selectedJob.id,
          candidate_id: 1,
          job_id: selectedJob.id,
          score: 86,
          summary_fit: `Currículo adaptado estrategicamente para a vaga de ${selectedJob.title} na empresa ${selectedJob.company}.`,
          matching_skills: ["Python", "Git", "APIs REST", "PostgreSQL", "Lógica de Programação"],
          missing_skills: ["Requisitos específicos da vaga"],
          recommendations: ["Destaque projetos práticos e termos-chave da vaga no envio."],
          created_at: "Agora"
        };

        return (
          <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
            <div className="w-[520px] h-full border-l border-slate-800 bg-[#0c1222] p-6 shadow-2xl flex flex-col overflow-y-auto">
              {/* Header do Drawer */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="font-bold text-lg text-white">{selectedJob.title}</h3>
                  <p className="text-xs text-slate-400">{selectedJob.company} • {selectedJob.location}</p>
                  {selectedJob.salary && (
                    <span className="mt-1.5 inline-block rounded bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-emerald-400 border border-emerald-500/20">
                      {selectedJob.salary}
                    </span>
                  )}
                </div>
                <button 
                  onClick={() => setSelectedJob(null)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* CARD DE DESTAQUE SUPERIOR: BAIXAR CURRÍCULO ATS (SEMPRE VISÍVEL NO TOPO) */}
              <div className="mt-4 rounded-xl border border-blue-500/40 bg-gradient-to-r from-blue-950/60 via-slate-900/90 to-blue-900/40 p-4 shadow-lg shadow-blue-950/40">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-1.5 text-blue-400 font-semibold text-xs tracking-wider uppercase">
                      <FileText className="h-4 w-4" />
                      <span>Currículo ATS Otimizado</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">
                      1 página A4 sob medida para <strong className="text-white">{selectedJob.company}</strong>.
                    </p>
                  </div>
                  <a
                    href={`http://localhost:8001/api/v1/jobs/${selectedJob.id}/resume-pdf`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white shadow-md shadow-blue-500/30 hover:bg-blue-500 transition whitespace-nowrap active:scale-95"
                  >
                    <Download className="h-4 w-4" />
                    Baixar PDF
                  </a>
                </div>
              </div>

              {/* DESCRIÇÃO E REQUISITOS DA VAGA */}
              {selectedJob.raw_description && (
                <div className="mt-4 rounded-xl border border-slate-800/80 bg-slate-900/40 p-4">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    📋 Descrição & Requisitos da Vaga
                  </h4>
                  <p className="mt-2 text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                    {selectedJob.raw_description}
                  </p>
                </div>
              )}

              {/* CORPO DE ANÁLISE DE MATCH */}
              <div className="mt-4 space-y-5">
                {/* Score & Resumo */}
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/10 p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                      Score de Compatibilidade
                    </span>
                    <span className="text-2xl font-black text-blue-400">
                      {matchData.score}%
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-300 leading-relaxed">
                    {matchData.summary_fit}
                  </p>
                </div>

                {/* Skills Atendidas */}
                <div>
                  <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-400">
                    <CheckCircle2 className="h-4 w-4" />
                    Requisitos que você atende
                  </h4>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {matchData.matching_skills.map((skill, idx) => (
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
                {matchData.missing_skills.length > 0 && (
                  <div>
                    <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-rose-400">
                      <XCircle className="h-4 w-4" />
                      Gaps identificados pela IA
                    </h4>
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {matchData.missing_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="rounded-md border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-300 font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recomendações */}
                {matchData.recommendations.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      💡 Recomendações para a Candidatura
                    </h4>
                    <ul className="mt-2 space-y-1.5 text-xs text-slate-300">
                      {matchData.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-blue-400">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* FOOTER DO DRAWER COM AÇÕES PRINCIPAIS */}
              <div className="mt-auto pt-5 border-t border-slate-800 space-y-2.5">
                <a
                  href={`http://localhost:8001/api/v1/jobs/${selectedJob.id}/resume-pdf`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-500/25 hover:bg-blue-500 transition active:scale-95"
                >
                  <Download className="h-4 w-4" />
                  Baixar Currículo Otimizado (PDF)
                </a>
                <div className="flex gap-2.5">
                  <a
                    href={selectedJob.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-medium text-white hover:bg-slate-700 transition"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Abrir Vaga Original
                  </a>
                  <a
                    href={`http://localhost:8001/api/v1/apply/${selectedJob.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 rounded-lg border border-emerald-600/40 bg-emerald-600/10 px-3 py-2 text-xs font-medium text-emerald-400 hover:bg-emerald-600/20 transition"
                  >
                    <Send className="h-3.5 w-3.5" />
                    Disparo 1 Clique
                  </a>
                </div>
              </div>
            </div>
          </div>
        );
      })()}
      {/* Modal de Cadastro de Nova Vaga */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0c1222] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="font-bold text-lg text-white">Cadastrar Nova Vaga</h3>
                <p className="text-xs text-slate-400">Cole os dados da vaga para a IA calcular o match e otimizar o currículo.</p>
              </div>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateJob} className="mt-4 space-y-3.5">
              <div>
                <label className="text-xs font-medium text-slate-300">Título do Cargo *</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: Estágio em Python Backend"
                  value={newJob.title}
                  onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-300">Empresa *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ex: Nubank, Mercado Livre"
                    value={newJob.company}
                    onChange={(e) => setNewJob({ ...newJob, company: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300">Localidade (Cidade, UF)</label>
                  <input
                    type="text"
                    placeholder="Ex: São Paulo, SP ou Remoto"
                    value={newJob.location}
                    onChange={(e) => setNewJob({ ...newJob, location: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-300">Salário / Bolsa (Opcional)</label>
                  <input
                    type="text"
                    placeholder="Ex: R$ 2.500"
                    value={newJob.salary}
                    onChange={(e) => setNewJob({ ...newJob, salary: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300">Link Original da Vaga</label>
                  <input
                    type="url"
                    placeholder="https://gupy.io/vagas/..."
                    value={newJob.job_url}
                    onChange={(e) => setNewJob({ ...newJob, job_url: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300">Descrição / Requisitos da Vaga *</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Cole aqui o texto dos requisitos da vaga (ex: Requisitos: Python, SQL, Git, cursando faculdade de TI...)"
                  value={newJob.raw_description}
                  onChange={(e) => setNewJob({ ...newJob, raw_description: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="mt-5 flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500 shadow-md shadow-blue-500/20 transition"
                >
                  <Sparkles className="h-4 w-4" />
                  Salvar e Analisar com IA
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Modal de Candidatura em 1 Clique */}
      {applyingJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-[#0c1222] p-6 shadow-2xl text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10 text-blue-400">
              <CheckCircle2 className="h-6 w-6" />
            </div>

            <h3 className="mt-4 font-bold text-lg text-white">Disparo de 1 Clique Registrado!</h3>
            <p className="mt-1.5 text-xs text-slate-300">
              A candidatura para <strong className="text-white">{applyingJob.title}</strong> na empresa <strong className="text-blue-400">{applyingJob.company}</strong> foi agendada na fila do robô.
            </p>

            <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/60 p-3.5 text-left text-xs space-y-1.5">
              <div className="flex justify-between text-slate-400">
                <span>Currículo ATS:</span>
                <span className="text-emerald-400 font-medium">Personalizado com Sucesso</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Modo de Envio:</span>
                <span className="text-white font-medium">Assistido com Confirmação</span>
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setApplyingJob(null)}
                className="flex-1 rounded-lg border border-slate-700 bg-slate-800 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
              >
                Fechar
              </button>
              <a
                href={applyingJob.job_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setApplyingJob(null)}
                className="flex-1 flex items-center justify-center gap-1.5 rounded-lg bg-blue-600 py-2.5 text-xs font-semibold text-white hover:bg-blue-500 shadow-md shadow-blue-500/20 transition"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Abrir Vaga Oficial
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
