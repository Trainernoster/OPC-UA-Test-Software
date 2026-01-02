#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse

""" 
Script to install Test Environment.

To make the script executable run:
    chmod +x install_python312.py
in the command line or run it with python.
"""
MAX_MB = 1900
max_bytes = MAX_MB * 1024 * 1024
large_files = []
split_file_parts = []
extensions = []

REOP_URL = "https://github.com/Trainernoster/OPC-UA-Test-Environment.git"
REPO_PATH = ["..", "..", "OPC-UA-Test-Environment"]
repo_path = os.path.dirname(os.path.abspath(__file__))
for foldername in REPO_PATH:
    if foldername == "..":
        repo_path = os.path.dirname(repo_path)
    else:
        repo_path = os.path.join(repo_path, foldername)
ignorefile = os.path.join(repo_path, ".gitignore")

### paser
parser = argparse.ArgumentParser(description="Download Test Environment.")
parser.add_argument(
    "--pull",
    required=False,
    action="store_true",
    help="Pull flag")
parser.add_argument(
    "--push",
    required=False,
    action="store_true",
    help="Push flag")
args = parser.parse_args()

def run(cmd):
    """Run shell command and exit if it fails."""
    print(f"Running: {cmd}")
    
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    result = subprocess.run(
        cmd,
        shell=True,
        env=env
    )

    if result.returncode != 0:
        print(f"Command failed: {cmd}")

def main():
    if args.pull == True and args.push == True:
        print("Cant Pull and Push at the same time!")
    elif args.push == True:
        push()
    elif args.pull == True:
        pull()
    else:
        pull()

def pull():
    print("Pull Test Environment!")
    
    os.chdir(os.path.dirname(repo_path))
    run(f"git lfs install")
    run(f"git config lfs.progress true")
    run(f"git clone {REOP_URL}")
    os.chdir(repo_path)
    print("end git")
    run("git lfs pull")
    print("end lfs")
    
    part_files = {}

    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            if ".part-" in filename:
                full_path = os.path.join(root, filename)

                # Original file name (strip .part-XXX)
                base_name = filename.split(".part-")[0]
                base_path = os.path.join(root, base_name)

                part_files.setdefault(base_path, []).append(full_path)

    if not part_files:
        print("No split files found.")
        return

    # Reassemble each file
    for base_file, parts in part_files.items():
        parts.sort()
        reassemble_parts(base_file, parts)

    print("Reassembly complete.")

def push():
    print("Push Test Environment!")
    # Scan files
    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            path = os.path.join(root, filename)

            try:
                size = os.path.getsize(path)
            except OSError:
                continue

            if size > max_bytes:
                abs_path = os.path.abspath(path)
                large_files.append(abs_path)

                _, ext = os.path.splitext(filename)
                if ext and ext not in extensions:
                    extensions.append(ext)

    # Read existing ignore file (if it exists)
    existing_lines = set()
    if os.path.exists(ignorefile):
        with open(ignorefile, "r", encoding="utf-8") as f:
            existing_lines = {line.strip() for line in f}

    # Filter extensions that already exist in ignore file
    new_extensions = []
    for ext in extensions:
        pattern = f"*{ext}"
        if pattern not in existing_lines:
            new_extensions.append(ext)

    # Write new extensions
    lines = []
    if os.path.exists(ignorefile):
        with open(ignorefile, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]
    # Ensure header block exists
    if "#Larg File Extensions" not in lines:
        lines.append("")
        lines.append("#Larg File Extensions")
        lines.append("#Do not change")
    if "*.part-*" not in lines:
        lines.append("*.part-*")
    # Add new extensions
    for ext in sorted(new_extensions):
        pattern = f"*{ext}"
        if pattern not in lines:
            lines.append(pattern)
    
    # Write only new extensions if new_extensions: 
    with open(ignorefile, "a", encoding="utf-8") as f:

        if "#Larg File Extensions" not in existing_lines:
            f.write("\n#Larg File Extensions\n")

        if "#Do not change" not in existing_lines:
            f.write("#Do not change\n")

        if "*.part-*" not in existing_lines:
            f.write("*.part-*\n")

        for ext in sorted(new_extensions):
            f.write(f"*{ext}\n")
    
    for file_path in large_files:
        split_large_file(file_path)

    os.chdir(repo_path)
    run("git add .gitignore")
    run(f"git commit -m \"add gitignore\"")
    run("git add .")
    run(f"git commit -m \"upload files\"")
    run("git push")

    if os.path.exists(ignorefile):
        with open(ignorefile, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip() != "*.part-*":
                new_lines.append(line)

        with open(ignorefile, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    
    
    run("git add .gitignore")
    run(f"git commit -m \"add gitignore\"")
    run("git push")
    run(f"git lfs track \"*.part-*\"")


    for split_file_part in split_file_parts:
        run(f"git add {split_file_part}")
        file_name = os.path.basename(split_file_part)
        print(file_name)
        run(f"git commit -m \"upload {file_name}\"")
        run("git lfs push")
        run("git push")

    # --- Delete the split files after push ---
    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            if ".part-" in filename:
                part_path = os.path.join(root, filename)
                try:
                    os.remove(part_path)
                    print(f"Deleted split file: {part_path}")
                except OSError as e:
                    print(f"Failed to delete {part_path}: {e}")

def split_large_file(file_path):
    if ".part-" in file_path:
        return

    part_size = max_bytes
    base_path = f"{file_path}.part-"

    print(f"Splitting large file: {file_path}")

    with open(file_path, "rb") as src:
        part_num = 0
        while True:
            chunk = src.read(part_size)
            if not chunk:
                break

            part_name = f"{base_path}{part_num:03d}"
            with open(part_name, "wb") as dst:
                dst.write(chunk)            
            
            split_file_parts.append(os.path.abspath(part_name))

            print(f"  created {part_name}")
            part_num += 1

def reassemble_parts(base_file, parts):
    print(f"Reassembling: {base_file}")

    with open(base_file, "wb") as out:
        for part in parts:
            with open(part, "rb") as src:
                out.write(src.read())

    # Delete part files after successful reassembly
    for part in parts:
        os.remove(part)
        print(f"  deleted {part}")


if __name__ == "__main__":
    main()