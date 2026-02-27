/* ──────────────────────────────────────────────────────────
 * Common / shared TypeScript types
 * Mirrors: backend/app/schemas/base.py
 * ────────────────────────────────────────────────────────── */

/** Generic paginated response from the API */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

/** Standard message response */
export interface MessageResponse {
  message: string;
}

/** Standard API error shape returned by FastAPI */
export interface ApiError {
  detail: string | { msg: string; type: string }[];
  status_code?: number;
}

/** Wrapper for typed API responses */
export type ApiResponse<T> = {
  data: T;
  status: number;
};

/** Pagination query params */
export interface PaginationParams {
  skip?: number;
  limit?: number;
}
