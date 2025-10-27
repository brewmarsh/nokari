import time
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Mock the Cognito sign-up call
        page.route(
            "**/api/register/",
            lambda route: route.fulfill(
                status=201,
                content_type="application/json",
                body='{"message": "User registered successfully."}',
            ),
        )

        time.sleep(5) # Wait for servers to start
        page.goto("http://localhost:30000/register")

        # Fill out the registration form
        page.get_by_placeholder("Email").first.fill("test@example.com")
        page.get_by_placeholder("Password").first.fill("password123")
        page.get_by_placeholder("Confirm Password").fill("password123")

        # Submit the form
        page.get_by_role("button", name="Register").click()

        # Verify that the registration was successful
        # The frontend should redirect to the login page
        expect(page).to_have_url("http://localhost:30000/login")

        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

if __name__ == "__main__":
    run()
