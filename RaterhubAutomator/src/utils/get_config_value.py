#!/usr/bin/env python
"""
Simple script to read values from config.json for use in batch files.
Usage: python get_config_value.py key_name
"""

import json
import sys
import os

def get_config_value(key):
    """Reads a value from config.json by key name."""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.json')
        
        # Read the config file
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Return the value if it exists
        if key in config:
            return config[key]
        else:
            return ""
    except Exception as e:
        # Return empty string on any error
        return ""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        key = sys.argv[1]
        value = get_config_value(key)
        print(value)
    else:
        print("")