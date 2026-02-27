/* ──────────────────────────────────────────────────────────
 * Admin Users Page
 * List, activate/deactivate users
 * ────────────────────────────────────────────────────────── */

"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import type { User } from "@/types/auth";
import type { PaginatedResponse } from "@/types/common";
import { AdminUserTable } from "@/components/admin/user-table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

const PAGE_SIZE = 20;

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(0);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const { data, isLoading } = useQuery<PaginatedResponse<User>>({
    queryKey: ["admin", "users", page],
    queryFn: () =>
      apiClient.get<PaginatedResponse<User>>(API_ROUTES.ADMIN.USERS, {
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      }),
  });

  const users = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleToggleActive = async (userId: string, action: "activate" | "deactivate") => {
    setTogglingId(userId);
    try {
      await apiClient.put(`${API_ROUTES.ADMIN.USERS}/${userId}?action=${action}`);
      toast.success(`User ${action}d successfully`);
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    } catch (error) {
      const message = error instanceof Error ? error.message : `Failed to ${action} user`;
      toast.error(message);
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <div className="container max-w-5xl space-y-6 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">User Management</h1>
        <p className="text-muted-foreground mt-1 text-sm">View and manage all registered users.</p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <AdminUserTable users={users} onToggleActive={handleToggleActive} togglingId={togglingId} />
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground text-sm">
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm font-medium">
              {page + 1} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page + 1 >= totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
