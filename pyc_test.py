import sys, shutil
from pycparser import parse_file
from pycparser.c_ast import *

class Scanner(NodeVisitor):
    searchin_funcs = set()
    searchin_vars = set()

    # Symbols
    functions = set()
    variables = set()
    types = set()
    structs = set()
    unions = set()

    coord = {}

    class GatherSymbols(NodeVisitor):
        local_variables = set()
        current_level_variables : set = None

        def __init__(self, parent):
            super().__init__()
            self.parent : Scanner = parent

        def visit_FuncCall(self, node):
            name : Node = node.name
            if type(name) is ID:
                self.parent.functions.add(name.name)
            else:
                self.visit(name)

            args : Node = node.args
            if args is not None:
                self.visit(args)

        def visit_ID(self, node):
            name : str = node.name
            if name not in self.local_variables:
                self.parent.variables.add(name)
                self.parent.searchin_vars.add(name)

        def visit_Compound(self, node):
            prev_level_variables = self.current_level_variables
            self.current_level_variables = set()

            self.generic_visit(node)

            self.local_variables -= self.current_level_variables
            self.current_level_variables = prev_level_variables

        def visit_Decl(self, node):
            self.local_variables.add(node.name)
            self.current_level_variables.add(node.name)

            self.visit(node.type)

        def visit_IdentifierType(self, node):
            self.parent.types.add(node.names[0])

        def visit_Struct(self, node):
            self.parent.structs.add(node.names[0])

        def visit_Struct(self, node):
            self.parent.unions.add(node.names[0])

        def visit_StructRef(self, node):
            self.visit(node.name)

    v_gatherSymbols : GatherSymbols

    def __init__(self, funcs):
        super().__init__()
        self.v_gatherSymbols = Scanner.GatherSymbols(self)
        for func in funcs:
            self.searchin_funcs.add(func)

    def visit_FuncDef(self, node : Node):
        name = node.decl.name
        if name in self.searchin_funcs:
            for param in node.decl.type.args.params:
                self.v_gatherSymbols.local_variables.add(param.name)

            self.v_gatherSymbols.visit(node.body)

            self.v_gatherSymbols.local_variables.clear()
            self.coord[name] = node.coord
        elif name in self.functions:
            self.coord[name] = node.coord
        elif name in self.variables:
            self.variables.remove(name)
            self.functions.add(name)

            self.coord[name] = node.coord

    def visit_Decl(self, node):
        name = node.name
        t = node.type
        if type(t) is FuncDecl:
        # it's a function declaration
            if name in self.functions:
                self.coord[name] = node.coord
            elif name in self.variables:
                self.variables.remove(name)
                self.functions.add(name)
                self.coord[name] = node.coord
        else:
            while type(t) is PtrDecl:
                t = t.type
            if type(t) is Struct:
            # it's a struct
                if name in self.structs:
                    self.coord[name] = node.coord
                    self.v_gatherSymbols.visit(node.type)
            elif type(t) is Union:
            # it's an union
                if name in self.unions:
                    self.coord[name] = node.coord
                    self.v_gatherSymbols.visit(node.type)
            else:
                t = t.type
                if type(t) is IdentifierType:
                # it's a variable declaration
                    if name in self.variables:
                        self.coord[name] = node.coord
                        self.v_gatherSymbols.visit(node.type)
                elif type(t) is Enum:
                # it's an enum
                    for enumerator in t.values.enumerators:
                        name = enumerator.name
                        if name in self.variables:
                            self.coord[name] = node.coord

    def visit_Typedef(self, node):
        name = node.name
        if name in self.types:
            self.coord[name] = node.coord
        self.visit_Decl(node)

    def generic_visit(self, node):
        return None

    def exec(self, node):
        for c in reversed([i for i in node]):
            self.visit(c)


filename = 'mm/src/code/z_message.c'
funcnames = [
    'Message_OpenText',
    'Message_Init',
]

include_dirs = [
    'mm',
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

v = Scanner(funcnames)
v.exec(ast)

coord = v.coord
for t in v.types:
    print('(type) %s\nat %s\n' % (t, coord[t] if t in coord else 'UNKNOWN'))

for var in v.variables:
    print('(variable) %s\nat %s\n' % (var, coord[var] if var in coord else 'UNKNOWN'))

for func in v.functions:
    print('(function) %s\nat %s\n' % (func, coord[func] if func in coord else 'UNKNOWN'))