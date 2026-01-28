from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": 28.6139, "longitude": 77.2090}
        )

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_timeout(4000)

        previous_height = page.evaluate("document.body.scrollHeight")

        while True:
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)

            new_height = page.evaluate("document.body.scrollHeight")

            if new_height == previous_height:
                break

            previous_height = new_height

        html_cont = page.content()
        browser.close()

        return html_cont
