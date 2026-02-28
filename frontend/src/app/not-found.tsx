import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/lib/constants";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 animate-fade-in">
      <div className="text-center">
        <h1 className="text-gradient text-8xl font-extrabold tracking-tight sm:text-9xl">404</h1>
        <p className="mt-4 text-lg text-zinc-500 dark:text-zinc-400">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
      </div>
      <Button asChild className="bg-gradient-brand rounded-xl px-6 shadow-md hover:brightness-110">
        <Link href={ROUTES.HOME}>Back to home</Link>
      </Button>
    </div>
  );
}
