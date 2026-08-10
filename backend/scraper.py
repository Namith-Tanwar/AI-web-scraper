from playwright.sync_api import sync_playwright


def scrape_page(url, max_scrolls=15):
    """
    Launches a headless Chromium browser, navigates to `url`, and
    incrementally scrolls to trigger lazy-loaded content, then returns
    the fully rendered HTML.

    max_scrolls caps how many scroll iterations we attempt so that
    infinite-scroll pages (feeds, listings) can't hang the request
    forever.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        try:
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                permissions=["geolocation"],
                geolocation={"latitude": 28.6139, "longitude": 77.2090},
            )

            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            page.wait_for_timeout(3000)

            previous_height = page.evaluate("document.body.scrollHeight")

            for _ in range(max_scrolls):
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(1200)

                new_height = page.evaluate("document.body.scrollHeight")

                if new_height == previous_height:
                    break

                previous_height = new_height

            html_cont = page.content()
            return html_cont

        finally:
            browser.close()
