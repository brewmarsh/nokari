import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Increase the default timeout
    page.set_default_timeout(10000)

    def handle_dialog(dialog):
        print(f"Dialog message: {dialog.message}")
        dialog.accept()

    page.on("dialog", handle_dialog)

    try:
        # Register a new user
        page.goto("http://localhost:5173/register")
        page.get_by_placeholder("Email").fill("testuser@example.com")
        page.get_by_role("textbox", name="Password", exact=True).fill("password123")
        page.get_by_placeholder("Confirm Password").fill("password123")
        page.get_by_role("button", name="Register").click()

        # Log in
        expect(page).to_have_url(re.compile(".*login"))
        page.get_by_placeholder("Email").fill("testuser@example.com")
        page.get_by_placeholder("Password").fill("password123")
        page.get_by_role("button", name="Login").click()

        # Verify dashboard and navigation
        expect(page).to_have_url(re.compile(".*dashboard"))
        expect(page.get_by_role("link", name="Dashboard")).to_be_visible()
        expect(page.get_by_role("button")).to_be_visible() # Profile icon button

        # Go to jobs page and verify changes
        page.goto("http://localhost:5173/dashboard") # jobs are on the dashboard

        # Wait for job cards to load
        expect(page.locator(".job-card").first).to_be_visible()

        # Verify first job card
        first_job_card = page.locator(".job-card").first
        expect(first_job_card.locator(".pin-icon")).to_be_visible()
        expect(first_job_card.locator(".action-menu")).to_be_visible()
        expect(first_job_card.locator("span").filter(has_text=re.compile(r'remote|hybrid|onsite', re.IGNORECASE))).to_be_visible()


        # Take a screenshot of the jobs page
        page.screenshot(path="jules-scratch/verification/jobs_page.png")

        # Go to settings page and verify
        page.get_by_role("button").click() # Open profile dropdown
        page.get_by_role("link", name="Settings").click()
        expect(page).to_have_url(re.compile(".*settings"))

        page.get_by_label("Preferred Work Arrangement").select_option("hybrid")
        page.get_by_role("button", name="Save Settings").click()
        expect(page.get_by_text("Your settings have been saved.")).to_be_visible()

        # Take a screenshot of the settings page
        page.screenshot(path="jules-scratch/verification/settings_page.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
