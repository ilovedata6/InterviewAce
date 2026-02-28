/* ──────────────────────────────────────────────────────────
 * Interview Configuration Form
 * Select resume, question count, difficulty, and focus areas
 * ────────────────────────────────────────────────────────── */

"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@/lib/zod-resolver";
import { interviewConfigSchema, type InterviewConfigFormValues } from "@/lib/validations/interview";
import { useResumes } from "@/hooks/use-resumes";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Play, FileText, Brain, Target, Hash } from "lucide-react";

interface InterviewConfigProps {
  onSubmit: (values: InterviewConfigFormValues) => void;
  isLoading?: boolean;
}

const DIFFICULTY_OPTIONS = [
  { value: "easy", label: "Easy", description: "Foundational concepts" },
  { value: "medium", label: "Medium", description: "Intermediate challenges" },
  { value: "hard", label: "Hard", description: "Advanced problems" },
  { value: "mixed", label: "Mixed", description: "Variety of difficulty levels" },
] as const;

export function InterviewConfig({ onSubmit, isLoading }: InterviewConfigProps) {
  const { data: resumeData, isLoading: resumesLoading } = useResumes({ limit: 50 });

  const form = useForm<InterviewConfigFormValues>({
    resolver: zodResolver(interviewConfigSchema),
    defaultValues: {
      resume_id: null,
      question_count: 12,
      difficulty: "mixed",
      focus_areas: null,
    },
  });

  const analyzedResumes = resumeData?.items?.filter((r) => r.status === "analyzed");

  return (
    <Card className="mx-auto w-full max-w-2xl border-zinc-200/80 shadow-lg dark:border-zinc-800/80">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/40">
            <Brain className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          Configure Your Interview
        </CardTitle>
        <CardDescription>
          Customize your AI-powered mock interview. Select a resume for personalized questions or
          start a general interview.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Resume Selection */}
            <FormField
              control={form.control}
              name="resume_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Resume (Optional)
                  </FormLabel>
                  <Select
                    onValueChange={(val) => field.onChange(val === "__none__" ? null : val)}
                    value={field.value ?? "__none__"}
                    disabled={resumesLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a resume for personalized questions" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="__none__">No resume — general interview</SelectItem>
                      {analyzedResumes?.map((resume) => (
                        <SelectItem key={resume.id} value={resume.id}>
                          <span className="flex items-center gap-2">
                            {resume.file_name}
                            <Badge variant="secondary" className="text-xs">
                              Analyzed
                            </Badge>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Selecting a resume generates questions tailored to your experience and skills.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Question Count */}
            <FormField
              control={form.control}
              name="question_count"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center gap-2">
                    <Hash className="h-4 w-4" />
                    Number of Questions
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={5}
                      max={30}
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value))}
                    />
                  </FormControl>
                  <FormDescription>
                    Choose between 5 and 30 questions. Default is 12.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Difficulty */}
            <FormField
              control={form.control}
              name="difficulty"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Difficulty
                  </FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {DIFFICULTY_OPTIONS.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>
                          <span className="flex items-center gap-2">
                            {opt.label}
                            <span className="text-muted-foreground text-xs">
                              — {opt.description}
                            </span>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Submit */}
            <Button
              type="submit"
              className="w-full rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-md shadow-blue-600/20 transition-all hover:shadow-lg hover:shadow-blue-600/25 hover:brightness-110"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting Interview…
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Start Interview
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
