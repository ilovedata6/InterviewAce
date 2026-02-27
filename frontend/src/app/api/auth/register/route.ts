/* BFF: POST /api/auth/register → FastAPI POST /auth/register */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function POST(req: NextRequest) {
  const body = await req.json();

  const { data, status } = await backendFetch("/auth/register", {
    method: "POST",
    body: {
      email: body.email,
      full_name: body.full_name,
      password: body.password,
    },
    noAuth: true,
  });

  return NextResponse.json(data, { status });
}
