import csv
import logging
import os
import sys
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm
from base_driver import BaseDriver


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
    WEBDRIVER_PATH: str = os.path.join(CURR_DIR, "resource/geckodriver.exe")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    with BaseDriver(WEBDRIVER_PATH) as base_driver:
        base_driver.load_page(
            page_url="https://pokemondb.net/pokedex/stats/gen1",
            wait_element=True,
            wait_element_id="pokedex",
            timeout=5
        )
        table_extracted = base_driver.lazy_table_to_csv(
            css_selector_table="#pokedex",
            csv_name=os.path.join(OUTPUT_DIR, "pokedex.csv"))

        base_driver.timeout = 30
        # skip table header
        # ['#', 'Name', 'Type', 'Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        for r in table_extracted[1:]:
            # navigate to first item on Name column
            base_driver.search_link_text_and_navigate(r[1], True, (By.CLASS_NAME, "data-table"))
            base_driver.driver.back()
            logging.debug("Going Back")


if __name__ == "__main__":
    main()
