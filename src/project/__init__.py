import os, shutil, json, subprocess
from typing import Union
from pathlib import Path

import util
import settings

class ProjectConfig():
    location: Path
    
    project_root: Path
    project_includes: list[Path]
    external_includes: list[Path]
    proproc_flags: list[str]
    
    class FileSpec:
        file: Path
        functions: list[str]
        preprocess: bool
        
        def __init__(self, file: Path, functions: list[str], preprocess = True):
            self.file = file
            self.functions = functions
            self.preprocess = preprocess
            
        def as_dict(self) -> dict:
            return {
                "file": str(self.file),
                "functions": self.functions,
                "preprocess": self.preprocess
            }
    
    process_specs: list[FileSpec]
    
    @classmethod
    def default_project_config_dict(cls):
        return {
            "project_root": ".",
            "project_includes": [
                ".",
                "include",
                "src",
                "assets",
            ],
            "external_includes": [],
            "process_specs": [
                {
                    "file": "test_file.c",
                    "functions": [
                        "TestFuncName"
                    ],
                    "preprocess": True
                }
            ]
        }
    
    def __init__(self, *, config_dict: dict = None):
        if config_dict is not None:
            self.load_from_dict(config_dict)
        else:    
            self.project_root = "."
            self.project_includes = []
            self.external_includes = []
            self.process_specs = []
            
    def load_from_dict(self, input):
        self.project_root = Path(input["project_root"])
        self.project_includes = [Path(i) for i in input["project_includes"]]
        self.external_includes = [Path(i) for i in input["external_includes"]]
        self.process_specs = [ProjectConfig.FileSpec(Path(i["file"]), i["functions"], i["preprocess"]) for i in input["process_specs"]]
        
    def save_to_dict(self):
        return {
            "project_root": str(self.project_root),
            "project_includes": [str(i) for i in self.project_includes],
            "external_includes": [str(i) for i in self.external_includes],
            "process_specs": [i.as_dict() for i in self.process_specs]
        }
    

class ProjectHandler:    
    config_path: Path = None
    config: dict = None
    
    
    
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
        
info = ProjectHandler()
