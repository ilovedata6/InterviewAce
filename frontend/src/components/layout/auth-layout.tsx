import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/lib/constants";

interface AuthLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-4 dark:bg-zinc-900">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <Link href={ROUTES.HOME}>
            <span className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
              Interview<span className="text-blue-600">Ace</span>
            </span>
          </Link>
        </div>

        {/* Auth card */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </CardHeader>
          <CardContent>{children}</CardContent>
        </Card>

        {/* Footer (e.g., "Already have an account? Sign in") */}
        {footer && <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">{footer}</p>}
      </div>
    </div>
  );
}
