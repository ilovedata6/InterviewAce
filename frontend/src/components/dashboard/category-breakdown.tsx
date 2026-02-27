/* ──────────────────────────────────────────────────────────
 * Dashboard Category Breakdown
 * Shows per-category average scores from interviews
 * ────────────────────────────────────────────────────────── */

"use client";

import { BarChart3 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import type { CategoryScore } from "@/types/dashboard";

interface CategoryBreakdownProps {
  data: Record<string, CategoryScore> | undefined;
  isLoading: boolean;
}

function formatCategory(cat: string): string {
  return cat.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function scorePercent(score: number): number {
  // Backend stores scores 0-10, convert to 0-100
  return Math.min(Math.round(score * 10), 100);
}

function scoreColor(score: number): string {
  const pct = score * 10;
  if (pct >= 80) return "text-emerald-600 dark:text-emerald-400";
  if (pct >= 50) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

export function CategoryBreakdown({ data, isLoading }: CategoryBreakdownProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-4 w-56" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-1">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-3 w-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const entries = data ? Object.entries(data) : [];
  const hasData = entries.length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Category Performance</CardTitle>
        <CardDescription>Average scores by question category</CardDescription>
      </CardHeader>
      <CardContent>
        {!hasData ? (
          <div className="flex flex-col items-center py-8 text-center">
            <BarChart3 className="text-muted-foreground/50 mb-3 h-10 w-10" />
            <p className="text-muted-foreground text-sm">No category data yet.</p>
            <p className="text-muted-foreground/70 text-xs">
              Complete interviews to see your performance breakdown.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {entries
              .sort(([, a], [, b]) => b.avg_score - a.avg_score)
              .map(([category, { avg_score, count }]) => (
                <div key={category}>
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-sm font-medium">{formatCategory(category)}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${scoreColor(avg_score)}`}>
                        {scorePercent(avg_score)}%
                      </span>
                      <span className="text-muted-foreground text-xs">
                        ({count} {count === 1 ? "question" : "questions"})
                      </span>
                    </div>
                  </div>
                  <Progress value={scorePercent(avg_score)} className="h-2" />
                </div>
              ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
