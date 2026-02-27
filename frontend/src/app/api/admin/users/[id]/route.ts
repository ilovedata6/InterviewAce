/* BFF: Admin user detail + activate/deactivate
 * GET   /api/admin/users/[id]            → FastAPI GET   /admin/users/{id}
 * PATCH /api/admin/users/[id]?action=... → FastAPI PATCH /admin/users/{id}/{action}
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

  if (action !== "activate" && action !== "deactivate") {
    return NextResponse.json({ detail: "Invalid action" }, { status: 400 });
  }

  const result = await backendFetch(`/admin/users/${id}/${action}`, {
    method: "PATCH",
  });
  return NextResponse.json(result.data, { status: result.status });
}
