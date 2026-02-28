import Link from "next/link";
import {
  BrainCircuit,
  FileText,
  LineChart,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Target,
  Zap,
  BarChart3,
  Shield,
  Clock,
  Users,
} from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 font-sans dark:bg-zinc-950">
      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 border-b border-zinc-200/50 bg-white/80 backdrop-blur-xl dark:border-zinc-800/50 dark:bg-zinc-950/80">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
              Interview<span className="bg-gradient-to-r from-blue-600 via-violet-600 to-blue-500 bg-clip-text text-transparent">Ace</span>
            </span>
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
              className="rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 px-4 py-2 text-sm font-medium text-white shadow-md transition-all hover:shadow-lg hover:brightness-110"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative flex flex-1 flex-col items-center justify-center overflow-hidden px-4 py-24 text-center sm:py-36">
        {/* Background decorative blobs */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="animate-float absolute -top-32 -right-32 h-96 w-96 rounded-full bg-blue-500/5 blur-3xl dark:bg-blue-500/10" />
          <div className="animate-float absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-violet-500/5 blur-3xl delay-1000 dark:bg-violet-500/10" />
          <div className="animate-pulse-soft absolute top-1/2 left-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-500/3 blur-3xl dark:bg-indigo-500/5" />
        </div>

        <div className="relative mx-auto max-w-3xl space-y-8 animate-fade-in-up">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200/80 bg-blue-50/80 px-4 py-1.5 text-sm font-medium text-blue-700 shadow-sm backdrop-blur dark:border-blue-800/60 dark:bg-blue-950/50 dark:text-blue-300">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Interview Preparation
          </div>

          {/* Heading */}
          <h1 className="text-4xl font-extrabold tracking-tight text-zinc-900 sm:text-6xl lg:text-7xl dark:text-zinc-50">
            Ace Your Next{" "}
            <span className="bg-gradient-to-r from-blue-600 via-violet-600 to-blue-500 bg-clip-text text-transparent">
              Interview
            </span>
            <br />
            with Confidence
          </h1>

          {/* Subheading */}
          <p className="mx-auto max-w-2xl text-lg leading-relaxed text-zinc-600 sm:text-xl dark:text-zinc-400">
            Practice with AI-generated questions tailored to your resume. Receive instant feedback,
            track your improvement, and walk into every interview prepared.
          </p>

          {/* CTA */}
          <div className="flex flex-col items-center justify-center gap-4 pt-2 sm:flex-row">
            <Link
              href="/register"
              className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 px-8 py-4 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:shadow-xl hover:shadow-blue-600/30 hover:brightness-110"
            >
              Start Practicing Free
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl border border-zinc-200 bg-white/80 px-8 py-4 text-sm font-semibold text-zinc-700 shadow-sm backdrop-blur transition-all hover:border-zinc-300 hover:bg-white hover:shadow-md dark:border-zinc-700 dark:bg-zinc-900/80 dark:text-zinc-300 dark:hover:border-zinc-600 dark:hover:bg-zinc-900"
            >
              I Have an Account
            </Link>
          </div>

          {/* Trust badges */}
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-2 pt-6 text-sm text-zinc-500 dark:text-zinc-400">
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
              Real-time AI feedback
            </span>
          </div>
        </div>
      </section>

      {/* ── Stats bar ── */}
      <section className="border-y border-zinc-200/60 bg-white/50 backdrop-blur dark:border-zinc-800/60 dark:bg-zinc-900/50">
        <div className="mx-auto grid max-w-5xl grid-cols-2 divide-x divide-zinc-200/60 dark:divide-zinc-800/60 sm:grid-cols-4">
          {[
            { label: "AI Models", value: "2", icon: BrainCircuit },
            { label: "Question Types", value: "3", icon: Target },
            { label: "Instant Feedback", value: "100%", icon: Zap },
            { label: "Score Tracking", value: "Real-time", icon: BarChart3 },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="flex flex-col items-center gap-1 px-4 py-6 sm:py-8">
              <Icon className="mb-1 h-5 w-5 text-blue-600 dark:text-blue-400" />
              <span className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">{value}</span>
              <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">{label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="px-4 py-24 sm:py-32">
        <div className="mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <p className="mb-3 text-sm font-semibold tracking-wider text-blue-600 uppercase dark:text-blue-400">
              Features
            </p>
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
              Everything You Need to Prepare
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-zinc-600 dark:text-zinc-400">
              Three powerful tools working together to help you land your dream job.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Feature 1 */}
            <div className="group relative overflow-hidden rounded-2xl border border-zinc-200/80 bg-white p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-zinc-800/80 dark:bg-zinc-900/50">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100 dark:from-blue-950/30" />
              <div className="relative">
                <div className="mb-5 inline-flex rounded-xl bg-blue-100 p-3 text-blue-600 shadow-sm dark:bg-blue-900/50 dark:text-blue-400">
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
            </div>

            {/* Feature 2 */}
            <div className="group relative overflow-hidden rounded-2xl border border-zinc-200/80 bg-white p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-zinc-800/80 dark:bg-zinc-900/50">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100 dark:from-emerald-950/30" />
              <div className="relative">
                <div className="mb-5 inline-flex rounded-xl bg-emerald-100 p-3 text-emerald-600 shadow-sm dark:bg-emerald-900/50 dark:text-emerald-400">
                  <FileText className="h-6 w-6" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                  Resume Analysis
                </h3>
                <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                  Upload your resume and get AI-powered analysis. Identify strengths, extract key
                  skills, and get questions that match your actual experience.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="group relative overflow-hidden rounded-2xl border border-zinc-200/80 bg-white p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-zinc-800/80 dark:bg-zinc-900/50">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100 dark:from-violet-950/30" />
              <div className="relative">
                <div className="mb-5 inline-flex rounded-xl bg-violet-100 p-3 text-violet-600 shadow-sm dark:bg-violet-900/50 dark:text-violet-400">
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
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="border-t border-zinc-200/60 bg-white/50 px-4 py-24 backdrop-blur sm:py-32 dark:border-zinc-800/60 dark:bg-zinc-900/30">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <p className="mb-3 text-sm font-semibold tracking-wider text-blue-600 uppercase dark:text-blue-400">
              How It Works
            </p>
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
              Three Steps to Interview Success
            </h2>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                step: "01",
                icon: FileText,
                title: "Upload Your Resume",
                description:
                  "Upload your PDF or DOCX resume. Our AI extracts skills, experience, and role information to personalize your interview.",
                color: "text-blue-600 dark:text-blue-400",
                bg: "bg-blue-50 dark:bg-blue-950/40",
              },
              {
                step: "02",
                icon: BrainCircuit,
                title: "Practice with AI",
                description:
                  "Start a mock interview configured to your preferences. Answer AI-generated questions and get instant, detailed feedback.",
                color: "text-violet-600 dark:text-violet-400",
                bg: "bg-violet-50 dark:bg-violet-950/40",
              },
              {
                step: "03",
                icon: LineChart,
                title: "Track & Improve",
                description:
                  "Review your scores, read per-question feedback, and track improvement trends over time with interactive dashboards.",
                color: "text-emerald-600 dark:text-emerald-400",
                bg: "bg-emerald-50 dark:bg-emerald-950/40",
              },
            ].map(({ step, icon: Icon, title, description, color, bg }) => (
              <div key={step} className="text-center">
                <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
                  <Icon className={`h-7 w-7 ${color}`} />
                </div>
                <span className={`mb-2 inline-block rounded-full ${bg} px-3 py-0.5 text-xs font-bold ${color}`}>
                  {step}
                </span>
                <h3 className="mb-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                  {title}
                </h3>
                <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                  {description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Why Choose Us ── */}
      <section className="px-4 py-24 sm:py-32">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <p className="mb-3 text-sm font-semibold tracking-wider text-blue-600 uppercase dark:text-blue-400">
              Why InterviewAce
            </p>
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
              Built for Serious Preparation
            </h2>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: BrainCircuit,
                title: "Dual AI Engine",
                description: "OpenAI GPT-5.2 primary with Gemini 2.0 fallback. Always available, always smart.",
              },
              {
                icon: Target,
                title: "Personalized Questions",
                description: "Questions are generated from YOUR resume — skills, projects, and experience.",
              },
              {
                icon: Clock,
                title: "Instant Feedback",
                description: "Get scored on each answer immediately. No waiting, no guessing.",
              },
              {
                icon: BarChart3,
                title: "Visual Analytics",
                description: "Score trends, skill radar charts, and category breakdowns at a glance.",
              },
              {
                icon: Shield,
                title: "Secure & Private",
                description: "JWT auth, encrypted passwords, rate limiting, and role-based access control.",
              },
              {
                icon: Users,
                title: "Admin Dashboard",
                description: "Platform-wide stats, user management, and moderation tools built in.",
              },
            ].map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="flex items-start gap-4 rounded-xl border border-zinc-200/60 bg-white/80 p-5 backdrop-blur transition-colors hover:border-zinc-300 dark:border-zinc-800/60 dark:bg-zinc-900/50 dark:hover:border-zinc-700"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/40">
                  <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="mb-1 text-sm font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
                  <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="px-4 py-24 sm:py-32">
        <div className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-700 px-8 py-16 text-center shadow-2xl sm:px-16">
          {/* Decorative circles */}
          <div className="pointer-events-none absolute -top-20 -right-20 h-60 w-60 rounded-full bg-white/10" />
          <div className="pointer-events-none absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-white/5" />

          <div className="relative">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to Ace Your Interview?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-blue-100">
              Join users who have improved their interview skills with AI-powered practice.
              Start your free session today — no credit card required.
            </p>
            <Link
              href="/register"
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-sm font-semibold text-blue-700 shadow-lg transition-all hover:bg-blue-50 hover:shadow-xl"
            >
              Create Free Account
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-zinc-200/60 bg-white/50 px-4 py-10 backdrop-blur dark:border-zinc-800/60 dark:bg-zinc-900/30">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-6 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700">
              <Sparkles className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
              Interview<span className="bg-gradient-to-r from-blue-600 via-violet-600 to-blue-500 bg-clip-text text-transparent">Ace</span>
            </span>
          </div>
          <div className="flex gap-8 text-sm text-zinc-500 dark:text-zinc-400">
            <Link href="/login" className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50">
              Sign In
            </Link>
            <Link href="/register" className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50">
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
