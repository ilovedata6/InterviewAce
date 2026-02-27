/* BFF: Resume sharing
 * POST /api/resumes/[id]/share   → FastAPI POST /resume/sharing/{id}/share
 * DELETE /api/resumes/[id]/share → FastAPI POST /resume/sharing/{id}/unshare
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, proxyResponse } from "@/lib/bff";

export async function POST(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const result = await backendFetch(`/resume/sharing/${id}/share`, {
    method: "POST",
    body,
  });
  return NextResponse.json(result.data, { status: result.status });
}

export async function DELETE(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/sharing/${id}/unshare`, {
    method: "POST",
  });
  return proxyResponse(result);
}
