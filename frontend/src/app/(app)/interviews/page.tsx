/* ──────────────────────────────────────────────────────────
 * Interview History Page
 * Lists all past and in-progress interviews
 * ────────────────────────────────────────────────────────── */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useInterviewHistory } from "@/hooks/use-interview";
import { InterviewHistoryTable } from "@/components/interview/interview-history-table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ROUTES } from "@/lib/constants";
import { Plus, ChevronLeft, ChevronRight } from "lucide-react";

const PAGE_SIZE = 10;

export default function InterviewsPage() {
  const [page, setPage] = useState(0);
  const { data, isLoading } = useInterviewHistory({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const sessions = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="container max-w-5xl space-y-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Interviews</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            View your interview history and past results.
          </p>
        </div>
        <Button asChild>
          <Link href={ROUTES.INTERVIEW_START}>
            <Plus className="mr-2 h-4 w-4" />
            New Interview
          </Link>
        </Button>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <InterviewHistoryTable sessions={sessions} />
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground text-sm">
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm font-medium">
              {page + 1} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page + 1 >= totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
