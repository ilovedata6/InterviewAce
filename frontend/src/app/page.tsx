import Link from "next/link";
import { BrainCircuit, FileText, LineChart, ArrowRight, CheckCircle2 } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 font-sans dark:bg-zinc-950">
      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link
            href="/"
            className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50"
          >
            Interview<span className="text-blue-600">Ace</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="flex flex-1 flex-col items-center justify-center px-4 py-20 text-center sm:py-32">
        <div className="mx-auto max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300">
            <BrainCircuit className="h-4 w-4" />
            AI-Powered Interview Preparation
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-zinc-900 sm:text-6xl dark:text-zinc-50">
            Ace Your Next Interview <span className="text-blue-600">with Confidence</span>
          </h1>
          <p className="mx-auto max-w-xl text-lg text-zinc-600 dark:text-zinc-400">
            Practice with AI-generated questions tailored to your resume, receive instant feedback
            on your answers, and track your improvement over time.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="group inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-600/30"
            >
              Start Practicing Free
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-lg border border-zinc-300 px-8 py-3.5 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              I Have an Account
            </Link>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 pt-4 text-sm text-zinc-500 dark:text-zinc-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Free to start
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              No credit card required
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              AI-powered feedback
            </span>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="border-t border-zinc-200 bg-white px-4 py-20 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto max-w-6xl">
          <div className="mb-14 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
              Everything You Need to Prepare
            </h2>
            <p className="mt-3 text-zinc-600 dark:text-zinc-400">
              Three powerful tools working together to help you land your dream job.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {/* Feature 1 */}
            <div className="group rounded-xl border border-zinc-200 bg-zinc-50 p-8 transition-shadow hover:shadow-lg dark:border-zinc-700 dark:bg-zinc-800/50">
              <div className="mb-4 inline-flex rounded-lg bg-blue-100 p-3 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                AI Mock Interviews
              </h3>
              <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                Get personalized interview questions based on your resume and target role. Practice
                behavioral, technical, and situational questions with real-time AI feedback.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group rounded-xl border border-zinc-200 bg-zinc-50 p-8 transition-shadow hover:shadow-lg dark:border-zinc-700 dark:bg-zinc-800/50">
              <div className="mb-4 inline-flex rounded-lg bg-emerald-100 p-3 text-emerald-600 dark:bg-emerald-900/50 dark:text-emerald-400">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                Resume Analysis
              </h3>
              <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                Upload your resume and get AI-powered analysis. Identify strengths, weaknesses, and
                get suggestions to optimize your resume for ATS systems and recruiters.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group rounded-xl border border-zinc-200 bg-zinc-50 p-8 transition-shadow hover:shadow-lg dark:border-zinc-700 dark:bg-zinc-800/50">
              <div className="mb-4 inline-flex rounded-lg bg-violet-100 p-3 text-violet-600 dark:bg-violet-900/50 dark:text-violet-400">
                <LineChart className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                Progress Tracking
              </h3>
              <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                Track your interview scores over time, identify patterns, and focus on areas that
                need improvement. Visual charts show your growth at a glance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Ready to Ace Your Interview?
          </h2>
          <p className="mt-3 text-zinc-600 dark:text-zinc-400">
            Join thousands of users who have improved their interview skills with InterviewAce.
            Start your free practice session today.
          </p>
          <Link
            href="/register"
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:bg-blue-700 hover:shadow-xl"
          >
            Create Free Account
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-zinc-200 bg-white px-4 py-8 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
            Interview<span className="text-blue-600">Ace</span>
          </div>
          <div className="flex gap-6 text-sm text-zinc-500 dark:text-zinc-400">
            <Link
              href="/login"
              className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50"
            >
              Register
            </Link>
          </div>
          <p className="text-sm text-zinc-400 dark:text-zinc-500">
            &copy; {new Date().getFullYear()} InterviewAce. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
