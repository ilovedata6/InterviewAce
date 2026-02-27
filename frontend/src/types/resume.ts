/* ──────────────────────────────────────────────────────────
 * Resume TypeScript types
 * Mirrors: backend/app/schemas/resume.py
 * ────────────────────────────────────────────────────────── */

/** Resume processing status */
export type ResumeStatus = "pending" | "processing" | "analyzed" | "error";

/** Allowed file MIME types */
export type FileType =
  | "application/pdf"
  | "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  | "application/msword"
  | "text/plain";

/** ── Nested value objects ── */

export interface Experience {
  company: string;
  position: string;
  start_date: string;
  end_date: string | null;
  description: string;
  location: string | null;
  is_current: boolean;
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date: string | null;
  gpa: number | null;
  is_current: boolean;
}

/** ── Request types ── */

export interface ResumeCreateRequest {
  title: string;
  description?: string | null;
  tags?: string[];
}

export interface ResumeUpdateRequest {
  title?: string | null;
  description?: string | null;
  tags?: string[] | null;
}

export interface ResumeShareRequest {
  is_public?: boolean;
  expiry_days?: number | null;
  allowed_emails?: string[] | null;
}

/** ── Response types ── */

export interface Resume {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  tags: string[];
  file_path: string;
  file_name: string;
  file_size: number;
  file_type: FileType;
  status: ResumeStatus;
  inferred_role: string | null;
  years_of_experience: number | null;
  skills: string[];
  created_at: string;
  updated_at: string;
  analysis: Record<string, unknown> | null;
  version: number;
  parent_version_id: string | null;
  is_public: boolean;
  share_token: string | null;
}

export interface ResumeAnalysis {
  skills: string[];
  experience: Experience[];
  education: Education[];
  summary: string;
  recommendations: string[];
  job_titles: string[];
  years_of_experience: number;
  confidence_score: number;
}

export interface ResumeAnalysisResponse {
  resume_id: string;
  analysis: Record<string, unknown> | null;
  status: ResumeStatus;
  created_at: string;
  processing_time: number | null;
  confidence_score: number | null;
}

export interface ResumeUploadResponse {
  id: string;
  file_name: string;
  status: ResumeStatus;
  message: string;
  file_size: number;
  file_type: FileType;
  task_id: string | null;
}

export interface ResumeList {
  resumes: Resume[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ResumeShareResponse {
  share_token: string;
  share_url: string;
  expiry_date: string | null;
  is_public: boolean;
}

export interface ResumeVersion {
  version: number;
  created_at: string;
  changes: string[];
  parent_version_id: string | null;
}

export interface ResumeVersionList {
  versions: ResumeVersion[];
  current_version: number;
}

/** Query params for resume list */
export interface ResumeListParams {
  skip?: number;
  limit?: number;
  status_filter?: ResumeStatus;
  search?: string;
}
