import sys, shutil
from pycparser import parse_file
from pycparser.c_ast import *
from pycparser.plyparser import Coord

class OutputNode:
    node: Node

    def __init__(self, node: Node):
        self.node = node

    @property
    def coord(self) -> Coord:
        return self.node.coord
    
    @property
    def line_number(self) -> str:
        return self.coord.line
    
    @property
    def node_type(self) -> type:
        return type(self.node)
    

class Scanner(NodeVisitor):
    searchin_funcs: set[str]

    # Symbols
    functions: set[str]
    variables: set[str]
    types: set[str]
    structs: set[str]
    unions: set[str]

    coord: dict[str, Coord]
    output_nodes: list[OutputNode]
    
    root_node: Node

    class GatherSymbols(NodeVisitor):
        local_variables = set()
        current_level_variables : set = None

        def __init__(self, parent):
            super().__init__()
            self.parent : Scanner = parent

        def visit_FuncCall(self, node: Node):
            name : Node = node.name
            if isinstance(name, ID):
                self.parent.functions.add(name.name)
            else:
                self.visit(name)

            args : Node = node.args
            if args is not None:
                self.visit(args)

        def visit_ID(self, node: ID):
            name : str = node.name
            if name not in self.local_variables:
                self.parent.variables.add(name)

        def visit_Compound(self, node: Compound):
            prev_level_variables = self.current_level_variables
            self.current_level_variables = set()

            self.generic_visit(node)

            self.local_variables -= self.current_level_variables
            self.current_level_variables = prev_level_variables

        def visit_Decl(self, node: Decl):
            self.local_variables.add(node.name)
            self.current_level_variables.add(node.name)

            self.visit(node.type)

        def visit_IdentifierType(self, node: IdentifierType):
            self.parent.types.add(node.names[0])

        def visit_Struct(self, node: Struct):
            self.parent.structs.add(node.name)

        def visit_Union(self, node: Union):
            self.parent.unions.add(node.name)

        def visit_StructRef(self, node: StructRef):
            self.visit(node.name)

    v_gatherSymbols : GatherSymbols

    def __init__(self, funcs):
        super().__init__()
        self.searchin_funcs = set()

        # Symbols
        self.functions= set()
        self.variables= set()
        self.types= set()
        self.structs= set()
        self.unions= set()

        self.coord= {}
        self.output_nodes = []
        
        self.v_gatherSymbols = Scanner.GatherSymbols(self)
        for func in funcs:
            self.searchin_funcs.add(func)

    def visit_FuncDef(self, node : FuncDef):
        name = node.decl.name
        is_tracked = False
        if name in self.searchin_funcs:
            for param in node.decl.type.args.params:
                self.v_gatherSymbols.local_variables.add(param.name)

            self.v_gatherSymbols.visit(node.body)

            self.v_gatherSymbols.local_variables.clear()
            is_tracked = True
        elif name in self.functions:
            is_tracked = True
        elif name in self.variables:
            self.variables.remove(name)
            self.functions.add(name)

            is_tracked = True

        if is_tracked:
            t = node.decl.type
            for param in t.args.params:
                self.v_gatherSymbols.visit(param.type)
            self.v_gatherSymbols.visit(t.type)
            self.coord[name] = node.coord
            self.output_nodes.append(OutputNode(node))


    def visit_Decl(self, node: Decl):
        name = node.name
        t = node.type
        if isinstance(t, FuncDecl):
        # function declaration
            is_tracked = False
            if name in self.functions:
                is_tracked = True
            elif name in self.variables:
                self.variables.remove(name)
                self.functions.add(name)
                is_tracked = True

            if is_tracked:
                t = node.type
                for param in t.args.params:
                    self.v_gatherSymbols.visit(param.type)
                self.v_gatherSymbols.visit(t.type)
                self.coord[name] = node.coord
                self.output_nodes.append(OutputNode(node))
                
        else:
            while isinstance(t, PtrDecl):
                t = t.type
            if isinstance(t, Struct):
            # struct declaration
                if name in self.structs:
                    self.coord[name] = node.coord
                    self.output_nodes.append(OutputNode(node))
                    self.v_gatherSymbols.visit(node.type)
            elif isinstance(t, Union):
            # union declaration
                if name in self.unions:
                    self.coord[name] = node.coord
                    self.output_nodes.append(OutputNode(node))
                    self.v_gatherSymbols.visit(node.type)
            else:
                t = t.type
                if isinstance(t, IdentifierType):
                # variable declaration
                    if name in self.variables:
                        self.coord[name] = node.coord
                        self.output_nodes.append(OutputNode(node))
                        self.v_gatherSymbols.visit(node.type)
                elif isinstance(t, Enum):
                # enum declaration
                    for enumerator in t.values.enumerators:
                        name = enumerator.name
                        if name in self.variables:
                            self.output_nodes.append(OutputNode(node))
                            self.coord[name] = node.coord

    def visit_Typedef(self, node: Typedef):
        name = node.name
        if name in self.types:
            self.output_nodes.append(OutputNode(node))
            self.coord[name] = node.coord
        self.visit_Decl(node)

    def generic_visit(self, node: Node):
        return None

    def exec(self, node):
        for c in reversed([i for i in node]):
            self.visit(c)
            

if __name__ == '__main__':
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
    
