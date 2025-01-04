import shutil, subprocess
from pathlib import Path

import pycparser
import util
import settings
from core import Scanner
from core.cpreprocessor import Preprocessor
from .config_macros import ConfigMacroProcessor

class PatchGenerator:
    macros_processor: ConfigMacroProcessor
    location: Path

    local_macros: dict[str, str]
    includes: list[Path]
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
            "local_macros": {
                "PROJECT_ROOT": "."
            },
            "includes": [
                "${PROJECT_ROOT}/.",
                "${PROJECT_ROOT}/include",
                "${PROJECT_ROOT}/src",
                "${PROJECT_ROOT}/assets",
            ],
            "preproc_command": "${DEFAULT_PREPROC}",
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
            "local_macros": {},
            "includes": [],
            "preproc_command": "",
            "preproc_flags": [],
            "process_specs": [],
        }

    @property
    def preproc_command_path(self):
        return shutil.which(self.preproc_command)

    def __init__(self, location: Path, *, config_dict: dict = None):
        self.macros_processor = ConfigMacroProcessor()
        
        self.location = location
        if config_dict is not None:
            self.configure_from_dict(config_dict)
        else:
            self.project_root = Path(".")
            self.includes = []
            self.preproc_command = ""
            self.preproc_flags = []
            self.process_specs = []
        

    def configure_from_dict(self, in_dict: dict):
        load_dict = self.base_config_dict()
        util.recursive_update_dict(load_dict, in_dict)
        
        # Load macros from file:
        for name, value in load_dict["local_macros"].items():
            self.macros_processor.add_macro(name, value)
            
        # Process all macros:
        self.macros_processor.process_recurse(load_dict)
        
        # print(load_dict)
        # load_dict = in_dict
        self.includes = [
            self.location.joinpath(i) for i in load_dict["includes"]
        ]
        self.preproc_command = load_dict["preproc_command"]
        self.preproc_flags = load_dict["preproc_flags"]
        self.process_specs = [
            PatchGenerator.FileSpec(
                self.location.joinpath(i["in_file"]),
                i["functions"],
                i["preprocess"],
                self.location.joinpath(i["out_file"]),
            )
            for i in load_dict["process_specs"]
        ]
        print("Config Loaded.")
        
    # Processing:
    def print_scanner(self, scanner: Scanner):
        coord = scanner.node
        tag_coord = scanner.tag_node
        print('[SYMBOLS]\n')
        for node in scanner.types:
            print('(type) %s\nat %s\n' % (node, coord[node].coord if node in coord else 'UNKNOWN'))

        for var in scanner.variables:
            print('(variable) %s\nat %s\n' % (var, coord[var].coord if var in coord else 'UNKNOWN'))

        for func in scanner.functions:
            print('(function) %s\nat %s\n' % (func, coord[func].coord if func in coord else 'UNKNOWN'))

        print('[TAGS]\n')
        for struct in scanner.structs:
            print('(struct) %s\nat %s\n' % (struct, tag_coord[struct].coord if struct in tag_coord else 'UNKNOWN'))

        for union in scanner.unions:
            print('(union) %s\nat %s\n' % (union, tag_coord[union].coord if union in tag_coord else 'UNKNOWN'))

        for enum in scanner.enums:
            print('(enum) %s\nat %s\n' % (enum, tag_coord[enum].coord if enum in tag_coord else 'UNKNOWN'))
                


    def preprocess(self):
        for i in self.process_specs:
            output_path = i.out_file.with_suffix(".preproc" + i.out_file.suffix)
            
            result = subprocess.run(
                [self.preproc_command_path, str(i.in_file)]
                + settings.current.preprocessing.default_flags
                + self.preproc_flags
                + [f"-I{i}" for i in self.includes]
                + ["-o", str(output_path)],                
            )
            
            return result.returncode


    def generate(self):
        for spec in self.process_specs:
            ast = pycparser.parse_file(
                spec.in_file,
                use_cpp=spec.preprocess,
                cpp_path=self.preproc_command_path,
                cpp_args=settings.current.preprocessing.default_flags + self.preproc_flags
                + [f"-I{i}" for i in self.includes]
            )

            scanner = Scanner(spec.functions)
            scanner.exec(ast)
            
            for name, node in scanner.filter_nodes_by_source(spec.in_file).items():
                print(name)
                
            for name, node in scanner.filter_tag_nodes_by_source(spec.in_file).items():
                print(name)
            
            include_strs = [str(include).replace("\\", "/") for include in self.includes]
            preproc = Preprocessor(include_strs)
            preproc.exec(spec.in_file)

