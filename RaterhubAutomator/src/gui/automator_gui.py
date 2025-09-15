
import PySimpleGUI as sg
import subprocess
import sys
import threading
import time
import socket
import logging
import os
import shutil

from ..utils.config_manager import config
from ..core.browser_manager import connect_to_chrome
from ..ai.ai_analyzer import AIAnalyzer, parse_ai_response
from ..core.raterhub_page import RaterHubPage


def setup_logging():
    """Sets up basic logging."""
    logging_config = config.get('logging', {})
    log_level = logging_config.get('level', 'INFO').upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        logging.warning(f"Invalid log level '{log_level}' specified in config. Using INFO.")
        numeric_level = logging.INFO

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.info("Logging setup complete.")

def is_port_open(host='127.0.0.1', port=9222):
    """Checks if a given port is open."""
    # Validate port range
    if not (0 <= port <= 65535):
        logging.error(f"Invalid port number: {port}. Port must be between 0 and 65535.")
        return False
        
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(config.get('port_check_timeout', 1))
    try:
        sock.connect((host, port))
        sock.close()
        logging.info(f"Port {port} is open.")
        return True
    except (socket.timeout, ConnectionRefusedError):
        logging.debug(f"Port {port} is not open or connection was refused.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while checking port {port}: {e}", exc_info=True)
        return False

def launch_chrome_debug(port=9222, user_data_dir=None):
    """Launches Chrome with remote debugging enabled."""
    chrome_path = config.get('chrome_path', r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not os.path.exists(chrome_path):
        logging.error(f"Chrome executable not found at '{chrome_path}'. Please update config.json or install Chrome.")
        return None, None

    temp_dir = user_data_dir or config.get('chrome_user_data_dir', None)
    if temp_dir is None:
        temp_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), "raterhub_chrome_debug")
        logging.debug(f"Using default temporary directory for Chrome: {temp_dir}")

    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            logging.info(f"Created Chrome user data directory: {temp_dir}")
        except OSError as e:
            logging.error(f"Error creating Chrome user data directory '{temp_dir}': {e}", exc_info=True)
            return None, None

    args = [
        chrome_path,
        f'--remote-debugging-port={port}',
        f'--user-data-dir="{temp_dir}"',
        '--profile-directory="DebugProfile"',
        '--remote-allow-origins=*',
        '--no-first-run',
        '--disable-infobars',
        '--disable-extensions'
    ]
    logging.info(f"Launching Chrome with arguments: {' '.join(args)}")
    try:
        process = subprocess.Popen(args, shell=False)
        logging.info(f"Chrome launched with PID: {process.pid}")
        return process, temp_dir
    except FileNotFoundError:
        logging.error(f"Error: Chrome executable not found at '{chrome_path}'.", exc_info=True)
        return None, None
    except Exception as e:
        logging.error(f"An error occurred while launching Chrome: {e}", exc_info=True)
        return None, None

