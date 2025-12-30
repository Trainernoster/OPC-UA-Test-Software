#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse
import json
import warnings

""" 
Script to build cpp. 

To make the script executable run:
    chmod +x install_python312.py
in the command line or runn it with python.
"""

### paser
parser = argparse.ArgumentParser(description="Build cmake projects")
parser.add_argument(
    "--build",
    required=False,
    nargs="+",
    help="Project(s) which should be build")
parser.add_argument(
    "--projPath",
    required=False,
    help="Projects json file path")
args = parser.parse_args()

# Warning formating
def custom_warn_format(message, category, filename, lineno, line=None):
    return f"Warning: {message}\n"

warnings.formatwarning = custom_warn_format

### json read
DEFAULT_PROJECTS_PATH = "builds.json"
def loadProjects():
    file_path = os.path.dirname(os.path.abspath(__file__))
    project_list = []
    data = None
    ### Load json path
    if args.projPath == None:
        file_path = os.path.join(file_path, DEFAULT_PROJECTS_PATH)
    else:
        file_path = args.projPath
    ### Check json file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist!")
    ### Read projects
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except Exception as e:
        raise RuntimeError(f"Can not read from file: {e}")
    ### Load projects
    try:
        for project in data["projects"]:
            try:
                if args.build is not None:
                    for name in args.build:
                        try:
                            if project["name"] == name:
                                project_list.append(project)
                                break
                        except Exception as e:
                            warnings.warn(message=(f"The Project does not contain: name!"))
                else:
                    project_list.append(project)
            except Exception as e:
                raise RuntimeError(f"args error {e}")
    except Exception as e:
        raise ValueError(f"The File does not contain: projects!")
    ### Check loaded projects
    if len(project_list) == 0:
        raise RuntimeError(f"No Project was loaded!")
    for name in args.build:
        loaded = False
        for loaded_project in project_list:
            if loaded_project["name"] == name:
                loaded = True 
                break
    if not loaded: 
        warnings.warn(message=(f"\"{name}\" was not loaded!"))
    return project_list

def makeAbsPath(base_dir, add_path):
    while add_path.startswith("../") or add_path.startswith("/../"):
        base_dir = os.path.dirname(base_dir)
        if add_path.startswith("../"):
            add_path = add_path[3:]
        else:
            add_path = add_path[4:]
    abs_path = os.path.join(base_dir, add_path)
    return os.path.abspath(abs_path)

def run(cmd):
    """Run shell command and exit if it fails."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def main():
    projects = loadProjects()
    src_folder = "src"
    build_folder = "build"
    CMakeFiles_folder = "CMakeFiles"
    cmake_init_flags = None
    ### Build
    for project in projects:
        print(f"Start buliding: {project["name"]}")
        current_path = os.path.dirname(os.path.abspath(__file__))
        if project["use_relative_pathes"] == True:
            src_folder = makeAbsPath(current_path, project["src_folder"])
            build_folder = makeAbsPath(current_path, project["build_folder"])
        else:
            src_folder = project["src_folder"]
            build_folder = project["build_folder"]
        CMakeFiles_folder = os.path.join(build_folder, "CMakeFiles")
        full_init = project["full_init"]
        cmake_init_flags = project["cmake_init_flags"]
        cmake_build_flags = project["cmake_build_flags"]
        just_init = project["just_init"]
        
        # Check if build folder exists
        if os.path.exists(build_folder):
            print("build folder exists")
        else:
            os.makedirs(build_folder)
            print("build folder was created")

        print(CMakeFiles_folder)
        # Check if CMakeFiles folder exist
        if os.path.exists(CMakeFiles_folder) and not full_init:
            print("Allready initialized")
        else:
            os.chdir(build_folder)
            if cmake_init_flags is None:
                run(f"cmake {src_folder}")
            else:
                run(f"cmake {cmake_init_flags} {src_folder}")
            print(current_path)
            print("Build initialized")

        if not just_init:
            if cmake_build_flags is None:
                run("cmake --build .")
            else:
                run(f"cmake --build . {cmake_build_flags}")
            os.chdir(current_path)
    
    ### Run
    for project in projects:
        if project["build_and_run"] == True:
            print(f"run {project["name"]}")
            run(project["executable"])
    
    ### Finish
    print("cmake finished build")

if __name__ == "__main__":
    main()
