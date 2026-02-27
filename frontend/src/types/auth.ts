/* ──────────────────────────────────────────────────────────
 * Auth & User TypeScript types
 * Mirrors: backend/app/schemas/auth.py, user.py
 * ────────────────────────────────────────────────────────── */

/** Enum: user roles */
export type UserRole = "user" | "admin" | "moderator";

/** ── Request types ── */

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface EmailVerificationRequest {
  token: string;
}

export interface ResendVerificationRequest {
  email: string;
}

/** ── Response types ── */

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: UserRole;
  created_at: string;
  updated_at: string;
}

export interface VerificationResponse {
  message: string;
}
