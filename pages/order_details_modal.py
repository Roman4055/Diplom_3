from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class OrderDetailsModal(BasePage):
    # --- Локаторы модального окна ---
    MODAL_CONTAINER = (By.CSS_SELECTOR, "section[class*='Modal_modal_opened']")
    BTN_CLOSE = (By.CSS_SELECTOR, "button[class*='Modal_modal_close_modified']")
    TITLE = (By.CSS_SELECTOR, "h2[class*='Modal_modal_title']")

    # --- Методы проверки состояния ---
    def is_open(self):
        return self.is_element_visible(self.MODAL_CONTAINER)

    def is_closed(self):
        return self.is_element_invisible(self.MODAL_CONTAINER)

    # --- Методы действий ---
    def close(self):
        self.click_element(self.BTN_CLOSE)
        self.is_closed()

    def get_title(self):
        return self.get_text(self.TITLE)
