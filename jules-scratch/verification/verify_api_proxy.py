import time
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Mock the API response
        page.route(
            "**/api/**",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body='{"Hello": "API is working!"}',
            ),
        )

        time.sleep(5) # Wait for servers to start
        page.goto("http://localhost:30000")

        # This is a placeholder for a real test.
        # In a real app, we would look for the result of the API call
        # to be displayed on the page.
        expect(page.locator("body")).to_contain_text("Nokori")

        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

if __name__ == "__main__":
    run()
