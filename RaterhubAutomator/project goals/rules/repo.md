# RaterHub Automator

## Overview
The RaterHub Automator is a Private and personal Python-based tool designed to streamline the evaluation of AI-generated responses on the RaterHub platform. It automates the process of capturing screenshots of the RaterHub webpage, sending them to an AI model (currently configured for Gemini) for analysis through vertexai api, parsing the AI's response, and filling in ratings, checkboxes, and comments on the RaterHub interface aligning with the parsed ratings outputted by the AI. The tool includes a graphical user interface (GUI) for user-friendly operation and supports both one-time and looped task processing. The tool is only to be used personally by Zade, the developer/overseer of the Raterhub Automator. Development should never consider other users using the tool, as it will only ever be used by Zade.

## Features
- **Automated Screenshot Capture**: Captures multiple screenshots of the RaterHub webpage to ensure all content is included.
- **AI Integration**: Sends screenshots to the Gemini AI model (via Vertex AI) for evaluation based on a predefined prompt.
- **Response Parsing**: Extracts ratings for Response A, Response B, Side-by-Side (SxS) comparison, and explanation from the AI's response.
- **Form Automation**: Automatically selects "None of the above" for response issues, sets helpfulness sliders, selects SxS radio buttons, and pastes explanations into the comment box.
- **GUI Interface**: Provides a simple PySimpleGUI interface with buttons to run automation, test the Chrome debug port, kill Chrome processes, and exit the application.
- **Chrome Debugging**: Launches and connects to a Chrome instance with remote debugging enabled (port 9222) for Selenium control.
- **Configurability**: Uses a `config.json` file to customize settings such as AI choice, auto-submit, loop tasks, delay between actions, and screenshot count.
- **Error Handling**: Includes robust error handling for Chrome connection issues, AI response parsing, and element interactions, with fallbacks to default values or task release.

## Prerequisites
- **Python 3.8+**
- **Google Chrome** installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Google Cloud Project** with Vertex AI API enabled and credentials configured
- **Dependencies**:
  - `selenium`
  - `webdriver_manager`
  - `Pillow`
  - `PySimpleGUI`
  - `pywin32`
  - `google-cloud-vertexai`
  Install dependencies using:
  ```bash
  pip install selenium webdriver_manager Pillow PySimpleGUI pywin32 google-cloud-vertexai
  ```

## Installation
1. Clone or download the project to your local machine:
   ```bash
   git clone <repository-url>
   cd RaterHubAutomator
   ```
2. Ensure Google Chrome is installed at the default path or update `automator_gui.py` with the correct path.
3. Set up Google Cloud credentials for Vertex AI:
   - Create a Google Cloud project and enable the Vertex AI API.
   - Download the service account key and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the key file path.
4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   (Create a `requirements.txt` with the listed dependencies if needed.)
5. Place the provided `config.json`, `launch-chrome.bat`, `raterhub_automator.py`, and `automator_gui.py` in the project directory.

## Usage
1. **Launch the GUI**:
   ```bash
   python automator_gui.py
   ```
2. **Prepare RaterHub and Gemini**:
   - Open a Chrome window with a RaterHub task and Gemini tab, or let the tool launch Chrome with debugging enabled.
   - Ensure you are logged into RaterHub and have a task open.
3. **Run Automation**:
   - Click "Run Full Automation" in the GUI.
   - If Chrome is not running with debugging, the tool will launch it.
   - Follow the prompt to confirm RaterHub and Gemini tabs are ready.
   - The tool will capture screenshots, analyze them with Gemini, and fill in the RaterHub form.
4. **Other GUI Options**:
   - **Test Port & Logs**: Checks if port 9222 is open and displays `netstat` output for debugging.
   - **Kill Chrome**: Terminates all Chrome processes.
   - **Exit**: Closes the GUI and terminates any launched Chrome processes.
5. **Configuration**:
   - Edit `config.json` to adjust:
     - `ai`: Set to `"gemini"` (only supported AI currently).
     - `auto_submit`: Set to `true` to auto-submit tasks or `false` to pause for manual review.
     - `loop_tasks`: Set to `true` to continuously process tasks or `false` for one-time execution.
     - `delay_seconds`: Time to wait between actions (default: 2 seconds).
     - `screenshot_count`: Number of screenshots to capture (default: 4).

## Project Structure
- `config.json`: Configuration file for automation settings.
- `launch-chrome.bat`: Batch script to manually launch Chrome with remote debugging.
- `raterhub_automator.py`: Core automation script handling screenshot capture, AI analysis, and form filling.
- `automator_gui.py`: GUI script for user interaction and process management.

## Priority Scope
- **Custom Prompts**: Allow users to define custom AI prompts via the GUI or config file.
- **Dynamic Screenshot Count**: Adjust screenshot count based on page length or content detection.
- **Error Logging**: Implement detailed logging to a file for easier debugging and auditing.
- **Clipboard Image Pasting**: Implement functionality to paste screenshots into an AI chat interface (e.g., Gemini's web UI) instead of using Vertex AI.

## Future Scope
- **Support for Additional AI Models**: Extend compatibility to other AI models like ChatGPT, Claude, or Grok.
- **Auto-Submit Enhancements**: Add conditional logic to skip submission for low-confidence AI responses.

## Notes
- Ensure Chrome is not blocked by a firewall for port 9222.
- The tool assumes a Windows environment due to `win32clipboard` and Chrome path dependencies.
- Vertex AI requires a valid Google Cloud project with billing enabled.
- For manual Chrome debugging, run `launch-chrome.bat` before starting the automation if not using the GUI.

## Troubleshooting
- **Port 9222 Not Open**: Check if Chrome is running with `--remote-debugging-port=9222` or if another process is using the port.
- **Vertex AI Errors**: Verify Google Cloud credentials and project settings.
- **Element Not Found**: Ensure the RaterHub task page is fully loaded and the correct task type is open.
- **Automation Skips Actions**: Check `config.json` settings, especially `auto_submit` and `loop_tasks`.