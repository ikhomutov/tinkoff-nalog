"""Модуль отвечающий за заполнение онлайн декларации на сайте nalog.ru"""
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from script.dto import Report


COUNTRY_MAPPER = {
    'США': '840',
}
CURRENCY_MAPPER = {
    'USD': '840'
}
INCOME_TYPE_CODE = '1010'  # Дивиденды
INCOME_RECEIVE_COUNTRY = '643'  # Россия
TAX_DEDUCTION_CODE = 'Не предоставлять вычет'


class Locator:
    foreign_tab = './/div[@class="fns-tabs__tabPanel" and @value="1"]'
    incomes_list = './div/div/div[@class="flex flex-col"]'  # relative to foreign_tab
    last_income_source = './div[last()]'  # relative to incomes_list
    last_income_source_form = './div[last()]'  # relative to last_income_source
    add_income_source_btn = './div/div/div[@class="flex justify-center mb-4"]//button'  # relative to foreign_tab
    add_income_form = './/div[@class="ReactModalPortal"]//form'
    add_income_name = './/input[@name="incomeSourceName"]'
    add_income_send_country = './/input[contains(@id, "oksmIst")]'
    add_income_receive_country = './/input[contains(@id, "oksmZach")]'
    add_income_form_submit = './/button[@type="submit"]'  # relative to add_income_form
    income_type = './/input[contains(@name, "incomeTypeCode")]'
    income_deduction = './/input[contains(@name, "taxDeductionCode")]'
    income_amount = './/input[contains(@name, "incomeAmountCurrency")]'
    income_date = './/input[contains(@id, "incomeDate")]'
    income_tax_date = './/input[contains(@id, "taxPaymentDate")]'
    income_currency = './/input[contains(@name, "currencyCode")]'
    income_convert_online = './/input[contains(@id, "module-checkbox")]'
    income_tax = './/input[contains(@name, "paymentAmountCurrency")]'
    dropdown_first_option = './/div[@class="fns-popover"]//li[last()]'


class Filler:
    def __init__(self):
        self.driver = webdriver.Chrome(service_log_path='NUL')
        self.driver.get('https://nalog.ru')

    def get_foreign_tab(self):
        return self.driver.find_element(
            By.XPATH, Locator.foreign_tab
        )

    def get_incomes_list(self):
        foreign_tab = self.get_foreign_tab()
        return foreign_tab.find_element(
            By.XPATH, Locator.incomes_list
        )

    def get_last_income(self):
        return self.get_incomes_list().find_element(By.XPATH, Locator.last_income_source)

    def add_new_income_element(self):
        actions = ActionChains(self.driver)
        add_income_button = self.get_foreign_tab().find_element(By.XPATH, Locator.add_income_source_btn)
        actions.move_to_element(add_income_button).click(add_income_button).perform()

    def _select_dropdown_choice(self, element, data):
        sleep(0.5)
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click(element).perform()
        sleep(0.5)
        element.send_keys(data)
        sleep(0.5)
        option = self.driver.find_element(By.XPATH, Locator.dropdown_first_option)
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
        self._send_keys(element, Locator.add_income_name, report.company)

    def _fill_income_countries(self, element, report):
        """Заполняет поля Страна источника выплаты и Страна зачисления выплаты"""
        input_element = element.find_element(
            By.XPATH, Locator.add_income_send_country
        )
        self._select_dropdown_choice(
            input_element, COUNTRY_MAPPER[report.country]
        )

        input_element = element.find_element(
            By.XPATH, Locator.add_income_receive_country
        )
        self._select_dropdown_choice(
            input_element, INCOME_RECEIVE_COUNTRY
        )

    def _fill_income_type(self, element, report):
        """Заполняет поле Код дохода"""
        input_element = element.find_element(
            By.XPATH, Locator.income_type
        )
        self._select_dropdown_choice(
            input_element, INCOME_TYPE_CODE
        )

    def _fill_income_deduction(self, element, report):
        """Заполняет поле Предоставить налоговый вычет"""
        input_element = element.find_element(
            By.XPATH, Locator.income_deduction
        )
        self._select_dropdown_choice(
            input_element, TAX_DEDUCTION_CODE
        )

    def _fill_income_amount(self, element, report):
        """Заполняет поле Сумма дохода в валюте"""
        self._send_keys(element, Locator.income_amount, str(report.amount))

    def _fill_income_dates(self, element, report):
        """Заполняет поля Дата получения дохода и Дата уплаты налога"""
        date = report.payment_date.strftime('%d.%M.%Y')
        self._send_keys(element, Locator.income_date, date)
        self._send_keys(element, Locator.income_tax_date, date)

    def _fill_income_currency(self, element, report):
        """Заполняет поле Код валюты"""
        input_element = element.find_element(
            By.XPATH, Locator.income_currency
        )
        self._select_dropdown_choice(
            input_element, CURRENCY_MAPPER[report.currency]
        )

    def _fill_income_convert_online(self, element, report):
        """Проставляет чекбокс Определить курс автоматически"""
        element.find_element(By.XPATH, Locator.income_convert_online).click()

    def _fill_income_tax(self, element, report):
        """Заполняет поле Сумма налога в иностранной валюте"""
        self._send_keys(element, Locator.income_tax, str(report.tax))

    def _add_income_source(self, report: Report):
        """Добавляет запись об источнике дохода"""
        self.add_new_income_element()
        sleep(0.5)
        form = self.driver.find_element(By.XPATH, Locator.add_income_form)
        self._fill_income_name(form, report)
        self._fill_income_countries(form, report)
        form.find_element(By.XPATH, Locator.add_income_form_submit).click()
        last_income_source = self.get_last_income()
        return last_income_source

    def _fill_income_source(self, element, report: Report):
        """Заполняет данными запись об источнике дохода"""
        self._fill_income_type(element, report)
        self._fill_income_deduction(element, report)
        self._fill_income_amount(element, report)
        self._fill_income_dates(element, report)
        self._fill_income_currency(element, report)
        self._fill_income_convert_online(element, report)
        self._fill_income_tax(element, report)

    def fill(self, report: Report):
        income_source_element = self._add_income_source(report)
        income_source_form = income_source_element.find_element(By.XPATH, Locator.last_income_source_form)
        if not income_source_form.is_displayed():
            income_source_element.click()
        self._fill_income_source(income_source_form, report)
