/* ──────────────────────────────────────────────────────────
 * Score Trend Chart
 * Line chart showing interview scores over time
 * ────────────────────────────────────────────────────────── */

"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { RecentSession } from "@/types/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";

interface ScoreTrendChartProps {
  sessions: RecentSession[];
}

export function ScoreTrendChart({ sessions }: ScoreTrendChartProps) {
  // Only show completed sessions with a score, sorted by date
  const data = sessions
    .filter((s) => s.completed_at && s.final_score != null)
    .sort((a, b) => new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime())
    .map((s) => ({
      date: new Date(s.completed_at!).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      }),
      score: s.final_score,
    }));

  if (data.length < 2) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="h-4 w-4" />
            Score Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground py-8 text-center text-sm">
            Complete at least 2 interviews to see your score trend.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <TrendingUp className="h-4 w-4" />
          Score Trend
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              className="fill-muted-foreground text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis
              domain={[0, 100]}
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
            <Line
              type="monotone"
              dataKey="score"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ r: 4, fill: "hsl(var(--primary))" }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
