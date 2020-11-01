import csv
from typing import List, Callable

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


class BaseDriver:
    def __init__(self, webdriver_path: str, timeout: int = 3):
        self.driver = webdriver.Firefox(executable_path=webdriver_path)
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.driver.quit()

    def browser_history_back(self, back_count: int = 1):
        self.driver.execute_script("window.history.go(-" + back_count.__str__() + ")")

    def load_page(self, page_url: str, wait_element: bool, wait_element_id: str, timeout: int = 0):
        self.driver.get(page_url)
        timeout = (timeout == 0) if self.timeout else timeout

        print("Page loading...")

        if wait_element:
            try:
                element_present = ec.presence_of_element_located((By.ID, wait_element_id))
                WebDriverWait(self.driver, timeout).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")

        privacy_byn = self.driver.find_elements(by=By.XPATH, value="/html/body/div/div/div/p[2]/button")
        if len(privacy_byn) > 0:
            privacy_byn[0].click()
            print("Privacy Button Clicked")

        print("Page loaded.")

    def get_table(self, css_selector_path: str) -> WebElement:
        return self.driver.find_element_by_css_selector(css_selector_path)

    @staticmethod
    def get_table_headers(reference_table: WebElement) -> List[str]:
        headers = reference_table.find_elements_by_css_selector("thead > tr > th")
        table_headers = [h.text for h in headers]
        return table_headers

    @staticmethod
    def get_table_data(reference_table: WebElement) -> List[WebElement]:
        table_data = reference_table.find_elements_by_css_selector("tbody > tr")
        return table_data

    @staticmethod
    def iterate_table_data(table_data: List[WebElement], handler_item_action: Callable):
        for row in table_data:
            handler_item_action(row)

    @staticmethod
    def get_table_row_columns(row: WebElement) -> List[WebElement]:
        columns = row.find_elements_by_css_selector("td")
        return columns

    def print_table_row_data(self, row):
        columns: List[WebElement] = self.get_table_row_columns(row)
        print([c.text for c in columns])

    def lazy_table_extract(self, table_headers: List[str], table_data: List[WebElement], csv_name: str) -> list:
        file = open(csv_name, "w", newline='', encoding='utf-8')
        writer = csv.writer(file)
        table_data_extracted: list = [table_headers]

        print("Lazy extracting init")

        for row in tqdm(table_data):
            columns: List[WebElement] = self.get_table_row_columns(row)
            table_data_extracted.append([str(c.text).replace('\n', '/').replace('\r', '') for c in columns])

        writer.writerows(table_data_extracted)
        file.close()

        print(f"Table extracted to: {csv_name}")

        return table_data_extracted

    def lazy_table_to_csv(self, css_selector_table: str, csv_name: str):
        table = self.get_table(css_selector_table)
        headers = self.get_table_headers(table)
        data = self.get_table_data(table)
        self.lazy_table_extract(table_headers=headers, table_data=data,csv_name=csv_name)

    def navigate_and_extract(self, row: WebElement):
        # Get the name column
        name = row.find_element_by_css_selector("td:nth-child(2) > a:nth-child(1)")

        # Wait until element has enable to click
        element_invisibility = ec.invisibility_of_element_located((By.ID, "gdpr-confirm"))
        WebDriverWait(self.driver, 3).until(element_invisibility)
        name.click()

        # Wait until page load
        element_present = ec.presence_of_element_located((By.CSS_SELECTOR, "ul.list-nav:nth-child(18)"))
        WebDriverWait(self.driver, 3).until(element_present)

        # Select Gen 1
        self.driver.find_element_by_css_selector("ul.list-nav:nth-child(18) > li:nth-child(2) > a:nth-child(1)").click()

        # Wait until table load
        element_present = ec.presence_of_element_located((
            By.CSS_SELECTOR,
            "#tabs-moves-1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > table:nth-child(1)"))
        WebDriverWait(self.driver, 3).until(element_present)
        table = self.get_table("#tabs-moves-1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > "
                               "table:nth-child(1)")
        data = self.get_table_data(table)

        self.iterate_table_data(data, self.print_table_row_data)
        self.browser_history_back(2)
