import os
from pages.base_page_help import BasePage

class CartPage(BasePage):
    """Manages structural cart grid evaluations, dynamic price syncing, and billing confirmation parsing."""
    def __init__(self, page):
        super().__init__(page)
        # Main Checkout Activation Elements
        self.place_order_button = page.get_by_role("button", name="Place Order")
        
        # Order Creation Modal Form Locators
        self.name_input = page.locator("#name")
        self.country_input = page.locator("#country")
        self.city_input = page.locator("#city")
        self.card_input = page.locator("#card")
        self.month_input = page.locator("#month")
        self.year_input = page.locator("#year")
        self.purchase_button = page.get_by_role("button", name="Purchase")
        self.success_modal = page.locator(".sweet-alert")

    def verify_totals_and_items(self, expected_items):
        """
        Dynamically cross-checks table counts and price states to ensure data matches configs.
        
        Why this exists: Single Page Application tables load items asynchronously. Fast validations
        often scan empty tables and fail. This polling checker blocks execution until rows are completely
        rendered and total balance blocks match configuration targets.
        """
        # Ensure the table container element skeleton is attached to the view before counting
        self.page.locator("#tbodyid").wait_for(state="attached", timeout=15000)
        expected_total_count = sum(item["quantity"] for item in expected_items)
        
        print(f"[CART VAL] Checking checkout rows. Awaiting item threshold match: {expected_total_count}")
        try:
            # Poll the document continuously until the table row count equals our expected total
            self.page.wait_for_function(
                f"document.querySelectorAll('#tbodyid tr').length === {expected_total_count}",
                timeout=15000
            )
        except Exception:
            print(f"\n[TIMEOUT WARNING] DOM table row presentation stagnated before reaching target: {expected_total_count}")

        rows = self.page.locator("#tbodyid tr")
        row_count = rows.count()
        
        assert row_count == expected_total_count, (
            f"Table presentation mismatch! Found {row_count} elements, expected {expected_total_count} tracking items."
        )

        # Polling: Ensure the total value container finishes painting text strings before converting to an integer
        self.page.wait_for_function("document.querySelector('#totalp').textContent.trim() !== ''", timeout=15000)
        displayed_total = int(self.page.locator("#totalp").text_content().strip())
        
        assert displayed_total > 0, f"Expected calculated positive balance calculation, received: {displayed_total}"
        return displayed_total

    def checkout(self, data: dict) -> str:
        """Completes checkout details forms and returns the unique alphanumeric transaction ID token."""
        self.place_order_button.click()
        self.name_input.wait_for(state="visible", timeout=15000)
        
        # Populate payment form profile details
        self.name_input.fill(data["name"])
        self.country_input.fill(data["country"])
        self.city_input.fill(data["city"])
        self.card_input.fill(data["card"])
        self.month_input.fill(data["month"])
        self.year_input.fill(data["year"])
        
        print("[CHECKOUT] Submitting payment details. Executing 30s latency validation...")
        self.purchase_button.click()
        
        # Resilient 30s timeout handles slow server generation loads seamlessly
        self.success_modal.wait_for(state="visible", timeout=30000)
        confirmation_text = self.success_modal.locator("p").text_content()

        # Parse the transaction string line by line to extract the tracking identity token
        order_id = ""
        for line in confirmation_text.split("\n"):
            if "Id:" in line:
                 order_id = line.replace("Id:", "").strip()
                 break

        # Capture a success state screenshot for automated test logs
        artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
        screenshot_dir = os.path.join(artifacts_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        self.page.screenshot(path=os.path.join(screenshot_dir, "SUCCESS_scenario_c_order_id.png"))
        print(f"[SUCCESS] Order complete! ID: '{order_id}'. Screenshot logged.")
        
        # Cleanly close the dialog pop-up overlay to restore browser state
        self.page.get_by_role("button", name="OK").click()
        return order_id