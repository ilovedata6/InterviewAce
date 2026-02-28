/* BFF: Admin user detail + activate/deactivate/role
 * GET   /api/admin/users/[id]                    → FastAPI GET   /admin/users/{id}
 * PATCH /api/admin/users/[id]?action=activate    → FastAPI PATCH /admin/users/{id}/activate
 * PATCH /api/admin/users/[id]?action=deactivate  → FastAPI PATCH /admin/users/{id}/deactivate
 * PATCH /api/admin/users/[id]?action=role        → FastAPI PATCH /admin/users/{id}/role  (body: {role})
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/admin/users/${id}`);
  return NextResponse.json(result.data, { status: result.status });
}

export async function PATCH(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const action = req.nextUrl.searchParams.get("action");

  if (action !== "activate" && action !== "deactivate" && action !== "role") {
    return NextResponse.json({ detail: "Invalid action" }, { status: 400 });
  }

  // Role change needs JSON body forwarded
  if (action === "role") {
    const body = await req.json();
    const result = await backendFetch(`/admin/users/${id}/role`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    return NextResponse.json(result.data, { status: result.status });
  }

  const result = await backendFetch(`/admin/users/${id}/${action}`, {
    method: "PATCH",
  });
  return NextResponse.json(result.data, { status: result.status });
}
