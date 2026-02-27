/* ──────────────────────────────────────────────────────────
 * Interview Progress Bar
 * Visual progress through questions (answered / total)
 * ────────────────────────────────────────────────────────── */

"use client";

import { Progress } from "@/components/ui/progress";
import { CheckCircle2 } from "lucide-react";

interface InterviewProgressBarProps {
  answered: number;
  total: number;
}

export function InterviewProgressBar({ answered, total }: InterviewProgressBarProps) {
  const percent = total > 0 ? Math.round((answered / total) * 100) : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground flex items-center gap-1.5">
          <CheckCircle2 className="h-4 w-4" />
          Progress
        </span>
        <span className="font-medium">
          {answered} / {total} answered ({percent}%)
        </span>
      </div>
      <Progress value={percent} className="h-2" />
    </div>
  );
}
