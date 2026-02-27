/* ──────────────────────────────────────────────────────────
 * React Query hooks for resume operations
 * ────────────────────────────────────────────────────────── */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import type { PaginatedResponse } from "@/types/common";
import type {
  Resume,
  ResumeAnalysisResponse,
  ResumeUploadResponse,
  ResumeUpdateRequest,
  ResumeShareRequest,
} from "@/types/resume";

/** Query keys */
const RESUME_KEYS = {
  all: ["resumes"] as const,
  lists: () => [...RESUME_KEYS.all, "list"] as const,
  list: (params: Record<string, unknown>) => [...RESUME_KEYS.lists(), params] as const,
  details: () => [...RESUME_KEYS.all, "detail"] as const,
  detail: (id: string) => [...RESUME_KEYS.details(), id] as const,
  analysis: (id: string) => [...RESUME_KEYS.all, "analysis", id] as const,
  versions: (id: string) => [...RESUME_KEYS.all, "versions", id] as const,
};

/** Params for listing resumes */
export interface ResumeListParams {
  skip?: number;
  limit?: number;
  status?: string;
  search?: string;
}

/** Fetch paginated resume list */
export function useResumes(params: ResumeListParams = {}) {
  return useQuery<PaginatedResponse<Resume>>({
    queryKey: RESUME_KEYS.list(params as Record<string, unknown>),
    queryFn: () =>
      apiClient.get<PaginatedResponse<Resume>>(
        API_ROUTES.RESUMES.LIST,
        params as Record<string, unknown>,
      ),
    staleTime: 60_000,
  });
}

/** Fetch single resume by ID */
export function useResume(id: string | undefined) {
  return useQuery<Resume>({
    queryKey: RESUME_KEYS.detail(id!),
    queryFn: () => apiClient.get<Resume>(API_ROUTES.RESUMES.DETAIL(id!)),
    enabled: !!id,
  });
}

/** Fetch resume analysis */
export function useResumeAnalysis(id: string | undefined) {
  return useQuery<ResumeAnalysisResponse>({
    queryKey: RESUME_KEYS.analysis(id!),
    queryFn: () => apiClient.get<ResumeAnalysisResponse>(API_ROUTES.RESUMES.ANALYSIS(id!)),
    enabled: !!id,
  });
}

/** Fetch resume versions */
export function useResumeVersions(id: string | undefined) {
  return useQuery({
    queryKey: RESUME_KEYS.versions(id!),
    queryFn: () =>
      apiClient.get<{
        versions: Array<{
          version: number;
          created_at: string;
          changes: string[];
          parent_version_id: string | null;
        }>;
        current_version: number;
      }>(API_ROUTES.RESUMES.VERSIONS(id!)),
    enabled: !!id,
  });
}

/** Upload a new resume file */
export function useUploadResume() {
  const queryClient = useQueryClient();

  return useMutation<ResumeUploadResponse, Error, File>({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.upload<ResumeUploadResponse>(API_ROUTES.RESUMES.LIST, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RESUME_KEYS.all });
    },
  });
}

/** Update resume metadata */
export function useUpdateResume(id: string) {
  const queryClient = useQueryClient();

  return useMutation<Resume, Error, ResumeUpdateRequest>({
    mutationFn: (data) => apiClient.put<Resume>(API_ROUTES.RESUMES.DETAIL(id), data),
    onSuccess: (updated) => {
      queryClient.setQueryData(RESUME_KEYS.detail(id), updated);
      queryClient.invalidateQueries({ queryKey: RESUME_KEYS.lists() });
    },
  });
}

/** Delete a resume */
export function useDeleteResume() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => apiClient.del(API_ROUTES.RESUMES.DETAIL(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RESUME_KEYS.all });
    },
  });
}

/** Share a resume */
export function useShareResume(id: string) {
  return useMutation({
    mutationFn: (data: ResumeShareRequest) =>
      apiClient.post<{
        share_token: string;
        share_url: string;
        expiry_date: string | null;
        is_public: boolean;
      }>(API_ROUTES.RESUMES.SHARE(id), data),
  });
}

/** Re-analyze a resume */
export function useReanalyzeResume(id: string) {
  const queryClient = useQueryClient();

  return useMutation<ResumeAnalysisResponse, Error>({
    mutationFn: () =>
      apiClient.post<ResumeAnalysisResponse>(`${API_ROUTES.RESUMES.ANALYSIS(id)}/reanalyze`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RESUME_KEYS.analysis(id) });
      queryClient.invalidateQueries({ queryKey: RESUME_KEYS.detail(id) });
    },
  });
}

/** Poll resume status until it leaves "pending" / "processing" */
export function useResumePolling(id: string | undefined, status: string | undefined) {
  return useQuery<Resume>({
    queryKey: [...RESUME_KEYS.detail(id!), "poll"],
    queryFn: () => apiClient.get<Resume>(API_ROUTES.RESUMES.DETAIL(id!)),
    enabled: !!id && (status === "pending" || status === "processing"),
    refetchInterval: 3000, // poll every 3s
  });
}
