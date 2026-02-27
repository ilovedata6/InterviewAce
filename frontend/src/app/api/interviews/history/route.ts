/* BFF: Interview history
 * GET /api/interviews/history?skip=&limit= → FastAPI GET /interview/history?skip=&limit=
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, buildQueryString, extractParams } from "@/lib/bff";

export async function GET(req: NextRequest) {
  const params = extractParams(req);
  const qs = buildQueryString(params);
  const result = await backendFetch(`/interview/history${qs}`);
  return NextResponse.json(result.data, { status: result.status });
}
