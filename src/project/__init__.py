import os, shutil, json, subprocess
from typing import Union
from pathlib import Path

import util
import settings

class ProjectInfo:
    CONFIG_FILE_NAME = "scb_project_config.json"
    CMAKE_CORE_DIR_NAME = "scb_cmake"
    
    config_path: Path = None
    config: dict = None
    
    @classmethod
    def default_project_config(cls):
        return {
            "name": "my_project",
            "version": "1.0.0",
            "description": "description of project",
            "authors": [
                "Author 1"
            ],
            "vcpkg": {
                "local_path": "./vcpkg",
                "packages": []
            }
        }
    
    def __init__(self, current_path: Path = None):
        pass
    
    # Get general information:
    @property
    def is_project(self) -> bool:
        return self.config_path is not None

    @property
    def project_root(self) -> Path:
        if self.is_project:
            return self.config_path.parent
        return None
    
    
    def get_project_cmake_core(self) -> Path:
        if self.is_project:
            return self.config_path.parent
        return None
    
    # Utilities:
    def attempt_create_project(self, current_path: Path = None):
        if current_path is None:
            current_path = Path(os.getcwd())
        
        # Create the project config file:
        self.config = self.default_project_config()
        self.config_path = current_path.joinpath(self.CONFIG_FILE_NAME)
        self.save_project_config(self.config_path)
        
        
    def attempt_load_project(self, current_path: Path = None):
        if current_path is None:
            current_path = Path(os.getcwd())
        
        self.config_path = self.locate_project_file()
        if self.config_path  is not None:
            self.load_project_config(self.config_path)
        
    
    def locate_project_file(self, current_path: Path = None) -> Path:
        if current_path is None:
            current_path = Path(os.getcwd())
        
        # Recurse up the current directory tree to find the current project file.
        search_dir = current_path;
        while True:
            for candidate in [search_dir.joinpath(i) for i in os.listdir(search_dir)]:
                if not candidate.is_file() or candidate.name !=self.CONFIG_FILE_NAME:
                    continue
                
                return candidate
            
            if len(search_dir.parents) == 0:
                break
            search_dir = search_dir.parent
            
        return None
    
    
    def load_project_config(self, file_path: Path = None):
        if file_path is None:
            file_path = self.config_path
        
        self.config = self.default_project_config()
        util.load_json_config(file_path, self.config)


    def save_project_config(self, file_path: Path = None):
        if file_path is None:
            file_path = self.config_path
            
        util.save_json_config(file_path, self.config)
        
info = ProjectInfo()
