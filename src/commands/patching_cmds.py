import sys, os, subprocess, argparse, shutil, json, io
from typing import Any
from pathlib import Path

import project
import util

from commands import SubCommandBase, CommandProcessorArgs

class CreateConfigCommand(SubCommandBase):
    name: str = "newcfg"
    kwargs: dict = {
        "aliases": ["n"],
        "help": "Creates a new config file to use for patch generation."
    }
    
    # Only defined for the sake of annotations. Isn't actually necessary, and doesn't do anything.
    class CreateConfigCommandArgs(CommandProcessorArgs):
        output: io.TextIOWrapper

    def setup_args(self):
        self.parser.add_argument('output', type=argparse.FileType('w', encoding='UTF-8'))

    def process(self, args: CreateConfigCommandArgs) -> Any:
        new_config = project.PatchGenerator.default_config_dict()
        
        json.dump(new_config, args.output, indent=4)
        args.output.close()
            
        return None
    

class PreprocessCommand(SubCommandBase):
    name: str = "preprocess"
    kwargs: dict = {
        "aliases": ["p"],
        "help": "Preprocesses code files from config."
    }

    class GeneratePatchCommandArgs(CommandProcessorArgs):
        config_path: Path
        output: io.TextIOWrapper

    def setup_args(self):
        self.parser.add_argument('config_path', type=Path)
        # self.parser.add_argument('--output', "-o", type=argparse.FileType('w', encoding='UTF-8'), default=None)

    def process(self, args: GeneratePatchCommandArgs) -> Any:
        new_config = project.PatchGenerator(args.config_path.parent, config_dict=json.loads(args.config_path.read_text()))
        
        return new_config.preprocess()
        
    


class GeneratePatchCommand(SubCommandBase):
    name: str = "generate"
    kwargs: dict = {
        "aliases": ["g"],
        "help": "Generates new code file for patching."
    }

    class GeneratePatchCommandArgs(CommandProcessorArgs):
        config_path: Path
        output: io.TextIOWrapper

    def setup_args(self):
        self.parser.add_argument('config_path', type=Path)
        self.parser.add_argument('--output', "-o", type=argparse.FileType('w', encoding='UTF-8'), default=None)

    def process(self, args: GeneratePatchCommandArgs) -> Any:
        new_config = project.PatchGenerator(args.config_path.parent, config_dict=json.loads(args.config_path.read_text()))
        
        new_config.generate()
        
        
        return None
    

