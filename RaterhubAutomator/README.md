# RaterHub Automator

A Python-based automation tool for RaterHub tasks that uses AI to analyze screenshots and automatically fill in ratings and comments.

## Features

- **AI-Powered Analysis**: Uses Google's Gemini model via Vertex AI to analyze task screenshots
- **Automated Form Filling**: Automatically fills in helpfulness ratings, side-by-side comparisons, and comments
- **Chrome Integration**: Connects to Chrome browser with remote debugging for seamless automation
- **Configurable Settings**: Flexible configuration for AI models, timeouts, and automation behavior
- **GUI Interface**: User-friendly PySimpleGUI interface for easy operation
- **Robust Error Handling**: Comprehensive error handling and logging throughout the application

## Requirements

- Python 3.8+
- Google Chrome browser
- Google Cloud Project with Vertex AI enabled
- Service account with Vertex AI User permissions

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Google Cloud credentials (see Configuration section)

## Project Structure

```
RaterhubAutomator/
├── main.py                 # Main entry point (imports from src/)
├── gui.py                  # GUI entry point (imports from src/)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/
│   └── config.json        # Main configuration file
├── credentials/
│   └── *.json            # Google Cloud service account keys
├── src/                   # Source code organized by functionality
│   ├── __init__.py
│   ├── core/              # Core automation modules
│   │   ├── __init__.py
│   │   ├── main.py        # Core automation logic
│   │   ├── browser_manager.py    # Chrome browser connection
│   │   └── raterhub_page.py      # RaterHub page interactions
│   ├── ai/                # AI analysis modules
│   │   ├── __init__.py
│   │   └── ai_analyzer.py # Gemini AI integration
│   ├── gui/               # GUI modules
│   │   ├── __init__.py
│   │   └── automator_gui.py      # PySimpleGUI interface
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── config_manager.py     # Configuration management
│       └── get_config_value.py   # Config value retrieval
├── scripts/               # Batch scripts and utilities
│   ├── launch-chrome.bat  # Chrome launcher with debugging
│   └── run_automator.bat  # Automation runner script
├── tests/                 # Test files
│   ├── test_all.py       # Comprehensive test suite
│   └── test_gemini.py    # Gemini API tests
├── docs/                  # Documentation
│   ├── Instructions.txt   # Setup instructions
│   └── BUG_FIXES_SUMMARY.md     # Bug fix documentation
├── backup/                # Backup files
│   └── *.bak             # Backup copies of modified files
└── temp/                  # Temporary files (screenshots, etc.)
```

## Configuration

### Google Cloud Setup

1. Create a Google Cloud Project
2. Enable the Vertex AI API
3. Create a service account with "Vertex AI User" role
4. Download the service account key file as JSON
5. Place the key file in the `credentials/` directory
6. Update `config/config.json` with your project details

### Configuration File

Edit `config/config.json` to customize the automation behavior:

```json
{
    "ai": "gemini",
    "auto_submit": false,
    "loop_tasks": false,
    "vertex_ai": {
        "model": "gemini-2.5-pro",
        "location": "us-central1", 
        "project": "your-project-id",
        "key_file": "credentials/your-service-account-key.json"
    }
}
```

Key settings:
- `auto_submit`: Whether to automatically submit tasks after rating
- `loop_tasks`: Whether to continuously process tasks
- `screenshot_count`: Number of screenshots to capture per task
- `chrome_debug_port`: Port for Chrome remote debugging

## Usage

### GUI Mode (Recommended)

1. Launch Chrome with remote debugging:
   ```bash
   scripts\launch-chrome.bat
   ```
2. Navigate to RaterHub in the opened Chrome window
3. Run the GUI application:
   ```bash
   python gui.py
   ```
4. Click "Start Automation" to begin processing tasks

### Command Line Mode

1. Launch Chrome with remote debugging
2. Navigate to RaterHub
3. Run the automation script:
   ```bash
   python main.py
   ```

## How It Works

1. **Screenshot Capture**: Takes multiple screenshots of the current RaterHub task
2. **AI Analysis**: Sends screenshots to Gemini model for analysis
3. **Response Parsing**: Extracts ratings and explanations from AI response
4. **Form Automation**: Automatically fills in the form fields based on AI analysis
5. **Task Completion**: Either submits the task or releases it based on AI recommendation

## Development

### Running Tests

Test all modules for import issues and basic functionality:
```bash
python tests\test_all.py
```

Test Gemini API connectivity:
```bash
python tests\test_gemini.py
```

### Module Organization

- **Core modules** (`src/core/`): Main automation logic, browser management, page interactions
- **AI modules** (`src/ai/`): AI analysis and response parsing
- **GUI modules** (`src/gui/`): User interface components
- **Utility modules** (`src/utils/`): Configuration management and helper functions

## Logging

The application provides comprehensive logging with configurable levels. Logs include:
- Connection status and errors
- Screenshot capture details
- AI analysis results
- Form interaction outcomes
- Performance metrics

Configure logging level in `config/config.json`:
```json
{
    "logging": {
        "level": "DEBUG"
    }
}
```

## Troubleshooting

### Common Issues

1. **Chrome Connection Failed**
   - Ensure Chrome is launched with `--remote-debugging-port=9222`
   - Check that no other automation tools are connected to Chrome
   - Verify the debug port in config matches the Chrome launch parameter

2. **AI Analysis Errors**
   - Verify Google Cloud credentials are correctly configured in `credentials/`
   - Check that Vertex AI API is enabled in your project
   - Ensure the service account has proper permissions

3. **Form Interaction Issues**
   - Check that you're on a valid RaterHub task page
   - Verify page elements haven't changed (selectors may need updating)
   - Enable debug logging for detailed interaction information

4. **Import Errors**
   - Run `python tests\test_all.py` to check for import issues
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is for educational and automation purposes. Please ensure compliance with RaterHub's terms of service when using this tool.