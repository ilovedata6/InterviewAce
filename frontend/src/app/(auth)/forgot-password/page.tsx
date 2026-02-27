"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@/lib/zod-resolver";
import Link from "next/link";
import { Loader2, MailCheck } from "lucide-react";
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
import { forgotPasswordSchema } from "@/lib/validations/auth";
import { apiClient, ApiClientError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import type { z } from "zod";

type ForgotPasswordValues = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);

  const form = useForm<ForgotPasswordValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  const onSubmit = async (values: ForgotPasswordValues) => {
    try {
      await apiClient.post(API_ROUTES.AUTH.FORGOT_PASSWORD, values);
      setSent(true);
    } catch (error) {
      if (error instanceof ApiClientError) {
        toast.error(typeof error.detail === "string" ? error.detail : "Request failed");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    }
  };

  if (sent) {
    return (
      <AuthLayout title="Check Your Email" description="We sent a password reset link">
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <div className="rounded-full bg-blue-100 p-4 dark:bg-blue-900/30">
            <MailCheck className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          </div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            If an account exists with that email, you&apos;ll receive a password reset link shortly.
          </p>
          <Link href={ROUTES.LOGIN} className="text-sm font-medium text-blue-600 hover:underline">
            Back to Sign In
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Forgot Password"
      description="Enter your email and we'll send you a reset link"
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
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="you@example.com"
                    autoComplete="email"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
            {form.formState.isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Sending...
              </>
            ) : (
              "Send Reset Link"
            )}
          </Button>
        </form>
      </Form>
    </AuthLayout>
  );
}
