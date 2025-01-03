import shutil
from pathlib import Path
from pycparser import parse_file
from pycparser.c_ast import *

class CodeEntry:
    coord: Coord

class CodeHandler:
    pass