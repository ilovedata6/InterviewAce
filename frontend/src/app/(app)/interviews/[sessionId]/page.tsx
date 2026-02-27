/* ──────────────────────────────────────────────────────────
 * Live Interview Page
 * Orchestrates: fetch session → get question → answer →
 * loop → complete → redirect to summary
 * ────────────────────────────────────────────────────────── */

"use client";

import { useEffect, useCallback, use } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useInterviewStore } from "@/stores/interview-store";
import {
  useInterviewSession,
  useFetchNextQuestion,
  useSubmitAnswer,
  useCompleteInterview,
} from "@/hooks/use-interview";
import { QuestionDisplay } from "@/components/interview/question-display";
import { AnswerInput } from "@/components/interview/answer-input";
import { InterviewProgressBar } from "@/components/interview/progress-bar";
import type { AnswerFormValues } from "@/lib/validations/interview";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";

export default function LiveInterviewPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const { sessionId } = use(params);
  const router = useRouter();

  /* ── Store ── */
  const {
    state,
    session,
    currentQuestion,
    questionsAnswered,
    totalQuestions,
    error,
    answerStartTime,
    setSession,
    setCurrentQuestion,
    setNoMoreQuestions,
    setSubmitting,
    setSummary,
    setError,
    incrementAnswered,
    resetInterview,
  } = useInterviewStore();

  /* ── Queries & Mutations ── */
  const { data: sessionData, isLoading: sessionLoading } = useInterviewSession(sessionId);
  const fetchNextQuestion = useFetchNextQuestion();
  const submitAnswer = useSubmitAnswer();
  const completeInterview = useCompleteInterview();

  /* ── Initialise session in store ── */
  useEffect(() => {
    if (sessionData && !session) {
      setSession(sessionData);
    }
  }, [sessionData, session, setSession]);

  /* ── Fetch first question once session is loaded ── */
  useEffect(() => {
    if (state === "loading" && session) {
      fetchNextQuestion.mutate(sessionId, {
        onSuccess: (question) => {
          if (question) {
            setCurrentQuestion(question);
          } else {
            setNoMoreQuestions();
          }
        },
        onError: (err) => {
          setError(err.message);
          toast.error("Failed to load question");
        },
      });
    }
    // Only run when state transitions to "loading"
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state, session?.id]);

  /* ── Submit answer handler ── */
  const handleSubmitAnswer = useCallback(
    (values: AnswerFormValues) => {
      if (!currentQuestion || !session) return;

      setSubmitting();
      submitAnswer.mutate(
        {
          sessionId: session.id,
          questionId: currentQuestion.question_id,
          answer: {
            answer_text: values.answer_text,
            time_taken_seconds: values.time_taken_seconds ?? undefined,
          },
        },
        {
          onSuccess: (nextQuestion) => {
            incrementAnswered();
            if (nextQuestion) {
              setCurrentQuestion(nextQuestion);
            } else {
              // No more questions — auto-complete
              setNoMoreQuestions();
            }
          },
          onError: (err) => {
            setError(err.message);
            toast.error("Failed to submit answer");
          },
        },
      );
    },
    [
      currentQuestion,
      session,
      setSubmitting,
      submitAnswer,
      incrementAnswered,
      setCurrentQuestion,
      setNoMoreQuestions,
      setError,
    ],
  );

  /* ── Complete interview handler ── */
  const handleComplete = useCallback(() => {
    if (!session) return;

    completeInterview.mutate(session.id, {
      onSuccess: (summary) => {
        setSummary(summary);
        toast.success("Interview completed!");
        router.push(`/interviews/${session.id}/summary`);
      },
      onError: (err) => {
        setError(err.message);
        toast.error("Failed to complete interview");
      },
    });
  }, [session, completeInterview, setSummary, router, setError]);

  /* ── Auto-complete when no more questions ── */
  useEffect(() => {
    if (state === "completing") {
      handleComplete();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  /* ── Cleanup on unmount ── */
  useEffect(() => {
    return () => {
      resetInterview();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── Loading state ── */
  if (sessionLoading || (state === "loading" && !currentQuestion)) {
    return (
      <div className="container max-w-3xl space-y-6 py-8">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  /* ── Error state ── */
  if (error && !currentQuestion) {
    return (
      <div className="container max-w-3xl py-8">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <AlertCircle className="text-destructive h-12 w-12" />
            <p className="text-destructive font-medium">{error}</p>
            <Button variant="outline" onClick={() => router.push("/interviews")}>
              Back to Interviews
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  /* ── Completing state ── */
  if (state === "completing") {
    return (
      <div className="container max-w-3xl py-8">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <Loader2 className="text-primary h-12 w-12 animate-spin" />
            <p className="text-lg font-medium">Completing your interview…</p>
            <p className="text-muted-foreground text-sm">
              Our AI is analyzing your responses. This may take a moment.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  /* ── Summary redirect (should not stay here long) ── */
  if (state === "summary") {
    return (
      <div className="container max-w-3xl py-8">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <CheckCircle className="h-12 w-12 text-green-500" />
            <p className="text-lg font-medium">Interview Complete!</p>
            <p className="text-muted-foreground text-sm">Redirecting to your summary…</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  /* ── Active Q&A ── */
  return (
    <div className="container max-w-3xl space-y-6 py-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Live Interview</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Answer each question thoughtfully. Take your time.
        </p>
      </div>

      {/* Progress */}
      <InterviewProgressBar answered={questionsAnswered} total={totalQuestions} />

      {/* Question */}
      {currentQuestion && (
        <QuestionDisplay question={currentQuestion} totalQuestions={totalQuestions} />
      )}

      {/* Answer Input */}
      {currentQuestion && state === "answering" && (
        <AnswerInput
          onSubmit={handleSubmitAnswer}
          isSubmitting={false}
          answerStartTime={answerStartTime}
        />
      )}

      {/* Submitting state */}
      {state === "submitting" && (
        <Card>
          <CardContent className="flex items-center justify-center gap-3 py-8">
            <Loader2 className="text-primary h-5 w-5 animate-spin" />
            <span className="text-muted-foreground">Submitting your answer…</span>
          </CardContent>
        </Card>
      )}

      {/* Error banner (non-blocking) */}
      {error && currentQuestion && (
        <div className="bg-destructive/10 text-destructive rounded-md p-3 text-sm">{error}</div>
      )}
    </div>
  );
}
