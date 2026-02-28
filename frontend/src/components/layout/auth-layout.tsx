import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/lib/constants";
import { Sparkles, BrainCircuit, FileText, LineChart } from "lucide-react";

interface AuthLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* ── Left decorative panel (hidden on mobile) ── */}
      <div className="bg-gradient-brand relative hidden w-1/2 overflow-hidden lg:flex lg:flex-col lg:justify-between">
        {/* Decorative shapes */}
        <div className="pointer-events-none absolute inset-0">
          <div className="animate-float absolute -top-20 -right-20 h-72 w-72 rounded-full bg-white/10" />
          <div className="animate-float absolute -bottom-16 -left-16 h-56 w-56 rounded-full bg-white/5 delay-700" />
          <div className="animate-pulse-soft absolute top-1/3 right-1/4 h-40 w-40 rounded-full bg-white/5" />
        </div>

        <div className="relative z-10 flex flex-1 flex-col justify-center p-12 xl:p-16">
          {/* Brand */}
          <Link href={ROUTES.HOME} className="mb-12 flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">InterviewAce</span>
          </Link>

          {/* Value proposition */}
          <h2 className="mb-4 text-3xl font-bold leading-tight text-white xl:text-4xl">
            Practice smarter.
            <br />
            Interview better.
          </h2>
          <p className="mb-10 max-w-sm text-sm leading-relaxed text-blue-100/80">
            AI-powered mock interviews tailored to your resume, with instant feedback and
            progress tracking.
          </p>

          {/* Feature list */}
          <div className="space-y-4">
            {[
              { icon: BrainCircuit, text: "AI-generated questions from your resume" },
              { icon: FileText, text: "Instant per-answer scoring & feedback" },
              { icon: LineChart, text: "Track improvement over time" },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/15 backdrop-blur">
                  <Icon className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium text-white/90">{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom quote */}
        <div className="relative z-10 border-t border-white/10 p-12 xl:p-16">
          <blockquote className="text-sm italic text-blue-100/70">
            &ldquo;The best preparation for tomorrow is doing your best today.&rdquo;
          </blockquote>
          <p className="mt-2 text-xs font-medium text-blue-200/50">— H. Jackson Brown Jr.</p>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex flex-1 flex-col items-center justify-center px-4 py-12 sm:px-8">
        <div className="w-full max-w-md space-y-6 animate-fade-in">
          {/* Mobile logo (hidden on lg+) */}
          <div className="text-center lg:hidden">
            <Link href={ROUTES.HOME} className="inline-flex items-center gap-2">
              <div className="bg-gradient-brand flex h-8 w-8 items-center justify-center rounded-lg">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                Interview<span className="text-gradient">Ace</span>
              </span>
            </Link>
          </div>

          {/* Auth card */}
          <Card className="border-zinc-200/80 shadow-lg dark:border-zinc-800/80">
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{title}</CardTitle>
              {description && <CardDescription>{description}</CardDescription>}
            </CardHeader>
            <CardContent>{children}</CardContent>
          </Card>

          {/* Footer */}
          {footer && (
            <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">{footer}</p>
          )}
        </div>
      </div>
    </div>
  );
}
