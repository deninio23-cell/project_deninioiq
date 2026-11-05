import os
import uuid
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.cart_workflows import CartWorkflows

# =============================================================================
# Scenario A: Account Creation (Isolated Atomic Test)
# =============================================================================
def test_demoblaze_account_creation(browser_context, test_data):
    """Verifies that a unique account can be generated through the sign-up modal interface."""
    page = browser_context
    page.goto(test_data["base_url"])
    
    home_page = HomePage(page)
    home_page.navigate_to_signup()

    # Generate a completely unique runtime username identity token
    unique_username = f"IQB_User_{uuid.uuid4().hex[:8]}"
    home_page.register_user(unique_username, test_data["login_credentials"]["password"])


# =============================================================================
# Scenario B: Populating Cart (Data-Driven Loop)
# =============================================================================
def test_demoblaze_cart_checkout(browser_context, test_data):
    """Validates data-driven product selection and dynamic checkout grid totals syncing."""
    page = browser_context
    page.goto(test_data["base_url"])

    home_page = HomePage(page)
    cart_page = CartPage(page)

    # 1. Establish an authenticated session using the Adaptive Failover Authentication Engine
    CartWorkflows.prepare_authenticated_user_session(page, test_data)

    # 2. Execute the data-driven shopping loop across dynamic categories
    CartWorkflows.populate_cart_from_json(page, test_data)
    
    # Navigate to the shopping basket view layout
    home_page.cart_nav.click()

    # Verify that the asynchronous polling table compiler successfully syncs and returns price states
    calculated_total = cart_page.verify_totals_and_items(test_data["cart_items"])
    assert calculated_total > 0, "Validation Failure: Cart calculated totals display an empty or negative balance state."

    # Save an a screenshot representing successful total 
    artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
    screenshot_dir = os.path.join(artifacts_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    page.screenshot(path=os.path.join(screenshot_dir, "SUCCESS_scenario_b_cart_totals.png"))
    print("\n[SUCCESS] Scenario B validation screenshot saved to disk.")


# =============================================================================
# Scenario C: Finalising Payment
# =============================================================================
def test_demoblaze_finalising_payment(browser_context, test_data):
    """Validates end-to-end checkout processing, payment forms submission, and receipt token generation."""
    page = browser_context
    page.goto(test_data["base_url"])

    home_page = HomePage(page)
    cart_page = CartPage(page)

    # 1. Establish an authenticated session using the Adaptive Failover Authentication Engine
    CartWorkflows.prepare_authenticated_user_session(page, test_data)

    # 2. Execute the data-driven shopping loop across dynamic categories
    CartWorkflows.populate_cart_from_json(page, test_data)
    
    # 3. Route to basket, evaluate metrics stability, and finalize order profile forms
    home_page.cart_nav.click()
    cart_page.verify_totals_and_items(test_data["cart_items"])

    # Submit billing payload metadata sheet and extract structural order ID strings
    order_id = cart_page.checkout(test_data["checkout_details"])
    
    print(f"\n[SUCCESS] Regression Run Complete. Generated Unique Order ID: {order_id}")
    assert len(order_id) > 0, "Validation Failure: Platform confirmation modal returned an empty receipt confirmation token."
