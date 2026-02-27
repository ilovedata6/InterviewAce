/* BFF: Interview session
 * GET /api/interviews/[id] → FastAPI GET /interview/{id}
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/interview/${id}`);
  return NextResponse.json(result.data, { status: result.status });
}
