import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/lib/constants";

export default function NotFound() {
  return (
    <div className="animate-fade-in flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="text-center">
        <h1 className="bg-gradient-to-r from-blue-600 via-violet-600 to-blue-500 bg-clip-text text-8xl font-extrabold tracking-tight text-transparent sm:text-9xl">
          404
        </h1>
        <p className="mt-4 text-lg text-zinc-500 dark:text-zinc-400">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
      </div>
      <Button
        asChild
        className="rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 px-6 shadow-md hover:brightness-110"
      >
        <Link href={ROUTES.HOME}>Back to home</Link>
      </Button>
    </div>
  );
}
