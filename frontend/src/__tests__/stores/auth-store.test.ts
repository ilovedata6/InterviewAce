/* ──────────────────────────────────────────────────────────
 * Unit Tests — Auth Store
 * ────────────────────────────────────────────────────────── */
import { describe, it, expect, beforeEach, vi } from "vitest";
import { useAuthStore } from "@/stores/auth-store";

// Mock the api-client module
vi.mock("@/lib/api-client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
  ApiClientError: class ApiClientError extends Error {
    status: number;
    constructor(message: string, status: number) {
      super(message);
      this.status = status;
    }
  },
}));

// Import after mocking
import { apiClient } from "@/lib/api-client";

const mockUser = {
  id: "u1",
  email: "test@example.com",
  full_name: "Test User",
  is_active: true,
  role: "user" as const,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

describe("useAuthStore", () => {
  beforeEach(() => {
    // Reset the store between tests
    useAuthStore.getState().reset();
    vi.clearAllMocks();
  });

  it("should have correct initial state", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false); // reset sets false
  });

  describe("fetchUser", () => {
    it("should populate user on success", async () => {
      vi.mocked(apiClient.get).mockResolvedValueOnce(mockUser);

      await useAuthStore.getState().fetchUser();
      const state = useAuthStore.getState();

      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
      expect(state.isLoading).toBe(false);
    });

    it("should clear user on failure", async () => {
      vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("401"));

      await useAuthStore.getState().fetchUser();
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });
  });

  describe("login", () => {
    it("should set user on successful login", async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce(mockUser);

      await useAuthStore.getState().login({ email: "test@example.com", password: "pass" });
      const state = useAuthStore.getState();

      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });

    it("should propagate error on failed login", async () => {
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error("Invalid credentials"));

      await expect(
        useAuthStore.getState().login({ email: "test@example.com", password: "wrong" }),
      ).rejects.toThrow("Invalid credentials");
    });
  });

  describe("register", () => {
    it("should return message on success", async () => {
      const msg = { message: "Check your email" };
      vi.mocked(apiClient.post).mockResolvedValueOnce(msg);

      const result = await useAuthStore.getState().register({
        email: "new@example.com",
        password: "Pass123!",
        full_name: "New User",
      });

      expect(result).toEqual(msg);
    });
  });

  describe("logout", () => {
    it("should clear state on logout", async () => {
      // First set up authenticated state
      useAuthStore.getState().setUser(mockUser);
      vi.mocked(apiClient.post).mockResolvedValueOnce(undefined);

      await useAuthStore.getState().logout();
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });

    it("should still clear state even if backend call fails", async () => {
      useAuthStore.getState().setUser(mockUser);
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error("Network error"));

      await useAuthStore.getState().logout();
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("setUser", () => {
    it("should set user and mark authenticated", () => {
      useAuthStore.getState().setUser(mockUser);
      const state = useAuthStore.getState();

      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
      expect(state.isLoading).toBe(false);
    });

    it("should clear auth when user is null", () => {
      useAuthStore.getState().setUser(null);
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("reset", () => {
    it("should return to initial state", () => {
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().reset();
      const state = useAuthStore.getState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });
  });
});
