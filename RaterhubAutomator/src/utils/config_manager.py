import json
import logging
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        # Make config_path absolute if it's relative
        if not os.path.isabs(config_path):
            # Go up two levels from src/utils to reach the root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(root_dir, 'config', config_path)
        
        self.config_path = config_path
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logging.info(f"Configuration loaded successfully from {config_path}")
            self._validate_config()
        except FileNotFoundError:
            logging.error(f"Configuration file not found at {config_path}. Using default configuration.")
            self.config = self._get_default_config()
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from configuration file at {config_path}: {e}. Using default configuration.")
            self.config = self._get_default_config()
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading configuration from {config_path}: {e}. Using default configuration.")
            self.config = self._get_default_config()

    def _get_default_config(self):
        """Returns a default configuration dictionary."""
        return {
            "ai": "gemini",
            "auto_submit": False,
            "loop_tasks": False,
            "delay_seconds": 2,
            "screenshot_count": 4,
            "chrome_debug_port": 9222,
            "webdriver_timeout": 30,
            "chrome_launch_timeout": 30,
            "vertex_ai": {
                "model": "gemini-1.5-pro",
                "location": "us-central1",
                "project": "raterhubautomation",
                "key_file": "credentials/raterhubautomation-7886dd999472.json"
            },
            "logging": {
                "level": "INFO"
            },
            "chrome_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "chrome_user_data_dir": "C:\\temp\\chrome_debug"
        }

    def _validate_config(self):
        """Validates critical configuration values and logs warnings for missing ones."""
        required_keys = {
            'vertex_ai.project': 'Vertex AI project ID',
            'vertex_ai.location': 'Vertex AI location',
            'vertex_ai.model': 'Vertex AI model name',
            'chrome_debug_port': 'Chrome debug port'
        }
        
        for key_path, description in required_keys.items():
            if not self._get_nested_value(key_path):
                logging.warning(f"Missing or empty configuration for {description} ({key_path}). Using default value.")
        
        # Validate Chrome path if specified
        chrome_path = self.get('chrome_path')
        if chrome_path and not os.path.exists(chrome_path):
            logging.warning(f"Chrome executable not found at configured path: {chrome_path}")
        
        # Validate key file path
        vertex_config = self.get('vertex_ai', {})
        key_file = vertex_config.get('key_file')
        if key_file:
            if not os.path.isabs(key_file):
                # Go up from config directory to root directory
                root_dir = os.path.dirname(os.path.dirname(self.config_path))
                key_file_path = os.path.join(root_dir, key_file)
            else:
                key_file_path = key_file
            
            if not os.path.exists(key_file_path):
                logging.warning(f"Vertex AI key file not found at: {key_file_path}")

    def _get_nested_value(self, key_path):
        """Gets a nested configuration value using dot notation (e.g., 'vertex_ai.project')."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_ai_choice(self, args_ai=None):
        return args_ai or self.config.get('ai', 'gemini')

    @property
    def vertex_ai_config(self):
        return self.get('vertex_ai', {})

# Create a single instance to be imported by other modules
config = ConfigManager()
