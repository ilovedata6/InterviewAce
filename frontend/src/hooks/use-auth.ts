/* ──────────────────────────────────────────────────────────
 * useAuth — convenience hook for components
 *
 * Provides everything a component needs for auth:
 *  • user, isAuthenticated, isLoading   (from zustand)
 *  • login(), register(), logout()      (from zustand)
 *  • isAdmin                            (derived)
 *
 * Also kicks off fetchUser() on first mount via an
 * initialisation effect in the AuthProvider.
 * ────────────────────────────────────────────────────────── */

"use client";

import { useAuthStore } from "@/stores/auth-store";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);
  const logout = useAuthStore((s) => s.logout);
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const setUser = useAuthStore((s) => s.setUser);

  const isAdmin = user?.role === "admin";

  return {
    user,
    isAuthenticated,
    isLoading,
    isAdmin,
    login,
    register,
    logout,
    fetchUser,
    setUser,
  };
}
