/* ──────────────────────────────────────────────────────────
 * Admin Layout
 * Wraps all /admin/* routes with AdminGuard
 * ────────────────────────────────────────────────────────── */

"use client";

import type { ReactNode } from "react";
import { AdminGuard } from "@/components/guards/admin-guard";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <AdminGuard>{children}</AdminGuard>;
}
