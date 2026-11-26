import os

import allure
from pages.main_page import MainPage
from pages.login_page import LoginPage
from pages.order_details_modal import OrderDetailsModal
from pages.orders_feed_page import OrdersFeedPage

BASE_URL = "https://stellarburgers.education-services.ru"
FEED_URL = BASE_URL + "/feed"

# Креденшелы берутся из файла .env в корне проекта.
# Сам .env в git не попадает (см. .gitignore).
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


def _load_env_file(path):
    """Читает .env в формате KEY=VALUE и кладёт в os.environ (без перезаписи)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env_file(ENV_PATH)

EMAIL = os.environ.get("SB_EMAIL", "")
PASSWORD = os.environ.get("SB_PASSWORD", "")


def create_order(main_page):
    """Логин, булка + начинка + кнопка оформления."""
    if not EMAIL or not PASSWORD:
        raise AssertionError(
            "Нет учетных данных: создай файл .env в корне проекта со строками\n"
            "SB_EMAIL=почта\nSB_PASSWORD=пароль"
        )
    login_page = LoginPage(main_page.driver)
    login_page.login(EMAIL, PASSWORD)

    main_page.add_ingredient_to_order("Краторная булка")
    main_page.add_ingredient_to_order("Говяжий метеорит")
    main_page.click_create_order()
    return main_page


@allure.feature("UI Автоматизация Stellar Burgers")
class TestStellarBurgersUI:

    @allure.title("Сценарий 1: переход в «Конструктор» по кнопке шапки")
    def test_go_to_constructor(self, driver):
        main_page = MainPage(driver)
        driver.get(FEED_URL)

        main_page.click_constructor()
        assert driver.current_url.startswith(BASE_URL), \
            f"Ожидалась главная страница, открыт: {driver.current_url}"

    @allure.title("Сценарий 2: переход в «Ленту заказов» по кнопке шапки")
    def test_go_to_orders_feed(self, driver):
        main_page = MainPage(driver)
        feed = OrdersFeedPage(driver)
        driver.get(BASE_URL)

        main_page.click_orders_feed()
        assert driver.current_url.endswith("/feed"), \
            f"Ожидалась лента заказов, открыт: {driver.current_url}"
        assert feed.is_page_open(), "Заголовок «Лента заказов» не виден"

    @allure.title("Сценарий 3: открытие модального окна с деталями ингредиента")
    def test_ingredient_modal_opens(self, driver):
        main_page = MainPage(driver)
        modal = OrderDetailsModal(driver)
        driver.get(BASE_URL)

        main_page.open_ingredient_modal("Краторная булка")
        assert modal.is_open(), "Модальное окно с деталями ингредиента не открылось"

    @allure.title("Сценарий 4: закрытие модального окна крестиком")
    def test_ingredient_modal_closes(self, driver):
        main_page = MainPage(driver)
        modal = OrderDetailsModal(driver)
        driver.get(BASE_URL)

        main_page.open_ingredient_modal("Краторная булка")
        assert modal.is_open(), "Модальное окно не открылось"

        modal.close()
        assert modal.is_closed(), "Модальное окно не закрылось после клика по крестику"

    @allure.title("Сценарий 5: счётчик ингредиента увеличивается при добавлении в заказ")
    def test_ingredient_counter_grows(self, driver):
        main_page = MainPage(driver)
        driver.get(BASE_URL)

        ingredient = "Говяжий метеорит"
        before = main_page.get_counter_by_name(ingredient)

        main_page.add_ingredient_to_order(ingredient)
        after = main_page.get_counter_by_name(ingredient)

        assert after == before + 1, \
            f"Счётчик должен вырасти на 1: было {before}, стало {after}"

    @allure.title("Сценарий 6: счётчики ленты заказов растут после оформления заказа")
    def test_feed_counters_grow(self, driver):
        main_page = MainPage(driver)
        feed = OrdersFeedPage(driver)

        driver.get(FEED_URL)
        before_all = feed.get_counter_all_time()
        before_today = feed.get_counter_today()

        driver.get(BASE_URL)
        create_order(main_page)

        driver.get(FEED_URL)
        after_all, after_today = feed.wait_counters_grow(before_all, before_today)

        assert after_all > before_all, \
            f"«Выполнено за всё время» не выросло: {before_all} -> {after_all}"
        assert after_today > before_today, \
            f"«Выполнено за сегодня» не выросло: {before_today} -> {after_today}"

    @allure.title("Сценарий 7: номер нового заказа появляется в ленте (В работе / Готовы)")
    def test_order_number_in_progress(self, driver):
        main_page = MainPage(driver)
        feed = OrdersFeedPage(driver)

        driver.get(BASE_URL)
        create_order(main_page)
        order_number = main_page.get_created_order_number()

        driver.get(FEED_URL)
        assert feed.wait_for_order_in_feed(order_number, timeout=20), \
            f"Заказ {order_number} не появился в ленте за 20 секунд"
