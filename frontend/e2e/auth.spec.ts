/* ──────────────────────────────────────────────────────────
 * E2E — Auth flow
 * register → verify → login → dashboard
 *
 * NOTE: These tests require the full backend stack running.
 * They are designed to be run manually or in a CI pipeline
 * with proper backend setup. Without a running backend they
 * will naturally fail on API calls.
 * ────────────────────────────────────────────────────────── */
import { test, expect } from "@playwright/test";

test.describe("Auth Flow", () => {
  test("should show login page", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByText("Welcome Back")).toBeVisible();
    await expect(page.getByPlaceholder("you@example.com")).toBeVisible();
    await expect(page.getByPlaceholder("Enter your password")).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("should show register page", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByText("Create Account")).toBeVisible();
    await expect(page.getByPlaceholder("you@example.com")).toBeVisible();
  });

  test("should navigate from login to register", async ({ page }) => {
    await page.goto("/login");
    await page.getByText("Sign up").click();
    await expect(page).toHaveURL(/\/register/);
  });

  test("should navigate from login to forgot password", async ({ page }) => {
    await page.goto("/login");
    await page.getByText("Forgot password?").click();
    await expect(page).toHaveURL(/\/forgot-password/);
  });

  test("should show validation errors on empty login submit", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: /sign in/i }).click();

    // Should show validation error messages
    await expect(page.locator("[data-slot='form-message']").first()).toBeVisible();
  });

  test("should redirect unauthenticated users to login", async ({ page }) => {
    await page.goto("/dashboard");
    // Middleware should redirect to /login
    await expect(page).toHaveURL(/\/login/);
  });
});
