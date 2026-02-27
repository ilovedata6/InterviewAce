/* ──────────────────────────────────────────────────────────
 * Interview TypeScript types
 * Mirrors: backend/app/schemas/interview.py
 * ────────────────────────────────────────────────────────── */

/** Interview difficulty levels */
export type InterviewDifficulty = "easy" | "medium" | "hard" | "mixed";

/** Question categories */
export type QuestionCategory =
  | "technical"
  | "behavioral"
  | "project"
  | "system_design"
  | "coding"
  | "general";

/** ── Request types ── */

export interface InterviewStartRequest {
  resume_id?: string | null;
  question_count?: number;
  difficulty?: InterviewDifficulty;
  focus_areas?: string[] | null;
}

export interface AnswerRequest {
  answer_text: string;
  time_taken_seconds?: number | null;
}

/** ── Response types ── */

export interface InterviewSession {
  id: string;
  user_id: string;
  resume_id: string;
  started_at: string;
  completed_at: string | null;
  final_score: number | null;
  feedback_summary: string | null;
  difficulty: string;
  question_count: number;
  focus_areas: string[] | null;
  score_breakdown: Record<string, unknown> | null;
}

export interface Question {
  question_id: string;
  question_text: string;
  category: string;
  difficulty: string;
  order_index: number;
}

export interface QuestionFeedback {
  question_id: string;
  evaluation_score: number;
  feedback_comment: string;
}

export interface InterviewSummary {
  session_id: string;
  final_score: number;
  feedback_summary: string;
  question_feedback: QuestionFeedback[];
  score_breakdown: Record<string, unknown> | null;
  strengths: string[] | null;
  weaknesses: string[] | null;
}

/** Interview flow state machine (client-side) */
export type InterviewState =
  | "configuring"
  | "loading"
  | "answering"
  | "submitting"
  | "feedback"
  | "completing"
  | "summary";
