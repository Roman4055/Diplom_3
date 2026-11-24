from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class OrdersFeedPage(BasePage):
    # --- Заголовок страницы ---
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(),'Лента заказов')]")

    # --- Счётчики (привязаны к подписям над ними) ---
    COUNTER_ALL_TIME = (By.XPATH,
        "//p[contains(text(),'Выполнено за все время')]/following::p[contains(@class,'text_type_digits-large')][1]")
    COUNTER_TODAY = (By.XPATH,
        "//p[contains(text(),'Выполнено за сегодня')]/following::p[contains(@class,'text_type_digits-large')][1]")

    # --- Секция «В работе»: это <p>, а не <h2>; номера — в соседнем ul ---
    IN_PROGRESS_TITLE = (By.XPATH,
        "//p[contains(@class,'text_type_main-medium') and text()='В работе:']")
    IN_PROGRESS_NUMBERS = (By.XPATH,
        "//p[text()='В работе:']/following-sibling::ul//p[contains(@class,'OrderFeed_number')]")

    # --- Методы получения данных ---

    def get_counter_all_time(self):
        """Число «Выполнено за все время» (4354). Пробелы-разряды убираем."""
        return int(self.get_text(self.COUNTER_ALL_TIME).replace(" ", ""))

    def get_counter_today(self):
        """Число «Выполнено за сегодня» (265)."""
        return int(self.get_text(self.COUNTER_TODAY).replace(" ", ""))

    def get_in_progress_numbers(self):
        """Список номеров заказов из секции «В работе» (без решётки)."""
        elements = self.find_elements(self.IN_PROGRESS_NUMBERS)
        return [el.text.replace("#", "") for el in elements]

    def is_order_number_in_progress(self, order_number):
        """Есть ли номер заказа в секции «В работе»."""
        return str(order_number) in self.get_in_progress_numbers()

    # --- Проверки страницы ---

    def is_page_open(self):
        return self.is_element_visible(self.PAGE_TITLE)
