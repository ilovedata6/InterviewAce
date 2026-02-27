/* BFF: Resume list + upload
 * GET  /api/resumes       → FastAPI GET  /resume/?skip=&limit=&status=&search=
 * POST /api/resumes       → FastAPI POST /resume/upload/ (multipart)
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch, backendUpload, buildQueryString, extractParams } from "@/lib/bff";

export async function GET(req: NextRequest) {
  const params = extractParams(req);
  const qs = buildQueryString(params);
  const result = await backendFetch(`/resume/${qs}`);
  return NextResponse.json(result.data, { status: result.status });
}

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const result = await backendUpload("/resume/upload/", formData);
  return NextResponse.json(result.data, { status: result.status });
}
