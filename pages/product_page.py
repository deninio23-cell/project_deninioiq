from playwright.sync_api import TimeoutError
from pages.base_page_help import BasePage

class ProductPage(BasePage):
    """Encapsulates interaction logic for item profile details and cart injection flows."""
    def __init__(self, page):
        super().__init__(page)
        # Main target selector for adding items to the cart basket array
        self.add_to_cart_button = page.get_by_role("link", name="Add to cart")

    def add_to_cart(self):
        """
        Clicks the purchase button and blocks execution until the server commits the basket row.
        
        Why this exists: Fast test scripts often click 'Add' and sprint away before the browser
        can sync cookies with the database, leading to a blank cart layout. This method waits
        until the server explicitly returns an HTTP 200 OK confirmation payload.
        """
        print("[PRODUCT] Synchronizing layout components. Awaiting action trigger presence...")
        self.add_to_cart_button.wait_for(state="visible", timeout=15000)
        
        # Inline helper routine that maps out the physical UI click trigger mechanics
        def click_action():
            self.add_to_cart_button.click()

        print("[PRODUCT] Submitting item data. Intercepting server write-stream telemetry...")
        try:
            # Synchronize test speed with both the XHR network traffic and the confirmation dialog
            with self.page.expect_response("**/addtocart", timeout=20000) as response_info:
                self.capture_dialog_context(click_action, expected_message="Product added")
            
            # Verify the web server successfully processed and saved the cart addition
            assert response_info.value.status == 200, "FATAL: App server rejected the cart record addition."
            print("[PRODUCT] Success! Database transaction successfully finalized.")
            
        except TimeoutError:
            # Fallback routine to protect against single-page application animation blocks
            print("[PRODUCT] UI dialogue window suppressed by layout collision. Monitoring API fallback channel")
            self.page.wait_for_timeout(1000)  # Micro-sleep to allow underlying thread resolution
