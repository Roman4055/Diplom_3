#main_page.py
import time

from selenium.common.exceptions import ElementClickInterceptedException
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
        "//button[contains(@class,'button_button_type_primary') and contains(., 'Оформить')]")

    BASKET_TOTAL = (By.XPATH,
        "//p[contains(@class,'text_type_digits-medium') and contains(@class,'BurgerConstructor')]")

    # --- Модальное окно (контейнер) ---
    MODAL_WINDOW = (By.CSS_SELECTOR, "section[class*='Modal_modal_opened']")

    # --- Окно успешного оформления заказа ---
    ORDER_NUMBER_IN_MODAL = (By.XPATH,
        "//section[contains(@class,'Modal_modal_opened')]//h2[contains(@class,'text_type_digits-large')]")

    # Эмуляция HTML5 drag&drop: используется, если ActionChains не дал эффекта
    DRAG_AND_DROP_SCRIPT = """
        function createEvent(type) {
            var event = document.createEvent('CustomEvent');
            event.initCustomEvent(type, true, true, null);
            event.dataTransfer = {
                data: {},
                setData: function(key, value) { this.data[key] = value; },
                getData: function(key) { return this.data[key]; }
            };
            return event;
        }
        function dispatch(element, event) {
            if (element.dispatchEvent) { element.dispatchEvent(event); }
        }
        var source = arguments[0], target = arguments[1];
        dispatch(source, createEvent('dragstart'));
        dispatch(target, createEvent('dragenter'));
        dispatch(target, createEvent('dragover'));
        dispatch(target, createEvent('drop'));
        dispatch(source, createEvent('dragend'));
    """

    # --- Методы навигации ---
    def click_constructor(self):
        self.click_element(self.BTN_CONSTRUCTOR)

    def click_orders_feed(self):
        self.click_element(self.BTN_ORDERS_FEED)

    # --- Методы работы с ингредиентами ---
    def _find_ingredient_card(self, ingredient_name):
        """Ищет карточку ингредиента с ожиданием: SPA отрисовывает список не мгновенно."""
        deadline = time.time() + 10
        while time.time() < deadline:
            cards = self.driver.find_elements(*self.INGREDIENT_CARD)
            for card in cards:
                if ingredient_name in card.text:
                    return card
            time.sleep(0.5)
        raise AssertionError(f"Ингредиент '{ingredient_name}' не найден на странице")

    def get_counter_by_name(self, ingredient_name):
        card = self._find_ingredient_card(ingredient_name)
        return int(card.find_element(*self.INGREDIENT_COUNTER).text)

    def add_ingredient_to_order(self, ingredient_name):
        """Перетаскивает ингредиент в корзину с самопроверкой:
        если ActionChains не дал эффекта (типично для Firefox) —
        эмулирует HTML5-события через JavaScript."""
        card = self._find_ingredient_card(ingredient_name)
        target = self.find_element(self.BASKET_SECTION)
        counter_before = self.get_counter_by_name(ingredient_name)

        # Прокручиваем оба элемента в центр экрана
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)

        # Основной способ: цепочка надёжнее drag_and_drop
        ActionChains(self.driver).click_and_hold(card).move_to_element(target).release().perform()

        # Ждём изменения счётчика до 2 секунд — реакция обновляет его не мгновенно
        for _ in range(10):
            if self.get_counter_by_name(ingredient_name) != counter_before:
                return
            time.sleep(0.2)

        # Запасной способ: JS-эмуляция drag&drop
        card = self._find_ingredient_card(ingredient_name)
        self.driver.execute_script(self.DRAG_AND_DROP_SCRIPT, card, target)

        for _ in range(10):
            if self.get_counter_by_name(ingredient_name) != counter_before:
                return
            time.sleep(0.2)

        raise AssertionError(
            f"Не удалось перетащить '{ingredient_name}' в корзину: счётчик остался {counter_before}"
        )

    def open_ingredient_modal(self, ingredient_name):
        card = self._find_ingredient_card(ingredient_name)
        # Без скролла карточка может быть перекрыта оверлеем в момент анимации
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        try:
            card.click()
        except ElementClickInterceptedException:
            # Оверлей перекрыл клик (гонка анимации в Firefox) — кликаем через JS
            self.driver.execute_script("arguments[0].click();", card)

    # --- Методы работы с корзиной ---
    def click_create_order(self):
        self.click_element(self.BTN_CREATE_ORDER)

    def get_basket_total(self):
        return int(self.get_text(self.BASKET_TOTAL))

    # --- Методы работы с модальным окном ---
    def is_modal_open(self):
        return self.is_element_visible(self.MODAL_WINDOW)

    def get_created_order_number(self):
        """Возвращает номер заказа без ведущих нулей.

        Стенд показывает номер не сразу: сначала в окне заглушка
        (пустая строка или 9999), реальный номер подтягивается позже.
        Крутим опрос до 10 секунд, пока не появится настоящий номер.
        """
        deadline = time.time() + 10
        number = "0"
        while time.time() < deadline:
            try:
                raw = self.get_text(self.ORDER_NUMBER_IN_MODAL).strip()
            except Exception:
                raw = ""
            stripped = raw.lstrip("0")
            if stripped and stripped != "9999":
                return stripped
            number = stripped or number
            time.sleep(0.5)
        return number
