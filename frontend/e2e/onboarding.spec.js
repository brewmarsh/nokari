import { test, expect } from '@playwright/test';

test('first user onboarding', async ({ page }) => {
  // This test needs to run against a clean database, so the user count is 0.
  // We can't guarantee this in the current test environment, so we'll have to assume it's the case.
  // In a real-world scenario, we would have a way to reset the database before each test run.

  // 1. Navigate to the application's root URL.
  await page.goto('/');

  // 2. Should be redirected to the /onboarding page.
  await expect(page).toHaveURL('/onboarding');

  // 3. Fill out the onboarding form with valid details and submit.
  await page.getByPlaceholder('Username').fill('testadmin');
  await page.getByPlaceholder('Email').fill('admin@example.com');
  await page.getByPlaceholder('Password').fill('password123');
  await page.getByRole('button', { name: 'Create Admin User' }).click();

  // 4. Should be redirected to the /dashboard.
  await expect(page).toHaveURL('/dashboard');

  // 5. The new user should have the 'admin' role.
  // We can check for the presence of the "Admin Tools" section.
  await expect(page.getByRole('heading', { name: 'Admin Tools' })).toBeVisible();
});
