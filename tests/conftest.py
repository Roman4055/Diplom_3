import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Базовый URL стенда — используется всеми тестами
BASE_URL = "https://stellarburgers.education-services.ru"


def pytest_addoption(parser):
    """Добавляет флаг --headless для запуска без окна браузера."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запускать браузер в headless-режиме",
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
        browser = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )

    browser.maximize_window()
    yield browser

    # Разрушение фикстуры: браузер закрывается после каждого теста,
    # даже если тест упал
    browser.quit()
