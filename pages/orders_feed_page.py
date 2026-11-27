#orders_feed_page.py
import time

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class OrdersFeedPage(BasePage):
    # --- Заголовок страницы ---
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(),'Лента заказов')]")

    # --- Счётчики (привязаны к подписям над ними) ---
    COUNTER_ALL_TIME = (By.XPATH,
        "//p[contains(text(),'Выполнено за все время')]"
        "/following::p[contains(@class,'text_type_digits-large')][1]")
    COUNTER_TODAY = (By.XPATH,
        "//p[contains(text(),'Выполнено за сегодня')]"
        "/following::p[contains(@class,'text_type_digits-large')][1]")

    # --- Номера заказов в блоке статусов.
    STATUS_NUMBERS = (By.XPATH, "//li[contains(@class,'text_type_digits-default')]")

    # --- Заголовок секции «В работе» (это <p>, а не <h2>) ---
    IN_PROGRESS_TITLE = (By.XPATH,
        "//p[contains(@class,'text_type_main-medium') and text()='В работе:']")

    # --- Методы получения данных ---

    def get_counter_all_time(self):
        """Число «Выполнено за все время». Пробелы-разряды убираем."""
        return int(self.get_text(self.COUNTER_ALL_TIME).replace(" ", ""))

    def get_counter_today(self):
        """Число «Выполнено за сегодня»."""
        return int(self.get_text(self.COUNTER_TODAY).replace(" ", ""))

    def get_status_numbers(self):
        """Все номера заказов в блоке статусов («В работе» + «Готовы»).

        Чистим пробелы и переносы: свежий номер может отрисовываться
        несколькими текстовыми узлами («0» + «4988»).
        """
        numbers = []
        for el in self.find_elements(self.STATUS_NUMBERS):
            raw = ''.join(el.text.split()).replace("#", "")
            if raw:
                numbers.append(raw.lstrip("0"))
        return numbers

    def is_page_open(self):
        return self.is_element_visible(self.PAGE_TITLE)

    # --- Хелперы ожидания: тесты вызывают их, не зная деталей ---

    def wait_for_order_in_feed(self, order_number, timeout=20):
        """Ждёт появления номера заказа в ленте (В работе + Готовы).

        Возвращает True, если номер найден, иначе False.
        """
        expected = str(order_number).lstrip("0")
        deadline = time.time() + timeout
        while time.time() < deadline:
            if expected in self.get_status_numbers():
                return True
            time.sleep(1)
            self.driver.refresh()
        return False

    def wait_counters_grow(self, before_all, before_today, timeout=30):
        """Ждёт, пока оба счётчика ленты превысят исходные значения.

        Возвращает кортеж (after_all, after_today) на момент успеха
        или последние прочитанные значения, если время вышло.
        """
        deadline = time.time() + timeout
        after_all, after_today = before_all, before_today
        while time.time() < deadline:
            after_all = self.get_counter_all_time()
            after_today = self.get_counter_today()
            if after_all > before_all and after_today > before_today:
                return after_all, after_today
            time.sleep(2)
            self.driver.refresh()
        return after_all, after_today
