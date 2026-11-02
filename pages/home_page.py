from playwright.sync_api import expect
from pages.base_page_help import BasePage

class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Selectors used to map demoblaze website layout
        self.signup_nav = page.locator("#signin2")
        self.signup_username = page.locator("#sign-username")
        self.signup_password = page.locator("#sign-password")

        self.login_nav = page.locator("#login2")
        self.login_username = page.locator("#loginusername")
        self.login_password = page.locator("#loginpassword")
        self.login_button = page.locator("button[onclick='logIn()']")
        self.welcome_user_text = page.locator("#nameofuser")

        # CSS selector to find the exact button that triggers register
        self.signup_button = page.locator("button[onclick='register()']")
        # Targets the close button specifically belonging to the sign in modal
        self.signup_close_button = page.locator("#signInModal bootstrap-modal-footer, button:has-text('Close')").first
        self.cart_nav = page.locator("#cartur")

    def login_user(self, username, password):
        """Navigates through the login modal and verifies the welcome token displays securely."""
        self.login_nav.click()
        self.login_username.wait_for(state="visible")
        self.login_username.fill(username)
        self.login_password.fill(password)
        self.login_button.click()
    
        # Wait for the top navbar text area container to render visibly
        self.welcome_user_text.wait_for(state="visible", timeout=5000)
        expect(self.welcome_user_text).to_contain_text(username, timeout=5000)

    def go_to_home_grid(self):
        """Reusable method to return to the home screen and wait for the marketplace database to load."""
        home_link = self.page.get_by_role("link", name="Home")
        
        # API Network Sync: Wait for the main database catalog entries to fully load
        with self.page.expect_response("**/entries", timeout=5000):
            home_link.click()
            
        self.page.locator("#tbodyid").wait_for(state="visible", timeout=5000)
        self.page.wait_for_timeout(500)

    def navigate_to_signup(self):
        self.signup_nav.click()
        self.signup_username.wait_for(state="visible")

    def register_user(self, username, password):
        """Fills and submits user registration, self-healing the state if the user already exists."""
        self.signup_username.fill(username)
        self.signup_password.fill(password)
        self.handle_next_alert("Sign up successful.")
        self.signup_button.click()

        try:
            self.signup_username.wait_for(state="hidden", timeout=3000)
        except Exception:
            print(f"\n[INFO] Registration modal stuck active for '{username}'. Handling self-healing close action.")
            self.page.evaluate("""() => {
                const closeBtn = document.querySelector('#signInModal .modal-footer button') || 
                                 document.querySelector('#signInModal .modal-header .close');
                if (closeBtn) closeBtn.click();
            }""")
            self.signup_username.wait_for(state="hidden", timeout=3000)

    def click_category(self, category_name: str):
        """Clicks a sidebar category and waits directly for the backend category API payload response."""
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
        
        # API Network Sync: Freeze execution until the database categories request endpoint clears
        with self.page.expect_response("**/bycat", timeout=5000):
            category_link.click()
        
        # Allow a split second for the browser rendering engine to paint the new items to the view canvas
        self.page.wait_for_timeout(500)

    def click_product(self, product_name: str):
        """Clicks on a specific product link from the grid layout safely."""
        product_link = self.page.get_by_role("link", name=product_name).first
        product_link.wait_for(state="visible", timeout=5000)
        product_link.click()
        self.page.wait_for_load_state("domcontentloaded")
