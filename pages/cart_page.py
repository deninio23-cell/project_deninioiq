import os
from pages.base_page_help import BasePage

class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Fixed syntax to use correct Python keyword arguments
        self.place_order_button = page.get_by_role("button", name="Place Order")
        
        # Place order modal selectors
        self.name_input = page.locator("#name")
        self.country_input = page.locator("#country")
        self.city_input = page.locator("#city")
        self.card_input = page.locator("#card")
        self.month_input = page.locator("#month")
        self.year_input = page.locator("#year")
        self.purchase_button = page.get_by_role("button", name="Purchase")
        self.success_modal = page.locator(".sweet-alert")

    def verify_totals_and_items(self, expected_items):
        """Dynamic validation that calculates cumulative cost based on items explicitly listed in cart."""
        self.page.wait_for_selector("#tbodyid tr", state="attached")
        
        # Calculate the absolute exact quantity of items we defined in our config
        expected_total_count = sum(item["quantity"] for item in expected_items)
        
        # CRITICAL ATOMIC PAUSE LOGIC:
        # Replaces raw .count() with a dynamic browser evaluation statement that polls 
        # until the rows count matches our JSON payload specifications (up to 5 seconds).
        try:
            self.page.wait_for_function(
                f"document.querySelectorAll('#tbodyid tr').length === {expected_total_count}",
                timeout=5000
            )
        except Exception:
            # Fallback error mapping descriptive print logs if threshold breaks
            print(f"\n[TIMEOUT] Expected {expected_total_count} items, but DOM row count stalled.")

        rows = self.page.locator("#tbodyid tr")
        row_count = rows.count()
        
        # Assert structural balance boundaries to stop false positives dead in their tracks
        assert row_count == expected_total_count, (
            f"Cart layout count mismatch! Found {row_count} rows in table UI, "
            f"but expected {expected_total_count} tracking items."
        )

        self.page.wait_for_function("document.querySelector('#totalp').textContent.trim() !== ''", timeout=5000)
        displayed_total = int(self.page.locator("#totalp").text_content().strip())
        assert displayed_total > 0, f"Expected calculated positive balance total, found: {displayed_total}"
        return displayed_total

    def checkout(self, data: dict) -> str:
        """Fills checkout billing details and extracts the confirmation order ID string token."""
        self.place_order_button.click()
        self.name_input.wait_for(state="visible")
        
        self.name_input.fill(data["name"])
        self.country_input.fill(data["country"])
        self.city_input.fill(data["city"])
        self.card_input.fill(data["card"])
        self.month_input.fill(data["month"])
        self.year_input.fill(data["year"])
        
        self.purchase_button.click()
        self.success_modal.wait_for(state="visible", timeout=5000)
        
        # Parse out unique Order ID details text block
        confirmation_text = self.success_modal.locator("p").text_content()

        order_id = ""
        for line in confirmation_text.split("\n"):
            if "Id:" in line:
                 order_id = line.replace("Id:", "").strip()
                 break

        screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        self.page.screenshot(path=os.path.join(screenshot_dir, "SUCCESS_scenario_c_order_id.png"))
        print("\n[SUCCESS] Scenario C confirmation screenshot saved to disk.")
        
        # Final confirmation action
        self.page.get_by_role("button", name="OK").click()
        return order_id
