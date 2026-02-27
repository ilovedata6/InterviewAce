/* ──────────────────────────────────────────────────────────
 * Resume Upload Page
 * ────────────────────────────────────────────────────────── */

"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeUploadZone, UploadStatus } from "@/components/resume/resume-upload-zone";
import { useUploadResume } from "@/hooks/use-resumes";
import { ROUTES } from "@/lib/constants";
import { toast } from "sonner";
import { ApiClientError } from "@/lib/api-client";

export default function ResumeUploadPage() {
  const router = useRouter();
  const uploadMutation = useUploadResume();
  const [uploadState, setUploadState] = useState<"idle" | "uploading" | "success" | "error">(
    "idle",
  );
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [uploadedId, setUploadedId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const handleFileSelected = useCallback(
    async (file: File) => {
      setUploadState("uploading");
      setUploadedFileName(file.name);
      setErrorMessage("");

      try {
        const result = await uploadMutation.mutateAsync(file);
        setUploadState("success");
        setUploadedId(result.id);
        toast.success("Resume uploaded successfully! Analysis in progress.");
      } catch (err) {
        setUploadState("error");
        const message =
          err instanceof ApiClientError ? err.message : "Upload failed. Please try again.";
        setErrorMessage(message);
        toast.error(message);
      }
    },
    [uploadMutation],
  );

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href={ROUTES.RESUMES}>
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back to resumes</span>
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Upload Resume</h1>
          <p className="text-muted-foreground">
            Upload a PDF or DOCX file. We&apos;ll analyze it with AI.
          </p>
        </div>
      </div>

      {/* Upload card */}
      <Card>
        <CardHeader>
          <CardTitle>Choose a File</CardTitle>
          <CardDescription>Supported formats: PDF, DOCX. Maximum file size: 10 MB.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {uploadState === "idle" || uploadState === "error" ? (
            <>
              <ResumeUploadZone onFileSelected={handleFileSelected} isUploading={false} />
              {uploadState === "error" && (
                <UploadStatus status="error" fileName={uploadedFileName} message={errorMessage} />
              )}
            </>
          ) : uploadState === "uploading" ? (
            <ResumeUploadZone onFileSelected={handleFileSelected} isUploading />
          ) : (
            /* success */
            <div className="space-y-4">
              <UploadStatus
                status="success"
                fileName={uploadedFileName}
                message="Your resume has been uploaded and is being analyzed. You can view the results shortly."
              />
              <div className="flex flex-col gap-2 sm:flex-row">
                {uploadedId && (
                  <Button className="flex-1" onClick={() => router.push(`/resumes/${uploadedId}`)}>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    View Resume
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setUploadState("idle");
                    setUploadedFileName("");
                    setUploadedId(null);
                  }}
                >
                  Upload Another
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
