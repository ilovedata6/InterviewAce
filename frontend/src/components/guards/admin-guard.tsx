"use client";

/* ──────────────────────────────────────────────────────────
 * AdminGuard — Client-side role check
 *
 * Wraps admin pages with a role check. The middleware already
 * redirects non-admin users based on the `user_role` cookie,
 * but this guard provides a second layer of defence after
 * the zustand store has hydrated.
 *
 * Usage:
 *   <AdminGuard>
 *     <AdminContent />
 *   </AdminGuard>
 * ────────────────────────────────────────────────────────── */

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Skeleton } from "@/components/ui/skeleton";

interface AdminGuardProps {
  children: ReactNode;
  /** Where to redirect non-admin users (default: /dashboard) */
  fallbackUrl?: string;
}

export function AdminGuard({ children, fallbackUrl = "/dashboard" }: AdminGuardProps) {
  const router = useRouter();
  const { isAdmin, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isAdmin)) {
      router.replace(fallbackUrl);
    }
  }, [isLoading, isAuthenticated, isAdmin, router, fallbackUrl]);

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  // Not admin — show nothing while redirect happens
  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  return <>{children}</>;
}
