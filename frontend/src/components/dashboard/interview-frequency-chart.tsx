/* ──────────────────────────────────────────────────────────
 * Interview Frequency Chart
 * Bar chart showing interviews per week/month
 * ────────────────────────────────────────────────────────── */

"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import type { RecentSession } from "@/types/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";

interface InterviewFrequencyChartProps {
  sessions: RecentSession[];
}

export function InterviewFrequencyChart({ sessions }: InterviewFrequencyChartProps) {
  // Group sessions by week (last 8 weeks)
  const now = new Date();
  const weeks: Record<string, number> = {};

  for (let i = 7; i >= 0; i--) {
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - i * 7);
    const label = weekStart.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
    weeks[label] = 0;
  }

  const weekLabels = Object.keys(weeks);

  sessions.forEach((s) => {
    if (!s.started_at) return;
    const sessionDate = new Date(s.started_at);
    const diff = Math.floor((now.getTime() - sessionDate.getTime()) / (7 * 24 * 60 * 60 * 1000));
    const weekIdx = 7 - diff;
    if (weekIdx >= 0 && weekIdx < weekLabels.length) {
      weeks[weekLabels[weekIdx]]++;
    }
  });

  const data = weekLabels.map((label) => ({
    week: label,
    interviews: weeks[label],
  }));

  const hasData = data.some((d) => d.interviews > 0);

  if (!hasData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart3 className="h-4 w-4" />
            Interview Frequency
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground py-8 text-center text-sm">
            Start interviewing to see your weekly activity.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <BarChart3 className="h-4 w-4" />
          Interview Frequency (Last 8 Weeks)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="week"
              className="fill-muted-foreground text-xs"
              tick={{ fontSize: 11 }}
            />
            <YAxis
              allowDecimals={false}
              className="fill-muted-foreground text-xs"
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "1px solid hsl(var(--border))",
                backgroundColor: "hsl(var(--popover))",
                color: "hsl(var(--popover-foreground))",
              }}
            />
            <Bar dataKey="interviews" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
