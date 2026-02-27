/* BFF: POST /api/auth/refresh → FastAPI POST /auth/refresh */

import { NextResponse } from "next/server";
import { backendFetch, clearAuthCookies, getRefreshToken, setAuthCookies } from "@/lib/bff";

export async function POST() {
  const refreshToken = await getRefreshToken();

  if (!refreshToken) {
    return NextResponse.json({ detail: "No refresh token" }, { status: 401 });
  }

  const { data, status } = await backendFetch<{
    access_token: string;
    refresh_token: string;
    token_type: string;
  }>("/auth/refresh", {
    method: "POST",
    headers: { Authorization: `Bearer ${refreshToken}` },
    noAuth: true,
  });

  if (status >= 400) {
    await clearAuthCookies();
    return NextResponse.json(data, { status });
  }

  await setAuthCookies(data.access_token, data.refresh_token);
  return NextResponse.json({ message: "Token refreshed" }, { status: 200 });
}
