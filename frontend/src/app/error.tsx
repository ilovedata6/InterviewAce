"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function RootError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
        <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
      </div>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">Something went wrong</h1>
        <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
          {error.message || "An unexpected error occurred."}
        </p>
      </div>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
