import sys, os, subprocess, argparse, shutil, json
from typing import Any
from pathlib import Path

from util import *
from colors import *

from commands import SubCommandBase

class CreateConfigCommand(SubCommandBase):
    name: str = "newcfg"
    kwargs: dict = {
        "aliases": ["n"],
        "help": "Creates a new config file to use for patch generation."
    }

    def setup_args(self):
        pass

    def process(self, args: argparse.Namespace) -> Any:
        print("CreateConfigCommand called")
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

