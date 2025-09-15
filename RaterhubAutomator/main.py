#!/usr/bin/env python3
"""
RaterHub Automator - Main Entry Point

This is the main entry point for the RaterHub Automator application.
It imports and runs the main function from the core module.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.main import main

if __name__ == "__main__":
    main()