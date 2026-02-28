/* ──────────────────────────────────────────────────────────
 * Answer Input Component
 * Textarea with character count, elapsed timer, submit button
 * ────────────────────────────────────────────────────────── */

"use client";

/* eslint-disable react-hooks/incompatible-library */
import { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@/lib/zod-resolver";
import { answerSchema, type AnswerFormValues } from "@/lib/validations/interview";
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2, Send, Clock } from "lucide-react";

interface AnswerInputProps {
  onSubmit: (values: AnswerFormValues) => void;
  isSubmitting?: boolean;
  /** Timestamp (ms) when the question was shown — used to calc time_taken */
  answerStartTime?: number | null;
}

const MAX_CHARS = 5000;

function formatTime(seconds: number) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function AnswerInput({ onSubmit, isSubmitting, answerStartTime }: AnswerInputProps) {
  const [elapsed, setElapsed] = useState(0);

  const form = useForm<AnswerFormValues>({
    resolver: zodResolver(answerSchema),
    defaultValues: {
      answer_text: "",
      time_taken_seconds: null,
    },
  });

  const answerText = form.watch("answer_text");

  // Tick elapsed timer every second
  useEffect(() => {
    if (!answerStartTime) return;
    setElapsed(0);
    const interval = setInterval(() => {
      setElapsed(Math.round((Date.now() - answerStartTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [answerStartTime]);

  const handleSubmit = useCallback(
    (values: AnswerFormValues) => {
      onSubmit({
        ...values,
        time_taken_seconds: answerStartTime
          ? Math.round((Date.now() - answerStartTime) / 1000)
          : null,
      });
      form.reset({ answer_text: "", time_taken_seconds: null });
    },
    [onSubmit, answerStartTime, form],
  );

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="answer_text"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Textarea
                  placeholder="Type your answer here…"
                  className="min-h-[180px] resize-y rounded-xl border-zinc-200/80 bg-zinc-50/50 transition-colors focus-visible:bg-white dark:border-zinc-800/80 dark:bg-zinc-900/50 dark:focus-visible:bg-zinc-950"
                  disabled={isSubmitting}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex items-center justify-between">
          {/* Left: timer + char count */}
          <div className="text-muted-foreground flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {formatTime(elapsed)}
            </span>
            <span>
              {answerText?.length ?? 0} / {MAX_CHARS}
            </span>
          </div>

          {/* Right: submit button */}
          <Button
            type="submit"
            disabled={isSubmitting || !answerText?.trim()}
            className="rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-md shadow-blue-600/20 transition-all hover:shadow-lg hover:shadow-blue-600/25 hover:brightness-110"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting…
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Submit Answer
              </>
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
}
