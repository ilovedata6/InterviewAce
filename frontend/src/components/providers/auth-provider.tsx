"use client";

/* ──────────────────────────────────────────────────────────
 * AuthProvider — Hydrate auth state on app mount
 *
 * Calls fetchUser() once on mount to populate the zustand
 * auth store from the BFF /api/auth/me endpoint. All child
 * components can then use useAuth() to read auth state
 * synchronously.
 * ────────────────────────────────────────────────────────── */

import { useEffect, type ReactNode } from "react";
import { useAuthStore } from "@/stores/auth-store";

export function AuthProvider({ children }: { children: ReactNode }) {
  const fetchUser = useAuthStore((s) => s.fetchUser);

  useEffect(() => {
    fetchUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <>{children}</>;
}
