/* BFF: Interview summary
 * GET /api/interviews/[id]/summary → FastAPI GET /interview/{id}/summary
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/interview/${id}/summary`);
  return NextResponse.json(result.data, { status: result.status });
}
