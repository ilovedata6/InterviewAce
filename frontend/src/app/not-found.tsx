import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/lib/constants";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="text-center">
        <h1 className="text-7xl font-extrabold text-zinc-900 dark:text-zinc-50">404</h1>
        <p className="mt-4 text-lg text-zinc-500 dark:text-zinc-400">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
      </div>
      <Button asChild>
        <Link href={ROUTES.HOME}>Back to home</Link>
      </Button>
    </div>
  );
}
