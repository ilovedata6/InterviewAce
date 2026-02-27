/* BFF: GET /api/auth/me → FastAPI GET /auth/me */

import { backendFetch, proxyResponse } from "@/lib/bff";

export async function GET() {
  const result = await backendFetch("/auth/me");
  return proxyResponse(result);
}
