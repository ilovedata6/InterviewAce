/* ──────────────────────────────────────────────────────────
 * Dashboard Stats Cards
 * 4 cards: Total Interviews, Average Score, Best Score,
 *          Resumes Uploaded
 * ────────────────────────────────────────────────────────── */

"use client";

import { Briefcase, FileText, Trophy, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DashboardStats } from "@/types/dashboard";

interface StatsCardsProps {
  data: DashboardStats | undefined;
  isLoading: boolean;
}

function formatScore(score: number | null): string {
  if (score === null || score === undefined) return "—";
  return `${(score * 10).toFixed(0)}%`;
}

const cards = [
  {
    key: "total-interviews",
    title: "Total Interviews",
    icon: Briefcase,
    getValue: (d: DashboardStats) => String(d.interviews.total),
    getSubtext: (d: DashboardStats) => `${d.interviews.completed} completed`,
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-50 dark:bg-blue-950/40",
  },
  {
    key: "avg-score",
    title: "Average Score",
    icon: TrendingUp,
    getValue: (d: DashboardStats) => formatScore(d.interviews.avg_score),
    getSubtext: () => "across all interviews",
    color: "text-emerald-600 dark:text-emerald-400",
    bgColor: "bg-emerald-50 dark:bg-emerald-950/40",
  },
  {
    key: "best-score",
    title: "Best Score",
    icon: Trophy,
    getValue: (d: DashboardStats) => formatScore(d.interviews.best_score),
    getSubtext: () => "personal record",
    color: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-50 dark:bg-amber-950/40",
  },
  {
    key: "resumes",
    title: "Resumes Uploaded",
    icon: FileText,
    getValue: (d: DashboardStats) => String(d.resumes.total),
    getSubtext: () => "available for interviews",
    color: "text-violet-600 dark:text-violet-400",
    bgColor: "bg-violet-50 dark:bg-violet-950/40",
  },
] as const;

export function StatsCards({ data, isLoading }: StatsCardsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-8 rounded-md" />
            </CardHeader>
            <CardContent>
              <Skeleton className="mb-1 h-8 w-16" />
              <Skeleton className="h-3 w-28" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(({ key, title, icon: Icon, getValue, getSubtext, color, bgColor }) => (
        <Card key={key} className="group relative overflow-hidden transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-blue-50/30 opacity-0 transition-opacity group-hover:opacity-100 dark:to-blue-950/20" />
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">{title}</CardTitle>
            <div className={`rounded-xl p-2.5 ${bgColor} transition-transform duration-300 group-hover:scale-110`}>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data ? getValue(data) : "—"}</div>
            <p className="text-muted-foreground mt-1 text-xs">{data ? getSubtext(data) : ""}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
