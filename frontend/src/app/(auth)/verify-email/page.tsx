"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/layout/auth-layout";
import { apiClient, ApiClientError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import { Suspense } from "react";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  // Derive initial state from token presence (no setState in effect)
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    token ? "loading" : "error",
  );
  const [message, setMessage] = useState(
    token ? "" : "No verification token found. Please check your email link.",
  );

  useEffect(() => {
    if (!token) return;

    apiClient
      .post(API_ROUTES.AUTH.VERIFY_EMAIL, { token })
      .then(() => {
        setStatus("success");
        setMessage("Your email has been verified successfully!");
      })
      .catch((error) => {
        setStatus("error");
        if (error instanceof ApiClientError) {
          setMessage(typeof error.detail === "string" ? error.detail : "Verification failed");
        } else {
          setMessage("Something went wrong. Please try again.");
        }
      });
  }, [token]);

  return (
    <div className="flex flex-col items-center gap-4 py-4 text-center">
      {status === "loading" && (
        <>
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-zinc-600 dark:text-zinc-400">Verifying your email...</p>
        </>
      )}

      {status === "success" && (
        <>
          <div className="rounded-full bg-emerald-100 p-4 dark:bg-emerald-900/30">
            <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">{message}</p>
          <Link href={ROUTES.LOGIN} className="text-sm font-medium text-blue-600 hover:underline">
            Go to Sign In
          </Link>
        </>
      )}

      {status === "error" && (
        <>
          <div className="rounded-full bg-red-100 p-4 dark:bg-red-900/30">
            <XCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
          </div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">{message}</p>
          <Link href={ROUTES.LOGIN} className="text-sm font-medium text-blue-600 hover:underline">
            Back to Sign In
          </Link>
        </>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <AuthLayout title="Email Verification">
      <Suspense
        fallback={
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        }
      >
        <VerifyEmailContent />
      </Suspense>
    </AuthLayout>
  );
}
