#!/usr/bin/env python3
"""
Simple launcher for Jenbina AGI Simulation
"""

import subprocess
import sys
import os

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Run streamlit with the core app
    cmd = [sys.executable, "-m", "streamlit", "run", "core/app.py"]
    
    print("Starting Jenbina AGI Simulation...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down Jenbina...")
    except subprocess.CalledProcessError as e:
        print(f"Error running Jenbina: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 