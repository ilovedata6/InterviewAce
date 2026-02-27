/* ──────────────────────────────────────────────────────────
 * Interview History Table
 * Sortable table: date, difficulty, questions, score, status
 * ────────────────────────────────────────────────────────── */

"use client";

import Link from "next/link";
import type { InterviewSession } from "@/types/interview";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Eye, BarChart3, Play } from "lucide-react";

interface InterviewHistoryTableProps {
  sessions: InterviewSession[];
}

function statusBadge(session: InterviewSession) {
  if (session.completed_at) {
    return <Badge variant="default">Completed</Badge>;
  }
  return (
    <Badge variant="secondary" className="animate-pulse">
      In Progress
    </Badge>
  );
}

function difficultyBadge(difficulty: string) {
  const colors: Record<string, string> = {
    easy: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    hard: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    mixed: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  };

  return (
    <Badge variant="secondary" className={`capitalize ${colors[difficulty] ?? ""}`}>
      {difficulty}
    </Badge>
  );
}

export function InterviewHistoryTable({ sessions }: InterviewHistoryTableProps) {
  if (sessions.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 py-12 text-center">
        <BarChart3 className="text-muted-foreground h-12 w-12" />
        <div>
          <p className="font-medium">No interviews yet</p>
          <p className="text-muted-foreground text-sm">
            Start your first mock interview to see your history here.
          </p>
        </div>
        <Button asChild>
          <Link href="/interviews/start">
            <Play className="mr-2 h-4 w-4" />
            Start Interview
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Difficulty</TableHead>
            <TableHead className="text-center">Questions</TableHead>
            <TableHead className="text-center">Score</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sessions.map((session) => (
            <TableRow key={session.id}>
              <TableCell className="font-medium">
                {new Date(session.started_at).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </TableCell>
              <TableCell>{difficultyBadge(session.difficulty)}</TableCell>
              <TableCell className="text-center">{session.question_count}</TableCell>
              <TableCell className="text-center">
                {session.final_score !== null ? (
                  <span className="font-semibold">
                    {session.final_score}
                    <span className="text-muted-foreground text-xs">/100</span>
                  </span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell>{statusBadge(session)}</TableCell>
              <TableCell className="text-right">
                {session.completed_at ? (
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/interviews/${session.id}/summary`}>
                      <Eye className="mr-1.5 h-3.5 w-3.5" />
                      Summary
                    </Link>
                  </Button>
                ) : (
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/interviews/${session.id}`}>
                      <Play className="mr-1.5 h-3.5 w-3.5" />
                      Continue
                    </Link>
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
