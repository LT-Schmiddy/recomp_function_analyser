import sys, shutil
from pycparser import parse_file

filename = 'mm/src/libultra/os/gettime.c'

include_dirs = [
    'mm/include',
    'mm/src',
    'mm/assets'
]

cpp_flags = [
    '-U__GNUC__',
    '-nostdinc',
    '-E',
    '-D_LANGUAGE_C',
    '-DMIPS',
]

# Attempting Analysis:
clang_path = shutil.which("clang")
ast = parse_file(filename, use_cpp=True,
        cpp_path=clang_path,
        cpp_args=cpp_flags + [
            f'-I{i}' for i in include_dirs
        ])
ast.show()