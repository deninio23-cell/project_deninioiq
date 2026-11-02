
from pages.base_page_help import BasePage

class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        #these are the selectors used to map demoblaze website
        self.signup_nav = page.locator("#signin2")
        self.signup_username = page.locator("#sign-username")
        self.signup_password = page.locator("#sign-password")

        # css celector to ignore text labels and find the exact button that triggers register
        self.signup_button = page.locator("button[onclick='register()']")
        # this will target the close button specifically belonging to the sign in modal
        self.signup_close_button = page.locator("#signInModal bootstrap-modal-footer, button:has-text('Close')").first
        self.cart_nav = page.locator("#cartur")

    def go_to_home_grid(self):
        """Reusable method to return to the home screen and wait for the grid container to load."""
        self.page.get_by_role("link", name="Home").click()
        self.page.locator("#tbodyid").wait_for(state="attached", timeout=5000)

    def navigate_to_signup(self):
        self.signup_nav.click()
        self.signup_username.wait_for(state="visible")

    def register_user(self, username, password):

        self.signup_username.fill(username)
        self.signup_password.fill(password)
        self.handle_next_alert("Sign up successful.")
        self.signup_button.click()
            
        self.signup_username.wait_for(state="hidden")

    def click_category(self, category_name: str):
        """Clicks a sidebar category and waits for the product grid content to attach cleanly."""
        name_lower = category_name.lower()
        
        # Maps variations like 'monitor' or 'monitors' to the website's plural label
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
        self.page.locator("#tbodyid").wait_for(state="attached", timeout=5000)

    def click_product(self, product_name: str):
        """Clicks on a specific product link from the grid layout."""
        self.page.get_by_role("link",  name = product_name ).first.click()
        self.page.wait_for_load_state("domcontentloaded")

        
        