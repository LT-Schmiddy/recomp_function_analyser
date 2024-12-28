import sys, shutil
from pathlib import Path
from pycparser import parse_file, c_generator
from pycparser.c_ast import *
from pycparser.plyparser import Coord

class OutputNode:
    depends_on: set[Node]
    node: Node

    def __init__(self, node: Node):
        self.node = node
        self.depends_on = []

    @property
    def coord(self) -> Coord:
        return self.node.coord
    
    @property
    def line_number(self) -> str:
        return self.coord.line
    
    @property
    def node_type(self) -> type:
        return type(self.node)
    

class TestVisitor(NodeVisitor):
    search_funcs: list[str]
    func_decl_nodes: list[FuncDef]
    code_gen: c_generator.CGenerator
    
    def __init__(self, funcs: list[str]):
        super().__init__()    
        self.search_funcs = funcs
        self.func_decl_nodes = []
        
        self.code_gen = c_generator.CGenerator()
        
    def visit_FuncCall(self, node: FuncCall):
            name : Node = node.name
            if isinstance(name, ID):
                self.parent.functions.add(name.name)
            else:
                self.visit(name)

            args : Node = node.args
            if args is not None:
                self.visit(args)
    
    def visit_FuncDef(self, node : FuncDef):
        if node.decl.name in self.search_funcs:
            self.func_decl_nodes.append(node)
            
            print(self.code_gen.visit(node.decl))
        
        self.visit(node.body)
            
    def analyse(self, node):
        for c in reversed([i for i in node]):
            self.visit(c)