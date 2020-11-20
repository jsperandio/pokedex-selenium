import logging
import os
import time

from selenium.webdriver.common.by import By
from tqdm import tqdm

from base_driver import BaseDriver


class Config:

    def __init__(self, output_dir: str = "output", webdriver_path: str = "resource/geckodriver.exe",
                 headless_driver: bool = False,
                 log_level: int = logging.DEBUG):

        self.CURR_DIR: str = os.path.abspath(os.getcwd())
        self.OUTPUT_DIR: str = os.path.join(self.CURR_DIR, output_dir)
        self.WEBDRIVER_PATH: str = os.path.join(self.CURR_DIR, webdriver_path)
        self.HEADLESS_DRIVER: bool = headless_driver

        if not log_level:
            logging.getLogger().disabled = True
        else:
            logging.basicConfig(level=log_level)
            logging.getLogger("urllib3").setLevel(logging.ERROR)


def extract_pokedex_robot(c: Config):
    with BaseDriver(c.WEBDRIVER_PATH, c.HEADLESS_DRIVER) as base_driver:
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

        # Skip table header
        # ['#', 'Name', 'Type', 'Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        progress_bar = tqdm(table_extracted[1:], desc="Pokemons", colour='green', leave=False, unit_scale=True)
        for r in progress_bar:
            progress_bar.set_description(f"Extracting moves from {r[1]}")

            # Navigate to first item on Name column
            base_driver.search_link_text_and_navigate(link_text=r[1], wait_element=True,
                                                      wait_element_locator=(By.CLASS_NAME, "data-table"))

            # Navigate for the first generation moves
            link = base_driver.search_link_by_text_and_attribute("1", ("title", "Generation 1: Red, Blue, Yellow"))
            base_driver.click_and_wait(element=link, wait_element_locator=(By.CLASS_NAME, "data-table"))

            base_driver.lazy_table_to_csv(
                css_selector_table="#tabs-moves-1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > "
                                   "table:nth-child(1)",
                csv_name=os.path.join(c.OUTPUT_DIR, f"moves_robot/moves_{r[1]}.csv"),
                use_progress_bar=False
            )
            time.sleep(2)
            base_driver.browser_history_back(2)


def extract_pokedex(c: Config):
    with BaseDriver(c.WEBDRIVER_PATH, c.HEADLESS_DRIVER) as base_driver:
        base_driver.load_page(
            page_url="https://pokemondb.net/pokedex/stats/gen1",
            wait_element=True,
            wait_element_id="pokedex",
            timeout=5
        )

        pokemon_table_extracted = base_driver.lazy_table_to_csv(
            css_selector_table="#pokedex",
            csv_name=os.path.join(c.OUTPUT_DIR, "pokedex.csv"))

        base_driver.timeout = 30

        # Skip table header
        # ['#', 'Name', 'Type', 'Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        progress_bar = tqdm(pokemon_table_extracted[1:], desc="Pokemons", colour='green', leave=False,
                            unit_scale=True)
        for r in progress_bar:
            pokemon_name: str = r[1]

            progress_bar.set_description(f"Extracting moves from {pokemon_name}")

            # Fuck nidorans, farfetch'd, mr. mine
            pokemon_name = pokemon_name.replace('♀', '-f')
            pokemon_name = pokemon_name.replace('♂', '-m')
            pokemon_name = pokemon_name.replace("'", '')
            pokemon_name = pokemon_name.replace(".", '-')
            pokemon_name = pokemon_name.replace(" ", '')

            # Navigate to moves list
            base_driver.load_page(
                page_url=f"https://pokemondb.net/pokedex/{pokemon_name}/moves/1",
                wait_element=True,
                wait_element_id="tabs-moves-1"
            )

            base_driver.lazy_table_to_csv(
                css_selector_table="#tabs-moves-1 > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > "
                                   "table:nth-child(1)",
                csv_name=os.path.join(c.OUTPUT_DIR, f"moves/moves_{r[1]}.csv"),
                use_progress_bar=False
            )
        progress_bar.close()


def main():
    conf = Config(log_level=0, headless_driver=False)

    # First way
    # extract_pokedex_robot(conf)

    # Second way
    extract_pokedex(conf)


if __name__ == "__main__":
    main()
