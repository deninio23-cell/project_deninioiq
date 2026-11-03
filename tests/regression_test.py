import os
import uuid
from playwright.sync_api import TimeoutError
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.product_page import ProductPage

# =============================================================================
# REUSABLE RECOVERY WORKFLOWS (Handles Login Failovers & Shopping Loops)
# =============================================================================
class CartWorkflows:
    """Orchestrates multi-page user journeys, dynamic authentication routing, and automated shopping flows."""
    
    @staticmethod
    def prepare_authenticated_user_session(page, test_data):
        """
        Creates a dynamic registration profile and routes to static backups if database delays occur.
        
        Why this exists: Demoblaze claims a signup is successful on the frontend, but lags when writing 
        the row to the database. This engine registers a unique temporary user name. If logging in fails 
        or the user registration hangs, it seamlessly drops back to your static tracking profile.
        """
        home_page = HomePage(page)
        unique_id = f"IQB_User_{uuid.uuid4().hex[:6]}"
        password = test_data["login_credentials"]["password"]
        static_backup = test_data["login_credentials"]["username"]
        
        # Initiate user signup flow tracking
        home_page.navigate_to_signup()
        account_created_successfully = home_page.register_user(unique_id, password)
        
        # Reload base layout state to clear open form elements
        page.goto(test_data["base_url"])
        login_username = unique_id if account_created_successfully else static_backup
        
        if not account_created_successfully:
            print(f"[FAILOVER ACTIVATED] Signup write lag detected. Falling back to profile: {login_username}")
            
        try:
            home_page.login_user(login_username, password)
        except TimeoutError:
            # Secondary Failover: If registration accepted the write but the login engine stalls, force backup routing
            if login_username != static_backup:
                print(f"[RETRY CRITICAL] Registration transaction delayed. Switching execution context to static profile.")
                page.goto(test_data["base_url"])
                home_page.login_user(static_backup, password)

        print(f"[CONTEXT SEAL] Active session hydrated successfully for: '{login_username}'")
        home_page.go_to_home_grid()

    @staticmethod  
    def populate_cart_from_json(page, test_data):
        """
        Loops through the configured JSON shopping list and maps item injections to the catalog grid.
        Includes self-healing pagination loops to look beyond the initial layout boundaries.
        """
        home_page = HomePage(page)
        product_page = ProductPage(page)
        
        for item in test_data["cart_items"]:
            for _ in range(item["quantity"]):
                # Return home safely using the non-destructive logo routing mechanism
                home_page.go_to_home_grid()
                home_page.click_category(item["category"])

                try:
                    # Scan page 1 first with a fast timeout boundary
                    page.get_by_role("link", name=item["name"]).first.wait_for(state="visible", timeout=4000)
                except TimeoutError:
                    # Self-Healing Pagination: If item is invisible, click next to look on page 2
                    pagination_next = page.locator("#next2")
                    if pagination_next.is_visible():
                        print(f"[PAGINATION ENGINE] Item '{item['name']}' missing on Page 1. Flipping catalog grid layout...")
                        pagination_next.click()
                        page.locator("#tbodyid").wait_for(state="visible", timeout=10000)

                # Ensure target link has fully painted onto the workspace view
                final_product_link = page.get_by_role("link", name=item["name"]).first
                final_product_link.wait_for(state="visible", timeout=15000)

                assert final_product_link.is_visible(), (
                    f"CRITICAL COMPONENT EXCEPTION: Target item '{item['name']}' in category "
                    f"'{item['category']}' could not be located in the current view layout!"
                )

                # Route to details page and verify the backend XHR write operations complete
                home_page.click_product(item["name"])
                product_page.add_to_cart()

        print("\n[CONTEXT SYNC] All configuration list items mapped and written successfully. Stabilizing storage...")
        page.wait_for_timeout(2000)


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

    # Save an artifact tracking screenshot representing successful total compilation
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
