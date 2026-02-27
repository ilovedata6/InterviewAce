/* BFF: Submit answer
 * POST /api/interviews/[id]/answer?question_id=... → FastAPI POST /interview/{id}/{question_id}/answer
 */

import { NextResponse, type NextRequest } from "next/server";
import { backendFetch } from "@/lib/bff";

export async function POST(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = await req.json();
  const { question_id, ...answerBody } = body as {
    question_id: string;
    answer_text: string;
    time_taken_seconds?: number;
  };

  const result = await backendFetch(`/interview/${id}/${question_id}/answer`, {
    method: "POST",
    body: answerBody,
  });

  if (result.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  return NextResponse.json(result.data, { status: result.status });
}
