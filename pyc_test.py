import sys, shutil
from pycparser import parse_file, c_ast

class FindDef(c_ast.NodeVisitor):
    res = None
    def __new__(cls, funcname):
        instance = super(FindDef, cls).__new__(cls)
        instance.funcname = funcname
        return instance

    def visit_FuncDef(self, node):
        if (node.decl.name == self.funcname):
            self.res = node


class FindFuncCalls(c_ast.NodeVisitor):
    res = []
    def visit_FuncCall(self, node):
        self.res += [node]


class FindFuncDeclarations(c_ast.NodeVisitor):
    def __new__(cls, funcnames):
        instance = super(FindFuncDeclarations, cls).__new__(cls)
        instance.funcnames = funcnames
        return instance

    def visit_FuncDecl(self, node):
        try:
            name = node.type.type.names[0]
            if name in self.funcnames:
                print('%s %s at %s' % (node.type.type.names[0], node.type.declname, node.coord))
        except:
            print('%s at %s' % (node.type, node.coord))


def gather_declarations(ast, funcname):
    # Find the definition of the function in the .c file
    v = FindDef(funcname)
    v.visit(ast)
    definition = v.res

    if definition is None:
        raise Exception("Definition for %s doesn't exist" % (funcname))
    # TODO Check if the definition isn't from an included file (weird, and shouldn't happen in any
    # serious decomp, but this probably should be detected for the general use)

    # Find names of functions called inside the definition
    v = FindFuncCalls()
    v.visit(definition.body)
    calls = v.res

    funcnames = set()
    for call in calls:
        funcnames.add(call.name.name)

    # TODO Separate functions declared in the .c file, then gather their declarations

    # TODO Find names of global variables used inside the definition

    # TODO Separate global variables declared in the .c file, then gather their declarations

    # TODO Find names of macros used inside the definition

    # TODO Separate macros declared in the .c file, then gather their declarations

    # TODO For the remaining functions, global variables and macros gather the closest headers which contain them

    print('%s' % (funcnames))

    v = FindFuncDeclarations(funcnames)
    v.visit(ast)

filename = 'mm/src/libultra/os/gettime.c'
funcname = 'osGetTime'

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
gather_declarations(ast, funcname)