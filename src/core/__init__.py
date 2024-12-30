import sys, shutil
from pycparser import parse_file
from pycparser.c_ast import *

class Scanner(NodeVisitor):
    TAG_PREFIX = ''

    searchin_funcs = set()

    # Symbols
    functions = set()
    variables = set()
    types = set()

    coord = {}

    # Tags
    structs = set()
    unions = set()
    enums = set()

    tag_coord = {}

    class GatherSymbols(NodeVisitor):
        local_variables : set[str] = set()
        current_level_variables : set[str] = None

        local_tags : set[str] = set()
        current_level_tags : set[str] = None

        def __init__(self, parent):
            super().__init__()
            self.parent : Scanner = parent

        def visit_FuncCall(self, node : Node):
            name : Node = node.name
            if isinstance(name, ID):
                self.parent.functions.add(name.name)
            else:
                self.visit(name)

            args : Node = node.args
            if args != None:
                self.visit(args)

        def visit_ID(self, node : Node):
            name : str = node.name
            if name not in self.local_variables:
                self.parent.variables.add(name)

        def visit_Compound(self, node : Node):
            prev_level_variables = self.current_level_variables
            self.current_level_variables = set()

            prev_level_tags = self.current_level_tags
            self.current_level_tags = set()

            self.generic_visit(node)

            self.local_tags -= self.current_level_tags
            self.current_level_tags = prev_level_tags

            self.local_variables -= self.current_level_variables
            self.current_level_variables = prev_level_variables

        def visit_Decl(self, node : Node):
            self.local_variables.add(node.name)
            self.current_level_variables.add(node.name)

            self.visit(node.type)

        def visit_IdentifierType(self, node : Node):
            self.parent.types.update(set(node.names))

        def visit_Struct(self, node : Node):
            self.handle_struct_union(node, self.parent.structs)

        def visit_Union(self, node : Node):
            self.handle_struct_union(node, self.parent.unions)

        def visit_Enum(self, node : Node):
            name : str = node.name
            values = node.values
            if values != None:
                if name != None:
                    self.local_tags.add(name)
                    self.current_level_tags.add(name)

                for enumerator in values.enumerators:
                    name = enumerator.name
                    if name in self.parent.variables:
                        self.coord[name] = node.coord
            elif name != None and name not in self.local_tags:
                self.parent.enums.add(Scanner.TAG_PREFIX + name)


        def handle_struct_union(self, node : Node, symbols : set[str]):
            name : str = node.name
            decls = node.decls

            if decls != None:
                if name != None:
                    self.local_tags.add(name)
                    self.current_level_tags.add(name)

                for decl in decls:
                    self.visit(decl.type)
            elif name != None and name not in self.local_tags:
                symbols.add(Scanner.TAG_PREFIX + name)

        def visit_StructRef(self, node : Node):
            self.visit(node.name)

        def visit_FuncDecl(self, node : Node):
            for param in node.args.params:
                self.visit(param.type)
            self.visit(node.type)

    v_gatherSymbols : GatherSymbols

    def __init__(self, funcs):
        super().__init__()
        self.v_gatherSymbols = Scanner.GatherSymbols(self)
        for func in funcs:
            self.searchin_funcs.add(func)

    def visit_FuncDef(self, node : Node):
        name = node.decl.name
        is_tracked = False

        t = node.decl.type
        args = t.args

        if name in self.searchin_funcs:
            if args != None:
                for param in args.params:
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
            if args != None:
                for param in args.params:
                    self.v_gatherSymbols.visit(param.type)
            self.v_gatherSymbols.visit(t.type)
            self.coord[name] = node.coord


    def visit_Decl(self, node : Node):
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
                self.v_gatherSymbols.visit(t)
                self.coord[name] = node.coord
        else:
            t = self.skip_array_ptr_declaration(t)

            if isinstance(t, TypeDecl) and not isinstance(t, Typedef):
            # variable declaration
                t = t.type
                if name in self.variables:
                    self.coord[name] = node.coord
                    self.v_gatherSymbols.visit(node.type)

            if isinstance(t, Enum):
            # enum declaration
                self.handle_enum_declaration(t, node.coord)
            else:
            # struct or union declaration
                self.handle_nested_struct_union_declarations(t, node.coord, [])

    def visit_Typedef(self, node : Node):
        name = node.name
        if name in self.types:
            self.coord[name] = node.coord
            t = node.type.type
            t = self.skip_array_ptr_declaration(t)

            if isinstance(t, TypeDecl):
                t = t.type

            if isinstance(t, IdentifierType):
                self.types.update(set(t.names))
            elif isinstance(t, Enum):
                self.handle_enum_declaration(t, node.coord)
            else:
                self.handle_nested_struct_union_declarations(t, node.coord, None)
        else:
            # handle this like a normal declaration
            self.visit_Decl(node)

    def skip_array_ptr_declaration(self, node : Node) -> Node:
        while isinstance(node, ArrayDecl):
            node = node.type
        while isinstance(node, PtrDecl):
            node = node.type
        return node


    def handle_enum_declaration(self, node : Node, origin_coord : str):
        values = node.values
        if values != None:
            name = node.name
            if name != None:
                name = Scanner.TAG_PREFIX + name
                self.tag_coord[name] = origin_coord
            for enumerator in values.enumerators:
                name = enumerator.name
                if name in self.variables:
                    self.coord[name] = origin_coord

    def handle_nested_struct_union_declarations(self, node : Node, origin_coord : str, gather_stash : list):
        node = self.skip_array_ptr_declaration(node)
        if isinstance(node, TypeDecl):
            node = node.type

        symbols : set[str] = None
        if isinstance(node, Struct):
            symbols = self.structs
        elif isinstance(node, Union):
            symbols = self.unions

        if symbols != None:
            name = node.name
            if name != None:
                name = Scanner.TAG_PREFIX + name
                if name in symbols and gather_stash != None:
                    for el in gather_stash:
                        self.v_gatherSymbols.visit(el)
                    gather_stash = None
            decls = node.decls
            if decls != None:
                if name != None:
                    self.tag_coord[name] = origin_coord
                for decl in decls:
                    self.handle_nested_struct_union_declarations(decl.type, origin_coord, gather_stash)
        elif isinstance(node, Enum):
            self.handle_enum_declaration(node, origin_coord)
        elif gather_stash != None:
            gather_stash += [node]
        else:
            self.v_gatherSymbols.visit(node)

    def generic_visit(self, node : Node):
        return None

    def exec(self, node : Node):
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
    tag_coord = v.tag_coord
    print('[SYMBOLS]\n')
    for node in v.types:
        print('(type) %s\nat %s\n' % (node, coord[node] if node in coord else 'UNKNOWN'))

    for var in v.variables:
        print('(variable) %s\nat %s\n' % (var, coord[var] if var in coord else 'UNKNOWN'))

    for func in v.functions:
        print('(function) %s\nat %s\n' % (func, coord[func] if func in coord else 'UNKNOWN'))

    print('[TAGS]\n')
    for struct in v.structs:
        print('(struct) %s\nat %s\n' % (struct, tag_coord[struct] if struct in tag_coord else 'UNKNOWN'))

    for union in v.unions:
        print('(union) %s\nat %s\n' % (union, tag_coord[union] if union in tag_coord else 'UNKNOWN'))

    for enum in v.enums:
        print('(enum) %s\nat %s\n' % (enum, tag_coord[enum] if enum in tag_coord else 'UNKNOWN'))