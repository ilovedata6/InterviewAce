/* ──────────────────────────────────────────────────────────
 * Interview Progress Bar
 * Visual progress through questions (answered / total)
 * ────────────────────────────────────────────────────────── */

"use client";

import { CheckCircle2 } from "lucide-react";

interface InterviewProgressBarProps {
  answered: number;
  total: number;
}

export function InterviewProgressBar({ answered, total }: InterviewProgressBarProps) {
  const percent = total > 0 ? Math.round((answered / total) * 100) : 0;

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          Progress
        </span>
        <span className="font-semibold">
          {answered} / {total}
          <span className="text-muted-foreground ml-1 font-normal">({percent}%)</span>
        </span>
      </div>
      <div className="relative h-3 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
