/* ──────────────────────────────────────────────────────────
 * Profile Page
 * View user info, change password, resend verification
 * ────────────────────────────────────────────────────────── */

"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@/lib/zod-resolver";
import { toast } from "sonner";
import { useAuth } from "@/hooks/use-auth";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import { changePasswordSchema, type ChangePasswordFormValues } from "@/lib/validations/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { User as UserIcon, Mail, Shield, Calendar, Lock, Loader2, Send } from "lucide-react";

export default function ProfilePage() {
  const { user, isLoading } = useAuth();
  const [changingPassword, setChangingPassword] = useState(false);
  const [resending, setResending] = useState(false);

  const form = useForm<ChangePasswordFormValues>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      old_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  const handleChangePassword = async (values: ChangePasswordFormValues) => {
    setChangingPassword(true);
    try {
      await apiClient.post(API_ROUTES.AUTH.CHANGE_PASSWORD, {
        old_password: values.old_password,
        new_password: values.new_password,
      });
      toast.success("Password changed successfully");
      form.reset();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to change password";
      toast.error(message);
    } finally {
      setChangingPassword(false);
    }
  };

  const handleResendVerification = async () => {
    if (!user?.email) return;
    setResending(true);
    try {
      await apiClient.post("/api/auth/resend-verification", {
        email: user.email,
      });
      toast.success("Verification email sent! Check your inbox.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to send verification email";
      toast.error(message);
    } finally {
      setResending(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container max-w-3xl space-y-6 py-8">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="container max-w-3xl space-y-6 py-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          View your account information and manage your settings.
        </p>
      </div>

      {/* User Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserIcon className="h-5 w-5" />
            Account Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <p className="text-muted-foreground flex items-center gap-1.5 text-sm">
                <UserIcon className="h-3.5 w-3.5" />
                Full Name
              </p>
              <p className="font-medium">{user?.full_name ?? "—"}</p>
            </div>

            <div className="space-y-1">
              <p className="text-muted-foreground flex items-center gap-1.5 text-sm">
                <Mail className="h-3.5 w-3.5" />
                Email
              </p>
              <p className="font-medium">{user?.email ?? "—"}</p>
            </div>

            <div className="space-y-1">
              <p className="text-muted-foreground flex items-center gap-1.5 text-sm">
                <Shield className="h-3.5 w-3.5" />
                Role
              </p>
              <Badge variant="secondary" className="capitalize">
                {user?.role ?? "user"}
              </Badge>
            </div>

            <div className="space-y-1">
              <p className="text-muted-foreground flex items-center gap-1.5 text-sm">
                <Calendar className="h-3.5 w-3.5" />
                Member Since
              </p>
              <p className="font-medium">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString(undefined, {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })
                  : "—"}
              </p>
            </div>
          </div>

          {/* Resend verification button */}
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email Verification</p>
              <p className="text-muted-foreground text-xs">
                If you haven&apos;t verified your email, request a new verification link.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleResendVerification}
              disabled={resending}
            >
              {resending ? (
                <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
              ) : (
                <Send className="mr-2 h-3.5 w-3.5" />
              )}
              Resend Verification
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Change Password Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Change Password
          </CardTitle>
          <CardDescription>
            Update your password. You&apos;ll need to enter your current password for verification.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleChangePassword)} className="space-y-4">
              <FormField
                control={form.control}
                name="old_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Current Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Enter current password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="new_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Enter new password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="confirm_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirm New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Confirm new password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" disabled={changingPassword}>
                {changingPassword ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Changing…
                  </>
                ) : (
                  "Change Password"
                )}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
