import sys, os, pathlib, json
from typing import Union
from pathlib import Path

import util

class PathHandler:
    exec_path: Path = None
    exec_dir: Path = None
    
    rfa_user_dir: Path = None
    rfa_user_settings_path: Path = None

    def load_paths(self):
        self.exec_path = Path(os.path.abspath(sys.argv[0]))
        self.exec_dir = self.exec_path.parent
        
        # Useful for development: set a custom path for the user home from a text file
        dev_paths = {}
        dev_paths_file = self.exec_dir.joinpath("dev_paths.json")
        if dev_paths_file.exists():
            dev_paths = json.loads(dev_paths_file.read_text())

        if "custom_user_path" in dev_paths:
            custom_user_path: Path = None
            
            if os.path.isabs(dev_paths["custom_user_path"]):
                custom_user_path = Path(dev_paths["custom_user_path"])
            else:
                custom_user_path = self.exec_dir.joinpath(dev_paths["custom_user_path"])
            
            self.rfa_user_dir = custom_user_path
            print(f"DEV: using custom user path '{custom_user_path}'")
        else:
            self.rfa_user_dir = Path.home().joinpath(".scb")
            
        # 
        self.rfa_user_settings_path = self.rfa_user_dir.joinpath("rfa_settings.json")
    
    
def make_path_str_forward_slashed(path_str: str) -> str:
    return path_str.replace('\\', '/')
