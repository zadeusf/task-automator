#!/usr/bin/env python3
"""
RaterHub Automator - GUI Entry Point

This is the GUI entry point for the RaterHub Automator application.
It imports and runs the GUI from the gui module.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.automator_gui import AutomatorGUI

if __name__ == "__main__":
    gui = AutomatorGUI()
    gui.run()