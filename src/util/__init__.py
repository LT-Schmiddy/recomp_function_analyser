import os, json, sys
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


def recursive_update_dict(base: dict, overlay: dict) -> dict:
    def recursive_load_list(base: list, overlay: list):
        for i in range(0, max(len(base), len(overlay))):
            # Found in both:
            if i < len(base) and i < len(overlay):
                if isinstance(overlay[i], dict):
                    recursive_load_dict(base[i], overlay[i])
                elif isinstance(overlay[i], list):
                    recursive_load_list(base[i], overlay[i])
                else:
                    base[i] = overlay[i]
            # Found in main only:
            elif i < len(overlay):
                base.append(overlay[i])


    def recursive_load_dict(base: dict, overlay: dict):
        new_update_dict = {}
        for key, value in base.items():
            if not (key in overlay):
                continue
            if isinstance(value, dict):
                recursive_load_dict(value, overlay[key])
            elif isinstance(value, list):
                recursive_load_list(value, overlay[key])
            else:
                new_update_dict[key] = overlay[key]
        
        # Load settings added to file:
        for key, value in overlay.items():
            if not (key in base):
                new_update_dict[key] = overlay[key]

        base.update(new_update_dict)
    
    recursive_load_dict(base, overlay)

def load_json_config(path: Path, default_config: dict):
    # load preexistent settings file
    if path.exists() and path.is_file():
        try:
            imported_config = json.loads(path.read_text())
            # current.update(imported_settings)
            recursive_update_dict(default_config, imported_config)
        except json.decoder.JSONDecodeError as e:
            print_error(f"CRITICAL ERROR IN LOADING FILE: {e}")
            print_error("Using default...")

    # settings file not found
    else:
        save_json_config(path, default_config)
        print(f"Created new file at '{path}'.")

def save_json_config(path: Path, config: dict):
    path.write_text(json.dumps(config, indent=4))
    

__all__ = (
    "is_build_version",
    "json_class",
    "list_contains",
    "list_get",
    "load_json_config",
    "mkdir_if_missing",
    "print_color",
    "print_error",
    "print_warning",
    "save_json_config",
    "yn_prompt",
)
