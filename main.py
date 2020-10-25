import os
from typing import List
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from tqdm import tqdm
import csv


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


def get_table_data(driver: webdriver) -> List[WebElement]:
    table_data = driver.find_elements_by_css_selector("#pokedex > tbody > tr")
    return table_data


def table_data_to_csv(headers, table_data, file_name: str):
    file = open(file_name, "w", newline='', encoding='utf-8')

    writer = csv.writer(file)

    # Write the csv first row (header)
    writer.writerow(headers)
    print("Start extract data...")
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

    driver: webdriver = init_driver(WEBDRIVER_PATH)
    load_page(driver,
              timeout=3,
              page_url="https://pokemondb.net/pokedex/stats/gen1",
              wait_element=True,
              wait_element_id="pokedex")

    table_headers: List[str] = get_table_headers(driver)
    table_data: List[WebElement] = get_table_data(driver)
    table_data_to_csv(table_headers, table_data, os.path.join(OUTPUT_DIR, "pokedex.csv"))

    close_driver(driver)


if __name__ == "__main__":
    main()
