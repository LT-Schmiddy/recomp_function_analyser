import sys, os, json
from pathlib import Path

from colors import *
import util
from . import path_handler
# If we're executing as the source version, the main .py file  is actually found in the `src` subdirectory
# of the project, and `exec_dir` is changed to reflect that. We'll create `exec_file_dir` in case we actually need the
# unmodified path to that script. Obviously, in build mode, these two values will be the same.

def default_settings():
    return {}

current = default_settings()
paths = path_handler.PathHandler()

def save_settings(path: Path = None, settings_dict: dict = current):
    if path is None:
        path = paths.rfa_user_settings_path
    
    util.save_json_config(path, settings_dict)


def load_settings(path: Path = None, settings_dict: dict = current):
    if path is None:
        path = paths.rfa_user_settings_path
    
    util.load_json_config(path, settings_dict)

