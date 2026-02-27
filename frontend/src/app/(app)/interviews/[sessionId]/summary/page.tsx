/* ──────────────────────────────────────────────────────────
 * Interview Summary Page
 * Displays full summary after interview completion
 * ────────────────────────────────────────────────────────── */

"use client";

import { use } from "react";
import Link from "next/link";
import { useInterviewSummary, useInterviewSession } from "@/hooks/use-interview";
import { InterviewSummaryDisplay } from "@/components/interview/interview-summary";
import { ScoreBreakdown } from "@/components/interview/score-breakdown";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle, ArrowLeft, RotateCcw } from "lucide-react";
import { ROUTES } from "@/lib/constants";

export default function InterviewSummaryPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useInterviewSummary(sessionId);
  const { data: session } = useInterviewSession(sessionId);

  if (summaryLoading) {
    return (
      <div className="container max-w-3xl space-y-6 py-8">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (summaryError || !summary) {
    return (
      <div className="container max-w-3xl py-8">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <AlertCircle className="text-destructive h-12 w-12" />
            <p className="text-destructive font-medium">
              {summaryError?.message || "Failed to load interview summary"}
            </p>
            <Button variant="outline" asChild>
              <Link href={ROUTES.INTERVIEWS}>Back to Interviews</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container max-w-3xl space-y-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interview Summary</h1>
          {session && (
            <p className="text-muted-foreground mt-1 text-sm">
              {session.difficulty} difficulty · {session.question_count} questions ·{" "}
              {session.started_at ? new Date(session.started_at).toLocaleDateString() : ""}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link href={ROUTES.INTERVIEWS}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              History
            </Link>
          </Button>
          <Button size="sm" asChild>
            <Link href={ROUTES.INTERVIEW_START}>
              <RotateCcw className="mr-2 h-4 w-4" />
              New Interview
            </Link>
          </Button>
        </div>
      </div>

      {/* Summary */}
      <InterviewSummaryDisplay summary={summary} />

      {/* Score Breakdown */}
      <ScoreBreakdown breakdown={summary.score_breakdown} />
    </div>
  );
}
