import time
from pages.home_page import HomePage
from pages.product_page import ProductPage

class CartWorkflows:
    @staticmethod
    def populate_cart_from_json(page, test_data):
        """Reusable workflow method to populate the cart dynamically using JSON data."""
        home_page = HomePage(page)
        product_page = ProductPage(page)
        
        for item in test_data["cart_items"]:
            for _ in range(item["quantity"]):
                home_page.go_to_home_grid()
                home_page.click_category(item["category"])

                page.wait_for_timeout(1000) 

                product_link = page.get_by_role("link", name=item["name"]).first

                if not product_link.is_visible():
                    pagination_next = page.locator("#next2")
                    if pagination_next.is_visible():
                        pagination_next.click()
                        # Allow half a second for the dynamic catalog layout items to paint the UI
                        page.wait_for_timeout(1500)

                assert product_link.is_visible(), (
                    f"CRITICAL TEST FAILURE: Request item '{item['name']}' in category "
                    f"'{item['category']}' could not be located on the platform view grid!"
                )

                home_page.click_product(item["name"])
                product_page.add_to_cart()
                page.wait_for_timeout(1500)