#order_details_modal.py
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage


class OrderDetailsModal(BasePage):
    # Контейнер открытого модального окна
    MODAL_CONTAINER = (By.CSS_SELECTOR, "section[class*='Modal_modal_opened']")

    # Стратегии закрытия: от точной к запасным
    BTN_CLOSE = (By.XPATH, "//button[contains(@class,'Modal_modal_close')]")
    BTN_FIRST_IN_MODAL = (By.XPATH,
        "//section[contains(@class,'Modal_modal_opened')]//button[1]")

    def is_open(self):
        return self.is_element_visible(self.MODAL_CONTAINER)

    def is_closed(self):
        return self.is_element_invisible(self.MODAL_CONTAINER)

    def close(self):
        """Закрывает модалку: сначала крестик по точному классу,
        затем первую кнопку внутри открытой секции, затем Escape."""
        for locator in (self.BTN_CLOSE, self.BTN_FIRST_IN_MODAL):
            try:
                self.click_element(locator)
                return
            except TimeoutException:
                continue
        self.find_element((By.TAG_NAME, "body")).send_keys(Keys.ESCAPE)

    def get_title(self):
        return self.get_text(self.MODAL_CONTAINER)
