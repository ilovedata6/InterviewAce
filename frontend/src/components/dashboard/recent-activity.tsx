/* ──────────────────────────────────────────────────────────
 * Dashboard Recent Activity
 * Shows recent interview sessions with score, difficulty,
 * and link to summary.
 * ────────────────────────────────────────────────────────── */

"use client";

import Link from "next/link";
import { Clock, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { RecentSession } from "@/types/dashboard";

interface RecentActivityProps {
  sessions: RecentSession[] | undefined;
  isLoading: boolean;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function difficultyVariant(
  difficulty: string | null,
): "default" | "secondary" | "destructive" | "outline" {
  switch (difficulty) {
    case "easy":
      return "secondary";
    case "medium":
      return "default";
    case "hard":
      return "destructive";
    default:
      return "outline";
  }
}

function scoreColor(score: number | null): string {
  if (score === null) return "text-muted-foreground";
  if (score >= 0.8) return "text-emerald-600 dark:text-emerald-400";
  if (score >= 0.5) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

export function RecentActivity({ sessions, isLoading }: RecentActivityProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-3 w-24" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const hasData = sessions && sessions.length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Your last interview sessions</CardDescription>
      </CardHeader>
      <CardContent>
        {!hasData ? (
          <div className="flex flex-col items-center py-8 text-center">
            <Clock className="text-muted-foreground/50 mb-3 h-10 w-10" />
            <p className="text-muted-foreground text-sm">No interviews yet.</p>
            <p className="text-muted-foreground/70 text-xs">
              Start your first interview to see activity here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className="hover:bg-muted/50 flex items-center justify-between gap-4 rounded-lg border p-3 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium">Interview Session</span>
                    {session.difficulty && (
                      <Badge variant={difficultyVariant(session.difficulty)} className="text-xs">
                        {session.difficulty}
                      </Badge>
                    )}
                  </div>
                  <p className="text-muted-foreground mt-0.5 text-xs">
                    {formatDate(session.started_at)}
                    {session.completed_at ? " • Completed" : " • In progress"}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {session.final_score !== null ? (
                    <span className={`text-lg font-bold ${scoreColor(session.final_score)}`}>
                      {(session.final_score * 10).toFixed(0)}%
                    </span>
                  ) : (
                    <span className="text-muted-foreground text-sm">—</span>
                  )}

                  {session.completed_at && (
                    <Button variant="ghost" size="icon" asChild>
                      <Link href={`/interviews/${session.session_id}/summary`}>
                        <ExternalLink className="h-4 w-4" />
                        <span className="sr-only">View summary</span>
                      </Link>
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
