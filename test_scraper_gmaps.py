import time

from Modules.module_scraper_gmaps import ModuleScraperGMaps

is_headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
scraper = ModuleScraperGMaps(
    headless=is_headless
)
scraper.target_add("restaurant", "37.7749", "-122.4194")
scraper.set_search_parameters(
    max_scrolls=1
)

scraper.start_Thread(
    start_task=True
)
# scraper.delay_url_load = 1.
# scraper.delay_target_iteration = 1.
# scraper.delay_scroll = 1.
scraper.delay_url_load = 1.
scraper.delay_target_iteration = 0.
scraper.delay_scroll = 0.5

print(" > Scraper started.")
time_start = time.time()
while True:
    # print("> Targets remaining:", scraper.target_get_count(), end="\r")

    # Simulate some processing
    if scraper.target_get_count() == 0:
        print("> All targets processed.")
        break
    # Sleep for a bit to avoid busy waiting
    time.sleep(1)
time_end = time.time()

results = scraper.results_get()
print(f"> Results in {time_end - time_start:.2f} seconds: {results}")

scraper.stop()
scraper.stop_Thread()
print(" > Stopping scraper...")
scraper.wait_To_Stop_Task()
print(" > Scraper stopped.")
