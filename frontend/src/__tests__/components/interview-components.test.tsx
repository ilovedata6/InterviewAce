/* ──────────────────────────────────────────────────────────
 * Component Tests — Interview components
 * (InterviewConfig, AnswerInput)
 * ────────────────────────────────────────────────────────── */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock api-client
vi.mock("@/lib/api-client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    del: vi.fn(),
  },
  ApiClientError: class extends Error {
    status: number;
    constructor(m: string, s: number) {
      super(m);
      this.status = s;
    }
  },
}));

// Mock react-query hooks used by InterviewConfig
vi.mock("@/hooks/use-resumes", () => ({
  useResumes: () => ({
    data: {
      items: [
        {
          id: "r1",
          file_name: "resume.pdf",
          status: "analyzed",
          created_at: "2024-01-01",
        },
      ],
      total: 1,
    },
    isLoading: false,
  }),
}));

// Mock sonner
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn() },
}));

import { AnswerInput } from "@/components/interview/answer-input";

describe("AnswerInput", () => {
  const onSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render textarea and submit button", () => {
    render(<AnswerInput onSubmit={onSubmit} />);

    expect(screen.getByPlaceholderText(/type your answer/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /submit answer/i })).toBeInTheDocument();
  });

  it("should disable submit button when textarea is empty", () => {
    render(<AnswerInput onSubmit={onSubmit} />);

    expect(screen.getByRole("button", { name: /submit answer/i })).toBeDisabled();
  });

  it("should enable submit button when text is entered", async () => {
    const user = userEvent.setup();
    render(<AnswerInput onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/type your answer/i), "My answer");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /submit answer/i })).toBeEnabled();
    });
  });

  it("should call onSubmit with answer text", async () => {
    const user = userEvent.setup();
    render(<AnswerInput onSubmit={onSubmit} answerStartTime={Date.now()} />);

    await user.type(
      screen.getByPlaceholderText(/type your answer/i),
      "This is my answer to the question",
    );
    await user.click(screen.getByRole("button", { name: /submit answer/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          answer_text: "This is my answer to the question",
        }),
      );
    });
  });

  it("should show submitting state", () => {
    render(<AnswerInput onSubmit={onSubmit} isSubmitting />);

    expect(screen.getByText(/submitting/i)).toBeInTheDocument();
  });

  it("should display elapsed timer", () => {
    render(<AnswerInput onSubmit={onSubmit} answerStartTime={Date.now()} />);

    // Timer should show 0:00 initially
    expect(screen.getByText("0:00")).toBeInTheDocument();
  });

  it("should show character count", async () => {
    const user = userEvent.setup();
    render(<AnswerInput onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/type your answer/i), "Hello");

    await waitFor(() => {
      expect(screen.getByText(/5 \/ 5000/)).toBeInTheDocument();
    });
  });
});
