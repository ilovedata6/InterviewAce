/* ──────────────────────────────────────────────────────────
 * Typed fetch wrapper for BFF API routes
 *
 * All requests go to same-origin /api/* routes (BFF layer).
 * The BFF forwards them to FastAPI with the JWT cookie.
 * ────────────────────────────────────────────────────────── */

import type { ApiError } from "@/types/common";

/** Custom error thrown when the API returns a non-2xx status */
export class ApiClientError extends Error {
  status: number;
  detail: ApiError["detail"];

  constructor(status: number, detail: ApiError["detail"]) {
    const msg = typeof detail === "string" ? detail : "Validation error";
    super(msg);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail;
  }
}

/** Default headers for JSON requests */
const JSON_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

/** Parse the response body, throwing ApiClientError on non-2xx */
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: ApiError["detail"] = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.message ?? res.statusText;
    } catch {
      /* body was not JSON — keep statusText */
    }
    throw new ApiClientError(res.status, detail);
  }

  // 204 No Content — return nothing
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

/** Build a URL with query params */
function buildUrl(path: string, params?: Record<string, unknown>): string {
  const url = new URL(path, window.location.origin);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

/** ── Public API client ── */

export const apiClient = {
  /** GET request */
  async get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    const res = await fetch(buildUrl(path, params), {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "include",
    });
    return handleResponse<T>(res);
  },

  /** POST request (JSON body) */
  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(path, {
      method: "POST",
      headers: JSON_HEADERS,
      credentials: "include",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(res);
  },

  /** PUT request (JSON body) */
  async put<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(path, {
      method: "PUT",
      headers: JSON_HEADERS,
      credentials: "include",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(res);
  },

  /** PATCH request (JSON body) */
  async patch<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(path, {
      method: "PATCH",
      headers: JSON_HEADERS,
      credentials: "include",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(res);
  },

  /** DELETE request */
  async del<T = void>(path: string): Promise<T> {
    const res = await fetch(path, {
      method: "DELETE",
      headers: { Accept: "application/json" },
      credentials: "include",
    });
    return handleResponse<T>(res);
  },

  /** Upload file (multipart/form-data) */
  async upload<T>(path: string, formData: FormData): Promise<T> {
    const res = await fetch(path, {
      method: "POST",
      credentials: "include",
      // Don't set Content-Type — browser sets it with boundary
      body: formData,
    });
    return handleResponse<T>(res);
  },
} as const;
