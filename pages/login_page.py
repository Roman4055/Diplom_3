#login_page.py
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    LOGIN_URL = "https://stellarburgers.education-services.ru/login"

    # Email: <input type="text" name="name"> — имя поля "name"
    EMAIL_INPUT = (By.XPATH, "//input[@name='name' and @type='text']")

    # Пароль: <input type="password" name="Пароль">
    PASSWORD_INPUT = (By.XPATH, "//input[@name='Пароль' and @type='password']")

    # Кнопка «Войти»: primary + size_medium, на этой странице она одна
    BTN_LOGIN = (By.XPATH,
        "//button[contains(@class,'button_button_type_primary') "
        "and contains(@class,'button_button_size_medium') and contains(., 'Войти')]")

    def open(self):
        self.driver.get(self.LOGIN_URL)

    def login(self, email, password):
        self.open()
        self.find_element(self.EMAIL_INPUT).send_keys(email)
        self.find_element(self.PASSWORD_INPUT).send_keys(password)
        self.click_element(self.BTN_LOGIN)
