import sys, os, subprocess, argparse, shutil, json, io
from typing import Any
from pathlib import Path

from project import ProjectConfig
from project.patch_generator import PatchGenerator
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
        self.parser.add_argument('output', type=argparse.FileType('w', encoding='UTF-8'), help="Location to save the new config file.")

    def process(self, args: CreateConfigCommandArgs) -> Any:
        new_config = ProjectConfig.default_config_dict()
        
        json.dump(new_config, args.output, indent=4)
        args.output.close()
            
        return None
    

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
        self.parser.add_argument('config_path', type=Path, help="Path of the config file to run. Paths within the config are relative to itself, not the working directory.")

    def process(self, args: GeneratePatchCommandArgs) -> Any:
        new_config = ProjectConfig(args.config_path.parent, config_dict=json.loads(args.config_path.read_text()))
        generator =  PatchGenerator(new_config)
        
        generator.process()
        
        return None
    

