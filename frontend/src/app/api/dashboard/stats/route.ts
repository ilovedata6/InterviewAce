/* BFF: Dashboard stats
 * GET /api/dashboard/stats → FastAPI GET /dashboard/stats
 */

import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function GET() {
  const result = await backendFetch("/dashboard/stats");
  return NextResponse.json(result.data, { status: result.status });
}
