from playwright.sync_api import Page, TimeoutError

class BasePage:
    """
    Core framework foundation class. All Page Object Models (POM) extend this base class
    to share low-level page interaction mechanics and unified dialog intercept engines.
    """
    def __init__(self, page: Page):
        """Initializes the base class with the active browser tab reference."""
        self.page = page

    def capture_dialog_context(self, trigger_action, expected_message: str = None, timeout: float = 15000):
       
        try:
            # Set up the event-driven listener to await the dialog event
            with self.page.expect_event("dialog", timeout=timeout) as dialog_info:
                trigger_action()  # Execute the UI interaction (e.g., clicking a button)
                
            dialog = dialog_info.value
            print(f"\n[ALERT INTERCEPT] Captured browser pop-up message: '{dialog.message}'")
            
            # Matcher that verifies if the website gave us the notification text we expected
            if expected_message and expected_message not in dialog.message:
                print(f"[MUTATION WARNING] Message mismatch! Expected text: '{expected_message}', but site showed: '{dialog.message}'")
                
            # Accept (clicks 'OK') on the native pop-up immediately to clear the UI viewport
            dialog.accept()
            return dialog.message
            
        except TimeoutError:
            # Handles edge cases where network lag prevents the alert from firing in time
            print(f"\n[ENGINE FATAL] Failure footprint: No dialog appeared within the {timeout}ms window constraint.")
            raise
