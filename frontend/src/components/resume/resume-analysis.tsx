/* ──────────────────────────────────────────────────────────
 * Resume Analysis Display
 * Structured view: summary, skills, experience, education,
 * recommendations
 * ────────────────────────────────────────────────────────── */

"use client";

import { Award, BookOpen, Briefcase, GraduationCap, Lightbulb, Loader2, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import type { ResumeAnalysisResponse } from "@/types/resume";

interface ResumeAnalysisProps {
  analysis: ResumeAnalysisResponse | undefined;
  isLoading: boolean;
}

/** Parse typed analysis from the raw dict */
function parseAnalysis(raw: Record<string, unknown> | null | undefined) {
  if (!raw) return null;
  return {
    summary: (raw.summary as string) || "",
    skills: (raw.skills as string[]) || [],
    experience: (raw.experience as Array<Record<string, unknown>>) || [],
    education: (raw.education as Array<Record<string, unknown>>) || [],
    recommendations: (raw.recommendations as string[]) || [],
    job_titles: (raw.job_titles as string[]) || [],
    years_of_experience: (raw.years_of_experience as number) || 0,
    confidence_score: (raw.confidence_score as number) || 0,
  };
}

export function ResumeAnalysis({ analysis, isLoading }: ResumeAnalysisProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-5 w-32" />
            </CardHeader>
            <CardContent className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!analysis || analysis.status === "pending" || analysis.status === "processing") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center py-12 text-center">
          <Loader2 className="text-primary mb-3 h-10 w-10 animate-spin" />
          <p className="text-sm font-medium">Analysis in progress...</p>
          <p className="text-muted-foreground text-xs">
            This typically takes 30–60 seconds. The page will update automatically.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (analysis.status === "error") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center py-12 text-center">
          <p className="text-destructive text-sm font-medium">Analysis failed</p>
          <p className="text-muted-foreground text-xs">
            There was an error processing your resume. Try re-uploading or re-analyzing.
          </p>
        </CardContent>
      </Card>
    );
  }

  const parsed = parseAnalysis(analysis.analysis);
  if (!parsed) return null;

  return (
    <div className="space-y-4">
      {/* Confidence + Processing Time */}
      <div className="flex flex-wrap items-center gap-4">
        {analysis.confidence_score !== null && (
          <div className="flex items-center gap-2">
            <Star className="h-4 w-4 text-amber-500" />
            <span className="text-sm font-medium">
              Confidence: {Math.round(analysis.confidence_score * 100)}%
            </span>
            <Progress value={analysis.confidence_score * 100} className="h-2 w-20" />
          </div>
        )}
        {analysis.processing_time !== null && (
          <span className="text-muted-foreground text-xs">
            Processed in {analysis.processing_time.toFixed(1)}s
          </span>
        )}
      </div>

      {/* Summary */}
      {parsed.summary && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <BookOpen className="h-4 w-4" />
              Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm leading-relaxed">{parsed.summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Skills */}
      {parsed.skills.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Award className="h-4 w-4" />
              Skills
            </CardTitle>
            <CardDescription>{parsed.skills.length} skills identified</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {parsed.skills.map((skill) => (
                <Badge key={skill} variant="secondary">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Job Titles + Experience */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Job Titles */}
        {parsed.job_titles.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Briefcase className="h-4 w-4" />
                Suggested Roles
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {parsed.job_titles.map((title) => (
                  <li key={title} className="text-muted-foreground text-sm">
                    • {title}
                  </li>
                ))}
              </ul>
              {parsed.years_of_experience > 0 && (
                <>
                  <Separator className="my-3" />
                  <p className="text-sm">
                    <span className="font-medium">{parsed.years_of_experience}</span> years of
                    experience
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        )}

        {/* Recommendations */}
        {parsed.recommendations.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Lightbulb className="h-4 w-4" />
                Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {parsed.recommendations.map((rec, i) => (
                  <li key={i} className="text-muted-foreground text-sm">
                    {i + 1}. {rec}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Experience */}
      {parsed.experience.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Briefcase className="h-4 w-4" />
              Experience
            </CardTitle>
            <CardDescription>{parsed.experience.length} positions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {parsed.experience.map((exp, i) => (
              <div key={i}>
                {i > 0 && <Separator className="mb-4" />}
                <div className="space-y-1">
                  <p className="text-sm font-semibold">{exp.position as string}</p>
                  <p className="text-muted-foreground text-sm">{exp.company as string}</p>
                  <p className="text-muted-foreground text-xs">
                    {exp.start_date as string}
                    {exp.end_date ? ` — ${exp.end_date as string}` : " — Present"}
                    {exp.location ? ` • ${exp.location as string}` : ""}
                  </p>
                  {exp.description ? (
                    <p className="text-muted-foreground mt-1 text-sm">{String(exp.description)}</p>
                  ) : null}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Education */}
      {parsed.education.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <GraduationCap className="h-4 w-4" />
              Education
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {parsed.education.map((edu, i) => (
              <div key={i}>
                {i > 0 && <Separator className="mb-4" />}
                <div className="space-y-1">
                  <p className="text-sm font-semibold">
                    {edu.degree as string}
                    {edu.field_of_study ? ` in ${edu.field_of_study as string}` : ""}
                  </p>
                  <p className="text-muted-foreground text-sm">{edu.institution as string}</p>
                  <p className="text-muted-foreground text-xs">
                    {edu.start_date as string}
                    {edu.end_date ? ` — ${edu.end_date as string}` : " — Present"}
                    {edu.gpa ? ` • GPA: ${edu.gpa}` : ""}
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
