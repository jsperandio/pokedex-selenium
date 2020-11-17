import csv
import logging
from typing import List, Callable, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


class BaseDriver:
    def __init__(self, webdriver_path: str, timeout: int = 3):
        LOGGER.setLevel(logging.ERROR)

        if webdriver_path.find('geckodriver.exe'):
            self.driver = webdriver.Firefox(executable_path=webdriver_path)
        else:
            self.driver = webdriver.Chrome(executable_path=webdriver_path)

        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.driver.quit()

    def browser_history_back(self, back_count: int = 1):
        # this does not work very well
        # self.driver.execute_script("window.history.go(-" + back_count.__str__() + ")")
        for i in range(back_count):
            self.driver.back()

    def load_page(self, page_url: str, wait_element: bool = False, wait_element_id: str = "", timeout: int = 0):
        self.driver.get(page_url)
        timeout = (timeout == 0) if self.timeout else timeout

        logging.debug("Page loading...")

        if wait_element:
            try:
                element_present = ec.presence_of_element_located((By.ID, wait_element_id))
                WebDriverWait(self.driver, timeout).until(element_present)
            except TimeoutException:
                logging.error("Timed out waiting for page to load")

        privacy_byn = self.driver.find_elements(by=By.XPATH, value="/html/body/div/div/div/p[2]/button")
        if len(privacy_byn) > 0:
            privacy_byn[0].click()
            logging.debug("Privacy Button Clicked")

        logging.debug("Page loaded.")

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
        logging.info([c.text for c in columns])

    def lazy_table_extract(self, table_headers: List[str], table_data: List[WebElement], csv_name: str,
                           use_progress_bar: bool = True) -> list:
        file = open(csv_name, "w", newline='', encoding='utf-8')
        writer = csv.writer(file)
        table_data_extracted: list = [table_headers]

        data_iteration = table_data
        if use_progress_bar:
            data_iteration = tqdm(table_data, colour='blue', desc="Pokedex")

        for row in data_iteration:
            columns: List[WebElement] = self.get_table_row_columns(row)

            # table_data_extracted.append([str(c.text).replace('\n', '/').replace('\r', '') for c in columns])

            values_list: list = list()
            for c in columns:
                if c.text == "":
                    # Case don't have Text property , probably is a img , so get the title
                    img = c.find_element_by_css_selector(":first-child")
                    values_list.append(img.get_attribute("title"))
                else:
                    values_list.append(str(c.text).replace('\n', '/').replace('\r', ''))

            table_data_extracted.append(values_list)

        writer.writerows(table_data_extracted)
        file.close()

        # logging.info(f"Table extracted to: {csv_name}")

        return table_data_extracted

    def lazy_table_to_csv(self, css_selector_table: str, csv_name: str, use_progress_bar: bool = True) -> list:
        table = self.get_table(css_selector_table)
        headers = self.get_table_headers(table)
        data = self.get_table_data(table)
        table_extracted = self.lazy_table_extract(table_headers=headers, table_data=data, csv_name=csv_name,
                                                  use_progress_bar=use_progress_bar)
        return table_extracted

    def search_element_by_locator(self, element_locator: Tuple = (By.ID, "html")):
        return self.driver.find_element(by=element_locator[0], value=element_locator[1])

    def search_link_by_text_and_attribute(self, link_text: str, attribute: Tuple = ("title", "link")):
        links = self.driver.find_elements_by_link_text(link_text)
        for l_ele in links:
            if l_ele.get_attribute(attribute[0]) == attribute[1]:
                return l_ele

    def search_link_text_and_navigate(self, link_text: str, wait_element: bool = False,
                                      wait_element_locator: Tuple = (By.ID, "html")):
        try:
            element_clickable = ec.element_to_be_clickable((By.LINK_TEXT, link_text))
            WebDriverWait(self.driver, self.timeout).until(element_clickable)
            link_element = self.driver.find_element_by_link_text(link_text)
            # logging.debug(f"Clicked at {link_text}")
            link_element.click()
        except Exception as e:
            logging.error(e.__str__())

        if wait_element:
            try:
                element_present = ec.presence_of_all_elements_located(wait_element_locator)
                WebDriverWait(self.driver, self.timeout).until(element_present)
            except TimeoutException:
                logging.error(f"Timed out waiting for page to load: {link_text}")

    def click_and_wait(self, element: WebElement, wait_element_locator: Tuple = (By.ID, "html")):
        try:
            element_present = ec.presence_of_all_elements_located(wait_element_locator)
            WebDriverWait(self.driver, self.timeout).until(element_present)
            element.click()
        except TimeoutException:
            logging.error(f"Timed out waiting for click on: {wait_element_locator}")

    def wait_for(self, lambda_callable):
        WebDriverWait(self.driver, timeout=self.timeout).until(lambda_callable)

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
