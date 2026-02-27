/** Application-wide constants */

export const APP_NAME = "InterviewAce";

/** Route paths */
export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  VERIFY_EMAIL: "/verify-email",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  DASHBOARD: "/dashboard",
  RESUMES: "/resumes",
  RESUME_UPLOAD: "/resumes/upload",
  INTERVIEWS: "/interviews",
  INTERVIEW_START: "/interviews/start",
  PROFILE: "/profile",
  ADMIN_USERS: "/admin/users",
  ADMIN_STATS: "/admin/stats",
} as const;

/** API route paths (BFF — same origin) */
export const API_ROUTES = {
  AUTH: {
    LOGIN: "/api/auth/login",
    REGISTER: "/api/auth/register",
    LOGOUT: "/api/auth/logout",
    REFRESH: "/api/auth/refresh",
    ME: "/api/auth/me",
    VERIFY_EMAIL: "/api/auth/verify-email",
    FORGOT_PASSWORD: "/api/auth/forgot-password",
    RESET_PASSWORD: "/api/auth/reset-password",
    CHANGE_PASSWORD: "/api/auth/change-password",
  },
  RESUMES: {
    LIST: "/api/resumes",
    DETAIL: (id: string) => `/api/resumes/${id}`,
    ANALYSIS: (id: string) => `/api/resumes/${id}/analysis`,
    VERSIONS: (id: string) => `/api/resumes/${id}/versions`,
    SHARE: (id: string) => `/api/resumes/${id}/share`,
    EXPORT: (id: string) => `/api/resumes/${id}/export`,
  },
  INTERVIEWS: {
    START: "/api/interviews/start",
    SESSION: (id: string) => `/api/interviews/${id}`,
    NEXT_QUESTION: (id: string) => `/api/interviews/${id}/next-question`,
    ANSWER: (id: string) => `/api/interviews/${id}/answer`,
    COMPLETE: (id: string) => `/api/interviews/${id}/complete`,
    SUMMARY: (id: string) => `/api/interviews/${id}/summary`,
    HISTORY: "/api/interviews/history",
  },
  DASHBOARD: {
    STATS: "/api/dashboard/stats",
  },
  ADMIN: {
    USERS: "/api/admin/users",
    STATS: "/api/admin/stats",
  },
} as const;

/** Public routes that don't require authentication */
export const PUBLIC_ROUTES = [
  ROUTES.HOME,
  ROUTES.LOGIN,
  ROUTES.REGISTER,
  ROUTES.VERIFY_EMAIL,
  ROUTES.FORGOT_PASSWORD,
  ROUTES.RESET_PASSWORD,
] as const;
