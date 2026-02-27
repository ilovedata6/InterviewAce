/* ──────────────────────────────────────────────────────────
 * Skill Radar Chart
 * Radar chart showing strengths/weaknesses by category
 * ────────────────────────────────────────────────────────── */

"use client";

import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
} from "recharts";
import type { CategoryScore } from "@/types/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Target } from "lucide-react";

interface SkillRadarChartProps {
  breakdown: Record<string, CategoryScore>;
}

function formatLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

export function SkillRadarChart({ breakdown }: SkillRadarChartProps) {
  const entries = Object.entries(breakdown);

  if (entries.length < 3) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Target className="h-4 w-4" />
            Skill Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground py-8 text-center text-sm">
            Interview more categories to see your skill radar.
          </p>
        </CardContent>
      </Card>
    );
  }

  const data = entries.map(([category, score]) => ({
    category: formatLabel(category),
    score: Math.round(score.avg_score),
    fullMark: 100,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Target className="h-4 w-4" />
          Skill Breakdown
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={data}>
            <PolarGrid className="stroke-muted" />
            <PolarAngleAxis
              dataKey="category"
              className="fill-muted-foreground text-xs"
              tick={{ fontSize: 11 }}
            />
            <PolarRadiusAxis
              domain={[0, 100]}
              tick={{ fontSize: 10 }}
              className="fill-muted-foreground text-xs"
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "1px solid hsl(var(--border))",
                backgroundColor: "hsl(var(--popover))",
                color: "hsl(var(--popover-foreground))",
              }}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.2}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
