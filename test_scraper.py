import time

from Modules.module_scraper import ModuleScraper

is_headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
scraper = ModuleScraper(
    headless=is_headless,
    version_main=135,
)
scraper.target_add(
    url="https://stackoverflow.com/questions/49782598/progress-bar-with-tqdm-while-iterating-over-the-items-in-a-python-dictionary",
    xpath="//div[contains(@class, 'accepted-answer')]//div[contains(@class, 'js-post-body')]",
    xpath_name="post_body"
)
scraper.target_add(
    url="https://en.wikipedia.org/wiki/Delayed-choice_quantum_eraser",
    xpath="//div[contains(@id, 'mw-content-text')]",
    xpath_name="post_body"
)

scraper.start_Thread(
    start_task=True
)
scraper.delay_url_load = 3.
scraper.delay_target_iteration = 0.

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
