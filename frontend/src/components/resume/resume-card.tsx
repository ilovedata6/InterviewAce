/* ──────────────────────────────────────────────────────────
 * Resume Card
 * Shows filename, date, status badge, skills, used in grid
 * ────────────────────────────────────────────────────────── */

"use client";

import Link from "next/link";
import { FileText, Clock, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import type { Resume } from "@/types/resume";

interface ResumeCardProps {
  resume: Resume;
}

function statusConfig(status: string) {
  switch (status) {
    case "analyzed":
      return {
        label: "Analyzed",
        icon: CheckCircle2,
        variant: "default" as const,
        color: "text-emerald-600 dark:text-emerald-400",
      };
    case "processing":
      return {
        label: "Processing",
        icon: Loader2,
        variant: "secondary" as const,
        color: "text-blue-600 dark:text-blue-400",
        animate: true,
      };
    case "pending":
      return {
        label: "Pending",
        icon: Clock,
        variant: "outline" as const,
        color: "text-amber-600 dark:text-amber-400",
      };
    case "error":
      return {
        label: "Error",
        icon: AlertCircle,
        variant: "destructive" as const,
        color: "text-red-600 dark:text-red-400",
      };
    default:
      return {
        label: status,
        icon: FileText,
        variant: "outline" as const,
        color: "text-muted-foreground",
      };
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ResumeCard({ resume }: ResumeCardProps) {
  const config = statusConfig(resume.status);
  const StatusIcon = config.icon;

  return (
    <Link href={`/resumes/${resume.id}`}>
      <Card className="group relative h-full border-zinc-200/80 transition-all duration-300 hover:-translate-y-1 hover:border-blue-300 hover:shadow-xl dark:border-zinc-800/80 dark:hover:border-blue-800">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-50/30 to-transparent opacity-0 transition-opacity group-hover:opacity-100 dark:from-blue-950/20" />
        <CardHeader className="relative pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex min-w-0 items-center gap-2.5">
              <div className="shrink-0 rounded-xl bg-blue-50 p-2.5 shadow-sm transition-transform duration-300 group-hover:scale-105 dark:bg-blue-950/40">
                <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="min-w-0">
                <h3 className="group-hover:text-primary truncate text-sm font-semibold transition-colors">
                  {resume.title || resume.file_name}
                </h3>
                <p className="text-muted-foreground truncate text-xs">{resume.file_name}</p>
              </div>
            </div>
            <Badge variant={config.variant} className="shrink-0 text-xs">
              <StatusIcon
                className={`mr-1 h-3 w-3 ${config.color} ${"animate" in config && config.animate ? "animate-spin" : ""}`}
              />
              {config.label}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="pb-3">
          {resume.skills.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {resume.skills.slice(0, 4).map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs font-normal">
                  {skill}
                </Badge>
              ))}
              {resume.skills.length > 4 && (
                <Badge variant="secondary" className="text-xs font-normal">
                  +{resume.skills.length - 4}
                </Badge>
              )}
            </div>
          )}
          {resume.inferred_role && (
            <p className="text-muted-foreground mt-2 text-xs">Role: {resume.inferred_role}</p>
          )}
        </CardContent>

        <CardFooter className="pt-0">
          <div className="text-muted-foreground flex w-full items-center justify-between text-xs">
            <span>{formatDate(resume.created_at)}</span>
            <span>{formatFileSize(resume.file_size)}</span>
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}
