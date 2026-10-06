const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";

export async function fetchJobs() {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, { cache: "no-store" });
    if (!res.ok) throw new Error("Falha ao buscar vagas");
    return await res.json();
  } catch (error) {
    console.warn("Backend offline ou erro na chamada, usando fallback local:", error);
    return null;
  }
}

export async function fetchJobMatches(jobId: number) {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/matches`, { cache: "no-store" });
    if (!res.ok) throw new Error("Falha ao buscar matches da vaga");
    return await res.json();
  } catch (error) {
    console.warn("Erro ao buscar matches:", error);
    return [];
  }
}

export async function triggerJobMatch(jobId: number, candidateId: number = 1) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/match/${candidateId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Falha ao disparar match");
  return await res.json();
}
