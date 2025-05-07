import time
from threading import Lock
import random

from Modules.module_thread import ModuleThread

import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm


class ModuleScraper(ModuleThread):
    """
    This class is used to scrape data from a website.
    """

    def __init__(self, path_driver: str = "", headless: bool = True, version_main: int | None = None, *args, **kwargs):
        kwargs["name"] = "ModuleScraper"
        super(ModuleScraper, self).__init__(*args, **kwargs)

        # Built-in variables
        self.web_driver = self.init_driver(
            path_driver=path_driver,
            headless=headless,
            version_main=version_main,
        )
        self.web_driver.implicitly_wait(10)  # Implicit wait for elements to load

        self.is_running: bool = True

        self.delay_target_iteration: float = 3.0
        self.delay_url_load: float = 3.0

        # Buffers #
        # Targets
        self.buffer_targets: dict[str, dict[str, str]] = {}
        self.buffer_lock_targets = Lock()
        # Results
        self.buffer_results: dict = {}
        self.buffer_lock_results = Lock()

    def target_add(self, url: str, xpath: str, xpath_name: str):
        """
        This method is used to add a target to the buffer.
        """
        self.logger.info(f"Adding {xpath_name} to {url}")
        self.buffer_lock_targets.acquire()
        if url not in self.buffer_targets:
            self.buffer_targets[url] = {}
        self.buffer_targets[url][xpath_name] = xpath
        self.buffer_lock_targets.release()

    def target_remove(self, url: str, xpath_name: str):
        """
        This method is used to add a target to the buffer.
        """
        self.buffer_lock_targets.acquire()
        if url in self.buffer_targets:
            if xpath_name in self.buffer_targets[url]:
                # If the xpath is in the buffer, remove it
                self.logger.info(f"Removing {xpath_name} from {url}")
                del self.buffer_targets[url][xpath_name]
                # If there are no more xpaths in the buffer, remove the url
                if not self.buffer_targets[url]:
                    self.logger.info(f"Removing {url} from buffer")
                    del self.buffer_targets[url]
        self.buffer_lock_targets.release()

    def target_clear(self):
        """
        This method is used to clear the buffer.
        """
        self.buffer_lock_targets.acquire()
        self.buffer_targets = {}
        self.buffer_lock_targets.release()

    def target_get(self):
        """
        This method is used to get the buffer.
        """
        return self.buffer_targets

    def target_get_count(self):
        """
        This method is used to get the count of the buffer.
        """
        self.buffer_lock_targets.acquire()
        count = len(self.buffer_targets)
        self.buffer_lock_targets.release()
        return count

    def target_url_get_count(self, url: str):
        """
        This method is used to get the count of the buffer.
        """
        self.buffer_lock_targets.acquire()
        if url in self.buffer_targets:
            count = len(self.buffer_targets[url])
        else:
            count = 0
        self.buffer_lock_targets.release()
        return count

    def __result_add(self, url: str, xpath_name, data: str | None):
        """
        This method is used to add a result to the buffer.
        """
        self.buffer_lock_results.acquire()
        if url not in self.buffer_results:
            self.buffer_results[url] = {}
        self.buffer_results[url][xpath_name] = data
        self.buffer_lock_results.release()

    # def results_convert(self, results):
    #     """
    #     This method is used to convert the results.
    #     """

    #     # Convert the results for saving in json or yaml respect to the same structure as the buffer_results
    #     results_converted = {}
    #     for keyword, pack in results.items():
    #         if keyword not in results_converted:
    #             results_converted[keyword] = {}
    #         for key_location, data in pack.items():
    #             key_location_str = f"{key_location[0]}, {key_location[1]}"
    #             if key_location_str not in results_converted[keyword]:
    #                 results_converted[keyword][key_location_str] = data
    #             else:
    #                 results_converted[keyword][key_location_str].extend(data)
    #     return results_converted

    def results_get(self):
        """
        This method is used to get the buffer.
        """
        return self.buffer_results

    def results_clear(self):
        """
        This method is used to clear the buffer.
        """
        self.buffer_lock_results.acquire()
        self.buffer_results = {}
        self.buffer_lock_results.release()

    @staticmethod
    def init_driver(path_driver: str = "", headless: bool = True, version_main: int | None = None) -> uc.Chrome:
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        # options.add_argument("--user-data-dir=/path/to/your/Chrome/User Data")
        options.add_argument("--profile-directory=Default")

        return uc.Chrome(options=options, version_main=version_main, driver_executable_path=path_driver if path_driver else None)

    # @staticmethod
    # def extract_information(driver, xpath: str) -> str | None:
    #     try:
    #         element = driver.find_element(By.XPATH, xpath)
    #         return element.text.strip()
    #     except Exception:
    #         return None

    @staticmethod
    def extract_information(driver, xpath: str) -> str | None:
        try:
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text.strip()
        except Exception as e:
            print(f"[ERROR] Failed to extract: {e}")
            return None

    def task(self):
        """
        This method is used to run the module.
        """
        self.logger.info("Scraping task started.")
        self.logger.info(f"Delays -> URL load: {self.delay_url_load}, Target Iteration: {self.delay_target_iteration}")
        while self.is_running:
            # Scrape data from the website
            temp_buffer = self.buffer_targets.copy()
            for url, xpaths in temp_buffer.items():
                self.logger.info(f"Scraping data for {url}")
                # for xpath_name, xpath in xpaths.items():
                for xpath_name, xpath in tqdm(list(xpaths.items()), desc="Extracting Information", unit="it"):
                    self.logger.info(f"Scraping data {xpath_name} -> {xpath}")
                    self.web_driver.get(url)
                    self.logger.info(f"Visiting URL: {url}")
                    time.sleep(self.delay_url_load)

                    # Simulate scroll
                    self.web_driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(random.uniform(1.5, 3.0))

                    # Move mouse randomly
                    actions = ActionChains(self.web_driver)
                    actions.move_by_offset(random.randint(10, 100), random.randint(10, 100)).perform()
                    time.sleep(random.uniform(1.0, 2.0))

                    # Extract data from the page
                    information = self.extract_information(
                        driver=self.web_driver,
                        xpath=xpath,
                    )
                    self.logger.info(f"Extracted information from '{xpath_name}': {information}")

                    # Add the results to the buffer
                    self.__result_add(
                        url=url,
                        xpath_name=xpath_name,
                        data=information,
                    )
                    self.logger.info(f"Added '{information}' to buffer")
                    self.target_remove(url, xpath_name)
                    self.logger.info(f"Removed {xpath_name} from {url} buffer")
                    time.sleep(self.delay_target_iteration)

            # If there are no targets, wait for a while
            if not self.buffer_targets:
                self.logger.info("No targets in buffer, waiting...")
                time.sleep(1)
            else:
                self.logger.info(f"{len(self.buffer_targets)} targets in buffer")
        self.logger.info("Scraping task ended.")
        return 0

    def stop(self):
        """
        This method is used to stop the module.
        """
        self.is_running = False
        self.logger.info("Stopping module...")
        self.web_driver.quit()
        self.logger.info("Module stopped.")
        self.target_clear()
        self.results_clear()
        self.logger.info("Buffers cleared.")
        self.logger.info("ModuleScraper stopped.")
