from subprocess import run, CalledProcessError
from pathlib import Path
from os import path, getcwd
import shutil
from sys import argv, exit

help_string = """\
setup = scaffolds a package

-- upload types --\n\
`r` = upload to pypi\n\
`t` = upload to test.pypi\n\
`a` = upload to pypi & test.pypi\n\
        
-- version upgrading --\n\
`-` upgrades from 0.0.0 to 0.0.1\n\
`m` upgrades from 0.0.0 to 0.1.0\n\
`s` upgrades from 0.0.0 to 1.0.0\n\
        
-- misc --\n\
`c` cleans up previous build files in dist, and .egg-info\n\

example:\n\
`pack r -`\n\
upgrades from 0.0.0 to 0.0.1 and uploads to pypi\
"""

pyproject_prefab = """\
[build-system]
requires = ["setuptools>=65.5.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "untitled_package"
version = "0.0.0"
description = ""
requires-python = ">=3"
readme = "README.md"
license = "MIT"
keywords = []
authors = [{name = ""}]
dependencies = [
]

[project.scripts]
...

[project.urls]
Homepage = ...
Repository = ...
"""

setup_prefab = """\
[metadata]
name = py-package-util
version = 0.0.0
author = R
description = 
long_description = file: README.md
long_description_content_type = text/markdown
url = 
classifiers = 
    Programming Language :: Python :: 3
    "Intended Audience :: Developers",
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent

[options]
packages = find:
python_requires = >=3

[options.packages.find]
where = .

"""

def package(as_module:bool=False) -> None:
    if as_module: argv.pop(0)
    if argv[1] in ["-h", "h", "help"]: (print(help_string), exit())

    print(" ".join(arg for arg in argv))
    print("Packaging...")
    
    working_directory = getcwd()

    version = None

    version_commands = ['s', 'm', '-']
    upload_commands = ['r', 't', 'a']

    dist_dir = Path(path.join(working_directory, "dist"))
    egg_info_dir = Path(path.join(working_directory, "CordForge.egg-info"))
    build_venv = Path(path.join(working_directory, "build_venv"))
    build_venv_python = path.join(build_venv, "Scripts", "python.exe")

    print(argv)

    if len(argv) == 2:
        version_update = argv[1] if argv[1] in version_commands else None
        upload_type = argv[1] if argv[1] in upload_commands else None
    if len(argv) == 3:
        version_update = argv[1] if argv[1] in version_commands else None
        version_update = (argv[2] if argv[2] in version_commands else None) if version_update == None else version_update
        
        upload_type = argv[1] if argv[1] in upload_commands else None
        upload_type = (argv[2] if argv[2] in upload_commands else None) if upload_type == None else upload_type

    print(f"Upload type: {upload_type}")
    print(f"Version update: {version_update}")

    if version_update:
        print("Updating version in pyproject.toml and setup.cfg")
        with open("pyproject.toml", "r") as TOML:
            content = TOML.readlines()
            previous_version = content[6].strip().split(" = ")[1].replace("\"", "")
            stable, major, minor = [int(Number) for Number in previous_version.split(".")]
            if version_update in ["s", "m"]:
                UserInput = input("You sure?\n")
                if UserInput.lower() != "yes": (print("Aborted packing"), exit())
                version = f"{stable+1}.{0}.{0}" if version_update == "s" else f"{stable}.{major+1}.{0}"
            elif version_update == "-":
                version = f"{stable}.{major}.{minor+1}"
            else:
                version = f"{stable}.{major}.{minor}"
            content[6] = f'version = "{version}"\n'

        with open("pyproject.toml", "w") as TOML:
            TOML.write("".join(content))

        with open("setup.cfg", "r") as CFG:
            content = CFG.readlines()
            content[2] = f"version = {version}\n"
            
        with open("setup.cfg", "w") as CFG:
            CFG.write("".join(content))
    else:
        with open("setup.cfg", "r") as CFG:
            version = CFG.readlines()[2].split("=")[1].strip()

    print("Removing previous versions dist and .egg-info")
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)

    if egg_info_dir.exists():
        for item in egg_info_dir.iterdir():
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)

    print(f"Building: {version}")
    run([build_venv_python, "-m", "build"], shell=True, check=True)

    print(f"Uploading: {version}")
    print(upload_type)
    if upload_type in ['t', 'a']:
        try:
            run([build_venv_python, "-m", "twine", "upload", "--repository", "testpypi", "dist/*", "--verbose"], shell=True, check=True)
            print("Uploaded test package")
        except CalledProcessError:
            print("Failed to upload test package")
    if upload_type in ['r', 'a']:
        try:
            run([build_venv_python, "-m", "twine", "upload", "dist/*", "--verbose"], shell=True, check=True)
            print("Uploaded pypi package")
        except CalledProcessError:
            print("Failed to upload official package")


def setup() -> None:
    working_directory = getcwd()
    print("Setting up a python package project...")

    print("Creating build_env...")
    run(["python", "-m", "venv", "build_venv"], shell=True, check=True)
    print("Downloading necessary packages to build_env...")
    run([path.join("build_venv","Scripts","python"), "-m", "pip","install", "--upgrade", "setuptools", "build", "wheel", "twine"], shell=True, check=True)

    pyproject_path = path.join(working_directory, "pyproject.toml")
    setupcfg_path = path.join(working_directory, "setup.cfg")

    if not path.exists(pyproject_path):
        print("Creating pyproject.toml...")
        with open(pyproject_path, "w+") as CFG: CFG.write(pyproject_prefab)

    if not path.exists(setupcfg_path):
        print("Creating setup.cfg...")
        with open(setupcfg_path, "w+") as CFG: CFG.write(setup_prefab)

    print("Finished setting")
