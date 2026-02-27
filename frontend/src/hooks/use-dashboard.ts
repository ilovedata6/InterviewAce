/* ──────────────────────────────────────────────────────────
 * React Query hook for dashboard data
 * ────────────────────────────────────────────────────────── */

"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import type { DashboardStats } from "@/types/dashboard";

/** Fetch dashboard stats with 2-minute stale time */
export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard", "stats"],
    queryFn: () => apiClient.get<DashboardStats>(API_ROUTES.DASHBOARD.STATS),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });
}
