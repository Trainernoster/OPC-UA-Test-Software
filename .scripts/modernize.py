#!/usr/bin/env python3
import os
import subprocess
import sys

""" 
Script to install modernize apt and Debian. 

To make the script executable run:
    chmod +x install_python312.py
in the command line or run it with python.
"""

SOURCE_LIST_FILE = "/etc/apt/sources.list.bak"
SOURCE_SOURCE_FILE = "/etc/apt/sources.list.d/moved-from-main.sources"
SOURCE_SOURCE_FILE_NEW = "/etc/apt/sources.list.d/debian_mirror.sources"

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

    # Change bak file
    if os.path.isfile(SOURCE_LIST_FILE):

        with open(SOURCE_LIST_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            ...
        else:
            first_line = lines[0]

            if first_line[0] == '#':
                modified_line = first_line[1:] if len(first_line) > 1 else ""
            else:
                modified_line = first_line

            with open(SOURCE_LIST_FILE, "w", encoding="utf-8") as f:
                f.write(modified_line)
    else:
        print(f"File does not exist: {SOURCE_LIST_FILE}")

    # Update .sources
    if os.path.isfile(SOURCE_SOURCE_FILE):

        with open(SOURCE_SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            ...
        else:
            new_lines = []
            new_lines.append("# Debian mirror\n")
            new_lines.append(lines[1])
            new_lines.append(lines[2])
            new_lines.append(lines[3])
            new_lines.append(lines[4])
            new_lines.append("Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg")

            with open(SOURCE_SOURCE_FILE_NEW, "w", encoding="utf-8") as f:
                for line in new_lines:
                    f.write(line)
            os.remove(SOURCE_SOURCE_FILE)
    else:
        print(f"File does not exist: {SOURCE_SOURCE_FILE}")

    print("Modernization completed successfully!")

if __name__ == "__main__":
    main()
