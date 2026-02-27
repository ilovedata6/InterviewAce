/* BFF: Admin routes
 * GET /api/admin/users                → FastAPI GET   /admin/users
 * GET /api/admin/stats                → FastAPI GET   /admin/stats
 * GET /api/admin/users/[id]           → (via sub-route)
 * PATCH /api/admin/users/[id]/activate   → (via sub-route)
 * PATCH /api/admin/users/[id]/deactivate → (via sub-route)
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, buildQueryString, extractParams } from "@/lib/bff";

export async function GET(req: NextRequest) {
  const params = extractParams(req);
  const qs = buildQueryString(params);
  const result = await backendFetch(`/admin/users${qs}`);
  return NextResponse.json(result.data, { status: result.status });
}
