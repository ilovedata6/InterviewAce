/* ──────────────────────────────────────────────────────────
 * Admin Stats Page
 * System-wide statistics: users, interviews, sessions
 * ────────────────────────────────────────────────────────── */

"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Users, FileText, Brain, Activity } from "lucide-react";

interface AdminStats {
  total_users: number;
  active_users: number;
  total_resumes: number;
  total_interviews: number;
  completed_interviews: number;
  average_score: number | null;
}

export default function AdminStatsPage() {
  const { data: stats, isLoading } = useQuery<AdminStats>({
    queryKey: ["admin", "stats"],
    queryFn: () => apiClient.get<AdminStats>(API_ROUTES.ADMIN.STATS),
    staleTime: 120_000,
  });

  if (isLoading) {
    return (
      <div className="container max-w-5xl space-y-6 py-8">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  const cards = [
    {
      title: "Total Users",
      value: stats?.total_users ?? 0,
      icon: Users,
      description: `${stats?.active_users ?? 0} active`,
    },
    {
      title: "Total Resumes",
      value: stats?.total_resumes ?? 0,
      icon: FileText,
      description: "Uploaded resumes",
    },
    {
      title: "Total Interviews",
      value: stats?.total_interviews ?? 0,
      icon: Brain,
      description: `${stats?.completed_interviews ?? 0} completed`,
    },
    {
      title: "Average Score",
      value: stats?.average_score != null ? `${Math.round(stats.average_score)}/100` : "N/A",
      icon: Activity,
      description: "Across all interviews",
    },
  ];

  return (
    <div className="container max-w-5xl space-y-6 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Statistics</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Overview of platform activity and usage metrics.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-muted-foreground text-sm font-medium">
                {card.title}
              </CardTitle>
              <card.icon className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{card.value}</div>
              <p className="text-muted-foreground mt-1 text-xs">{card.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
