/* BFF: Interview start
 * POST /api/interviews/start → FastAPI POST /interview/start
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const result = await backendFetch("/interview/start", { method: "POST", body });
  return NextResponse.json(result.data, { status: result.status });
}
