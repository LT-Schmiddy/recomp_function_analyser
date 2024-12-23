import sys, os, shutil, json, subprocess, io
from typing import Union
from pathlib import Path

import pycparser

import util
import settings
from core import Scanner

class PatchGenerator():
    location: Path
    
    project_root: Path
    project_includes: list[Path]
    external_includes: list[Path]
    preproc_command: str
    preproc_flags: list[str]
    
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
    def default_config_dict(cls):
        return {
            "project_root": ".",
            "project_includes": [
                ".",
                "include",
                "src",
                "assets",
            ],
            "external_includes": [],
            "preproc_command": "clang",
            "preproc_flags": [
                '-U__GNUC__',
                '-nostdinc',
                '-E',
                '-D_LANGUAGE_C',
                '-DMIPS',
            ],
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
        
    @classmethod
    def base_config_dict(cls):
        return {
            "project_root": "",
            "project_includes": [],
            "external_includes": [],
            "preproc_command": "",
            "preproc_flags": [],
            "process_specs": []
        }
        
    @property
    def preproc_command_path(self):
        return shutil.which(self.preproc_command)
    
    def __init__(self, location: Path, *, config_dict: dict = None):
        self.location = location
        
        if config_dict is not None:
            self.configure_from_dict(config_dict)
        else:    
            self.project_root = Path(".")
            self.project_includes = []
            self.external_includes = []
            self.preproc_command = ""
            self.preproc_flags = []
            self.process_specs = []

                   
    def configure_from_dict(self, input: dict):
        # load_dict = self.base_config_dict()
        # util.recursive_update_dict(load_dict, input)
        
        load_dict = input
        
        self.project_root = self.location.joinpath(load_dict["project_root"])
        self.project_includes = [self.project_root.joinpath(i) for i in load_dict["project_includes"]]
        self.external_includes = [self.location.joinpath(i) for i in load_dict["external_includes"]]
        self.preproc_command = load_dict["preproc_command"]
        self.preproc_flags = load_dict["preproc_flags"]
        self.process_specs = [PatchGenerator.FileSpec(self.project_root.joinpath(i["file"]), i["functions"], i["preprocess"]) for i in load_dict["process_specs"]]

    # Processing:
    
    def preprocess(self, out: io.TextIOWrapper = None):
        if out is None:
            out = sys.stdout
        
        for i in self.process_specs:
            result = subprocess.run(
                [
                    self.preproc_command_path,
                    str(i.file)
                ] +
                self.preproc_flags + [
                    f'-I{i}' for i in self.project_includes
                ]+ [
                    f'-I{i}' for i in self.external_includes
                ],
                stdout=out
            )
            

    def generate(self):
        for i in self.process_specs:
            ast = pycparser.parse_file(i.file, use_cpp=True,
                cpp_path = self.preproc_command_path,
                cpp_args = self.preproc_flags + [
                    f'-I{i}' for i in self.project_includes
                ]+ [
                    f'-I{i}' for i in self.external_includes
                ]
            )
            
            
            v = Scanner(i.functions)
            v.exec(ast)

            coord = v.coord
            for t in v.types:
                print('(type) %s\nat %s\n' % (t, coord[t] if t in coord else 'UNKNOWN'))

            for var in v.variables:
                print('(variable) %s\nat %s\n' % (var, coord[var] if var in coord else 'UNKNOWN'))

            for func in v.functions:
                print('(function) %s\nat %s\n' % (func, coord[func] if func in coord else 'UNKNOWN'))
    