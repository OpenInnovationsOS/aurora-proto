# agents/tools/web_browse.py
"""
Web Browse Tool — Uses Playwright to browse websites
- Headless by default
- Blocks popups/ad trackers
- Returns HTML/text content
"""

from playwright.sync_api import sync_playwright
import time

class WebBrowseTool:
    name = "web_browse"

    def __init__(self, headless: bool = True):
        self.headless = headless

    def run(self, url: str, max_wait: int = 10) -> Dict[str, Any]:
        """Browse a URL and return content"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()

                # Block ads/popups
                page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

                page.goto(url, timeout=max_wait * 1000)
                page.wait_for_load_state("networkidle", timeout=max_wait * 1000)

                title = page.title()
                content = page.inner_text("body")
                html = page.content()

                browser.close()

                return {
                    "title": title,
                    "content": content[:5000],  # Truncate long content
                    "html": html[:10000],
                    "url": url
                }

        except Exception as e:
            return {"error": str(e)}
