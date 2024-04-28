"""Модуль отвечающий за заполнение онлайн декларации на сайте nalog.ru"""
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from script.dto import Report


COUNTRY_MAPPER = {
    'США': '840',
}
CURRENCY_MAPPER = {
    'USD': '840',
    'RUB': '643',
}
INCOME_TYPE_CODE = '1010'  # Дивиденды
INCOME_RECEIVE_COUNTRY = '643'  # Россия
TAX_DEDUCTION_CODE = 'Не предоставлять вычет'


class Locator:
    login_username_input = './/form//input[@name="username"]'
    login_password_input = './/form//input[@name="password"]'
    login_submit = './/form//button[@type="submit"]'
    foreign_tab = './/div[@class="m-tabPanel" and @role="tabpanel"]'
    incomes_list = './div/div/div[@class="flex flex-col"]'  # relative to foreign_tab
    last_income_source = './div[last()]'  # relative to incomes_list
    last_income_source_form = './div[last()]'  # relative to last_income_source
    add_income_source_btn = './div/div/div[@class="flex justify-center mb-4"]//button'  # relative to foreign_tab
    add_income_form = './/div[@class="ReactModalPortal"]//form'
    add_income_name_input = './/input[@name="incomeSourceName"]'
    add_income_send_country_dropdown = './/label[contains(@for, "oksmIst")]/parent::div'
    add_income_receive_country_dropdown = './/label[contains(@for, "oksmZach")]/parent::div'
    add_income_form_submit = './/button[@type="submit"]'  # relative to add_income_form
    income_type_dropdown = './/label[contains(@for, "incomeTypeCode")]/parent::div'
    income_deduction_dropdown = './/label[contains(@for, "taxDeductionCode")]/parent::div'
    income_amount_input = './/input[contains(@id, "incomeAmountCurrency")]'
    income_date_input = './/input[contains(@id, "incomeDate")]'
    income_tax_date_input = './/input[contains(@id, "taxPaymentDate")]'
    income_currency_dropdown = './/label[contains(@for, "currencyCode")]/parent::div'
    income_convert_online_input = './/input[contains(@id, "module:checkbox")]'
    income_tax_input = './/input[contains(@id, "paymentAmountCurrency")]'
    dropdown_search_input = './/input[@class="m-select__searchInput"]'
    dropdown_first_option = './/div[contains(@class, "m-popover")]//li[last()]'


