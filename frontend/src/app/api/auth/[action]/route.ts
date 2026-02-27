/* BFF: Remaining auth routes
 * POST /api/auth/verify-email       → FastAPI POST /auth/verify-email
 * POST /api/auth/resend-verification → FastAPI POST /auth/resend-verification
 * POST /api/auth/forgot-password    → FastAPI POST /auth/reset-password-request
 * POST /api/auth/reset-password     → FastAPI POST /auth/reset-password-confirm
 * POST /api/auth/change-password    → FastAPI POST /auth/change-password
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

/** Map BFF route names to FastAPI paths */
const ROUTE_MAP: Record<string, { backendPath: string; requiresAuth: boolean }> = {
  "verify-email": { backendPath: "/auth/verify-email", requiresAuth: false },
  "resend-verification": { backendPath: "/auth/resend-verification", requiresAuth: false },
  "forgot-password": { backendPath: "/auth/reset-password-request", requiresAuth: false },
  "reset-password": { backendPath: "/auth/reset-password-confirm", requiresAuth: false },
  "change-password": { backendPath: "/auth/change-password", requiresAuth: true },
};

export async function POST(req: NextRequest, { params }: { params: Promise<{ action: string }> }) {
  const { action } = await params;
  const route = ROUTE_MAP[action];

  if (!route) {
    return NextResponse.json({ detail: "Unknown auth action" }, { status: 404 });
  }

  const body = await req.json();
  const { data, status } = await backendFetch(route.backendPath, {
    method: "POST",
    body,
    noAuth: !route.requiresAuth,
  });

  return NextResponse.json(data, { status });
}
