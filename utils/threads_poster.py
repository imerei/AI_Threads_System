from playwright.sync_api import sync_playwright


class ThreadsPoster:
    def post_content(self, text):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Login and posting logic from previous answer
            # ...

            context.close()