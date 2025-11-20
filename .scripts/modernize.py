#!/usr/bin/env python3
import os
import subprocess
import sys

""" 
Script to install modernize apt and Debian. 

To make the script executable run:
    chmod +x install_python312.py
in the command line or runn it with python.
"""

PYTHON_VERSION = "3.12.10"
SRC_DIR = "/usr/src"
TAR_FILE = f"Python-{PYTHON_VERSION}.tgz"
URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/{TAR_FILE}"

def run(cmd):
    """Run shell command and exit if it fails."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def main():
    # update and upgrade
    run("sudo apt update")
    run("sudo apt upgrade -y")
    run("sudo apt full-upgrade -y")
    run("sudo apt modernize-sources")
    run("cd /etc/apt/sources.list.d")

    print("Modernization completed successfully!")

if __name__ == "__main__":
    main()
