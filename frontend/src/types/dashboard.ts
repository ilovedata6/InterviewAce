/* ──────────────────────────────────────────────────────────
 * Dashboard TypeScript types
 * Mirrors: backend/app/api/v1/endpoints/dashboard.py
 * ────────────────────────────────────────────────────────── */

/** Interview stats section */
export interface InterviewStats {
  total: number;
  completed: number;
  avg_score: number | null;
  best_score: number | null;
}

/** Resume stats section */
export interface ResumeStats {
  total: number;
}

/** Recent session entry */
export interface RecentSession {
  session_id: string;
  started_at: string | null;
  completed_at: string | null;
  final_score: number | null;
  difficulty: string | null;
}

/** Category performance breakdown */
export interface CategoryScore {
  avg_score: number;
  count: number;
}

/** Full dashboard stats response from GET /api/dashboard/stats */
export interface DashboardStats {
  interviews: InterviewStats;
  resumes: ResumeStats;
  recent_sessions: RecentSession[];
  category_breakdown: Record<string, CategoryScore>;
}
