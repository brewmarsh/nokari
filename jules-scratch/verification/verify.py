from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the register page
        page.goto("http://localhost:3000/register")

        # Fill in the registration form
        page.get_by_placeholder("Email").fill("test@test.com")
        page.get_by_placeholder("Password").first.fill("password")
        page.get_by_placeholder("Confirm Password").fill("password")

        # Click the register button
        page.get_by_role("button", name="Register").click()

        # Wait for navigation to the login page
        page.wait_for_url("http://localhost:3000/login")

        # Fill in the login form
        page.get_by_placeholder("Email").fill("test@test.com")
        page.get_by_placeholder("Password").fill("password")

        # Click the login button
        page.get_by_role("button", name="Login").click()

        # Wait for the dashboard to load
        page.wait_for_url("http://localhost:3000/dashboard")
        page.wait_for_selector('.jobs-container')

        # Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")

        browser.close()

if __name__ == "__main__":
    run()
