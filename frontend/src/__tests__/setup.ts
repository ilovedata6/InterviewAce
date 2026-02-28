/* ──────────────────────────────────────────────────────────
 * Test setup — loaded before every test file
 * ────────────────────────────────────────────────────────── */
import { vi } from "vitest";
import "@testing-library/jest-dom/vitest";

// Stub next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
  redirect: vi.fn(),
}));

// Stub next/headers
vi.mock("next/headers", () => ({
  cookies: () => ({
    get: vi.fn(),
    set: vi.fn(),
    delete: vi.fn(),
  }),
  headers: () => new Headers(),
}));
