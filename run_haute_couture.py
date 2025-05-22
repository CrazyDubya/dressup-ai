#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import signal
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import requests
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def start_server():
    """Start the FastAPI server."""
    print("Starting Haute Couture API server...")
    server_process = subprocess.Popen(
        [sys.executable, "haute_couture_api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Wait for server to start
    return server_process

def generate_outfits():
    """Generate the outfits."""
    print("\nGenerating haute couture outfits...")
    subprocess.run([sys.executable, "generate_outfits.py"])

def find_latest_outfit_file():
    """Find the most recently generated outfit file."""
    outfit_files = list(Path(".").glob("haute_couture_outfits_*.json"))
    if outfit_files:
        return max(outfit_files, key=lambda x: x.stat().st_mtime)
    return None

def main():
    # Check and install dependencies if needed
    if not check_dependencies():
        print("Installing required packages...")
        install_dependencies()

    # Start the server
    server_process = start_server()
    
    try:
        # Generate outfits
        generate_outfits()
        
        # Find the generated file
        outfit_file = find_latest_outfit_file()
        if outfit_file:
            print(f"\nOutfits generated successfully!")
            print(f"Results saved to: {outfit_file}")
            
            # Open the API documentation in browser
            print("\nOpening API documentation...")
            webbrowser.open("http://127.0.0.1:5002/docs")
            
            print("\nServer is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main() 