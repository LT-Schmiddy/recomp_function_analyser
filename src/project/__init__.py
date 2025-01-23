import shutil, subprocess
from pathlib import Path

import pycparser
import util
import settings
from .config_macros import ConfigMacroProcessor

class ProjectConfig:
    config_macros: ConfigMacroProcessor
    location: Path

    local_macros: dict[str, str]
    standard_c_lib_dir: str
    includes: list[Path]
    preproc_command: str
    preproc_flags: list[str]

    class FileSpec:
        in_file: Path
        functions: list[str]
        preprocess: bool
        out_file: Path

        def __init__(
            self, in_file: Path, functions: list[str], mode: str, preprocess: bool, out_file: Path
        ):
            self.in_file = in_file
            self.functions = functions
            self.mode = mode
            self.preprocess = preprocess
            self.out_file = out_file

        def as_dict(self) -> dict:
            return {
                "in_file": str(self.in_file),
                "functions": self.functions,
                "mode": self.mode,
                "preprocess": self.preprocess,
                "out_file": str(self.out_file),
            }

    process_specs: list[FileSpec]

    @classmethod
    def default_config_dict(cls):
        return {
            "local_macros": {
                "PROJECT_ROOT": ".",
                "DEFAULT_MODE": "analysis_only"
            },
            "standard_c_lib_dir" : "",
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
                "-D_LANGUAGE_C",
                "-DMIPS",
            ],
            "process_specs": [
                {
                    "in_file": "test_file.c",
                    "functions": ["TestFuncName"],
                    "mode": "${DEFAULT_MODE}",
                    "preprocess": True,
                    "out_file": "out_file.c",
                }
            ],
        }

    @classmethod
    def base_config_dict(cls):
        return {
            "local_macros": {},
            "standard_c_lib_dir" : "",
            "includes": [],
            "preproc_command": "",
            "preproc_flags": [],
            "process_specs": [],
        }

    @property
    def preproc_command_path(self) -> Path:
        retVal = Path(self.preproc_command)
        if retVal.is_file():
            return retVal
        else:
            return Path(shutil.which(self.preproc_command))

    def __init__(self, location: Path, *, config_dict: dict = None):
        self.config_macros = ConfigMacroProcessor()

        self.location = location.absolute()
        if config_dict is not None:
            self.configure_from_dict(config_dict)
        else:
            self.standard_c_lib_dir = ""
            self.includes = []
            self.preproc_command = ""
            self.preproc_flags = []
            self.process_specs = []


    def configure_from_dict(self, in_dict: dict):
        load_dict = self.base_config_dict()
        util.recursive_update_dict(load_dict, in_dict)

        # Load macros from file:
        for name, value in load_dict["local_macros"].items():
            self.config_macros.add_macro(name, value)

        # Process all macros:
        self.config_macros.process_recurse(load_dict)

        # print(load_dict)
        # load_dict = in_dict
        self.includes = [
            self.location.joinpath(i) for i in load_dict["includes"]
        ]
        self.standard_c_lib_dir = load_dict["standard_c_lib_dir"]
        self.preproc_command = load_dict["preproc_command"]
        self.preproc_flags = load_dict["preproc_flags"]
        self.process_specs = [
            ProjectConfig.FileSpec(
                self.location.joinpath(i["in_file"]),
                i["functions"],
                i["mode"],
                i["preprocess"],
                self.location.joinpath(i["out_file"]),
            )
            for i in load_dict["process_specs"]
        ]
        print("Config Loaded.")
    # Processing:

    def preprocess(self):
        for i in self.process_specs:
            output_path = i.out_file.with_suffix(".preproc" + i.out_file.suffix)

            result = subprocess.run(
                [str(self.preproc_command_path), str(i.in_file)]
                + settings.current.preprocessing.default_flags
                + self.preproc_flags
                + [f"-I{i}" for i in self.includes]
                + ["-o", str(output_path)],
            )

            return result.returncode

