/* ──────────────────────────────────────────────────────────
 * Unit Tests — Interview Store (state machine transitions)
 * ────────────────────────────────────────────────────────── */
import { describe, it, expect, beforeEach, vi } from "vitest";
import { useInterviewStore } from "@/stores/interview-store";
import type { InterviewSession, Question, InterviewSummary } from "@/types/interview";

const mockSession: InterviewSession = {
  id: "sess-1",
  resume_id: "res-1",
  difficulty: "intermediate",
  question_count: 5,
  categories: ["javascript", "react"],
  status: "in_progress",
  started_at: "2024-06-01T10:00:00Z",
};

const mockQuestion: Question = {
  id: "q-1",
  question_text: "What is a closure?",
  category: "javascript",
  difficulty: "intermediate",
  question_number: 1,
};

const mockSummary: InterviewSummary = {
  session_id: "sess-1",
  overall_score: 85,
  total_questions: 5,
  questions_answered: 5,
  duration_seconds: 600,
  difficulty: "intermediate",
  categories: ["javascript", "react"],
  category_scores: { javascript: 90, react: 80 },
  strengths: ["Good understanding of closures"],
  improvements: ["Need more practice with hooks"],
  started_at: "2024-06-01T10:00:00Z",
  completed_at: "2024-06-01T10:10:00Z",
};

describe("useInterviewStore", () => {
  beforeEach(() => {
    useInterviewStore.getState().resetInterview();
  });

  it("should start in configuring state", () => {
    const state = useInterviewStore.getState();
    expect(state.state).toBe("configuring");
    expect(state.session).toBeNull();
    expect(state.currentQuestion).toBeNull();
    expect(state.questionsAnswered).toBe(0);
    expect(state.totalQuestions).toBe(0);
    expect(state.summary).toBeNull();
    expect(state.error).toBeNull();
  });

  describe("setSession", () => {
    it("should transition to loading and store session", () => {
      useInterviewStore.getState().setSession(mockSession);
      const state = useInterviewStore.getState();

      expect(state.state).toBe("loading");
      expect(state.session).toEqual(mockSession);
      expect(state.totalQuestions).toBe(5);
      expect(state.error).toBeNull();
    });
  });

  describe("setCurrentQuestion", () => {
    it("should transition to answering and start timer", () => {
      const now = Date.now();
      vi.spyOn(Date, "now").mockReturnValue(now);

      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      const state = useInterviewStore.getState();

      expect(state.state).toBe("answering");
      expect(state.currentQuestion).toEqual(mockQuestion);
      expect(state.answerStartTime).toBe(now);

      vi.restoreAllMocks();
    });
  });

  describe("setSubmitting", () => {
    it("should transition to submitting", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      useInterviewStore.getState().setSubmitting();

      expect(useInterviewStore.getState().state).toBe("submitting");
    });
  });

  describe("setFeedback", () => {
    it("should transition to feedback", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      useInterviewStore.getState().setSubmitting();
      useInterviewStore.getState().setFeedback();

      expect(useInterviewStore.getState().state).toBe("feedback");
    });
  });

  describe("setNoMoreQuestions", () => {
    it("should transition to completing and clear question", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      useInterviewStore.getState().setNoMoreQuestions();
      const state = useInterviewStore.getState();

      expect(state.state).toBe("completing");
      expect(state.currentQuestion).toBeNull();
    });
  });

  describe("setSummary", () => {
    it("should transition to summary and store data", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setSummary(mockSummary);
      const state = useInterviewStore.getState();

      expect(state.state).toBe("summary");
      expect(state.summary).toEqual(mockSummary);
      expect(state.currentQuestion).toBeNull();
    });
  });

  describe("setError", () => {
    it("should set error and keep configuring if no session", () => {
      useInterviewStore.getState().setError("Something went wrong");
      const state = useInterviewStore.getState();

      expect(state.error).toBe("Something went wrong");
      expect(state.state).toBe("configuring");
    });

    it("should set error and fall back to answering if session exists", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      useInterviewStore.getState().setError("Network error");
      const state = useInterviewStore.getState();

      expect(state.error).toBe("Network error");
      expect(state.state).toBe("answering");
    });
  });

  describe("incrementAnswered", () => {
    it("should increment the questions answered counter", () => {
      useInterviewStore.getState().incrementAnswered();
      expect(useInterviewStore.getState().questionsAnswered).toBe(1);

      useInterviewStore.getState().incrementAnswered();
      expect(useInterviewStore.getState().questionsAnswered).toBe(2);
    });
  });

  describe("getElapsedSeconds", () => {
    it("should return 0 when timer not started", () => {
      expect(useInterviewStore.getState().getElapsedSeconds()).toBe(0);
    });

    it("should calculate elapsed time correctly", () => {
      const start = 1000000;
      vi.spyOn(Date, "now")
        .mockReturnValueOnce(start) // setCurrentQuestion call
        .mockReturnValueOnce(start + 5000); // getElapsedSeconds call

      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);

      expect(useInterviewStore.getState().getElapsedSeconds()).toBe(5);

      vi.restoreAllMocks();
    });
  });

  describe("resetInterview", () => {
    it("should reset all state back to initial", () => {
      useInterviewStore.getState().setSession(mockSession);
      useInterviewStore.getState().setCurrentQuestion(mockQuestion);
      useInterviewStore.getState().incrementAnswered();
      useInterviewStore.getState().resetInterview();

      const state = useInterviewStore.getState();
      expect(state.state).toBe("configuring");
      expect(state.session).toBeNull();
      expect(state.currentQuestion).toBeNull();
      expect(state.questionsAnswered).toBe(0);
      expect(state.totalQuestions).toBe(0);
      expect(state.summary).toBeNull();
      expect(state.error).toBeNull();
      expect(state.answerStartTime).toBeNull();
    });
  });

  describe("full flow: configuring → answering → summary", () => {
    it("should complete the full state machine flow", () => {
      const store = useInterviewStore;

      // Start
      expect(store.getState().state).toBe("configuring");

      // Session created
      store.getState().setSession(mockSession);
      expect(store.getState().state).toBe("loading");

      // Question received
      store.getState().setCurrentQuestion(mockQuestion);
      expect(store.getState().state).toBe("answering");

      // User submits answer
      store.getState().setSubmitting();
      expect(store.getState().state).toBe("submitting");

      // Feedback received
      store.getState().setFeedback();
      expect(store.getState().state).toBe("feedback");
      store.getState().incrementAnswered();

      // No more questions
      store.getState().setNoMoreQuestions();
      expect(store.getState().state).toBe("completing");

      // Summary received
      store.getState().setSummary(mockSummary);
      expect(store.getState().state).toBe("summary");
      expect(store.getState().summary?.overall_score).toBe(85);
    });
  });
});
