
import logging
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementClickInterceptedException, StaleElementReferenceException
from ..utils.config_manager import config

class RaterHubPage:
    # --- SELECTORS ---
    # Using robust CSS selectors instead of brittle XPaths
    HELPFULNESS_RADIO = 'input[name="{name}"][value="{value}"]'
    SXS_RADIO = 'input[name="score"][value="{value}"]'
    NONE_CHECKBOX_A = 'input#editable-2555-input' # From previous analysis
    NONE_CHECKBOX_B = 'input#editable-2557-input' # From previous analysis
    COMMENT_BOX = 'textarea[id^="editable-"]' # More flexible selector
    SUBMIT_BUTTON = '#ewok-task-submit-button'
    RELEASE_BUTTON = '#ewok-release-button'

    # --- RATING MAPS ---
    RATING_MAP = {'Not at all helpful': 1, 'Somewhat helpful': 2, 'Somewhat helpful+': 3, 'Mostly helpful': 4, 'Mostly helpful+': 5, 'Very helpful': 6, 'Very helpful+': 7, 'Extremely helpful': 8}
    SXS_MAP = {'Much Better on left': 'MuchBetterThan', 'Better on left': 'BetterThan', 'Slightly Better on left': 'SlightlyBetterThan', 'About The Same': 'AboutTheSameAs', 'Slightly Better on right': 'SlightlyWorseThan', 'Better on right': 'WorseThan', 'Much Better on right': 'MuchWorseThan'}

    def __init__(self, driver):
        self.driver = driver
        # Get WebDriverWait timeout from config, default to 20 seconds
        wait_timeout = config.get('webdriver_timeout', 20)
        self.wait = WebDriverWait(self.driver, wait_timeout)
        logging.info(f"RaterHubPage initialized with WebDriverWait timeout of {wait_timeout} seconds.")

    def take_screenshots(self, count=4):
        """Takes multiple screenshots of the page and returns their paths."""
        logging.info(f"Attempting to take {count} screenshots.")
        paths = []
        try:
            # Scroll to top to start
            self.driver.execute_script("window.scrollTo(0, 0);")
            # Use config for the initial scroll delay
            initial_scroll_delay = config.get('screenshot_scroll_delay', 1.0)
            logging.debug(f"Waiting {initial_scroll_delay} seconds after initial scroll.")
            time.sleep(initial_scroll_delay)

            page_height = self.driver.execute_script("return document.body.scrollHeight")
            logging.debug(f"Page height detected: {page_height} pixels.")

            for i in range(count):
                # Calculate scroll position, handle case count=1 to avoid division by zero
                scroll_pos = (page_height / (count - 1 if count > 1 else 1)) * i
                logging.debug(f"Scrolling to position: {scroll_pos} for screenshot {i+1}/{count}.")
                self.driver.execute_script(f"window.scrollTo(0, {scroll_pos});")

                # Use config for the delay after scrolling and before capturing
                capture_delay = config.get('screenshot_capture_delay', 1.5)
                logging.debug(f"Waiting {capture_delay} seconds before capturing screenshot.")
                time.sleep(capture_delay)

                path = f"screenshot_{i}.png"
                try:
                    self.driver.save_screenshot(path)
                    paths.append(path)
                    logging.debug(f"Saved screenshot to {path}.")
                except WebDriverException as e:
                    logging.warning(f"WebDriverException while saving screenshot {i+1}: {e}. Skipping this screenshot.", exc_info=True)
                except Exception as e:
                    logging.warning(f"An unexpected error occurred while saving screenshot {i+1}: {e}. Skipping this image.", exc_info=True)

            logging.info(f"Finished attempting to take screenshots. {len(paths)} screenshots saved.")
            return paths
        except WebDriverException as e:
            logging.error(f"WebDriverException occurred during screenshot capture: {e}", exc_info=True)
            return [] # Return empty list on failure
        except Exception as e:
            logging.error(f"An unexpected error occurred during screenshot capture: {e}", exc_info=True)
            return [] # Return empty list on failure


    def _click_element(self, by, value, element_name):
        """Helper function to safely wait for and click an element."""
        logging.debug(f"Attempting to click element '{element_name}' using locator By.{by}='{value}'.")
        try:
            # Wait until the element is clickable
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            # Scroll element into view if it's not already
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            # Use config for the small delay after scrolling into view
            post_scroll_delay = config.get('action_post_delay', 0.5)
            logging.debug(f"Waiting {post_scroll_delay} seconds after scrolling element into view.")
            time.sleep(post_scroll_delay)
            element.click()
            logging.info(f"Successfully clicked '{element_name}'.")
            return True
        except TimeoutException:
            logging.warning(f"Timeout: Element '{element_name}' not clickable within the allowed time using locator By.{by}='{value}'.", exc_info=True)
            return False
        except NoSuchElementException:
            logging.warning(f"NoSuchElementException: Element '{element_name}' not found using locator By.{by}='{value}'.", exc_info=True)
            return False
        except ElementClickInterceptedException:
            logging.warning(f"ElementClickInterceptedException: Click on '{element_name}' intercepted. Another element is covering it.", exc_info=True)
            # Could add retry logic or JS click here if needed
            return False
        except StaleElementReferenceException:
            logging.warning(f"StaleElementReferenceException: Element '{element_name}' is no longer attached to the DOM. Retrying might be needed in calling code.", exc_info=True)
            return False
        except WebDriverException as e:
            logging.error(f"WebDriverException occurred while trying to click '{element_name}': {e}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred while trying to click '{element_name}': {e}", exc_info=True)
            return False

    def _fill_text(self, by, value, text, element_name):
        """Helper function to safely wait for and fill text into an element."""
        if not text:
            logging.debug(f"No text provided to fill into '{element_name}'. Skipping.")
            return True # Consider it successful if no text is needed

        logging.debug(f"Attempting to fill text into element '{element_name}' using locator By.{by}='{value}'.")
        try:
            # Wait until the element is present and visible (clickable is often too strict for input)
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            # Use config for the small delay after scrolling into view
            post_scroll_delay = config.get('action_post_delay', 0.5)
            logging.debug(f"Waiting {post_scroll_delay} seconds after scrolling element into view.")
            time.sleep(post_scroll_delay)

            element.clear()
            element.send_keys(text)
            logging.info(f"Successfully filled text into '{element_name}'.")
            return True
        except TimeoutException:
            logging.warning(f"Timeout: Element '{element_name}' not present/visible within the allowed time using locator By.{by}='{value}'.", exc_info=True)
            return False
        except NoSuchElementException:
            logging.warning(f"NoSuchElementException: Element '{element_name}' not found using locator By.{by}='{value}'.", exc_info=True)
            return False
        except StaleElementReferenceException:
            logging.warning(f"StaleElementReferenceException: Element '{element_name}' is no longer attached to the DOM. Retrying might be needed in calling code.", exc_info=True)
            return False
        except WebDriverException as e:
            logging.error(f"WebDriverException occurred while trying to fill text into '{element_name}': {e}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred while trying to fill text into '{element_name}': {e}", exc_info=True)
            return False

    def set_helpfulness(self, response_letter, rating_text):
        """Sets helpfulness by clicking the underlying radio button."""
        name = "helpful1" if response_letter.upper() == 'A' else "helpful2"
        # Default to 'Mostly helpful' (value 4) if rating_text is not found in map or is None
        value = self.RATING_MAP.get(rating_text, 4)

        selector = self.HELPFULNESS_RADIO.format(name=name, value=value)
        element_name = f"Response {response_letter} helpfulness ('{rating_text}')"

        # Use the helper function
        return self._click_element(By.CSS_SELECTOR, selector, element_name)


    def set_sxs_rating(self, sxs_text):
        """Sets the Side-by-Side rating."""
        # Default to 'About The Same' if sxs_text is not found in map or is None
        value = self.SXS_MAP.get(sxs_text, 'AboutTheSameAs')
        selector = self.SXS_RADIO.format(value=value)
        element_name = f"SxS rating ('{sxs_text}')"

        # Use the helper function
        return self._click_element(By.CSS_SELECTOR, selector, element_name)


    def check_none_of_the_above(self):
        """Checks 'None of the Above' checkboxes if they are present and unchecked."""
        logging.info("Checking 'None of the Above' checkboxes if applicable...")
        checkboxes = {
            'A': self.NONE_CHECKBOX_A,
            'B': self.NONE_CHECKBOX_B
        }
        for name, selector in checkboxes.items():
            element_name = f"'None of the Above' checkbox for Response {name}"
            try:
                # Use presence_of_element_located as the checkbox might not be immediately clickable if hidden/styled
                checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if checkbox.is_displayed():
                    logging.debug(f"'{element_name}' is displayed.")
                    if not checkbox.is_selected():
                        logging.info(f"Attempting to check '{element_name}' using selector: {selector}")
                        # Use JavaScript click for maximum reliability with hidden/styled elements
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        logging.info(f"Successfully checked '{element_name}'.")
                    else:
                        logging.info(f"'{element_name}' is already checked.")
                else:
                    logging.debug(f"'{element_name}' is not displayed. Assuming not applicable for this task type.")

            except TimeoutException:
                logging.info(f"Timeout: '{element_name}' not found or not visible within timeout. Assuming not applicable.")
            except NoSuchElementException:
                logging.info(f"NoSuchElementException: '{element_name}' not found. Assuming not applicable.")
            except StaleElementReferenceException:
                logging.warning(f"StaleElementReferenceException: '{element_name}' is no longer attached to the DOM. Skipping.", exc_info=True)
            except WebDriverException as e:
                logging.error(f"WebDriverException occurred while trying to check '{element_name}': {e}", exc_info=True)
            except Exception as e:
                logging.error(f"An unexpected error occurred while trying to check '{element_name}': {e}", exc_info=True)


    def fill_comment(self, comment_text):
        """Fills the explanation into the comment box."""
        if not comment_text or comment_text.lower().strip() == 'none':
            logging.info("No significant comment text provided by AI ('none' or empty). Skipping comment box fill.")
            return True # Consider it successful if no text is needed

        selector = self.COMMENT_BOX
        element_name = "comment box"

        # Use the helper function for filling text
        return self._fill_text(By.CSS_SELECTOR, selector, comment_text, element_name)


    def submit_task(self):
        """Submits the completed task."""
        logging.info("Attempting to click the submit button.")
        selector = self.SUBMIT_BUTTON
        element_name = "submit button"

        success = self._click_element(By.CSS_SELECTOR, selector, element_name)
        if success:
            # Use config for the wait after submit
            submit_wait_delay = config.get('submit_release_wait_delay', 5.0)
            logging.info(f"Clicked submit button. Waiting for {submit_wait_delay} seconds for page to load.")
            time.sleep(submit_wait_delay)
        return success


    def release_task(self):
        """Releases the current task."""
        logging.info("Attempting to click the release task button.")
        selector = self.RELEASE_BUTTON
        element_name = "release task button"

        success = self._click_element(By.CSS_SELECTOR, selector, element_name)
        if success:
            # Use config for the wait after release
            release_wait_delay = config.get('submit_release_wait_delay', 5.0) # Use same delay as submit for consistency or add separate key
            logging.info(f"Clicked release button. Waiting for {release_wait_delay} seconds for page to load.")
            time.sleep(release_wait_delay)
        return success

