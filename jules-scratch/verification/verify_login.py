import time

from playwright.sync_api import expect, sync_playwright


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Mock the Cognito sign-in call
        page.route(
            "**/api/login/",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body='{"access": "test_access_token", "refresh": "test_refresh_token"}',
            ),
        )

        time.sleep(5)  # Wait for servers to start
        page.goto("http://localhost:30000/login")

        # Fill out the login form
        page.get_by_placeholder("Email").fill("test@example.com")
        page.get_by_placeholder("Password").fill("password123")

        # Submit the form
        page.get_by_role("button", name="Login").click()

        # Verify that the login was successful
        # The frontend should redirect to the dashboard
        expect(page).to_have_url("http://localhost:30000/dashboard")

        page.screenshot(
            path="jules-scratch/verification/login_verification.png")
        browser.close()


if __name__ == "__main__":
    run()
