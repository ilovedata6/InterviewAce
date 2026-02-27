"use client";

/* ──────────────────────────────────────────────────────────
 * QueryProvider — React Query configuration
 *
 * Wraps the app with QueryClientProvider so that any
 * component can use React Query hooks (useQuery, etc.).
 * ────────────────────────────────────────────────────────── */

import { useState, type ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}

export function QueryProvider({ children }: { children: ReactNode }) {
  // Create a stable QueryClient per component mount (avoids
  // sharing state between SSR requests).
  const [queryClient] = useState(() => makeQueryClient());

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
