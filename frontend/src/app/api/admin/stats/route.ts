/* BFF: Admin stats
 * GET /api/admin/stats → FastAPI GET /admin/stats
 */

import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET() {
  const result = await backendFetch("/admin/stats");
  return NextResponse.json(result.data, { status: result.status });
}
