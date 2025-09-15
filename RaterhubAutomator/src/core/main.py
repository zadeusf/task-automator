
import logging
import os
import time
import subprocess
import sys
import threading
import socket
import shutil

from .browser_manager import connect_to_chrome
from ..ai.ai_analyzer import AIAnalyzer, parse_ai_response
from .raterhub_page import RaterHubPage
from ..utils.config_manager import config # Import the config instance


def setup_logging():
    """Sets up basic logging configuration."""
    log_level = config.get('logging', {}).get('level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO), # Safely get log level
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[logging.StreamHandler()] # Using StreamHandler for console output
        # For file logging, a FileHandler would be added here, potentially using config for path/rotation
    )
    logging.info("Logging configured.")


def process_single_task(driver, analyzer, page):
    """Orchestrates the processing of a single RaterHub task."""
    logging.info("Starting processing of a single task.")
    screenshot_paths = []
    try:
        # 1. Capture page state
        logging.info(f"Attempting to take {config.get('screenshot_count', 4)} screenshots.")
        screenshot_paths = page.take_screenshots(config.get('screenshot_count', 4))
        logging.info(f"Captured {len(screenshot_paths)} screenshots.")

        # 2. Analyze with AI
        if not screenshot_paths:
             logging.warning("No screenshots captured. Skipping AI analysis.")
             parsed_data = {'action': 'release', 'explanation': 'No screenshots captured.'}
        else:
            logging.info(f"Sending {len(screenshot_paths)} screenshots to AI for analysis.")
            raw_response = analyzer.analyze_screenshots(screenshot_paths)
            logging.info("Received raw AI response.")
            
            # 3. Parse AI response
            logging.info("Parsing AI response.")
            parsed_data = parse_ai_response(raw_response)
            logging.info(f"Parsed AI response: {parsed_data}")
            
            # Clean up screenshots after successful AI analysis and parsing
            for path in screenshot_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        logging.debug(f"Removed screenshot file: {path}")
                except OSError as e:
                    logging.warning(f"Error removing screenshot file {path}: {e}")
            # Clear the list to avoid double cleanup in finally block
            screenshot_paths = []

        # 4. Interact with the page based on parsed action
        action = parsed_data.get('action')
        logging.info(f"Determined action from AI analysis: {action}")

        if action == 'release':
            logging.info("AI requested task release.")
            page.release_task()
            logging.info("Task released.")
        elif action == 'rate':
            logging.info("AI requested task rating and submission.")
            page.check_none_of_the_above()
            page.set_helpfulness('A', parsed_data.get('a_rating', ''))
            page.set_helpfulness('B', parsed_data.get('b_rating', ''))
            page.set_sxs_rating(parsed_data.get('sxs', ''))
            page.fill_comment(parsed_data.get('explanation', ''))

            if config.get('auto_submit', False):
                logging.info("Auto-submit is enabled. Attempting to submit task.")
                page.submit_task()
                logging.info("Task submission initiated (check logs for outcome).")
            else:
                logging.info("Auto-submit is disabled. Pausing for manual review before submission.")
        else:
            logging.warning(f"Unknown action '{action}' received from AI. Defaulting to releasing task.")
            page.release_task()
            logging.info("Task released due to unknown AI action.")


    except Exception as e:
        logging.error(f"An unhandled error occurred during task processing: {e}", exc_info=True)
        # Attempt to release the task as a safe fallback in case of unhandled errors
        logging.warning("Attempting to release task due to unhandled error.")
        try:
            page.release_task()
            logging.info("Task successfully released after unhandled error.")
        except Exception as release_e:
            logging.error(f"Failed to release task after unhandled error: {release_e}", exc_info=True)
    finally:
        # Ensure any remaining screenshots are cleaned up even if errors occurred
        for path in screenshot_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logging.debug(f"Removed remaining screenshot file in finally block: {path}")
                except OSError as e:
                    logging.warning(f"Error removing remaining screenshot file {path}: {e}")


def main():
    """Main function to run the RaterHub automation loop."""
    setup_logging()
    logging.info("RaterHub Automator started.")

    driver = None
    try:
        logging.info("Attempting to connect to Chrome browser.")
        driver = connect_to_chrome()
        if not driver:
            logging.error("Failed to connect to Chrome. Exiting.")
            return
        logging.info("Successfully connected to Chrome.")

        logging.info("Initializing AI Analyzer.")
        analyzer = AIAnalyzer()
        logging.info("AI Analyzer initialized.")

        logging.info("Initializing RaterHub Page object.")
        page = RaterHubPage(driver)
        logging.info("RaterHub Page object initialized.")


        loop_tasks = config.get('loop_tasks', False)
        logging.info(f"Task looping is {'enabled' if loop_tasks else 'disabled'}.")

        while True:
            logging.info("--- Starting next task iteration ---")
            process_single_task(driver, analyzer, page)
            logging.info("--- Task iteration finished ---")

            if not loop_tasks:
                logging.info("Looping is disabled. Automation finished.")
                break

            delay = config.get('delay_seconds', 2)
            logging.info(f"Waiting for {delay} seconds before next task.")
            time.sleep(delay)

    except Exception as e:
        logging.critical(f"A critical error occurred in the main loop: {e}", exc_info=True)
    finally:
        if driver:
            logging.info("Closing browser.")
            driver.quit()
            logging.info("Browser closed.")
        logging.info("RaterHub Automator finished.")


if __name__ == "__main__":
    main()
