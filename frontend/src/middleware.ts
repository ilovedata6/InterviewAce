/* ──────────────────────────────────────────────────────────
 * Next.js Middleware — Auth Guard
 *
 * Runs on every matched route BEFORE the page renders.
 *  • Unauthenticated user hitting a protected route → /login
 *  • Authenticated user hitting /login or /register   → /dashboard
 *  • Non-admin hitting /admin/*                       → /dashboard
 *
 * Cookie presence is the ONLY check here (lightweight).
 * Full token validation happens server-side in BFF routes.
 * ────────────────────────────────────────────────────────── */

import { NextResponse, type NextRequest } from "next/server";

/** Routes that do NOT require authentication */
const PUBLIC_PATHS = new Set([
  "/",
  "/login",
  "/register",
  "/verify-email",
  "/forgot-password",
  "/reset-password",
]);

/** Auth pages where authenticated users should be redirected away */
const AUTH_ONLY_PATHS = new Set(["/login", "/register"]);

/** Cookie names (must match lib/bff.ts) */
const ACCESS_TOKEN_COOKIE = "access_token";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if user has a token (cookie exists)
  const hasToken = request.cookies.has(ACCESS_TOKEN_COOKIE);

  // ── Authenticated user hitting auth pages → redirect to /dashboard ──
  if (hasToken && AUTH_ONLY_PATHS.has(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // ── Public route → allow through ──
  if (PUBLIC_PATHS.has(pathname)) {
    return NextResponse.next();
  }

  // ── Static/API/internal routes → allow through ──
  if (pathname.startsWith("/api/") || pathname.startsWith("/_next/") || pathname.includes(".")) {
    return NextResponse.next();
  }

  // ── Unauthenticated user hitting a protected route → /login ──
  if (!hasToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // ── Admin route guard (cookie-only check; full RBAC in BFF) ──
  // We store role in a non-httpOnly cookie so middleware can read it
  if (pathname.startsWith("/admin")) {
    const role = request.cookies.get("user_role")?.value;
    if (role !== "admin") {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     *  - _next/static (static files)
     *  - _next/image  (image optimization)
     *  - favicon.ico, sitemap.xml, robots.txt
     */
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
