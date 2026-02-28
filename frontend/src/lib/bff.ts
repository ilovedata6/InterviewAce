/* ──────────────────────────────────────────────────────────
 * BFF Proxy Utility
 *
 * Central helper for Next.js API route handlers to:
 *  1. Read JWT from httpOnly cookies
 *  2. Forward requests to the FastAPI backend
 *  3. Handle token refresh transparently
 * ────────────────────────────────────────────────────────── */

import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000/api/v1";
const ACCESS_TOKEN_COOKIE = "access_token";
const REFRESH_TOKEN_COOKIE = "refresh_token";

/** Max age for auth cookies (7 days) */
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7;

/** Shared cookie options */
const COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
  maxAge: COOKIE_MAX_AGE,
};

/** ── Cookie helpers ── */

export async function getAccessToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(ACCESS_TOKEN_COOKIE)?.value;
}

export async function getRefreshToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(REFRESH_TOKEN_COOKIE)?.value;
}

export async function setAuthCookies(accessToken: string, refreshToken: string) {
  const cookieStore = await cookies();
  cookieStore.set(ACCESS_TOKEN_COOKIE, accessToken, COOKIE_OPTIONS);
  cookieStore.set(REFRESH_TOKEN_COOKIE, refreshToken, COOKIE_OPTIONS);
}

export async function clearAuthCookies() {
  const cookieStore = await cookies();
  cookieStore.delete(ACCESS_TOKEN_COOKIE);
  cookieStore.delete(REFRESH_TOKEN_COOKIE);
}

/** ── Backend fetch helper ── */

interface BackendFetchOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  /** If true, skip adding Authorization header */
  noAuth?: boolean;
  /** Content type override */
  contentType?: string;
}

/**
 * Fetch from the FastAPI backend.
 * Automatically attaches the JWT from cookies.
 * If 401, attempts a token refresh and retries once.
 */
export async function backendFetch<T = unknown>(
  path: string,
  options: BackendFetchOptions = {},
): Promise<{ data: T; status: number }> {
  const { method = "GET", body, headers = {}, noAuth = false, contentType } = options;

  const url = `${BACKEND_URL}${path}`;

  // Build headers
  const reqHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };

  if (!noAuth) {
    const token = await getAccessToken();
    if (token) {
      reqHeaders["Authorization"] = `Bearer ${token}`;
    }
  }

  // Body handling
  let reqBody: string | undefined;
  if (body !== undefined) {
    if (contentType === "application/x-www-form-urlencoded") {
      reqBody = body as string;
      reqHeaders["Content-Type"] = "application/x-www-form-urlencoded";
    } else {
      reqBody = JSON.stringify(body);
      reqHeaders["Content-Type"] = "application/json";
    }
  }

  let res = await fetch(url, {
    method,
    headers: reqHeaders,
    body: reqBody,
    signal: AbortSignal.timeout(120_000), // 2 min timeout for LLM-heavy endpoints
  });

  // If unauthorized, try refreshing the token
  if (res.status === 401 && !noAuth) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const newToken = await getAccessToken();
      if (newToken) {
        reqHeaders["Authorization"] = `Bearer ${newToken}`;
      }
      res = await fetch(url, {
        method,
        headers: reqHeaders,
        body: reqBody,
        signal: AbortSignal.timeout(120_000),
      });
    }
  }

  // Parse response
  if (res.status === 204) {
    return { data: undefined as T, status: 204 };
  }

  const contentTypeHeader = res.headers.get("content-type") ?? "";
  if (contentTypeHeader.includes("application/json")) {
    const data = (await res.json()) as T;
    return { data, status: res.status };
  }

  // Non-JSON (e.g., file download) — return raw text
  const text = await res.text();
  return { data: text as unknown as T, status: res.status };
}

/**
 * Fetch for file downloads (returns the raw Response so caller can stream the body).
 */
export async function backendFetchRaw(path: string): Promise<Response> {
  const url = `${BACKEND_URL}${path}`;
  const token = await getAccessToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return fetch(url, { method: "GET", headers });
}

/**
 * Forward a multipart upload to the backend.
 */
export async function backendUpload<T = unknown>(
  path: string,
  formData: FormData,
): Promise<{ data: T; status: number }> {
  const url = `${BACKEND_URL}${path}`;
  const token = await getAccessToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  // Don't set Content-Type — let fetch set it with boundary
  const res = await fetch(url, { method: "POST", headers, body: formData });
  if (res.status === 204) {
    return { data: undefined as T, status: 204 };
  }
  const data = (await res.json()) as T;
  return { data, status: res.status };
}

/** ── Token refresh ── */

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${BACKEND_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${refreshToken}`,
        Accept: "application/json",
      },
    });

    if (!res.ok) {
      await clearAuthCookies();
      return false;
    }

    const data = (await res.json()) as {
      access_token: string;
      refresh_token: string;
    };
    await setAuthCookies(data.access_token, data.refresh_token);
    return true;
  } catch {
    await clearAuthCookies();
    return false;
  }
}

/** ── Response helpers ── */

/** Convert a backendFetch result into a NextResponse */
export function proxyResponse<T>(result: { data: T; status: number }): NextResponse {
  if (result.status === 204) {
    return new NextResponse(null, { status: 204 });
  }
  return NextResponse.json(result.data, { status: result.status });
}

/** Extract search params from a NextRequest as a plain Record */
export function extractParams(req: NextRequest): Record<string, string> {
  const params: Record<string, string> = {};
  req.nextUrl.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  return params;
}

/** Build a query string from a Record */
export function buildQueryString(params: Record<string, string>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== "",
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries).toString();
}
