
import importlib
from pathlib import Path
from sys import getsizeof
from datetime import datetime
import json
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import yaml


def create_logger(
    name: str,
    path: str | Path = "",
    level_stdout: int = logging.DEBUG,
    level_file: int = logging.DEBUG,
    mode: str = "a",
    maxBytes: int = 5 * 1024 * 1024,
    backupCount: int = 2
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stdout_formatter = logging.Formatter(
        '%(levelname)s | %(name)s | %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        '%m-%d-%Y %H:%M:%S'
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level_stdout)
    stdout_handler.setFormatter(stdout_formatter)
    logger.addHandler(stdout_handler)

    if path:
        path_obj = Path(path)
        if not path_obj.parent.exists():
            path_obj.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            path_obj, mode=mode, maxBytes=maxBytes, backupCount=backupCount
        )
        file_handler.setLevel(level_file)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def readJsonFile(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File Can Not be found: {path}")
        return {}
    except json.JSONDecodeError:
        print(f"Corrupt JSON File: {path}")
        return {}
    except Exception as Error:
        print(f"Error Occurred '{path}' -> {Error}")
        return {}


def saveJsonFile(path: str, data: dict) -> bool:
    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
            print("Settings have been saved successfully.")
        return True
    except IOError:
        print(f"Error writing to the file: {path}")
        return False
    except Exception as Error:
        print(f"Error Occurred '{path}' -> {Error}")
        return False


def read_yaml(path: Path | str) -> dict:
    """
    Reads the train configuration YAML file from the given path.
    """
    if isinstance(path, str):
        path = Path(path)
    with path.open('r') as file:
        yaml_obj = yaml.safe_load(file)
    return yaml_obj


def convert_yaml(yaml_object: bytes) -> dict:
    """
    Converts a YAML object from bytes to a dictionary.
    """
    return yaml.safe_load(yaml_object)


def get_current_time(format="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.now().strftime(format)


def get_size(variable, unit='bytes'):
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        print("Unit not found. Defaulting to mb.")
        unit = 'mb'
    size = getsizeof(variable) / (1024 ** exponents_map[unit])
    return round(size, 3)


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def import_module_pyinstaller(module_name, module_path):
    """ Helper function to import a module by name and path """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    else:
        return None


def list_files(directory, endswith: str = ""):
    try:
        # List all files in the directory
        files = os.listdir(directory)
        if endswith:
            # Filter out only .png files
            files = [file for file in files if file.endswith(endswith)]
        return files
    except FileNotFoundError:
        return f"Directory {directory} not found."


def command_run(
    command: list[str] | str,
    parse: bool = True,
    sudo_password: str = ""
) -> subprocess.CompletedProcess[str] | str:
    if parse:
        if isinstance(command, str):
            command = command.split()
        elif not isinstance(command, list):
            raise ValueError("Command must be a list or a string.")

    if sudo_password:
        # Prepare the command string if a sudo password is provided
        if isinstance(command, list):
            command = ['sudo', '-S'] + command
        elif isinstance(command, str):
            command = f"sudo -S {command}"

        # Use Popen to securely input sudo password and run the command
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Send sudo password followed by a newline to simulate Enter key
        stdout, stderr = process.communicate(input=f"{sudo_password}\n")
        if process.returncode != 0:
            return f"Command '{' '.join(command)}' failed with exit status {process.returncode}: {stderr}"
        else:
            return stdout
    else:
        # Run the command without sudo password
        try:
            command_response = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return command_response.stdout
        except subprocess.CalledProcessError as error:
            return f"Command '{' '.join(command)}' failed with exit status {error.returncode}: {error.stderr}"
        except Exception as error:
            return f"Error Occurred '{' '.join(command)}': {error}"
