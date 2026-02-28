/* ──────────────────────────────────────────────────────────
 * Dashboard Quick Actions
 * Primary CTA buttons: Start Interview, Upload Resume
 * ────────────────────────────────────────────────────────── */

"use client";

import Link from "next/link";
import { Mic, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/lib/constants";

export function QuickActions() {
  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>
          Jump into your next practice session or upload a new resume.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 sm:flex-row">
        <Button
          asChild
          size="lg"
          className="flex-1 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-md shadow-blue-600/20 transition-all hover:shadow-lg hover:shadow-blue-600/25 hover:brightness-110"
        >
          <Link href={ROUTES.INTERVIEW_START}>
            <Mic className="mr-2 h-4 w-4" />
            Start Interview
          </Link>
        </Button>
        <Button asChild size="lg" variant="outline" className="flex-1 rounded-xl">
          <Link href={ROUTES.RESUME_UPLOAD}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Resume
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
