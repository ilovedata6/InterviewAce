/* BFF: POST /api/auth/login → FastAPI POST /auth/login (form-encoded) */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, setAuthCookies } from "@/lib/bff";
import { cookies } from "next/headers";
import type { User } from "@/types/auth";

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

  // Set httpOnly cookies
  await setAuthCookies(data.access_token, data.refresh_token);

  // Fetch user profile so we can return it and set role cookie
  const { data: user, status: meStatus } = await backendFetch<User>("/auth/me", {
    headers: { Authorization: `Bearer ${data.access_token}` },
  });

  if (meStatus >= 400) {
    // Token worked for login but /me failed — still return success
    return NextResponse.json({ message: "Login successful" }, { status: 200 });
  }

  // Set a non-httpOnly cookie so middleware can read the user role
  const cookieStore = await cookies();
  cookieStore.set("user_role", user.role ?? "user", {
    httpOnly: false,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  return NextResponse.json(user, { status: 200 });
}
