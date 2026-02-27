/* ──────────────────────────────────────────────────────────
 * Zod validation schemas for interview forms
 * Mirrors: FastAPI Pydantic models in schemas/interview.py
 * ────────────────────────────────────────────────────────── */

import { z } from "zod";

export const interviewConfigSchema = z.object({
  resume_id: z.string().uuid("Please select a resume").optional().nullable(),
  question_count: z
    .number()
    .int()
    .min(5, "Minimum 5 questions")
    .max(30, "Maximum 30 questions")
    .default(12),
  difficulty: z.enum(["easy", "medium", "hard", "mixed"]).default("mixed"),
  focus_areas: z.array(z.string()).max(10, "Maximum 10 focus areas").optional().nullable(),
});

export const answerSchema = z.object({
  answer_text: z
    .string()
    .min(1, "Please provide an answer")
    .max(5000, "Answer must be at most 5000 characters"),
  time_taken_seconds: z.number().int().min(0).optional().nullable(),
});

/** Inferred types from Zod schemas */
export type InterviewConfigFormValues = z.infer<typeof interviewConfigSchema>;
export type AnswerFormValues = z.infer<typeof answerSchema>;
