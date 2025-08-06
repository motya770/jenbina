#!/usr/bin/env python3
"""
Launcher script for Jenbina AGI Simulation
This script properly imports the core module and runs the Streamlit app
"""

import sys
import os

# Add the current directory to Python path so we can import core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    from core import app
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", "core/app.py"]
    sys.exit(stcli.main()) 