/* ──────────────────────────────────────────────────────────
 * Admin User Table
 * Paginated table with name, email, role, status, actions
 * ────────────────────────────────────────────────────────── */

"use client";

import type { User } from "@/types/auth";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Shield, ShieldOff, Loader2 } from "lucide-react";

interface AdminUserTableProps {
  users: User[];
  onToggleActive: (userId: string, action: "activate" | "deactivate") => void;
  togglingId: string | null;
}

export function AdminUserTable({ users, onToggleActive, togglingId }: AdminUserTableProps) {
  if (users.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 py-12 text-center">
        <p className="text-muted-foreground">No users found.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Joined</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell className="font-medium">{user.full_name}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>
                <Badge variant="outline" className="capitalize">
                  {user.role ?? "user"}
                </Badge>
              </TableCell>
              <TableCell>
                {user.is_active ? (
                  <Badge variant="default">Active</Badge>
                ) : (
                  <Badge variant="destructive">Inactive</Badge>
                )}
              </TableCell>
              <TableCell>
                {new Date(user.created_at).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </TableCell>
              <TableCell className="text-right">
                {user.is_active ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onToggleActive(user.id, "deactivate")}
                    disabled={togglingId === user.id}
                  >
                    {togglingId === user.id ? (
                      <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <ShieldOff className="mr-1.5 h-3.5 w-3.5" />
                    )}
                    Deactivate
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onToggleActive(user.id, "activate")}
                    disabled={togglingId === user.id}
                  >
                    {togglingId === user.id ? (
                      <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Shield className="mr-1.5 h-3.5 w-3.5" />
                    )}
                    Activate
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
