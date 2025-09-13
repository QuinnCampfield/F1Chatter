#!/usr/bin/env python3
"""
F1 Chat Agent Runner
This script sets up the path and runs the F1 Chat Agent
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import and run the agent
from application.main import main

if __name__ == "__main__":
    main()
