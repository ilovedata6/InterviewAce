export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-zinc-950">
      <main className="flex flex-col items-center gap-8 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
          Interview<span className="text-blue-600">Ace</span>
        </h1>
        <p className="max-w-md text-lg text-zinc-600 dark:text-zinc-400">
          AI-Powered Interview Preparation. Practice with intelligent questions,
          get instant feedback, and land your dream job.
        </p>
        <div className="flex gap-4">
          <a
            href="/login"
            className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Get Started
          </a>
          <a
            href="/login"
            className="rounded-lg border border-zinc-300 px-6 py-3 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            Sign In
          </a>
        </div>
      </main>
    </div>
  );
}
