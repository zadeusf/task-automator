
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from ..utils.config_manager import config

def connect_to_chrome():
    """Connects to an existing Chrome instance with remote debugging."""
    port = config.get('chrome_debug_port', 9222)
    webdriver_timeout = config.get('webdriver_timeout', 30) # Get timeout from config

    logging.info(f"Attempting to connect to Chrome on debugger address 127.0.0.1:{port} with a timeout of {webdriver_timeout} seconds.")

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    try:
        # Use ChromeDriverManager to get the latest driver executable
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info(f"Successfully connected to Chrome on port {port}.")
        return driver
    except SessionNotCreatedException as e:
        logging.error(f"SessionNotCreatedException: Could not connect to Chrome on port {port}. "
                      f"Ensure Chrome is running with --remote-debugging-port={port} and that no other WebDriver session is active. "
                      f"Error details: {e}", exc_info=True)
        return None
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred while connecting to Chrome: {e}. "
                      f"This might be due to network issues, Chrome crashing, or incorrect driver setup.", exc_info=True)
        return None
    except Exception as e:
        # Catch any other unexpected errors during the connection process
        logging.error(f"An unexpected error occurred while attempting to connect to Chrome: {e}", exc_info=True)
        return None
