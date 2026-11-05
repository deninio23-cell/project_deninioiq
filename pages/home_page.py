from playwright.sync_api import expect
from pages.base_page_help import BasePage

class HomePage(BasePage):
    """Handles core homepage logic, modal authentication flows, and non-destructive navigation routing."""
    def __init__(self, page):
        super().__init__(page)
        # Main Navigation Bar Locators
        self.signup_nav = page.locator("#signin2")
        self.login_nav = page.locator("#login2")
        self.cart_nav = page.locator("#cartur")
        self.welcome_user_text = page.locator("#nameofuser")
        
        # Sign Up Modal Form Field Locators
        self.signup_username = page.locator("#sign-username")
        self.signup_password = page.locator("#sign-password")
        self.signup_button = page.locator("button[onclick='register()']")
        
        # Log In Modal Form Field Locators
        self.login_username = page.locator("#loginusername")
        self.login_password = page.locator("#loginpassword")
        self.login_button = page.locator("button[onclick='logIn()']")

    def navigate_to_signup(self):
        """Clicks the navigation header sign-up action and awaits dialog presentation."""
        self.signup_nav.click()
        self.signup_username.wait_for(state="visible", timeout=5000)

    def register_user(self, username, password):
        """Registers a user profile by awaiting explicit server-side HTTP database write confirmation."""
        self.signup_username.fill(username)
        self.signup_password.fill(password)
        self.signup_button.wait_for(state="visible")
        
        print(f"\n[NETWORK SYNC] Submitting registration for '{username}'...")
        # Intercept both the network transaction and the pop-up event simultaneously
        with self.page.expect_response("**/signup", timeout=15000) as response_info:
            with self.page.expect_event("dialog", timeout=15000) as dialog_info:
                self.signup_button.click()
                
        dialog = dialog_info.value
        print(f"[ALERT INTERCEPT] Registration system response: '{dialog.message}'")
        dialog.accept()
        
        is_successful = response_info.value.status == 200
        
        # Safely shut down the registration modal interface container programmatically
        self.page.evaluate("""() => {
            const closeBtn = document.querySelector('#signInModal .modal-footer button');
            if (closeBtn) closeBtn.click();
        }""")
        self.signup_username.wait_for(state="hidden")
        return is_successful

    def login_user(self, username, password):
        """Authenticates user profile data with session guardrails to protect against race conditions."""
        # Guardrail: If already authenticated to this user profile context, bypass execution to save time
        if self.welcome_user_text.is_visible() and f"Welcome {username}" in (self.welcome_user_text.text_content() or ""):
            print(f"[AUTH GUARDRAIL] Active validation session detected for '{username}'. Skipping login routine.")
            return

        self.login_nav.click()
        self.login_username.wait_for(state="visible", timeout=5000)
        self.login_username.fill(username)
        self.login_password.fill(password)
        
        print(f"[NETWORK SYNC] Deserializing login request stream for: '{username}'")
        with self.page.expect_response("**/login", timeout=15000) as response_info:
            self.login_button.click()
            
        assert response_info.value.status == 200, "CRITICAL ERROR: API engine rejected login credentials."
        self.welcome_user_text.wait_for(state="visible", timeout=15000)
        expect(self.welcome_user_text).to_contain_text(f"Welcome {username}", timeout=15000)

    def go_to_home_grid(self):
        """
        Routes the browser context back to the primary category layout catalog.
        Uses the high-level brand logo text link to avoid clearing active memory session store values.
        """
        # Architectural Fix: Click the logo instead of standard 'Home' nav link to protect cookie arrays
        self.page.get_by_role("link", name="PRODUCT STORE").click()
        self.page.locator("#tbodyid").wait_for(state="visible", timeout=15000)

    def click_category(self, category_name: str):
        """Filters catalog items via sidebar category navigation selectors."""
        name_lower = category_name.lower()
        if "monit" in name_lower or "mont" in name_lower:
            normalized_name = "Monitors"
        elif "phon" in name_lower:
            normalized_name = "Phones"
        elif "lapt" in name_lower:
            normalized_name = "Laptops"
        else:
            normalized_name = category_name

        category_link = self.page.get_by_role("link", name=normalized_name, exact=True)
        category_link.click()
        self.page.locator("#tbodyid").wait_for(state="visible", timeout=5000)

    def click_product(self, product_name: str):
        """Executes a thread-safe navigation link click directly targeting a product listing."""
        product_link = self.page.get_by_role("link", name=product_name).first
        product_link.wait_for(state="visible", timeout=5000)
        product_link.click()
        self.page.wait_for_load_state("domcontentloaded")