class Filler:
    def __init__(self):
        self.username = os.getenv("NALOG_USERNAME")
        self.password = os.getenv("NALOG_PASSWORD")

        self.driver = webdriver.Chrome(service_log_path='NUL')
        self.driver.get('https://nalog.ru')
        self.locator = Locator

    def login(self):
        username_input = self.driver.find_element(
            By.XPATH, self.locator.login_username_input
        )
        password_input = self.driver.find_element(
            By.XPATH, self.locator.login_password_input
        )
        submit_button = self.driver.find_element(
            By.XPATH, self.locator.login_submit
        )
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        submit_button.click()

    def get_foreign_tab(self):
        return self.driver.find_element(
            By.XPATH, self.locator.foreign_tab
        )

    def get_incomes_list(self):
        foreign_tab = self.get_foreign_tab()
        return foreign_tab.find_element(
            By.XPATH, self.locator.incomes_list
        )

    def get_last_income(self):
        return self.get_incomes_list().find_element(By.XPATH, self.locator.last_income_source)

    def add_new_income_element(self):
        actions = ActionChains(self.driver)
        add_income_button = self.get_foreign_tab().find_element(By.XPATH, self.locator.add_income_source_btn)
        actions.move_to_element(add_income_button).click(add_income_button).perform()

    def _select_dropdown_choice(self, element, data):
        sleep(0.5)
        search_element = element.find_element(By.XPATH, self.locator.dropdown_search_input)

        actions = ActionChains(self.driver)
        actions.move_to_element(element).click(element).perform()
        sleep(0.5)
        search_element.send_keys(data)
        sleep(0.5)
        option = self.driver.find_element(By.XPATH, self.locator.dropdown_first_option)
        option.click()
        sleep(0.5)

    def _send_keys(self, element, locator, keys):
        sleep(0.5)
        input_element = element.find_element(
            By.XPATH, locator
        )
        actions = ActionChains(self.driver)
        actions.move_to_element(input_element).click(input_element).perform()
        input_element.send_keys(keys)
        sleep(0.5)

    def _fill_income_name(self, element, report):
        """Заполняет поле Наименование"""
        self._send_keys(element, self.locator.add_income_name_input, report.company)

    def _fill_income_send_country(self, element, report):
        """Заполняет поля Страна источника выплаты"""
        dropdown_element = element.find_element(
            By.XPATH, self.locator.add_income_send_country_dropdown
        )
        self._select_dropdown_choice(
            dropdown_element, COUNTRY_MAPPER[report.country]
        )

    def _fill_income_receive_country(self, element, report):
        """Заполняет поле Страна зачисления выплаты"""
        dropdown_element = element.find_element(
            By.XPATH, self.locator.add_income_receive_country_dropdown
        )
        self._select_dropdown_choice(
            dropdown_element, INCOME_RECEIVE_COUNTRY
        )

    def _fill_income_type(self, element, report):
        """Заполняет поле Код дохода"""
        dropdown_element = element.find_element(
            By.XPATH, self.locator.income_type_dropdown
        )
        self._select_dropdown_choice(
            dropdown_element, INCOME_TYPE_CODE
        )

    def _fill_income_deduction(self, element, report):
        """Заполняет поле Предоставить налоговый вычет"""
        input_element = element.find_element(
            By.XPATH, self.locator.income_deduction_dropdown
        )
        self._select_dropdown_choice(
            input_element, TAX_DEDUCTION_CODE
        )

    def _fill_income_amount(self, element, report):
        """Заполняет поле Сумма дохода в валюте"""
        self._send_keys(element, self.locator.income_amount_input, str(report.amount))

    def _fill_income_dates(self, element, report):
        """Заполняет поля Дата получения дохода и Дата уплаты налога"""
        date = report.payment_date.strftime('%d%m%Y')
        self._send_keys(element, self.locator.income_date_input, date)
        self._send_keys(element, self.locator.income_tax_date_input, date)

    def _fill_income_currency(self, element, report):
        """Заполняет поле Код валюты"""
        input_element = element.find_element(
            By.XPATH, self.locator.income_currency_dropdown
        )
        self._select_dropdown_choice(
            input_element, CURRENCY_MAPPER[report.currency]
        )

    def _fill_income_convert_online(self, element, report):
        """Проставляет чекбокс Определить курс автоматически"""
        element.find_element(By.XPATH, self.locator.income_convert_online_input).click()

    def _fill_income_tax(self, element, report):
        """Заполняет поле Сумма налога в иностранной валюте"""
        self._send_keys(element, self.locator.income_tax_input, str(report.tax))

    def _add_income_source(self, report: Report):
        """Добавляет запись об источнике дохода"""
        self.add_new_income_element()
        sleep(0.5)
        form = self.driver.find_element(By.XPATH, self.locator.add_income_form)
        self._fill_income_name(form, report)
        self._fill_income_send_country(form, report)
        self._fill_income_receive_country(form, report)
        form.find_element(By.XPATH, self.locator.add_income_form_submit).click()

    def _fill_income_source(self, element, report: Report):
        """Заполняет данными запись об источнике дохода"""
        self._fill_income_type(element, report)
        self._fill_income_deduction(element, report)
        self._fill_income_amount(element, report)
        self._fill_income_dates(element, report)
        self._fill_income_currency(element, report)
        sleep(1)
        self._fill_income_convert_online(element, report)
        self._fill_income_tax(element, report)

    def get_income_source_form(self):
        income_source_element = self.get_last_income()
        income_source_form = income_source_element.find_element(By.XPATH, self.locator.last_income_source_form)
        if not income_source_form.is_displayed():
            income_source_element.click()
        return income_source_form

    def fill(self, report: Report):
        self._add_income_source(report)
        income_source_form = self.get_income_source_form()
        self._fill_income_source(income_source_form, report)
