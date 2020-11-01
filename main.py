import csv
import os
from typing import List, Callable

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


class BaseDriver:
    def __init__(self, webdriver_path: str):
        self.driver = webdriver.Firefox(executable_path=webdriver_path)

    def close(self):
        self.driver.quit()

    def browser_history_back(self, back_count: int = 1):
        self.driver.execute_script("window.history.go(-" + back_count.__str__() + ")")

    def load_page(self, timeout: int, page_url: str, wait_element: bool, wait_element_id: str):
        self.driver.get(page_url)

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

    def lazy_table_extract(self,table_headers: List[str], table_data: List[WebElement], csv_name: str) -> list:
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


def init_driver(webdriver_path: str = "") -> webdriver:
    driver = webdriver.Firefox(executable_path=webdriver_path)
    return driver


def close_driver(driver: webdriver):
    driver.quit()


def load_page(driver: webdriver, timeout: int, page_url: str, wait_element: bool, wait_element_id: str):
    driver.get(page_url)

    print("Page loading...")

    if wait_element:
        try:
            element_present = ec.presence_of_element_located((By.ID, wait_element_id))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

    privacy_byn = driver.find_elements(by=By.XPATH, value="/html/body/div/div/div/p[2]/button")
    if len(privacy_byn) > 0:
        privacy_byn[0].click()
        print("Privacy Button Clicked")

    print("Page loaded.")


def get_table_headers(driver: webdriver) -> List[str]:
    headers = driver.find_elements_by_css_selector("#pokedex > thead > tr > th")
    table_headers = [h.text for h in headers]
    return table_headers


def get_table_data(driver: webdriver, css_selector_path: str) -> List[WebElement]:
    table_data = driver.find_elements_by_css_selector(css_selector_path)
    return table_data


def table_data_to_csv(headers: List[str], table_data: List[WebElement], file_name: str):
    file = open(file_name, "w", newline='', encoding='utf-8')

    writer = csv.writer(file)

    # Write the csv first row (header)
    writer.writerow(headers)
    print("Start extracting data...")
    for r in tqdm(table_data):
        # column_desc = r.find_elements_by_css_selector("td:nth-child(1) > span")
        try:
            column_desc_img = r.find_element_by_css_selector("td:nth-child(1) > span:nth-child(1) > img")
            img_url = column_desc_img.get_attribute("src")
        except:
            column_desc_img = r.find_element_by_css_selector("td:nth-child(1) > span:nth-child(1) > span")
            img_url = column_desc_img.get_attribute("data-src")

        column_desc_number = r.find_element_by_css_selector("td:nth-child(1) > span:nth-child(2)")
        column_name = r.find_element_by_css_selector("td:nth-child(2) > a")
        column_types = r.find_elements_by_css_selector("td:nth-child(3) > a")
        column_total = r.find_element_by_css_selector("td:nth-child(4)")
        column_hp = r.find_element_by_css_selector("td:nth-child(5)")
        column_atk = r.find_element_by_css_selector("td:nth-child(6)")
        column_def = r.find_element_by_css_selector("td:nth-child(7)")
        column_sp_atk = r.find_element_by_css_selector("td:nth-child(8)")
        column_sp_def = r.find_element_by_css_selector("td:nth-child(9)")
        column_spd = r.find_element_by_css_selector("td:nth-child(10)")

        row = [column_desc_number.text + " | " + img_url,
               column_name.text,
               # ','.join([t.text for t in column_types]),
               [t.text for t in column_types],
               column_total.text,
               column_hp.text,
               column_atk.text,
               column_def.text,
               column_sp_atk.text,
               column_sp_def.text,
               column_spd.text]

        writer.writerow(row)

    file.close()


def main():
    CURR_DIR: str = os.path.abspath(os.getcwd())
    OUTPUT_DIR: str = os.path.join(CURR_DIR, "output")
    WEBDRIVER_PATH: str = os.path.join(CURR_DIR, "geckodriver.exe")

    base_driver = BaseDriver(WEBDRIVER_PATH)
    base_driver.load_page(
        timeout=3,
        page_url="https://pokemondb.net/pokedex/stats/gen1",
        wait_element=True,
        wait_element_id="pokedex"
    )

    table = base_driver.get_table("#pokedex")
    headers = base_driver.get_table_headers(table)
    data = base_driver.get_table_data(table)
    base_driver.lazy_table_extract(table_headers=headers, table_data=data,
                                   csv_name=os.path.join(OUTPUT_DIR, "pokedex.csv"))

    # base_driver.iterate_table_data(table_data=data, handler_item_action=base_driver.print_table_row_data)
    base_driver.close()

    # driver: webdriver = init_driver(WEBDRIVER_PATH)
    # load_page(driver,
    #           timeout=3,
    #           page_url="https://pokemondb.net/pokedex/stats/gen1",
    #           wait_element=True,
    #           wait_element_id="pokedex")
    #
    # table_headers: List[str] = get_table_headers(driver)
    # table_data: List[WebElement] = get_table_data(driver, "#pokedex > tbody > tr")
    # table_data_to_csv(table_headers, table_data, os.path.join(OUTPUT_DIR, "pokedex.csv"))
    #
    # close_driver(driver)


if __name__ == "__main__":
    main()
