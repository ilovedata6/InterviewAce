/* ──────────────────────────────────────────────────────────
 * Resume Version History
 * Timeline showing version history with changes
 * ────────────────────────────────────────────────────────── */

"use client";

import { GitBranch, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface ResumeVersion {
  version: number;
  created_at: string;
  changes: string[];
  parent_version_id: string | null;
}

interface ResumeVersionsProps {
  versions:
    | {
        versions: ResumeVersion[];
        current_version: number;
      }
    | undefined;
  isLoading: boolean;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ResumeVersions({ versions, isLoading }: ResumeVersionsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-6 w-6 rounded-full" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-48" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (!versions || versions.versions.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center py-8 text-center">
          <GitBranch className="text-muted-foreground/50 mb-3 h-8 w-8" />
          <p className="text-muted-foreground text-sm">No version history available.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <GitBranch className="h-4 w-4" />
          Version History
        </CardTitle>
        <CardDescription>
          Current version: {versions.current_version} • {versions.versions.length} version
          {versions.versions.length !== 1 ? "s" : ""}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-0">
          {/* Vertical line */}
          <div className="bg-border absolute top-0 bottom-0 left-3 w-px" />

          {versions.versions.map((version, i) => (
            <div key={version.version} className="relative flex gap-4 pb-6 last:pb-0">
              {/* Dot */}
              <div
                className={`relative z-10 mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-xs font-bold ${
                  i === 0
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border bg-background text-muted-foreground"
                }`}
              >
                {version.version}
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Version {version.version}</span>
                  {i === 0 && (
                    <Badge variant="default" className="text-xs">
                      Current
                    </Badge>
                  )}
                </div>
                <div className="text-muted-foreground mt-0.5 flex items-center gap-1 text-xs">
                  <Clock className="h-3 w-3" />
                  {formatDate(version.created_at)}
                </div>
                {version.changes.length > 0 && (
                  <ul className="mt-2 space-y-0.5">
                    {version.changes.map((change, j) => (
                      <li key={j} className="text-muted-foreground text-sm">
                        • {change}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
