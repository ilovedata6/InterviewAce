/* BFF: POST /api/auth/login → FastAPI POST /auth/login (form-encoded) */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, setAuthCookies } from "@/lib/bff";

export async function POST(req: NextRequest) {
  const body = await req.json();

  // FastAPI login expects OAuth2 form data
  const formBody = new URLSearchParams({
    username: body.email,
    password: body.password,
  }).toString();

  const { data, status } = await backendFetch<{
    access_token: string;
    refresh_token: string;
    token_type: string;
  }>("/auth/login", {
    method: "POST",
    body: formBody,
    contentType: "application/x-www-form-urlencoded",
    noAuth: true,
  });

  if (status >= 400) {
    return NextResponse.json(data, { status });
  }

  // Set httpOnly cookies and return sanitized response
  await setAuthCookies(data.access_token, data.refresh_token);

  return NextResponse.json(
    { token_type: data.token_type, message: "Login successful" },
    { status: 200 },
  );
}
