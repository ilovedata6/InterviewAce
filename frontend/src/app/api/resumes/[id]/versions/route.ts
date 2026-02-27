/* BFF: Resume versions
 * GET /api/resumes/[id]/versions → FastAPI GET /resume/version/{id}/versions
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await backendFetch(`/resume/version/${id}/versions`);
  return NextResponse.json(result.data, { status: result.status });
}
