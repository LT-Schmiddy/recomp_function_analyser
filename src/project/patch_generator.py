from pathlib import Path

import pycparser
from pycparser.c_generator import CGenerator
from pycparser.c_ast import *

from project import ProjectConfig
import settings

from core.scanner import Scanner
from core.cpreprocessor import Preprocessor
from core.macro import MacroSource, CodeSource, ExternalSource

class PatchGenerator:
    config: ProjectConfig
    
    class CustomCGenerator(CGenerator):
        def _make_indent(self):
            return ' ' * self.indent_level
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        
    def process(self):
        for spec in self.config.process_specs:
            getattr(self, spec.mode)(spec)
    
    def analysis_only(self, spec: ProjectConfig.FileSpec):
        # Analyze code file:
        # Not using deep analyis right now:
        preproc = Preprocessor([str(i) for i in self.config.includes], "", False)
        preproc.exec(spec.in_file)
        
        # Analyze preprocessed AST:
        ast = pycparser.parse_file(
            spec.in_file,
            use_cpp=spec.preprocess,
            cpp_path=str(self.config.preproc_command_path),
            cpp_args=settings.current.preprocessing.default_flags + self.config.preproc_flags
            + [f"-I{i}" for i in self.config.includes]
        )
        scanner = Scanner(spec.functions)
        scanner.exec(ast)
        
        # Prepping for output:
        c_gen = self.CustomCGenerator()
        output = f"# Analysis of '{spec.in_file.relative_to(self.config.location)}'\n\n"
        
        # Functions Analyzed:
        output += f"## Functions Analyzed\n\n"
        for func_name in spec.functions:
            output += f"- {func_name}\n"
        
        # Analysis:
        output += f"\n## Analysis\n"
        
        # Gathering Includes:
        output += f"\n### Includes\n\n```C\n"
        for include in preproc.detected_includes:
            output += f"#include {include}\n"
        output += f"```\n"
        
        # Gathering Macros:
        output += f"\n### Macros\n\n```C\n"
        for name, macro in preproc.macros.items():
            if isinstance(macro.macros, tuple) and len(macro.macros) > 1:
                macro_str: str = macro.macros[1]
                
                # Not a perfect solution, but good enough for now.
                if not macro_str.strip().startswith("#"):
                    continue
                
                output += f"{macro_str}"
        output += f"```\n"
        
        # Gathering Tag Information:
        file_tag_nodes = scanner.filter_tag_nodes_by_source(spec.in_file)
        output += f"\n### Tags\n\n```C\n"
        for name, node in reversed(file_tag_nodes.items()):
            output += c_gen.visit(node) + ";\n"
        output += f"```\n"
        
        # Gathering Def Information:
        file_nodes = scanner.filter_nodes_by_source(spec.in_file)

        # Variable Declarations:
        static_vars = []
        
        output += f"\n### Variable Declarations\n\n```C\n"        
        # for var_name in scanner.variables:
        #     if var_name in file_nodes:
        for name, node in reversed(file_nodes.items()):
            if name in scanner.variables:
                var: Decl = node
                # We'll deal with static variables later:
                if 'static' in var.storage:
                    static_vars.append(var)
                    continue
                # Convert the node into a extern declaration:
                var.storage.insert(0, 'extern')
                var.init = None
                output += c_gen.visit(var) + ";\n"
                
        output += f"```\n"
        
        # Function Declarations:
        output += f"\n### Function Declarations\n\n```C\n"        
        for name, node in reversed(file_nodes.items()):
            if name in scanner.functions: # and func_name not in spec.functions:
                if isinstance(node, FuncDef):
                    output += c_gen.visit(node.decl) + ";\n"
                else:
                    output += c_gen.visit(node) + ";\n"
                
        output += f"```\n"
        
        spec.out_file.write_text(output)
        
    # Methods beyond this point are experimental:
    def ast_only(self, spec: ProjectConfig.FileSpec):
        ast = pycparser.parse_file(
            spec.in_file,
            use_cpp=spec.preprocess,
            cpp_path=str(self.config.preproc_command_path),
            cpp_args=settings.current.preprocessing.default_flags + self.config.preproc_flags
            + [f"-I{i}" for i in self.config.includes]
        )

        scanner = Scanner(spec.functions)
        scanner.exec(ast)
        
        out_code = ""
        c_gen = self.CustomCGenerator()
        
        for name, node in reversed(scanner.node.items()):
            out_code += c_gen.visit(node) + ";\n"
            
        spec.out_file.write_text(out_code)
            
    def includes_and_ast(self, spec: ProjectConfig.FileSpec):
        ast = pycparser.parse_file(
            spec.in_file,
            use_cpp=spec.preprocess,
            cpp_path=str(self.config.preproc_command_path),
            cpp_args=settings.current.preprocessing.default_flags + self.config.preproc_flags
            + [f"-I{i}" for i in self.config.includes]
        )

        scanner = Scanner(spec.functions)
        scanner.exec(ast)
        
        out_code = ""
        c_gen = self.CustomCGenerator()
        
        for i in scanner.collect_includes():
            print(i)
            include_str = str(i).replace("\\\\", "/")
            
            out_code += f"#include \"{include_str}\"\n"
            
        for name, node in reversed(scanner.filter_tag_nodes_by_source(spec.in_file).items()):
            print(f"TAG_NODE: {name}")
            out_code += c_gen.visit(node) + ";\n"
        
        for name, node in reversed(scanner.filter_nodes_by_source(spec.in_file).items()):
            print(f"NODE: {name}")
            
            if isinstance(node, FuncDef) and node.decl.name not in spec.functions:
                out_code += c_gen.visit(node.decl) + ";\n"
            else:
                out_code += c_gen.visit(node) + ";\n"
            
        spec.out_file.write_text(out_code)
        
