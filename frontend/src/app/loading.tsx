import { Sparkles } from "lucide-react";

export default function RootLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
      <div className="flex flex-col items-center gap-5 animate-fade-in">
        <div className="relative">
          <div className="h-12 w-12 animate-spin rounded-full border-[3px] border-zinc-200 border-t-blue-600 dark:border-zinc-800 dark:border-t-blue-400" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Loading...</p>
      </div>
    </div>
  );
}
