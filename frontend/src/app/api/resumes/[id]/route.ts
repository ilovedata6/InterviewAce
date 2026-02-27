/* BFF: Resume detail
 * GET    /api/resumes/[id] → FastAPI GET    /resume/{id}
 * PUT    /api/resumes/[id] → FastAPI PUT    /resume/{id}
 * DELETE /api/resumes/[id] → FastAPI DELETE /resume/{id}
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, proxyResponse } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/${id}`);
  return proxyResponse(result);
}

export async function PUT(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const result = await backendFetch(`/resume/${id}`, { method: "PUT", body });
  return proxyResponse(result);
}

export async function DELETE(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/${id}`, { method: "DELETE" });
  return proxyResponse(result);
}
