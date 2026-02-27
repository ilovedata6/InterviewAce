/* ──────────────────────────────────────────────────────────
 * Resumes List Page
 * Grid of resume cards + upload button + status filter
 * ────────────────────────────────────────────────────────── */

"use client";

import { useState } from "react";
import Link from "next/link";
import { FileText, Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import { ResumeCard } from "@/components/resume/resume-card";
import { useResumes } from "@/hooks/use-resumes";
import { ROUTES } from "@/lib/constants";

const PAGE_SIZE = 12;

export default function ResumesPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("all");
  const [page, setPage] = useState(0);

  const { data, isLoading, isError, refetch } = useResumes({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    status: status === "all" ? undefined : status,
    search: search || undefined,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Resumes</h1>
          <p className="text-muted-foreground">
            Upload and manage your resumes for AI-powered analysis.
          </p>
        </div>
        <Button asChild>
          <Link href={ROUTES.RESUME_UPLOAD}>
            <Plus className="mr-2 h-4 w-4" />
            Upload Resume
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
          <Input
            placeholder="Search resumes..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="pl-9"
          />
        </div>
        <Select
          value={status}
          onValueChange={(v) => {
            setStatus(v);
            setPage(0);
          }}
        >
          <SelectTrigger className="w-full sm:w-[160px]">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="analyzed">Analyzed</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="error">Error</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-6">
              <div className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-md" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
                <Skeleton className="h-5 w-16" />
              </div>
              <div className="mt-4 flex gap-1">
                <Skeleton className="h-5 w-14" />
                <Skeleton className="h-5 w-14" />
                <Skeleton className="h-5 w-14" />
              </div>
              <div className="mt-4 flex justify-between">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-3 w-12" />
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="flex flex-col items-center py-12 text-center">
          <p className="text-destructive text-sm">Failed to load resumes.</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && data && data.items.length === 0 && (
        <div className="flex flex-col items-center py-16 text-center">
          <FileText className="text-muted-foreground/50 mb-4 h-12 w-12" />
          <h3 className="text-lg font-semibold">No resumes found</h3>
          <p className="text-muted-foreground mt-1 text-sm">
            {search
              ? "Try adjusting your search or filter."
              : "Upload your first resume to get started."}
          </p>
          {!search && (
            <Button asChild className="mt-4">
              <Link href={ROUTES.RESUME_UPLOAD}>
                <Plus className="mr-2 h-4 w-4" />
                Upload Resume
              </Link>
            </Button>
          )}
        </div>
      )}

      {/* Resume grid */}
      {!isLoading && !isError && data && data.items.length > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((resume) => (
              <ResumeCard key={resume.id} resume={resume} />
            ))}
          </div>

          {/* Pagination */}
          {data.has_more || page > 0 ? (
            <div className="flex items-center justify-between pt-4">
              <p className="text-muted-foreground text-sm">
                Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, data.total)} of{" "}
                {data.total}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={!data.has_more}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
