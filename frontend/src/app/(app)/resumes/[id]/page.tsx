/* ──────────────────────────────────────────────────────────
 * Resume Detail Page
 * Shows file info, analysis, versions, and actions
 * ────────────────────────────────────────────────────────── */

"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, FileText, RefreshCw, Share2, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import {
  useResume,
  useResumeAnalysis,
  useResumeVersions,
  useResumePolling,
  useDeleteResume,
  useReanalyzeResume,
} from "@/hooks/use-resumes";
import { ResumeAnalysis } from "@/components/resume/resume-analysis";
import { ResumeVersions } from "@/components/resume/resume-versions";
import { DeleteConfirmDialog } from "@/components/shared/delete-confirm-dialog";
import { ROUTES, API_ROUTES } from "@/lib/constants";
import { ApiClientError } from "@/lib/api-client";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    weekday: "short",
    month: "long",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ResumeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();

  const { data: resume, isLoading } = useResume(id);
  const { data: analysis, isLoading: analysisLoading } = useResumeAnalysis(id);
  const { data: versions, isLoading: versionsLoading } = useResumeVersions(id);
  const deleteMutation = useDeleteResume();
  const reanalyzeMutation = useReanalyzeResume(id);

  // Poll while status is pending/processing
  const { data: polledResume } = useResumePolling(id, resume?.status);
  const displayResume = polledResume || resume;

  const [deleteOpen, setDeleteOpen] = useState(false);

  // Update analysis when polling detects completion
  useEffect(() => {
    if (polledResume && polledResume.status === "analyzed" && resume?.status !== "analyzed") {
      toast.success("Analysis complete!");
    }
  }, [polledResume, resume?.status]);

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(id);
      toast.success("Resume deleted.");
      router.push(ROUTES.RESUMES);
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : "Failed to delete resume.";
      toast.error(message);
    }
  };

  const handleReanalyze = async () => {
    try {
      await reanalyzeMutation.mutateAsync();
      toast.success("Re-analysis started. This may take a moment.");
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : "Failed to start re-analysis.";
      toast.error(message);
    }
  };

  const handleExport = (format: string) => {
    const url = `${API_ROUTES.RESUMES.EXPORT(id)}?format=${format}`;
    window.open(url, "_blank");
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Skeleton className="h-9 w-9" />
          <div>
            <Skeleton className="h-7 w-48" />
            <Skeleton className="mt-1 h-4 w-32" />
          </div>
        </div>
        <Card>
          <CardContent className="space-y-4 pt-6">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!displayResume) {
    return (
      <div className="flex flex-col items-center py-16 text-center">
        <FileText className="text-muted-foreground/50 mb-4 h-12 w-12" />
        <h3 className="text-lg font-semibold">Resume not found</h3>
        <p className="text-muted-foreground mt-1 text-sm">
          The resume may have been deleted or you don&apos;t have access.
        </p>
        <Button asChild className="mt-4">
          <Link href={ROUTES.RESUMES}>Back to Resumes</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild>
            <Link href={ROUTES.RESUMES}>
              <ArrowLeft className="h-4 w-4" />
              <span className="sr-only">Back</span>
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {displayResume.title || displayResume.file_name}
            </h1>
            <p className="text-muted-foreground text-sm">
              Uploaded {formatDate(displayResume.created_at)}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleReanalyze}
            disabled={reanalyzeMutation.isPending}
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${reanalyzeMutation.isPending ? "animate-spin" : ""}`}
            />
            Re-analyze
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport("original")}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => toast.info("Share feature coming soon!")}
          >
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* File info card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">File Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-muted-foreground text-xs">File Name</p>
              <p className="mt-0.5 truncate text-sm font-medium">{displayResume.file_name}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs">Size</p>
              <p className="mt-0.5 text-sm font-medium">
                {formatFileSize(displayResume.file_size)}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs">Status</p>
              <Badge variant="outline" className="mt-0.5">
                {displayResume.status}
              </Badge>
            </div>
            <div>
              <p className="text-muted-foreground text-xs">Version</p>
              <p className="mt-0.5 text-sm font-medium">v{displayResume.version}</p>
            </div>
          </div>
          {displayResume.skills.length > 0 && (
            <div className="mt-4">
              <p className="text-muted-foreground mb-1 text-xs">Skills</p>
              <div className="flex flex-wrap gap-1">
                {displayResume.skills.map((skill) => (
                  <Badge key={skill} variant="secondary" className="text-xs">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs: Analysis + Versions */}
      <Tabs defaultValue="analysis">
        <TabsList>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
        </TabsList>
        <TabsContent value="analysis" className="mt-4">
          <ResumeAnalysis analysis={analysis} isLoading={analysisLoading} />
        </TabsContent>
        <TabsContent value="versions" className="mt-4">
          <ResumeVersions versions={versions} isLoading={versionsLoading} />
        </TabsContent>
      </Tabs>

      {/* Delete dialog */}
      <DeleteConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        onConfirm={handleDelete}
        title="Delete Resume"
        description="This will permanently delete this resume, its analysis, and all version history. This action cannot be undone."
        isDeleting={deleteMutation.isPending}
      />
    </div>
  );
}
