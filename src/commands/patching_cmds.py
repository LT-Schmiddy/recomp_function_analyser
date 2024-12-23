import sys, os, subprocess, argparse, shutil, json
from typing import Any
from pathlib import Path

import project
import util

from commands import SubCommandBase

class CreateConfigCommand(SubCommandBase):
    name: str = "newcfg"
    kwargs: dict = {
        "aliases": ["n"],
        "help": "Creates a new config file to use for patch generation."
    }

    def setup_args(self):
        self.hello: Path = Path("dist")
        
        pass

    def process(self, args: argparse.Namespace) -> Any:
        new_config = project.ProjectConfig.default_project_config_dict()
        
        print(json.dumps(new_config, indent=4))
        
        return None
    

class GeneratePatchCommand(SubCommandBase):
    name: str = "generate"
    kwargs: dict = {
        "aliases": ["g"],
        "help": "Generates new code file for patching."
    }

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace) -> Any:
        print("GeneratePatchCommand called")
        return None
    

