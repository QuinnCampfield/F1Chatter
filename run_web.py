#!/usr/bin/env python3
"""
F1 Chat Agent - Web Interface Launcher
Simple launcher for the Gradio web interface
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from gradio_app import main

if __name__ == "__main__":
    main()
