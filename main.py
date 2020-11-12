import csv
import logging
import os
import time
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


class Config:
    def __init__(self):
        self.CURR_DIR: str = os.path.abspath(os.getcwd())
        self.OUTPUT_DIR: str = os.path.join(self.CURR_DIR, "output")
        self.WEBDRIVER_PATH: str = os.path.join(self.CURR_DIR, "resource/chromedriver.exe")

        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.ERROR)


def extract_pokemon_moves_manually(c: Config):
    with BaseDriver(c.WEBDRIVER_PATH) as base_driver:
        base_driver.load_page(
            page_url="https://pokemondb.net/pokedex/stats/gen1",
            wait_element=True,
            wait_element_id="pokedex",
            timeout=5
        )
        table_extracted = base_driver.lazy_table_to_csv(
            css_selector_table="#pokedex",
            csv_name=os.path.join(c.OUTPUT_DIR, "pokedex.csv"))

        base_driver.timeout = 30
        # skip table header
        # ['#', 'Name', 'Type', 'Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        progress_bar = tqdm(table_extracted[1:], desc="Pokemons", colour='green', leave=False, unit_scale=True)
        for r in progress_bar:
            progress_bar.set_description(f"Extracting moves from {r[1]}")
            # navigate to first item on Name column
            base_driver.search_link_text_and_navigate(link_text=r[1], wait_element=True,
                                                      wait_element_locator=(By.CLASS_NAME, "data-table"))
            # get the moves generations list
            # moves_generations_list = base_driver.search_element_by_locator((By.XPATH, "/html/body/main/ul[3]"))
            # first_gen = moves_generations_list.find_element_by_link_text("1")

            # navigate for the first generation moves
            link = base_driver.search_link_by_text_and_attribute("1", ("title", "Generation 1: Red, Blue, Yellow"))
            base_driver.click_and_wait(element=link, wait_element_locator=(By.CLASS_NAME, "data-table"))



            base_driver.lazy_table_to_csv(
                css_selector_table="#tabs-moves-1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > "
                                   "table:nth-child(1)",
                csv_name=os.path.join(c.OUTPUT_DIR, f"moves/moves_{r[1]}.csv"),
                use_progress_bar=False
            )
            time.sleep(2)
            base_driver.browser_history_back(2)


def main():
    conf = Config()
    extract_pokemon_moves_manually(conf)




if __name__ == "__main__":
    main()
