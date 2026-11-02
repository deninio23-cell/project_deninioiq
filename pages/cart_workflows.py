import time
import uuid
from pages.home_page import HomePage
from pages.product_page import ProductPage

class CartWorkflows:
    @staticmethod
    def prepare_authenticated_user_session(page, test_data):
        """Generates a completely unique runtime profile to guarantee an isolated, empty cart state."""
        home_page = HomePage(page)
        
        unique_id = f"IQB_User_{uuid.uuid4().hex[:6]}"
        password = test_data["login_credentials"]["password"]
        
        home_page.navigate_to_signup()
        home_page.register_user(unique_id, password)
        page.wait_for_timeout(1000)
        
        home_page.login_user(unique_id, password)
        
        page.reload()
        home_page.go_to_home_grid()
        print(f"\n[ISOLATION] Provisioned fresh test context session user account: {unique_id}")

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
                        page.wait_for_timeout(1500)

                assert product_link.is_visible(), (
                    f"CRITICAL TEST FAILURE: Request item '{item['name']}' in category "
                    f"'{item['category']}' could not be located on the platform view grid!"
                )

                home_page.click_product(item["name"])
                product_page.add_to_cart()
                
                # CRITICAL STABILIZATION PAUSE:
                # Forces the browser execution thread to wait until Demoblaze completely commits 
                # the product record into its backend DB session tables before navigating home.
                page.wait_for_timeout(2000)
