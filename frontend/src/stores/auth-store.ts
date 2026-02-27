/* ──────────────────────────────────────────────────────────
 * Auth Store — Zustand
 *
 * Global client-side auth state:
 *  • user          — the current User object (or null)
 *  • isAuthenticated — derived boolean
 *  • isLoading     — true while hydrating from /api/auth/me
 *  • login()       — POST /api/auth/login, populate user
 *  • register()    — POST /api/auth/register
 *  • logout()      — POST /api/auth/logout, clear state
 *  • fetchUser()   — GET /api/auth/me, populate user
 *
 * The store does NOT touch JWTs — those live in httpOnly
 * cookies managed by the BFF layer.
 * ────────────────────────────────────────────────────────── */

import { create } from "zustand";
import { apiClient, ApiClientError } from "@/lib/api-client";
import { API_ROUTES } from "@/lib/constants";
import type { User, LoginRequest, RegisterRequest } from "@/types/auth";
import type { MessageResponse } from "@/types/common";

/* ── State shape ── */

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  /** Hydrate user from the /me endpoint (called on mount) */
  fetchUser: () => Promise<void>;

  /** Authenticate with email + password */
  login: (data: LoginRequest) => Promise<void>;

  /** Create a new account */
  register: (data: RegisterRequest) => Promise<MessageResponse>;

  /** Sign out and clear state */
  logout: () => Promise<void>;

  /** Manually set user (e.g. from SSR) */
  setUser: (user: User | null) => void;

  /** Reset the store to initial state */
  reset: () => void;
}

/* ── Initial (unauthenticated) values ── */

const INITIAL_STATE = {
  user: null,
  isAuthenticated: false,
  isLoading: true, // true until first fetchUser resolves
};

/* ── Store ── */

export const useAuthStore = create<AuthState>()((set, get) => ({
  ...INITIAL_STATE,

  fetchUser: async () => {
    try {
      set({ isLoading: true });
      const user = await apiClient.get<User>(API_ROUTES.AUTH.ME);
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      // Not authenticated or token expired
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (data: LoginRequest) => {
    // BFF login route sets httpOnly cookies and returns user
    const user = await apiClient.post<User>(API_ROUTES.AUTH.LOGIN, data);
    set({ user, isAuthenticated: true });
  },

  register: async (data: RegisterRequest) => {
    const response = await apiClient.post<MessageResponse>(API_ROUTES.AUTH.REGISTER, data);
    return response;
  },

  logout: async () => {
    try {
      await apiClient.post(API_ROUTES.AUTH.LOGOUT);
    } catch {
      // Even if the backend call fails, clear local state
    }
    set({ ...INITIAL_STATE, isLoading: false });
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user, isLoading: false });
  },

  reset: () => {
    set({ ...INITIAL_STATE, isLoading: false });
  },
}));
