/* BFF: Resume export / download
 * GET /api/resumes/[id]/export?format=pdf → FastAPI GET /resume/export/{id}/download?format=pdf
 */

import { type NextRequest } from "next/server";
import { backendFetchRaw, extractParams, buildQueryString } from "@/lib/bff";

export async function GET(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const queryParams = extractParams(req);
  const qs = buildQueryString(queryParams);

  const backendRes = await backendFetchRaw(`/resume/export/${id}/download${qs}`);

  // Stream the file response back to the client
  return new Response(backendRes.body, {
    status: backendRes.status,
    headers: {
      "Content-Type": backendRes.headers.get("content-type") ?? "application/octet-stream",
      "Content-Disposition": backendRes.headers.get("content-disposition") ?? "",
    },
  });
}
