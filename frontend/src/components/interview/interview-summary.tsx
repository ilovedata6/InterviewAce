/* ──────────────────────────────────────────────────────────
 * Interview Summary Component
 * Displays final score, feedback, per-question breakdown
 * ────────────────────────────────────────────────────────── */

"use client";

import type { InterviewSummary } from "@/types/interview";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Trophy, MessageSquare, ThumbsUp, ThumbsDown, Star } from "lucide-react";

interface InterviewSummaryDisplayProps {
  summary: InterviewSummary;
}

function scoreColor(score: number) {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function scoreBadgeVariant(score: number): "default" | "secondary" | "destructive" {
  if (score >= 80) return "default";
  if (score >= 60) return "secondary";
  return "destructive";
}

export function InterviewSummaryDisplay({ summary }: InterviewSummaryDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card className="overflow-hidden">
        <CardContent className="flex flex-col items-center gap-4 py-10">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-100 to-amber-50 shadow-sm dark:from-amber-900/40 dark:to-amber-950/20">
            <Trophy className="h-8 w-8 text-amber-600 dark:text-amber-400" />
          </div>
          <div className={`text-6xl font-extrabold tracking-tight ${scoreColor(summary.final_score)}`}>
            {summary.final_score}
            <span className="text-muted-foreground text-2xl font-normal">/100</span>
          </div>
          <p className="text-muted-foreground max-w-md text-center leading-relaxed">{summary.feedback_summary}</p>
        </CardContent>
      </Card>

      {/* Strengths & Weaknesses */}
      <div className="grid gap-4 md:grid-cols-2">
        {summary.strengths && summary.strengths.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <ThumbsUp className="h-4 w-4 text-green-500" />
                Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {summary.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Star className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-green-500" />
                    {s}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {summary.weaknesses && summary.weaknesses.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <ThumbsDown className="h-4 w-4 text-red-500" />
                Areas for Improvement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {summary.weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Star className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-red-500" />
                    {w}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Per-Question Feedback */}
      {summary.question_feedback && summary.question_feedback.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageSquare className="h-4 w-4" />
              Question-by-Question Feedback
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {summary.question_feedback.map((qf, idx) => (
              <div key={qf.question_id}>
                {idx > 0 && <Separator className="mb-4" />}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">Question {idx + 1}</span>
                      <Badge variant={scoreBadgeVariant(qf.evaluation_score)}>
                        {qf.evaluation_score}/100
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-sm">{qf.feedback_comment}</p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
