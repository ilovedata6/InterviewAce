/* ──────────────────────────────────────────────────────────
 * React Query hooks for interview operations
 * ────────────────────────────────────────────────────────── */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import type { PaginatedResponse } from "@/types/common";
import type {
  InterviewSession,
  InterviewStartRequest,
  Question,
  AnswerRequest,
  InterviewSummary,
} from "@/types/interview";

/** Query keys */
export const INTERVIEW_KEYS = {
  all: ["interviews"] as const,
  lists: () => [...INTERVIEW_KEYS.all, "list"] as const,
  list: (params: Record<string, unknown>) => [...INTERVIEW_KEYS.lists(), params] as const,
  details: () => [...INTERVIEW_KEYS.all, "detail"] as const,
  detail: (id: string) => [...INTERVIEW_KEYS.details(), id] as const,
  nextQuestion: (id: string) => [...INTERVIEW_KEYS.all, "next-question", id] as const,
  summary: (id: string) => [...INTERVIEW_KEYS.all, "summary", id] as const,
};

/** Params for listing interview history */
export interface InterviewHistoryParams {
  skip?: number;
  limit?: number;
}

/** Fetch interview history (paginated) */
export function useInterviewHistory(params: InterviewHistoryParams = {}) {
  return useQuery<PaginatedResponse<InterviewSession>>({
    queryKey: INTERVIEW_KEYS.list(params as Record<string, unknown>),
    queryFn: () =>
      apiClient.get<PaginatedResponse<InterviewSession>>(
        API_ROUTES.INTERVIEWS.HISTORY,
        params as Record<string, unknown>,
      ),
    staleTime: 60_000,
  });
}

/** Fetch a single interview session */
export function useInterviewSession(sessionId: string | undefined) {
  return useQuery<InterviewSession>({
    queryKey: INTERVIEW_KEYS.detail(sessionId!),
    queryFn: () => apiClient.get<InterviewSession>(API_ROUTES.INTERVIEWS.SESSION(sessionId!)),
    enabled: !!sessionId,
  });
}

/** Fetch interview summary */
export function useInterviewSummary(sessionId: string | undefined) {
  return useQuery<InterviewSummary>({
    queryKey: INTERVIEW_KEYS.summary(sessionId!),
    queryFn: () => apiClient.get<InterviewSummary>(API_ROUTES.INTERVIEWS.SUMMARY(sessionId!)),
    enabled: !!sessionId,
  });
}

/** Start a new interview */
export function useStartInterview() {
  const queryClient = useQueryClient();
  return useMutation<InterviewSession, Error, InterviewStartRequest>({
    mutationFn: (config) => apiClient.post<InterviewSession>(API_ROUTES.INTERVIEWS.START, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: INTERVIEW_KEYS.lists() });
    },
  });
}

/** Fetch next question (manual — not auto-refetch) */
export function useFetchNextQuestion() {
  return useMutation<Question | null, Error, string>({
    mutationFn: async (sessionId) => {
      const result = await apiClient.get<Question | undefined>(
        API_ROUTES.INTERVIEWS.NEXT_QUESTION(sessionId),
      );
      // apiClient returns undefined for 204 No Content (no more questions)
      return result ?? null;
    },
  });
}

/** Submit an answer */
export function useSubmitAnswer() {
  return useMutation<
    Question | null,
    Error,
    { sessionId: string; questionId: string; answer: AnswerRequest }
  >({
    mutationFn: async ({ sessionId, questionId, answer }) => {
      const result = await apiClient.post<Question | undefined>(
        API_ROUTES.INTERVIEWS.ANSWER(sessionId),
        {
          question_id: questionId,
          ...answer,
        },
      );
      // apiClient returns undefined for 204 No Content (no more questions)
      return result ?? null;
    },
  });
}

/** Complete interview and get summary */
export function useCompleteInterview() {
  const queryClient = useQueryClient();
  return useMutation<InterviewSummary, Error, string>({
    mutationFn: (sessionId) =>
      apiClient.post<InterviewSummary>(API_ROUTES.INTERVIEWS.COMPLETE(sessionId)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: INTERVIEW_KEYS.lists() });
      if (data.session_id) {
        queryClient.setQueryData(INTERVIEW_KEYS.summary(data.session_id), data);
      }
    },
  });
}