class AutomatorGUI:
    def __init__(self):
        logging.info("Initializing AutomatorGUI.")
        # sg.theme(config.get('gui_theme', 'LightBlue3')) # Temporarily removed due to AttributeError

        layout = [
            [sg.Text("RaterHub Automator", font=('Helvetica', 15, 'bold'))],
            [sg.Button("Run Full Automation", key='-RUN-', size=(20, 2)),
             sg.Button("Test Port & Logs", key='-TEST_PORT_LOGS-', size=(20, 2)),
             sg.Button("Kill Chrome", key='-KILL_CHROME-', size=(20, 2)),
             sg.Button("Exit", key='-EXIT-', size=(10, 2))],
            [sg.HorizontalSeparator()],
            [sg.Text("Output Log:", font=('Helvetica', 12))],
            [sg.Output(size=(100, 25), key='-OUTPUT-', font=('Courier New', 10), echo_stdout_stderr=True)]
        ]

        self.window = sg.Window("RaterHub Automator", layout, finalize=True)

        setup_logging()

        self.chrome_process = None
        self.temp_dir = None
        self._automation_thread = None
        self._stop_event = threading.Event()

    def run(self):
        """Runs the main GUI event loop."""
        logging.info("Starting GUI event loop.")
        while True:
            event, values = self.window.read(timeout=100)

            if event == sg.WIN_CLOSED or event == '-EXIT-':
                logging.info("Exit button clicked or window closed. Initiating shutdown.")
                self._stop_automation_thread()
                self._cleanup()
                break

            if event == '-RUN-':
                logging.info("Run Full Automation button clicked.")
                if self._automation_thread and self._automation_thread.is_alive():
                    logging.warning("Automation is already running.")
                    sg.popup_non_blocking("Automation is already running. Please wait for it to complete.")
                else:
                    self._stop_event.clear()
                    logging.info("Starting automation thread.")
                    self._automation_thread = threading.Thread(target=self._run_automation_thread, args=(self._stop_event, self.window.write_event_queue,), daemon=True)
                    self._automation_thread.start()
                    self.window['-RUN-'].update(disabled=True)
                    self.window['-TEST_PORT_LOGS-'].update(disabled=True)
                    self.window['-KILL_CHROME-'].update(disabled=True)

            if event == '-TEST_PORT_LOGS-':
                logging.info("Test Port & Logs button clicked.")
                threading.Thread(target=self._test_port_and_logs, daemon=True).start()

            if event == '-KILL_CHROME-':
                logging.info("Kill Chrome button clicked.")
                threading.Thread(target=self._kill_chrome, daemon=True).start()

            if event == '-AUTOMATION_STATUS-':
                 status_message = values['-AUTOMATION_STATUS-']
                 logging.info(f"Automation Status: {status_message}")
                 if status_message == 'Finished' or status_message.startswith('Error') or status_message == 'ThreadExited':
                     self.window['-RUN-'].update(disabled=False)
                     self.window['-TEST_PORT_LOGS-'].update(disabled=False)
                     self.window['-KILL_CHROME-'].update(disabled=False)

    def _run_automation_thread(self, stop_event, event_queue):
        """The target function for the automation thread."""
        logging.info("Automation worker thread started.")
        driver = None
        try:
            port = config.get('chrome_debug_port', 9222)
            if is_port_open(port=port):
                logging.info(f"Existing Chrome session detected on port {port}. Skipping launch and using current session.")
            else:
                logging.info(f"No session on port {port}. Launching new Chrome with debug port...")
                self.chrome_process, self.temp_dir = launch_chrome_debug(port=port)
                if not self.chrome_process:
                    logging.error("Failed to launch Chrome.")
                    event_queue.put(('-AUTOMATION_STATUS-', 'Error: Failed to launch Chrome'))
                    return

                launch_timeout = config.get('chrome_launch_timeout', 30)
                logging.info(f"Waiting up to {launch_timeout} seconds for Chrome debug port {port} to open.")
                start_time = time.time()
                while not is_port_open(port=port) and (time.time() - start_time) < launch_timeout and not stop_event.is_set():
                    time.sleep(0.5)

                if not is_port_open(port=port):
                    if stop_event.is_set():
                        logging.info("Port check interrupted by stop signal.")
                    else:
                        logging.error(f"Port {port} still not open after {launch_timeout} seconds.")
                        event_queue.put(('-AUTOMATION_STATUS-', f'Error: Port {port} not open after {launch_timeout}s'))
                        self._cleanup_chrome()
                        return

            if stop_event.is_set():
                logging.info("Automation thread received stop signal before connecting to WebDriver.")
                return

            logging.info("Connecting to Chrome via Selenium WebDriver.")
            driver = connect_to_chrome()
            if not driver:
                logging.error("Failed to connect to WebDriver.")
                event_queue.put(('-AUTOMATION_STATUS-', 'Error: Failed to connect to WebDriver'))
                return

            logging.info("WebDriver connected. Initializing AIAnalyzer and RaterHubPage.")
            analyzer = AIAnalyzer()
            page = RaterHubPage(driver)

            loop_tasks = config.get('loop_tasks', False)
            logging.info(f"Loop tasks is set to: {loop_tasks}")

            task_count = 0
            while not stop_event.is_set():
                task_count += 1
                logging.info(f"--- Processing Task #{task_count} ---")
                try:
                    self._process_single_task(driver, analyzer, page)
                except Exception as e:
                    logging.error(f"An unhandled error occurred while processing task #{task_count}: {e}", exc_info=True)
                    logging.warning("Attempting to release task due to unhandled error.")
                    try:
                        page.release_task()
                    except Exception as release_e:
                        logging.error(f"Failed to release task after error: {release_e}", exc_info=True)

                if not loop_tasks:
                    logging.info("Looping is disabled. Automation finished after one task.")
                    break

                if not stop_event.is_set():
                    logging.info(f"Task #{task_count} finished. Waiting for next task...")
                    delay = config.get('delay_seconds', 2)
                    logging.info(f"Waiting {delay} seconds before checking for the next task.")
                    stop_event.wait(delay)

            logging.info("Automation loop finished or stopped.")
            event_queue.put(('-AUTOMATION_STATUS-', 'Finished'))

        except Exception as e:
            logging.critical(f"Critical error in automation worker thread: {e}", exc_info=True)
            event_queue.put(('-AUTOMATION_STATUS-', f'Error: Critical error occurred - {e}'))

        finally:
            if driver:
                try:
                    logging.info("Quitting WebDriver in automation thread.")
                    driver.quit()
                except Exception as quit_e:
                    logging.warning(f"Error quitting WebDriver in automation thread: {quit_e}", exc_info=True)

            logging.info("Automation worker thread finished execution.")
            event_queue.put(('-AUTOMATION_STATUS-', 'ThreadExited'))

    def _stop_automation_thread(self):
        """Signals the automation thread to stop."""
        if self._automation_thread and self._automation_thread.is_alive():
            logging.info("Signaling automation thread to stop.")
            self._stop_event.set()

    def _process_single_task(self, driver, analyzer, page):
        """Orchestrates the processing of a single RaterHub task."""
        if self._stop_event.is_set():
            logging.info("Stop signal received during task processing. Aborting task.")
            return

        logging.info("Starting processing of a single task.")
        screenshot_paths = []
        try:
            screenshot_count = config.get('screenshot_count', 4)
            logging.info(f"Capturing {screenshot_count} screenshots.")
            screenshot_paths = page.take_screenshots(screenshot_count)
            if not screenshot_paths:
                logging.error("Failed to capture any screenshots. Cannot proceed with analysis.")
                page.release_task()
                return

            if self._stop_event.is_set():
                logging.info("Stop signal received after screenshots. Aborting task.")
                self._cleanup_screenshots(screenshot_paths)
                return

            logging.info("Analyzing screenshots with AI.")
            raw_response = analyzer.analyze_screenshots(screenshot_paths)
            logging.info(f"Raw AI response received: {raw_response[:200]}...")

            self._cleanup_screenshots(screenshot_paths)
            screenshot_paths = []

            if self._stop_event.is_set():
                logging.info("Stop signal received after AI analysis. Aborting task.")
                return

            logging.info("Parsing AI response.")
            parsed_data = parse_ai_response(raw_response)

            action = parsed_data.get('action')
            logging.info(f"AI parsed action: {action}")

            if action == 'release':
                logging.info("AI action is 'release'. Releasing task.")
                page.release_task()
                return

            elif action == 'rate':
                logging.info("AI action is 'rate'. Attempting to fill form.")
                required_keys = ['a_rating', 'b_rating', 'sxs', 'explanation']
                if not all(key in parsed_data for key in required_keys):
                    logging.error(f"Parsed data for 'rate' action is missing required keys: {required_keys}. Defaulting to release.")
                    logging.debug(f"Parsed data: {parsed_data}")
                    page.release_task()
                    return

                page.check_none_of_the_above()
                page.set_helpfulness('A', parsed_data['a_rating'])
                page.set_helpfulness('B', parsed_data['b_rating'])
                page.set_sxs_rating(parsed_data['sxs'])
                page.fill_comment(parsed_data['explanation'])

                auto_submit = config.get('auto_submit', False)
                if auto_submit:
                    logging.info("Auto-submit is enabled. Submitting task.")
                    page.submit_task()
                else:
                    logging.info("Auto-submit is disabled. Pausing for manual review before submitting.")
                    sg.popup_ok_non_blocking("Automation complete. Please review the ratings and submit manually if needed.")

            else:
                logging.warning(f"Unknown AI action '{action}'. Defaulting to release.")
                page.release_task()

        except Exception as e:
            logging.error(f"An unhandled error occurred during single task processing: {e}", exc_info=True)
            logging.warning("Attempting to release task due to error.")
            try:
                page.release_task()
            except Exception as release_e:
                logging.error(f"Failed to release task after error: {release_e}", exc_info=True)
        finally:
            self._cleanup_screenshots(screenshot_paths)

    def _test_port_and_logs(self):
        """Tests the Chrome debug port and displays netstat output (run in a thread)."""
        port = config.get('chrome_debug_port', 9222)
        logging.info(f"Testing port {port}...")
        if is_port_open(port=port):
            logging.info(f"Success: Port {port} is open!")
        else:
            logging.warning(f"Error: Port {port} is not open. Ensure Chrome is running with --remote-debugging-port={port}.")

        logging.info("Netstat check for port 9222:")
        try:
            netstat_command = f'netstat -ano | findstr ":{port}"'
            logging.debug(f"Executing netstat command: {netstat_command}")

            netstat_result = subprocess.run(
                netstat_command,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )

            if netstat_result.returncode == 0:
                 logging.info("Netstat output:")
                 logging.info(netstat_result.stdout.strip())
            elif netstat_result.returncode == 1:
                 logging.info(f"Netstat found no processes using port {port}.")
            else:
                 logging.warning(f"Netstat command failed with return code {netstat_result.returncode}. Stdout: {netstat_result.stdout.strip()} Stderr: {netstat_result.stderr.strip()}")

        except FileNotFoundError:
             logging.error("Netstat command not found. Ensure it's in your system's PATH.")
        except Exception as e:
            logging.error(f"An error occurred during netstat check: {e}", exc_info=True)

    def _kill_chrome(self):
        """Terminates all Chrome processes (run in a thread)."""
        logging.warning("Attempting to kill all Chrome processes.")
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'], check=True, capture_output=True, text=True, shell=False)
            logging.info("All Chrome processes killed successfully.")
        except FileNotFoundError:
            logging.error("taskkill command not found. This function is for Windows only or taskkill is not in PATH.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to kill Chrome processes. Command failed with return code {e.returncode}. Stdout: {e.stdout.strip()} Stderr: {e.stderr.strip()}", exc_info=True)
        except Exception as e:
            logging.error(f"An unexpected error occurred while trying to kill Chrome: {e}", exc_info=True)

        self._cleanup_chrome()

    def _cleanup(self):
        """Performs cleanup before exiting."""
        logging.info("Performing cleanup.")
        self._stop_automation_thread()
        if self._automation_thread and self._automation_thread.is_alive():
            logging.info("Waiting briefly for automation thread to finish cleanup.")
            self._automation_thread.join(timeout=2)

        self._cleanup_chrome()
        self._cleanup_temp_dir()

    def _cleanup_chrome(self):
        """Terminates the specific Chrome process launched by the GUI."""
        if self.chrome_process and self.chrome_process.poll() is None:
            logging.info(f"Terminating Chrome process with PID {self.chrome_process.pid}.")
            try:
                self.chrome_process.terminate()
                try:
                    self.chrome_process.wait(timeout=5)
                    logging.info("Chrome process terminated.")
                except subprocess.TimeoutExpired:
                    logging.warning(f"Chrome process {self.chrome_process.pid} did not terminate within 5 seconds. Forcing kill.")
                    self.chrome_process.kill()
                    self.chrome_process.wait()
                    logging.info("Chrome process forcefully killed.")
            except Exception as e:
                logging.warning(f"Error terminating Chrome process: {e}", exc_info=True)
            self.chrome_process = None
        elif self.chrome_process and self.chrome_process.poll() is not None:
            logging.debug(f"Chrome process (PID {self.chrome_process.pid}) was already terminated.")
            self.chrome_process = None

    def _cleanup_temp_dir(self):
        """Removes the temporary user data directory if it was created by the GUI."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            logging.info(f"Attempting to remove temporary Chrome user data directory: {self.temp_dir}")
            try:
                expected_name = "raterhub_chrome_debug"
                if os.path.basename(self.temp_dir) == expected_name and (
                    os.path.normpath(os.path.dirname(self.temp_dir)) == os.path.normpath(os.environ.get('TEMP', os.path.expanduser('~'))) or
                    os.path.normpath(self.temp_dir) == os.path.normpath(config.get('chrome_user_data_dir', ''))
                ):
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                    logging.info(f"Removed temporary directory: {self.temp_dir}")
                else:
                    logging.warning(f"Safety check failed: Directory {self.temp_dir} does not match expected pattern for cleanup. Skipping removal.")
            except Exception as e:
                logging.warning(f"Error removing temporary directory '{self.temp_dir}': {e}", exc_info=True)
            self.temp_dir = None

    def _cleanup_screenshots(self, screenshot_paths):
        """Cleans up temporary screenshot files."""
        logging.info(f"Cleaning up {len(screenshot_paths)} screenshot files.")
        for path in screenshot_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logging.debug(f"Removed screenshot file: {path}")
                except OSError as e:
                    logging.warning(f"Error removing screenshot file '{path}': {e}", exc_info=True)
                except Exception as e:
                    logging.warning(f"An unexpected error occurred while removing screenshot file '{path}': {e}", exc_info=True)

if __name__ == "__main__":
    logging.info("Script executed directly. Starting Automator GUI.")
    gui = AutomatorGUI()
    gui.run()
    logging.info("Automator GUI application finished.")
