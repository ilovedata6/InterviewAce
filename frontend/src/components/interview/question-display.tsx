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
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground text-sm font-medium">
            Question {question.order_index + 1} of {totalQuestions}
          </span>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="capitalize">
              {question.category.replace("_", " ")}
            </Badge>
            <Badge variant="secondary" className={difficultyColor[question.difficulty] ?? ""}>
              {question.difficulty}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-3">
          <div className="mt-1 flex-shrink-0">
            <MessageSquare className="text-primary h-5 w-5" />
          </div>
          <p className="text-lg leading-relaxed">{question.question_text}</p>
        </div>
      </CardContent>
    </Card>
  );
}
