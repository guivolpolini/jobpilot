export interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  workplace_type?: string;
  job_url: string;
  salary?: string;
  raw_description: string;
  created_at: string;
}

export interface JobMatch {
  id: number;
  candidate_id: number;
  job_id: number;
  score: number;
  summary_fit: string;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
  tailored_resume_url?: string;
  created_at: string;
}
