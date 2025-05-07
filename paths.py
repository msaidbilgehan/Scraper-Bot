from pathlib import Path


DIR_LOGGER_ROOT = Path(__file__).parent / 'logs'
DIR_LOGGER_ROOT.mkdir(parents=True, exist_ok=True)

DIR_LOGGER_MAIN = DIR_LOGGER_ROOT / 'business_scraper.log'

DIR_LOGGER_SCRAPER = DIR_LOGGER_ROOT / 'scraper.log'
