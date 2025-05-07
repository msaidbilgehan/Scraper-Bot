# Scraper-GMaps-Bot

**Scraper-GMaps-Bot** is a multi-threaded, automated scraper designed to extract business listings from Google Maps based on specified keywords and geolocations. Built with Selenium and Python, it enables scalable data collection with headless browser support and JSON export. License located [here](LICENSE).

---

## 📦 Features

- 🔍 Search businesses by **keywords** and **GPS coordinates**
- 🌐 Supports **headless mode** for performance and deployment
- 🔁 Multi-threaded scraping with real-time status tracking
- 🧭 Automated scrolling and dynamic data loading
- 🗃️ Configurable via YAML
- 💾 Exports data in JSON format
- 📑 Modular and extensible codebase

---

## 🧱 Project Structure

``` shell
Scraper-GMaps-Bot/
├── config.yaml                  # Configuration file (keywords, locations, etc.)
├── main.py                      # Entry point of the application
├── paths.py                     # Logger path definitions
├── test_scraper.py              # Script for testing the scraper
├── Library/
│   ├── tools.py                 # Utilities (YAML reader, logger, JSON writer)
│   └── download_chrome_driver.py # ChromeDriver management (not fully implemented)
├── Modules/
│   ├── module_logger.py         # Logger wrapper
│   ├── module_thread.py         # Threading base class
│   └── module_scraper_gmaps.py  # Google Maps scraper core logic
```

---

## ⚙️ Installation

1. Clone the repository or unzip the package.
2. Install dependencies:

    ```bash

        pip install -r requirements.txt

    ```

3. Download and set up the correct version of ChromeDriver. Ensure it's in your system `PATH` or modify the `download_chrome_driver.py`.

---

## 🚀 Usage

### Step 1: Configure Targets

Edit the `config.yaml` file to define your scraping parameters:

```yaml
headless: true
max_scrolls: 1
delay_url_load: 1.0
delay_target_iteration: 0.5
delay_scroll: 0.5
zoom: 7
keywords: ["AVM", "business", "OSB"]
locations: [
  "41.3976985,33.7469701",  # Kastamonu, Turkey
  "41.0053702,28.6825439" # İstanbul, Turkey
]
output: "results.json"
```

### Step 2: Run the Scraper

```bash
python main.py --config config.yaml
```

This will:

- Load the configuration
- Start Chrome in headless mode
- Combine keywords and locations into Google Maps queries
- Scroll, load, and scrape listing data
- Save results to a JSON file

---

## 🧪 Testing

Use `test_scraper.py` for module testing or extend it to validate scraper outputs.

---

## 🛠️ Developer Notes

- Core scraping logic resides in `module_scraper_gmaps.py`, which inherits from a generic threading class `module_thread.py`.
- Selenium is initialized in headless mode unless disabled via config.
- Data is gathered via keyword-location URL templates and progressively loaded via simulated scrolling.

---

## 📤 Output Format

Results are saved to `results.json`. The format depends on the HTML structure of Google Maps at the time of scraping (data extraction logic can be extended per use case).

---

## ⚠️ Legal Notice

License located [here](LICENSE). Scraping Google Maps may violate its [Terms of Service](https://policies.google.com/terms). Use this tool only for research, testing, or with appropriate permissions.

---

## 📈 Future Improvements

- Add CAPTCHA handling
- Integrate proxy rotation
- Parse contact info from listings
- Implement email automation (referenced in docstring but not included)
