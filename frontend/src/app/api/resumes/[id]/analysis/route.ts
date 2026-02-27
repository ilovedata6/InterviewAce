/* BFF: Resume analysis
 * GET  /api/resumes/[id]/analysis             → FastAPI GET  /resume/analysis/{id}
 * POST /api/resumes/[id]/analysis/reanalyze   → FastAPI POST /resume/analysis/{id}/reanalyze
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/analysis/${id}`);
  return NextResponse.json(result.data, { status: result.status });
}

export async function POST(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/analysis/${id}/reanalyze`, {
    method: "POST",
  });
  return NextResponse.json(result.data, { status: result.status });
}
