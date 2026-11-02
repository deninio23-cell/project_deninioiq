import os
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def handle_next_alert(self, expected_message: str):
        """Listens for the next alert, pauses briefly so it's visible, and accepts it."""
        def alert_handler(dialog):
            assert expected_message in dialog.message
            

            if expected_message == "Sign up successful.":
                self.page.wait_for_timeout(2000)
                    

            dialog.accept()

        self.page.once("dialog", alert_handler)

