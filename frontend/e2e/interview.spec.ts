/* ──────────────────────────────────────────────────────────
 * E2E — Interview flow
 * start interview → answer → summary
 *
 * NOTE: Requires running backend with database.
 * ────────────────────────────────────────────────────────── */
import { test, expect } from "@playwright/test";

test.describe("Interview Flow", () => {
  test("should redirect to login when accessing interview unauthenticated", async ({ page }) => {
    await page.goto("/interview");
    await expect(page).toHaveURL(/\/login/);
  });

  test("should show interview page when authenticated", async ({ page }) => {
    test.skip(true, "Requires authenticated session");

    await page.goto("/interview");
    await expect(page.getByText(/interview/i)).toBeVisible();
  });

  test("should show interview history when authenticated", async ({ page }) => {
    test.skip(true, "Requires authenticated session");

    await page.goto("/interview/history");
    await expect(page.getByText(/history/i)).toBeVisible();
  });
});
