import sys, os, shutil, json, subprocess, io
from typing import Union
from pathlib import Path

import pycparser
from pycparser import c_generator
import util
import settings
from core.ast_code_generator import TestVisitor


class PatchGenerator:
    location: Path

    project_root: Path
    project_includes: list[Path]
    external_includes: list[Path]
    preproc_command: str
    preproc_flags: list[str]

    class FileSpec:
        in_file: Path
        functions: list[str]
        preprocess: bool
        out_file: Path

        def __init__(
            self, in_file: Path, functions: list[str], preprocess: bool, out_file: Path
        ):
            self.in_file = in_file
            self.functions = functions
            self.preprocess = preprocess
            self.out_file = out_file

        def as_dict(self) -> dict:
            return {
                "in_file": str(self.in_file),
                "functions": self.functions,
                "preprocess": self.preprocess,
                "out_file": str(self.out_file),
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
                "-U__GNUC__",
                "-nostdinc",
                "-E",
                "-D_LANGUAGE_C",
                "-DMIPS",
            ],
            "process_specs": [
                {
                    "in_file": "test_file.c",
                    "functions": ["TestFuncName"],
                    "preprocess": True,
                    "out_file": "out_file.c",
                }
            ],
        }

    @classmethod
    def base_config_dict(cls):
        return {
            "project_root": "",
            "project_includes": [],
            "external_includes": [],
            "preproc_command": "",
            "preproc_flags": [],
            "process_specs": [],
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
        self.project_includes = [
            self.project_root.joinpath(i) for i in load_dict["project_includes"]
        ]
        self.external_includes = [
            self.location.joinpath(i) for i in load_dict["external_includes"]
        ]
        self.preproc_command = load_dict["preproc_command"]
        self.preproc_flags = load_dict["preproc_flags"]
        self.process_specs = [
            PatchGenerator.FileSpec(
                self.project_root.joinpath(i["in_file"]),
                i["functions"],
                i["preprocess"],
                self.location.joinpath(i["out_file"]),
            )
            for i in load_dict["process_specs"]
        ]

    # Processing:

    def preprocess(self, out: io.TextIOWrapper = None):
        if out is None:
            out = sys.stdout

        for i in self.process_specs:
            result = subprocess.run(
                [self.preproc_command_path, str(i.in_file)]
                + self.preproc_flags
                + [f"-I{i}" for i in self.project_includes]
                + [f"-I{i}" for i in self.external_includes],
                stdout=out,
            )
            
            if result.returncode != 0:
                return result.returncode
            
        

    def generate(self):
        for i in self.process_specs:
            ast = pycparser.parse_file(
                i.in_file,
                use_cpp=i.preprocess,
                cpp_path=self.preproc_command_path,
                cpp_args=self.preproc_flags
                + [f"-I{i}" for i in self.project_includes]
                + [f"-I{i}" for i in self.external_includes],
            )

            test = TestVisitor(i.functions)
            test.analyse(ast)
            
            generator = c_generator.CGenerator()
            out_str = ""            
            for j in reversed(test.func_decl_nodes):
                out_str += generator.visit(j.param_decls) + ";\n"
                out_str += generator.visit(j.decl) + ";\n"
                
            i.out_file.write_text(out_str)
                

