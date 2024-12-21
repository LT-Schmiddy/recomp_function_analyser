import os, json
from pathlib import Path

from colors import *

def is_build_version():
    return getattr(sys, 'frozen', False)


def mkdir_if_missing(dir_path: str) -> bool:
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
        return True
    
    return False

def list_contains(p_filter, p_list):
    for x in p_list:
        if p_filter(x):
            return True
    return False

def list_get(p_filter, p_list):
    retVal = []
    for x in p_list:
        if p_filter(x):
            retVal.append(x)
    return retVal

def print_color(fg: str, *args, **kwargs):
    p_list = []
    for i in args:
        p_list.append(color(str(i), fg=fg))

    print(*p_list, **kwargs)


def print_error(*args, **kwargs):
    print_color("red", *args, **kwargs)


def print_warning(*args, **kwargs):
    print_color("yellow", *args, **kwargs)


def yn_prompt(msg: str = "", default=None):
    while True:
        result = input(msg).lower()

        if result == "y":
            return True
        if result == "n":
            return False

        if default is not None:
            print_error("Using default...")
            return default

        print_error("Invalid response. Try again...")


def save_json_config(path: Path, config: dict):
    path.write_text(json.dumps(config, indent=4))
    

def load_json_config(path: Path, default_config: dict):
    
    def recursive_load_list(main: list, loaded: list):
        for i in range(0, max(len(main), len(loaded))):
            # Found in both:
            if i < len(main) and i < len(loaded):
                if isinstance(loaded[i], dict):
                    recursive_load_dict(main[i], loaded[i])
                elif isinstance(loaded[i], list):
                    recursive_load_list(main[i], loaded[i])
                else:
                    main[i] = loaded[i]
            # Found in main only:
            elif i < len(loaded):
                main.append(loaded[i])


    def recursive_load_dict(main: dict, loaded: dict):
        new_update_dict = {}
        for key, value in main.items():
            if not (key in loaded):
                continue
            if isinstance(value, dict):
                recursive_load_dict(value, loaded[key])
            elif isinstance(value, list):
                recursive_load_list(value, loaded[key])
            else:
                new_update_dict[key] = loaded[key]
        
        # Load settings added to file:
        for key, value in loaded.items():
            if not (key in main):
                new_update_dict[key] = loaded[key]

        main.update(new_update_dict)

    # load preexistent settings file
    if path.exists() and path.is_file():
        try:
            imported_config = json.loads(path.read_text())
            # current.update(imported_settings)
            recursive_load_dict(default_config, imported_config)
        except json.decoder.JSONDecodeError as e:
            print_error(f"CRITICAL ERROR IN LOADING SETTINGS: {e}")
            print_error("Using default settings...")

    # settings file not found
    else:
        save_json_config(path, default_config)
        print(f"Created new settings file at '{path}'.")


__all__ = (
    "mkdir_if_missing",
    "list_contains",
    "list_get",
    "print_color",
    "print_error",
    "print_warning",
    "yn_prompt"
)
