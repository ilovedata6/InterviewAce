/* BFF: POST /api/auth/logout → FastAPI POST /auth/logout + clear cookies */

import { NextResponse } from "next/server";
import { backendFetch, clearAuthCookies, getAccessToken } from "@/lib/bff";
import { cookies } from "next/headers";

export async function POST() {
  const token = await getAccessToken();

  if (token) {
    // Best-effort: tell FastAPI to invalidate the session
    await backendFetch("/auth/logout", { method: "POST" }).catch(() => {});
  }

  await clearAuthCookies();

  // Clear the role cookie used by middleware
  const cookieStore = await cookies();
  cookieStore.delete("user_role");

  return NextResponse.json({ message: "Logged out" }, { status: 200 });
}
