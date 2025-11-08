#!/usr/bin/env python3
import os
import subprocess
import sys

""" 
Script to install python on debian from source. 

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
    # Install dependencies
    run("sudo apt update")
    run("sudo apt install -y wget build-essential libssl-dev zlib1g-dev "
        "libncurses5-dev libnss3-dev libreadline-dev libffi-dev "
        "libsqlite3-dev libbz2-dev liblzma-dev tk-dev")

    # Download source
    os.chdir(SRC_DIR)
    if not os.path.exists(TAR_FILE):
        run(f"sudo wget {URL}")
    run(f"sudo tar xzf {TAR_FILE}")
    os.chdir(f"{SRC_DIR}/Python-{PYTHON_VERSION}")

    # Configure
    run("sudo ./configure --enable-optimizations --with-ensurepip=install")

    # Compile
    run(f"sudo make -j$(nproc)")

    # Install
    run("sudo make altinstall")

    # Verify installation
    run("python3.12 --version")
    run("pip3.12 --version")
    print("Python 3.12.10 installation completed successfully!")

if __name__ == "__main__":
    main()
