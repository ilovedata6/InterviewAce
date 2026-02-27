"use client";

import { useState } from "react";
import Link from "next/link";
import { MailCheck } from "lucide-react";
import { AuthLayout } from "@/components/layout/auth-layout";
import { RegisterForm } from "@/components/auth/register-form";
import { ROUTES } from "@/lib/constants";

export default function RegisterPage() {
  const [success, setSuccess] = useState(false);

  if (success) {
    return (
      <AuthLayout title="Check Your Email" description="We sent you a verification link">
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <div className="rounded-full bg-emerald-100 p-4 dark:bg-emerald-900/30">
            <MailCheck className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Please check your email inbox and click the verification link to activate your account.
          </p>
          <Link href={ROUTES.LOGIN} className="text-sm font-medium text-blue-600 hover:underline">
            Go to Sign In
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Create an Account"
      description="Start preparing for your next interview"
      footer={
        <>
          Already have an account?{" "}
          <Link href={ROUTES.LOGIN} className="font-medium text-blue-600 hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <RegisterForm onSuccess={() => setSuccess(true)} />
    </AuthLayout>
  );
}
