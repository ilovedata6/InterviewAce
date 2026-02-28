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
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 animate-fade-in">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-red-50 shadow-sm dark:bg-red-950/30">
        <AlertTriangle className="h-9 w-9 text-red-600 dark:text-red-400" />
      </div>
      <div className="text-center">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">Something went wrong</h1>
        <p className="mt-2 max-w-md text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
          {error.message || "An unexpected error occurred."}
        </p>
      </div>
      <Button onClick={reset} className="rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 px-6 shadow-md hover:brightness-110">Try again</Button>
    </div>
  );
}
