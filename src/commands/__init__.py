import sys, os, argparse
from typing import Any, Callable

import version_info

class SubCommandBase:
    # Class-wide variables. Used to create the sub-parser:
    name: str = ""
    kwargs: dict = {}
    
    parser: argparse.ArgumentParser

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        self.parser.set_defaults(subcommand_func=lambda args: self.process(args))
        self.setup_args()
        
    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace) -> Any:
        return None


class CommandProcessor:
    parser: argparse.ArgumentParser
    subparsers: Any
    subcommands: dict[str, SubCommandBase]
    
    def __init__(self):
        # self.parser = argparse.ArgumentParser(prog = "rfa", description="Function Analyser for Zelda64Recomp")
        self.parser = argparse.ArgumentParser(description="Function Analyser for Zelda64Recomp")
        self.subparsers = self.parser.add_subparsers(required=True, dest="subcommand", title='subcommands', description='valid subcommands', help='additional help')
        
        self.subcommands = {}

        for i in SubCommandBase.__subclasses__():
            
            new_parser = self.subparsers.add_parser(i.name, **i.kwargs)
            subcommand = i(new_parser)
            
            self.subcommands[i.name] = subcommand

    def process(self, cmd: list[str]) -> Any:
        args = self.parser.parse_args(cmd)
        if hasattr(args, "subcommand_func"):
            return args.subcommand_func(args)
        
        return None

class CommandProcessorArgs(argparse.Namespace):
    subcommand: str
    process_func: Callable

# Importing and declaring all commands here:
from .patching_cmds import *
from .settings_cmds import *

class VersionCommand(SubCommandBase):
    name: str = "version"
    kwargs: dict = {
        "aliases": ["v"],
        "help": "Print version information."
    }

    def setup_args(self):
        pass

    def process(self, args) -> Any:
        print(version_info.name)
        print(version_info.version_string)
        return None
    
