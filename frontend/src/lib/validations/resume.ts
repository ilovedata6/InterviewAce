/* ──────────────────────────────────────────────────────────
 * Zod validation schemas for resume forms
 * Mirrors: FastAPI Pydantic models in schemas/resume.py
 * ────────────────────────────────────────────────────────── */

import { z } from "zod";

/** Allowed MIME types for resume upload */
const ALLOWED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/msword",
  "text/plain",
] as const;

/** Max file size: 10 MB */
const MAX_FILE_SIZE = 10 * 1024 * 1024;

export const uploadSchema = z.object({
  file: z
    .instanceof(File, { message: "Please select a file" })
    .refine((f) => f.size > 0, "File is empty")
    .refine((f) => f.size <= MAX_FILE_SIZE, "File must be 10 MB or less")
    .refine(
      (f) => (ALLOWED_FILE_TYPES as readonly string[]).includes(f.type),
      "Only PDF, DOCX, DOC, and TXT files are allowed",
    ),
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be at most 100 characters")
    .optional(),
  description: z.string().max(500, "Description must be at most 500 characters").optional(),
  tags: z.array(z.string().max(30)).max(10, "Maximum 10 tags allowed").optional().default([]),
});

export const resumeUpdateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be at most 100 characters")
    .optional(),
  description: z
    .string()
    .max(500, "Description must be at most 500 characters")
    .optional()
    .nullable(),
  tags: z.array(z.string().max(30)).max(10, "Maximum 10 tags allowed").optional().nullable(),
});

export const exportSchema = z.object({
  format: z.enum(["pdf", "docx", "txt"], {
    message: "Please select an export format",
  }),
});

export const shareSchema = z.object({
  is_public: z.boolean().default(false),
  expiry_days: z.number().int().min(1).max(30).optional().nullable(),
  allowed_emails: z
    .array(z.string().email("Invalid email address"))
    .max(10, "Maximum 10 emails allowed")
    .optional()
    .nullable(),
});

/** Inferred types from Zod schemas */
export type UploadFormValues = z.infer<typeof uploadSchema>;
export type ResumeUpdateFormValues = z.infer<typeof resumeUpdateSchema>;
export type ExportFormValues = z.infer<typeof exportSchema>;
export type ShareFormValues = z.infer<typeof shareSchema>;
