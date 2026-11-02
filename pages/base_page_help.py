import os
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def handle_next_alert(self, expected_message: str):
        """Listens for native platform browser dialog popups and dismisses them instantly."""
        def alert_handler(dialog):
            print(f"\n[ALERT DIALOG INTERCEPTED] System Message: '{dialog.message}'")
            # Dismiss immediately to let the underlying single-page app continue operation
            dialog.accept()

        self.page.once("dialog", alert_handler)

