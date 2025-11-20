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

SOURCE_LIST_FILE = "/etc/apt/sources.list.d/modernize.list" 

def run(cmd):
    """Run shell command and exit if it fails."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def main():
    # update and upgrade
    #run("sudo apt update")
    #run("sudo apt upgrade -y")
    #run("sudo apt full-upgrade -y")
    #run("sudo apt modernize-sources")


    if os.path.isfile(SOURCE_LIST_FILE):
        print(f"Editing file: {SOURCE_LIST_FILE}")

        with open(SOURCE_LIST_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            print("File is empty, nothing to edit.")
        else:
            first_line = lines[0]

            # remove the first character
            if first_line[0] == '#':
                modified_line = first_line[1:] if len(first_line) > 1 else ""
            else:
                modified_line = first_line

            # overwrite file with ONLY the modified first line
            with open(SOURCE_LIST_FILE, "w", encoding="utf-8") as f:
                f.write(modified_line)

            print("First character removed and all other lines deleted.")
    else:
        print(f"File does not exist: {target_file}")

    print("Modernization completed successfully!")

if __name__ == "__main__":
    main()
