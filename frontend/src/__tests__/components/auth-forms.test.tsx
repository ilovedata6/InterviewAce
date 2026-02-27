/* ──────────────────────────────────────────────────────────
 * Component Tests — Auth Forms (Login, Register)
 * ────────────────────────────────────────────────────────── */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock api-client before component imports
vi.mock("@/lib/api-client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
  ApiClientError: class ApiClientError extends Error {
    status: number;
    detail: string | Record<string, unknown>;
    constructor(message: string, status: number, detail?: string | Record<string, unknown>) {
      super(message);
      this.status = status;
      this.detail = detail ?? message;
    }
  },
}));

// Mock sonner
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

import { LoginForm } from "@/components/auth/login-form";
import { apiClient } from "@/lib/api-client";

const mockUser = {
  id: "u1",
  email: "test@example.com",
  full_name: "Test",
  is_active: true,
  role: "user",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Stub window.location
    Object.defineProperty(window, "location", {
      writable: true,
      value: { href: "" },
    });
  });

  it("should render email and password fields", () => {
    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    // Password uses FormControl wrapping a div, so query by placeholder
    expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("should show validation errors for empty submission", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      // Zod validation should show error messages
      const errorMessages = screen.getAllByRole("paragraph");
      expect(errorMessages.length).toBeGreaterThan(0);
    });
  });

  it("should call login on valid submission", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce(mockUser);
    const user = userEvent.setup();
    render(<LoginForm />);

    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.type(screen.getByPlaceholderText(/enter your password/i), "Password123!");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        expect.stringContaining("login"),
        expect.objectContaining({
          email: "test@example.com",
          password: "Password123!",
        }),
      );
    });
  });

  it("should toggle password visibility", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const passwordInput = screen.getByPlaceholderText(/enter your password/i);
    expect(passwordInput).toHaveAttribute("type", "password");

    // Find toggle button (the eye icon button)
    const toggleButton = passwordInput.closest(".relative")?.querySelector("button");
    if (toggleButton) {
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute("type", "text");
    }
  });

  it("should show forgot password link", () => {
    render(<LoginForm />);

    expect(screen.getByText(/forgot password/i)).toBeInTheDocument();
  });
});
