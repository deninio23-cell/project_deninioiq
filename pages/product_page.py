from pages.base_page_help import BasePage

class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_to_cart_button = page.get_by_role("link",  name= "Add to cart" )

    def add_to_cart(self):
        self.handle_next_alert("Product added")
        self.add_to_cart_button.click()
        self.page.wait_for_load_state("domcontentloaded")