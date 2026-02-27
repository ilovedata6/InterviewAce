/* BFF: Complete interview
 * POST /api/interviews/[id]/complete → FastAPI POST /interview/{id}/complete
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function POST(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/interview/${id}/complete`, { method: "POST" });
  return NextResponse.json(result.data, { status: result.status });
}
