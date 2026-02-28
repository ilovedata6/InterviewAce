/* ──────────────────────────────────────────────────────────
 * Dashboard Page
 * Authenticated landing: stats, quick actions, recent
 * activity, and category performance.
 * ────────────────────────────────────────────────────────── */

"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentActivity } from "@/components/dashboard/recent-activity";
import { CategoryBreakdown } from "@/components/dashboard/category-breakdown";
import { ScoreTrendChart } from "@/components/dashboard/score-trend-chart";
import { SkillRadarChart } from "@/components/dashboard/skill-radar-chart";
import { InterviewFrequencyChart } from "@/components/dashboard/interview-frequency-chart";
import { useDashboardStats } from "@/hooks/use-dashboard";
import { useAuth } from "@/hooks/use-auth";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, isError, error, refetch, isRefetching } = useDashboardStats();

  // Time-of-day greeting
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {greeting}
            {user?.full_name ? `, ${user.full_name}` : ""} &#128075;
          </h1>
          <p className="text-muted-foreground">
            Here&apos;s an overview of your interview preparation progress.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isRefetching}
          className="rounded-lg"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefetching ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Error banner */}
      {isError && (
        <div className="border-destructive/50 bg-destructive/10 flex items-center gap-3 rounded-lg border p-4">
          <AlertCircle className="text-destructive h-5 w-5" />
          <div className="flex-1">
            <p className="text-destructive text-sm font-medium">Failed to load dashboard data</p>
            <p className="text-destructive/80 text-xs">
              {error instanceof Error ? error.message : "An unexpected error occurred."}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {/* Stats overview */}
      <StatsCards data={data} isLoading={isLoading} />

      {/* Quick actions */}
      <QuickActions />

      {/* Two-column layout for recent activity + category breakdown */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivity sessions={data?.recent_sessions} isLoading={isLoading} />
        <CategoryBreakdown data={data?.category_breakdown} isLoading={isLoading} />
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ScoreTrendChart sessions={data?.recent_sessions ?? []} />
        <SkillRadarChart breakdown={data?.category_breakdown ?? {}} />
      </div>

      {/* Interview frequency */}
      <InterviewFrequencyChart sessions={data?.recent_sessions ?? []} />
    </div>
  );
}
