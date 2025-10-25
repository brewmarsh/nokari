import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # The frontend is now running on port 30000
        time.sleep(5) # Add a delay to wait for the server to start
        page.goto("http://localhost:30000")
        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

if __name__ == "__main__":
    run()
