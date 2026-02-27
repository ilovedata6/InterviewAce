/* ──────────────────────────────────────────────────────────
 * E2E — Resume flow
 * upload resume → view analysis
 *
 * NOTE: Requires running backend with database.
 * ────────────────────────────────────────────────────────── */
import { test, expect } from "@playwright/test";

test.describe("Resume Flow", () => {
  test("should redirect to login when accessing resumes unauthenticated", async ({ page }) => {
    await page.goto("/resumes");
    await expect(page).toHaveURL(/\/login/);
  });

  test("should show resume page when authenticated", async ({ page }) => {
    // This test requires authentication cookies.
    // In a full CI setup, use storageState from a login fixture.
    test.skip(true, "Requires authenticated session");

    await page.goto("/resumes");
    await expect(page.getByText(/resume/i)).toBeVisible();
  });
});
