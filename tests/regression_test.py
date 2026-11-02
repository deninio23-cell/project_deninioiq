import uuid
import os
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.cart_workflows import CartWorkflows


def test_demoblaze_account_creation(browser_context, test_data):
    page = browser_context
    page.goto(test_data["base_url"])
    
    home_page = HomePage(page)
    home_page.navigate_to_signup()

    # Generates completely unique runtime credentials to bypass "User already exists" failures
    unique_username = f"IQB_User_{uuid.uuid4().hex[:8]}"
    home_page.register_user(unique_username, "SecurePass123!")

    # -------------------------------------------------------------
    # Scenario B: Populating Cart (Data-Driven Loop)
    # -------------------------------------------------------------

def test_demoblaze_cart_checkout(browser_context, test_data):
    page = browser_context
    page.goto(test_data["base_url"])

    home_page = HomePage(page)
    cart_page = CartPage(page)

    CartWorkflows.populate_cart_from_json(page, test_data)

    # Navigate directly to Cart Page for validation
    home_page.cart_nav.click()

    calculated_total = cart_page.verify_totals_and_items(test_data["cart_items"])
    assert calculated_total > 0, "Cart total value should be calculated and displayed properly"

    screenshot_dir = os.path.join(os.path.dirname(__file__), "..", "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    page.screenshot(path=os.path.join(screenshot_dir, "SUCCESS_scenario_b_cart_totals.png"))
    print("\n[SUCCESS] Scenario B validation screenshot saved to disk.")

    # -------------------------------------------------------------
    # Scenario C: Finalising Payment
    # -------------------------------------------------------------

def test_demoblaze_finalising_payment(browser_context, test_data):

    page = browser_context
    page.goto(test_data["base_url"])

    home_page = HomePage(page)
    cart_page = CartPage(page)

    CartWorkflows.populate_cart_from_json(page, test_data)

    home_page.cart_nav.click()

    cart_page.verify_totals_and_items(test_data["cart_items"])

    order_id = cart_page.checkout(test_data["checkout_details"])
    
    
    print(f"\n[SUCCESS] Regression Run Complete. Generated Unique Order ID: {order_id}")
    assert len(order_id) > 0, "Unique Order ID should be returned from the platform confirmation modal."
