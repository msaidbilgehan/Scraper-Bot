#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Business Scraper & Emailer

A multi-threaded application for scraping business information from Google Maps
and sending personalized emails.
"""

import argparse
import time

from paths import DIR_LOGGER_MAIN, DIR_LOGGER_SCRAPER
from Library.tools import create_logger, read_yaml, saveJsonFile
from Modules.module_scraper_gmaps import ModuleScraperGMaps


def arg_parser():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="GMaps Scraper")
    parser.add_argument(
        "--config",
        type=str,
        default="",
        help="Path to the YAML configuration file."
    )

    return parser.parse_args()


def main():
    """Main entry point for the application."""

    # Create logger
    logger = create_logger(
        name="GMaps Scraper",
        path=DIR_LOGGER_MAIN,
        maxBytes=1 * 1024 * 1024,
    )
    logger.info("Starting GMaps Scraper...")

    # Parse command-line arguments
    args = arg_parser()

    # Load configuration
    if args.config == "":
        args.config = "config.yaml"
    config = read_yaml(args.config)

    logger.info(f"Configuration loaded from {args.config}")
    logger.info(f"Parameters: {config}")

    # Initialize the scraper module
    scraper = ModuleScraperGMaps(
        headless=config["headless"],
        logger_file_path=DIR_LOGGER_SCRAPER,
    )
    logger.info("Scraper initialized.")

    # Add targets to the scraper
    # Parse locations from string format: "lat, lon"
    locations = [
        tuple(map(str, loc.strip().split(",")))
        for loc in config["locations"]
    ]
    logger.info(f"Locations parsed ({len(locations)}): {locations}")
    logger.info(f"Keywords parsed ({len(config['keywords'])}): {config['keywords']}")

    # Create combinations of keywords and locations
    for keyword in config["keywords"]:
        for latitude, longitude in locations:
            scraper.target_add(
                keyword=keyword,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
            )

    scraper.set_search_parameters(
        max_scrolls=config["max_scrolls"],
        zoom=config["zoom"]
    )

    scraper.start_Thread(
        start_task=True
    )
    scraper.delay_url_load = config["delay_url_load"]
    scraper.delay_target_iteration = config["delay_target_iteration"]
    scraper.delay_scroll = config["delay_scroll"]

    logger.info("Scraper started.")
    time_start = time.time()
    while True:
        if scraper.target_get_count() == 0:
            logger.info("All targets processed.")
            break
        # Sleep for a bit to avoid busy waiting
        time.sleep(1)
    time_end = time.time()

    results = scraper.results_get()
    results_converted = scraper.results_convert(results)

    saveJsonFile(config["output"], results_converted)
    logger.info(f"Results in {time_end - time_start:.2f} seconds: {results_converted}")

    scraper.stop()
    scraper.stop_Thread()
    logger.info("Stopping scraper...")
    scraper.wait_To_Stop_Task()
    logger.info("Scraper stopped.")


if __name__ == "__main__":
    main()
