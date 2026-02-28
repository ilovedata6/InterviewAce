/* ──────────────────────────────────────────────────────────
 * Question Display Component
 * Shows current question text, number, category, difficulty
 * ────────────────────────────────────────────────────────── */

"use client";

import type { Question } from "@/types/interview";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare } from "lucide-react";

interface QuestionDisplayProps {
  question: Question;
  totalQuestions: number;
}

const difficultyColor: Record<string, string> = {
  easy: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  hard: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  mixed: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
};

export function QuestionDisplay({ question, totalQuestions }: QuestionDisplayProps) {
  return (
    <Card className="animate-fade-in-up overflow-hidden border-zinc-200/80 shadow-sm dark:border-zinc-800/80">
      <CardHeader className="border-b border-zinc-100 bg-zinc-50/50 pb-3 dark:border-zinc-800/50 dark:bg-zinc-900/30">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground text-sm font-semibold">
            Question {question.order_index + 1}
            <span className="font-normal"> of {totalQuestions}</span>
          </span>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="rounded-lg capitalize">
              {question.category.replace("_", " ")}
            </Badge>
            <Badge variant="secondary" className={`rounded-lg ${difficultyColor[question.difficulty] ?? ""}`}>
              {question.difficulty}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-5">
        <div className="flex gap-3">
          <div className="mt-1 flex-shrink-0">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/40">
              <MessageSquare className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <p className="text-lg leading-relaxed">{question.question_text}</p>
        </div>
      </CardContent>
    </Card>
  );
}
