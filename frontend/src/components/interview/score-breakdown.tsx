/* ──────────────────────────────────────────────────────────
 * Score Breakdown Component
 * Visual display of scores by category (horizontal bars)
 * ────────────────────────────────────────────────────────── */

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { BarChart3 } from "lucide-react";

interface ScoreBreakdownProps {
  /** score_breakdown from the interview summary — Record<category, score> */
  breakdown: Record<string, unknown> | null | undefined;
}

function formatLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

export function ScoreBreakdown({ breakdown }: ScoreBreakdownProps) {
  if (!breakdown || Object.keys(breakdown).length === 0) return null;

  // Filter to entries that are numeric scores
  const entries = Object.entries(breakdown)
    .filter(([, v]) => typeof v === "number")
    .sort(([, a], [, b]) => (b as number) - (a as number)) as [string, number][];

  if (entries.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <BarChart3 className="h-4 w-4" />
          Score Breakdown
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {entries.map(([category, score]) => (
          <div key={category} className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{formatLabel(category)}</span>
              <span className={scoreColor(score)}>{score}/100</span>
            </div>
            <Progress value={score} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
