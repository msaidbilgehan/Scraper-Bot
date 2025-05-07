import time
from threading import Lock

from Modules.module_thread import ModuleThread

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm


class ModuleScraperGMaps(ModuleThread):
    """
    This class is used to scrape data from a website.
    """

    def __init__(self, path_driver: str = "", headless: bool = True, *args, **kwargs):
        kwargs["name"] = "ModuleScraperGMaps"
        super(ModuleScraperGMaps, self).__init__(*args, **kwargs)

        # URLs for Google Maps
        # self.url_gmaps_location = "https://www.google.com/maps/search/{location}"
        self.url_gmaps_keyword = "https://www.google.com/maps/search/{keyword}/@{longitude},{latitude}"

        # Built-in variables
        self.web_driver = self.init_driver(
            path_driver=path_driver,
            headless=headless
        )
        self.web_driver.implicitly_wait(10)  # Implicit wait for elements to load

        self.is_running: bool = True
        self.max_scrolls: int = 10
        self.zoom: int = 10

        self.delay_scroll: float = 2.0
        self.delay_target_iteration: float = 3.0
        self.delay_url_load: float = 3.0

        # XPATHs
        self.xpath_results = "Nv2PK"
        self.xpath_name = "qBF1Pd"
        self.xpath_address: str = './/div[contains(@class, "W4Efsd")]/div[contains(@class, "W4Efsd")]'
        self.xpath_phone = './/span[contains(@class, "UsdlK")]'
        self.xpath_website = './/a[contains(@aria-label, "Visit")]'

        # Buffers
        self.buffer_targets: dict = {}
        self.buffer_targets_lock = Lock()
        self.buffer_results: dict = {}
        self.buffer_results_lock = Lock()

    def set_xpaths(
        self,
        xpath_results: str = "",
        xpath_name: str = "",
        xpath_address: str = "",
        xpath_phone: str = "",
        xpath_website: str = ""
    ):
        """
        This method is used to set the XPATHs.
        """
        if xpath_results:
            self.xpath_results = xpath_results
        if xpath_name:
            self.xpath_name = xpath_name
        if xpath_address:
            self.xpath_address = xpath_address
        if xpath_phone:
            self.xpath_phone = xpath_phone
        if xpath_website:
            self.xpath_website = xpath_website

        self.logger.info(f"XPATHs set to: {self.xpath_results}, {self.xpath_name}, {self.xpath_address}, {self.xpath_phone}, {self.xpath_website}")

    def target_add(self, keyword: str, latitude: str, longitude: str):
        """
        This method is used to add a target to the buffer.
        """
        self.buffer_targets_lock.acquire()
        if keyword in self.buffer_targets:
            self.buffer_targets[keyword].append((latitude, longitude))
        else:
            # If the keyword is not in the buffer, add it with the coordinates
            self.buffer_targets[keyword] = [(latitude, longitude)]
        self.buffer_targets_lock.release()

    def target_remove(self, keyword: str, latitude: str, longitude: str):
        """
        This method is used to add a target to the buffer.
        """
        self.buffer_targets_lock.acquire()
        if keyword in self.buffer_targets:
            if (latitude, longitude) in self.buffer_targets[keyword]:
                self.buffer_targets[keyword].remove((latitude, longitude))
                if not self.buffer_targets[keyword]:
                    del self.buffer_targets[keyword]
        self.buffer_targets_lock.release()

    def target_clear(self):
        """
        This method is used to clear the buffer.
        """
        self.buffer_targets_lock.acquire()
        self.buffer_targets = {}
        self.buffer_targets_lock.release()

    def target_get(self):
        """
        This method is used to get the buffer.
        """
        return self.buffer_targets

    def target_get_count(self):
        """
        This method is used to get the count of the buffer.
        """
        self.buffer_targets_lock.acquire()
        count = len(self.buffer_targets)
        self.buffer_targets_lock.release()
        return count

    def __result_add(self, keyword: str, latitude: str, longitude: str, data: dict):
        """
        This method is used to add a result to the buffer.
        """
        self.buffer_results_lock.acquire()
        if keyword in self.buffer_results:
            if (latitude, longitude) not in self.buffer_results[keyword]:
                # If the coordinates are not in the buffer, add them with the data
                self.buffer_results[keyword][(latitude, longitude)] = [data]
            else:
                self.buffer_results[keyword][(latitude, longitude)].append(data)
        else:
            # If the keyword is not in the buffer, add it with the coordinates
            self.buffer_results[keyword] = {}
            self.buffer_results[keyword][(latitude, longitude)] = [data]
        self.buffer_results_lock.release()

    def __result_add_bulk(self, keyword: str, latitude: str, longitude: str, data: list[dict]):
        """
        This method is used to add a result to the buffer.
        """
        self.buffer_results_lock.acquire()
        if keyword in self.buffer_results:
            if (latitude, longitude) not in self.buffer_results[keyword]:
                # If the coordinates are not in the buffer, add them with the data
                self.buffer_results[keyword][(latitude, longitude)] = data
            else:
                # If the coordinates are already in the buffer, extend the list with new data
                self.buffer_results[keyword][(latitude, longitude)].extend(data)
        else:
            # If the keyword is not in the buffer, add it with the coordinates
            self.buffer_results[keyword] = {}
            self.buffer_results[keyword][(latitude, longitude)] = data
        self.buffer_results_lock.release()

    def results_convert(self, results):
        """
        This method is used to convert the results.
        """

        # Convert the results for saving in json or yaml respect to the same structure as the buffer_results
        results_converted = {}
        for keyword, pack in results.items():
            if keyword not in results_converted:
                results_converted[keyword] = {}
            for key_location, data in pack.items():
                key_location_str = f"{key_location[0]}, {key_location[1]}"
                if key_location_str not in results_converted[keyword]:
                    results_converted[keyword][key_location_str] = data
                else:
                    results_converted[keyword][key_location_str].extend(data)
        return results_converted

    def results_get(self):
        """
        This method is used to get the buffer.
        """
        return self.buffer_results

    def results_clear(self):
        """
        This method is used to clear the buffer.
        """
        self.buffer_results_lock.acquire()
        self.buffer_results = {}
        self.buffer_results_lock.release()

    # def build_maps_location_url(self, location: str = "İstanbul"):
    #     """
    #     This method is used to build the URL for the Google Maps location.
    #     """
    #     return self.url_gmaps_location.format(location=location)

    def build_maps_search_url(self, keyword: str = "business", latitude: str = "0.0", longitude: str = "0.0", zoom: int = 10):
        if zoom < 1 or zoom > 21:
            return self.url_gmaps_keyword.format(
                keyword=keyword,
                latitude=latitude,
                longitude=longitude,
            )
        else:
            url = self.url_gmaps_keyword
            url += ",{zoom}z"
            return url.format(
                keyword=keyword,
                latitude=latitude,
                longitude=longitude,
                zoom=zoom
            )

    @staticmethod
    def init_driver(path_driver: str = "", headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # if path_driver:
        #     options.add_argument(f"user-data-dir={path_driver}")

        if path_driver:
            from selenium.webdriver.chrome.service import Service
            service = Service(path_driver)
            return webdriver.Chrome(service=service)
        else:
            return webdriver.Chrome(options=options)

    @staticmethod
    def scroll_results(driver, pause_time: float = 2., max_scrolls: int = 10, scrollable_div_xpath: str = '//div[@role="feed"]'):
        for _ in range(max_scrolls):
            try:
                scroll_box = driver.find_element(By.XPATH, scrollable_div_xpath)
                driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollHeight',
                    scroll_box
                )
                time.sleep(pause_time)
            except Exception:
                break

    @staticmethod
    def extract_places(driver, xpath_results: str, xpath_name: str, xpath_address: str, xpath_phone: str, xpath_website: str):
        places = []
        # Extract the places from the results
        cards = driver.find_elements(By.CLASS_NAME, xpath_results)

        # Extract the name, address, phone, and website from each card
        for card in tqdm(cards, desc="Extracting places", unit="it"):
            # Name
            try:
                name = card.find_element(By.CLASS_NAME, xpath_name).text
            except Exception:
                name = None

            # Address
            try:
                address_element = card.find_element(By.XPATH, xpath_address)
                address = address_element.text if address_element else None
            except Exception:
                address = None

            # Phone
            try:
                phone_element = card.find_element(By.XPATH, xpath_phone)
                phone = phone_element.text if phone_element else None
            except Exception:
                phone = None

            # Website
            try:
                website_element = card.find_element(By.XPATH, xpath_website)
                website = website_element.get_attribute('href') if website_element else None
            except Exception:
                website = None

            places.append({
                'name': name,
                'address': address,
                'phone': phone,
                'website': website
            })

        return places

    def set_search_parameters(self, max_scrolls: int = 10, zoom: int = 10):
        """
        This method is used to set the search parameters.
        """
        self.max_scrolls = max_scrolls
        self.zoom = zoom

    def task(self):
        """
        This method is used to run the module.
        """
        self.logger.info("Scraping task started.")
        self.logger.info(f"Delays -> URL load: {self.delay_url_load}, Scroll: {self.delay_scroll}, Target Iteration: {self.delay_target_iteration}")
        self.logger.info(f"Scroll {self.max_scrolls} times")
        while self.is_running:
            # Scrape data from the website
            temp_buffer = self.buffer_targets.copy()
            for keyword, coordinates in temp_buffer.items():
                for latitude, longitude in coordinates:
                    self.logger.info(f"Scraping data for {keyword} at {latitude}, {longitude}")
                    url = self.build_maps_search_url(keyword, latitude, longitude, zoom=self.zoom)
                    self.web_driver.get(url)
                    self.logger.info(f"Visiting URL: {url}")
                    time.sleep(self.delay_url_load)

                    # Scroll through the results
                    self.scroll_results(
                        driver=self.web_driver,
                        pause_time=self.delay_scroll,
                        max_scrolls=self.max_scrolls
                    )

                    # Extract data from the results
                    places = self.extract_places(
                        driver=self.web_driver,
                        xpath_results=self.xpath_results,
                        xpath_name=self.xpath_name,
                        xpath_address=self.xpath_address,
                        xpath_phone=self.xpath_phone,
                        xpath_website=self.xpath_website
                    )
                    self.logger.info(f"Extracted {len(places)} places from {keyword} at {latitude}, {longitude}")

                    # Add the results to the buffer
                    self.__result_add_bulk(
                        keyword=keyword,
                        latitude=latitude,
                        longitude=longitude,
                        data=places
                    )
                    self.logger.info(f"Added {len(places)} places to buffer")
                    self.target_remove(keyword, latitude, longitude)
                    self.logger.info(f"Removed {keyword} at {latitude}, {longitude} from buffer")
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
        self.logger.info("ModuleScraperGMaps stopped.")
