/* ──────────────────────────────────────────────────────────
 * Interview Start Page
 * Configure → Start → Redirect to live interview session
 * ────────────────────────────────────────────────────────── */

"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { InterviewConfig } from "@/components/interview/interview-config";
import { useStartInterview } from "@/hooks/use-interview";
import type { InterviewConfigFormValues } from "@/lib/validations/interview";

export default function InterviewStartPage() {
  const router = useRouter();
  const startInterview = useStartInterview();

  const handleStart = (values: InterviewConfigFormValues) => {
    startInterview.mutate(
      {
        resume_id: values.resume_id ?? undefined,
        question_count: values.question_count,
        difficulty: values.difficulty,
        focus_areas: values.focus_areas ?? undefined,
      },
      {
        onSuccess: (session) => {
          toast.success("Interview started!");
          router.push(`/interviews/${session.id}`);
        },
        onError: (error) => {
          toast.error(error.message || "Failed to start interview");
        },
      },
    );
  };

  return (
    <div className="container max-w-4xl py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight">New Interview</h1>
        <p className="text-muted-foreground mt-2">
          Configure your mock interview and get AI-powered feedback on your responses.
        </p>
      </div>
      <InterviewConfig onSubmit={handleStart} isLoading={startInterview.isPending} />
    </div>
  );
}
