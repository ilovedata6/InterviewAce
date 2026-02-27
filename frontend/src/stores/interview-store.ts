/* ──────────────────────────────────────────────────────────
 * Interview Zustand Store
 * State machine: configuring → loading → answering → submitting
 *                → feedback → completing → summary
 * ────────────────────────────────────────────────────────── */

"use client";

import { create } from "zustand";
import type {
  InterviewSession,
  InterviewState,
  Question,
  InterviewSummary,
} from "@/types/interview";

interface InterviewStore {
  /* ── state ── */
  state: InterviewState;
  session: InterviewSession | null;
  currentQuestion: Question | null;
  questionsAnswered: number;
  totalQuestions: number;
  summary: InterviewSummary | null;
  error: string | null;
  answerStartTime: number | null;

  /* ── actions ── */
  /** Transition to configuring (initial / reset) */
  resetInterview: () => void;

  /** Session created — move to loading first question */
  setSession: (session: InterviewSession) => void;

  /** First / next question received */
  setCurrentQuestion: (question: Question) => void;

  /** No more questions (204) */
  setNoMoreQuestions: () => void;

  /** User is submitting an answer */
  setSubmitting: () => void;

  /** Answer accepted — brief feedback state before next q */
  setFeedback: () => void;

  /** Interview completed — summary received */
  setSummary: (summary: InterviewSummary) => void;

  /** Error */
  setError: (error: string) => void;

  /** Start the answer timer */
  startAnswerTimer: () => void;

  /** Get elapsed answer time in seconds */
  getElapsedSeconds: () => number;

  /** Increment questions answered count */
  incrementAnswered: () => void;
}

export const useInterviewStore = create<InterviewStore>((set, get) => ({
  /* ── initial state ── */
  state: "configuring",
  session: null,
  currentQuestion: null,
  questionsAnswered: 0,
  totalQuestions: 0,
  summary: null,
  error: null,
  answerStartTime: null,

  /* ── actions ── */
  resetInterview: () =>
    set({
      state: "configuring",
      session: null,
      currentQuestion: null,
      questionsAnswered: 0,
      totalQuestions: 0,
      summary: null,
      error: null,
      answerStartTime: null,
    }),

  setSession: (session) =>
    set({
      state: "loading",
      session,
      totalQuestions: session.question_count,
      error: null,
    }),

  setCurrentQuestion: (question) =>
    set({
      state: "answering",
      currentQuestion: question,
      error: null,
      answerStartTime: Date.now(),
    }),

  setNoMoreQuestions: () =>
    set({
      state: "completing",
      currentQuestion: null,
    }),

  setSubmitting: () =>
    set({
      state: "submitting",
    }),

  setFeedback: () =>
    set({
      state: "feedback",
    }),

  setSummary: (summary) =>
    set({
      state: "summary",
      summary,
      currentQuestion: null,
    }),

  setError: (error) =>
    set({
      error,
      state: get().session ? "answering" : "configuring",
    }),

  startAnswerTimer: () =>
    set({
      answerStartTime: Date.now(),
    }),

  getElapsedSeconds: () => {
    const start = get().answerStartTime;
    if (!start) return 0;
    return Math.round((Date.now() - start) / 1000);
  },

  incrementAnswered: () =>
    set((prev) => ({
      questionsAnswered: prev.questionsAnswered + 1,
    })),
}));
