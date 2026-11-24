from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MainPage(BasePage):
    # --- Шапка: навигация ---
    BTN_CONSTRUCTOR = (By.XPATH,
        "//p[contains(@class,'AppHeader_header__linkText') and text()='Конструктор']")
    BTN_ORDERS_FEED = (By.XPATH,
        "//p[contains(@class,'AppHeader_header__linkText') and text()='Лента Заказов']")

    # --- Ингредиенты ---
    INGREDIENT_CARD = (By.CSS_SELECTOR, "a[class*='BurgerIngredient_ingredient']")
    INGREDIENT_COUNTER = (By.CSS_SELECTOR, "p[class*='counter__num']")

    # --- Корзина конструктора ---
    BASKET_SECTION = (By.CSS_SELECTOR, "section[class*='BurgerConstructor_basket']")
    BTN_CREATE_ORDER = (By.XPATH,
        "//button[contains(@class,'button_button_type_primary') and text()='Оформить заказ']")
    BASKET_TOTAL = (By.XPATH,
        "//p[contains(@class,'text_type_digits-medium') and contains(@class,'BurgerConstructor')]")

    # --- Модальное окно (контейнер) ---
    MODAL_WINDOW = (By.CSS_SELECTOR, "section[class*='Modal_modal_opened']")

    # --- Методы навигации ---
    def click_constructor(self):
        self.click_element(self.BTN_CONSTRUCTOR)

    def click_orders_feed(self):
        self.click_element(self.BTN_ORDERS_FEED)

    # --- Методы работы с ингредиентами ---
    def _find_ingredient_card(self, ingredient_name):
        cards = self.driver.find_elements(*self.INGREDIENT_CARD)
        for card in cards:
            if ingredient_name in card.text:
                return card
        raise AssertionError(f"Ингредиент '{ingredient_name}' не найден на странице")

    def get_counter_by_name(self, ingredient_name):
        card = self._find_ingredient_card(ingredient_name)
        return int(card.find_element(*self.INGREDIENT_COUNTER).text)

    def add_ingredient_to_order(self, ingredient_name):
        card = self._find_ingredient_card(ingredient_name)
        target = self.find_element(self.BASKET_SECTION)
        ActionChains(self.driver).drag_and_drop(card, target).perform()

    # --- Методы работы с корзиной ---
    def click_create_order(self):
        self.click_element(self.BTN_CREATE_ORDER)

    def get_basket_total(self):
        return int(self.get_text(self.BASKET_TOTAL))

    # --- Методы работы с модальным окном ---
    def open_ingredient_modal(self, ingredient_name):
        self._find_ingredient_card(ingredient_name).click()

    def is_modal_open(self):
        return self.is_element_visible(self.MODAL_WINDOW)
