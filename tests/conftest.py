#conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запускать браузеры в headless-режиме",
    )


@pytest.fixture(params=["chrome", "firefox"])
def driver(request):
    """Фикстура браузера: запускается для chrome и firefox по очереди.

    Использование в тесте:
        def test_example(driver):
            driver.get(BASE_URL)
    """
    headless = request.config.getoption("--headless")

    if request.param == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=options)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        browser = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )

    # maximize_window() в headless-Firefox падает с "Browsing context has
    # been discarded" — задаём размер без максимизации, с защитой от гонки
    try:
        browser.set_window_size(1920, 1080)
    except Exception:
        pass  # контекст ещё не готов — окно уже задано опциями

    browser.implicitly_wait(3)
    yield browser

    browser.quit()
