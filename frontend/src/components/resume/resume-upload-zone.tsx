/* ──────────────────────────────────────────────────────────
 * Resume Upload Zone — drag-and-drop file upload
 * Validates file type and size client-side
 * ────────────────────────────────────────────────────────── */

"use client";

import { useCallback, useState } from "react";
import { FileUp, X, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

const ALLOWED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

const ALLOWED_EXTENSIONS = [".pdf", ".docx"];
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  isUploading: boolean;
  uploadProgress?: number;
}

export function ResumeUploadZone({ onFileSelected, isUploading, uploadProgress }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const validateFile = useCallback((file: File): boolean => {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_TYPES.includes(file.type) && !ALLOWED_EXTENSIONS.includes(ext)) {
      toast.error("Invalid file type. Only PDF and DOCX files are accepted.");
      return false;
    }
    if (file.size > MAX_SIZE) {
      toast.error("File too large. Maximum size is 10 MB.");
      return false;
    }
    return true;
  }, []);

  const handleFile = useCallback(
    (file: File) => {
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelected(file);
      }
    },
    [validateFile, onFileSelected],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const clearFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
          dragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
        } ${isUploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleInputChange}
          className="absolute inset-0 cursor-pointer opacity-0"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-3 text-center">
            <Loader2 className="text-primary h-10 w-10 animate-spin" />
            <div>
              <p className="text-sm font-medium">Uploading...</p>
              <p className="text-muted-foreground text-xs">
                Please wait while we process your file.
              </p>
            </div>
            {uploadProgress !== undefined && (
              <Progress value={uploadProgress} className="h-2 w-48" />
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="bg-primary/10 rounded-full p-4">
              <FileUp className="text-primary h-8 w-8" />
            </div>
            <div>
              <p className="text-sm font-medium">
                {dragActive ? "Drop your file here" : "Drag & drop your resume"}
              </p>
              <p className="text-muted-foreground mt-1 text-xs">
                or click to browse — PDF or DOCX, up to 10 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Selected file preview */}
      {selectedFile && !isUploading && (
        <div className="flex items-center gap-3 rounded-lg border p-3">
          <div className="bg-muted rounded-md p-2">
            <FileText className="text-muted-foreground h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{selectedFile.name}</p>
            <p className="text-muted-foreground text-xs">{formatFileSize(selectedFile.size)}</p>
          </div>
          <Button variant="ghost" size="icon" onClick={clearFile}>
            <X className="h-4 w-4" />
            <span className="sr-only">Remove file</span>
          </Button>
        </div>
      )}
    </div>
  );
}

/** Upload status display — shown after upload initiated */
interface UploadStatusProps {
  status: "uploading" | "success" | "error";
  fileName?: string;
  message?: string;
}

export function UploadStatus({ status, fileName, message }: UploadStatusProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border p-4">
      {status === "uploading" && (
        <>
          <Loader2 className="text-primary h-5 w-5 animate-spin" />
          <div>
            <p className="text-sm font-medium">Uploading {fileName}...</p>
            <p className="text-muted-foreground text-xs">This may take a moment.</p>
          </div>
        </>
      )}
      {status === "success" && (
        <>
          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          <div>
            <p className="text-sm font-medium">Upload successful!</p>
            <p className="text-muted-foreground text-xs">
              {message || "Your resume is being analyzed."}
            </p>
          </div>
        </>
      )}
      {status === "error" && (
        <>
          <AlertCircle className="text-destructive h-5 w-5" />
          <div>
            <p className="text-sm font-medium">Upload failed</p>
            <p className="text-muted-foreground text-xs">
              {message || "Something went wrong. Please try again."}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
