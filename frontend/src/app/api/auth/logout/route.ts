/* BFF: POST /api/auth/logout → FastAPI POST /auth/logout + clear cookies */

import { NextResponse } from "next/server";
import { backendFetch, clearAuthCookies, getAccessToken } from "@/lib/bff";

export async function POST() {
  const token = await getAccessToken();

  if (token) {
    // Best-effort: tell FastAPI to invalidate the session
    await backendFetch("/auth/logout", { method: "POST" }).catch(() => {});
  }

  await clearAuthCookies();

  return NextResponse.json({ message: "Logged out" }, { status: 200 });
}
