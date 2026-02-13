"""
Simple setup script for GrowFund backend
Run: py setup.py
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*50}")
    print(f"{description}...")
    print(f"{'='*50}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✓ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(e.stderr)
        return False

def main()