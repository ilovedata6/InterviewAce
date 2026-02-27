import { Suspense } from "react";
import { AuthLayout } from "@/components/layout/auth-layout";
import { LoginContent } from "./login-content";
import Link from "next/link";
import { ROUTES } from "@/lib/constants";

export default function LoginPage() {
  return (
    <AuthLayout
      title="Welcome Back"
      description="Sign in to your InterviewAce account"
      footer={
        <>
          Don&apos;t have an account?{" "}
          <Link href={ROUTES.REGISTER} className="font-medium text-blue-600 hover:underline">
            Sign up
          </Link>
        </>
      }
    >
      <Suspense>
        <LoginContent />
      </Suspense>
    </AuthLayout>
  );
}
