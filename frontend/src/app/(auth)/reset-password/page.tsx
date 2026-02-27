"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@/lib/zod-resolver";
import Link from "next/link";
import { Loader2, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";

import { AuthLayout } from "@/components/layout/auth-layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { resetPasswordSchema } from "@/lib/validations/auth";
import { apiClient, ApiClientError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import type { z } from "zod";

type ResetPasswordValues = z.infer<typeof resetPasswordSchema>;

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);

  const form = useForm<ResetPasswordValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  if (!token) {
    return (
      <AuthLayout title="Invalid Link">
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            This password reset link is invalid or has expired. Please request a new one.
          </p>
          <Link
            href={ROUTES.FORGOT_PASSWORD}
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            Request New Reset Link
          </Link>
        </div>
      </AuthLayout>
    );
  }

  if (success) {
    return (
      <AuthLayout title="Password Reset" description="Your password has been updated">
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <div className="rounded-full bg-emerald-100 p-4 dark:bg-emerald-900/30">
            <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Your password has been reset successfully. You can now sign in with your new password.
          </p>
          <Link href={ROUTES.LOGIN} className="text-sm font-medium text-blue-600 hover:underline">
            Go to Sign In
          </Link>
        </div>
      </AuthLayout>
    );
  }

  const onSubmit = async (values: ResetPasswordValues) => {
    try {
      await apiClient.post(API_ROUTES.AUTH.RESET_PASSWORD, {
        token,
        new_password: values.new_password,
      });
      setSuccess(true);
    } catch (error) {
      if (error instanceof ApiClientError) {
        const msg = typeof error.detail === "string" ? error.detail : "Reset failed";
        toast.error(msg);
        // If token is invalid, redirect to forgot password
        if (error.status === 400 || error.status === 404) {
          setTimeout(() => router.push(ROUTES.FORGOT_PASSWORD), 2000);
        }
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <AuthLayout
      title="Reset Password"
      description="Enter your new password"
      footer={
        <>
          Remember your password?{" "}
          <Link href={ROUTES.LOGIN} className="font-medium text-blue-600 hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="new_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>New Password</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter new password"
                      autoComplete="new-password"
                      {...field}
                    />
                    <button
                      type="button"
                      className="absolute top-1/2 right-3 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
                      onClick={() => setShowPassword((prev) => !prev)}
                      tabIndex={-1}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
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
                <FormLabel>Confirm Password</FormLabel>
                <FormControl>
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Confirm new password"
                    autoComplete="new-password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <p className="text-xs text-zinc-500">
            Password must be at least 8 characters with uppercase, lowercase, and a number.
          </p>

          <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Resetting...
              </>
            ) : (
              "Reset Password"
            )}
          </Button>
        </form>
      </Form>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <AuthLayout title="Reset Password">
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        </AuthLayout>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
