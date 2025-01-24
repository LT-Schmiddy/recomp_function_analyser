from pathlib import Path
import subprocess

import pycparser
from pycparser.c_generator import CGenerator
from pycparser.c_ast import *

from project import ProjectConfig
import settings

from core.scanner import Scanner
from core.cpreprocessor import Preprocessor
from core.macro import MacroSource, CodeSource, ExternalSource

class PatchGenerator:
    modes: dict[str, str] = {
        "basic_analysis_only": "Performs basic analysis on the input to determine function dependencies.",
        "preprocess_only": "Preprocesses the input file and outputs the result."
    }
    
    config: ProjectConfig
    
    class CustomCGenerator(CGenerator):
        def _make_indent(self):
            return ' ' * self.indent_level
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        
    def process(self):
        for spec in self.config.process_specs:
            if spec.mode in self.modes:
                getattr(self, spec.mode)(spec)
            else:
                raise ValueError(f"'{spec.mode}' is not a valid analysis mode.")
    
    def _create_source_include_code(self, preproc: Preprocessor) -> str:
        retVal = ""
        
        for include in sorted(preproc.detected_includes):
            retVal += f"#include {include}\n"
            
        return retVal
    
    def _create_source_macro_code(self, preproc: Preprocessor) -> str:
        retVal = ""
        for name, macro in preproc.macros.items():
            if isinstance(macro.macros, tuple) and len(macro.macros) > 1:
                macro_str: str = macro.macros[1]
                
                # Not a perfect solution, but good enough for now.
                if not macro_str.strip().startswith("#"):
                    continue
                
                retVal += f"{macro_str}"
        
        return retVal
    
    def _create_ast_tag_node_code(self, scanner: Scanner, c_gen: CGenerator, filter: str = None):
        retVal = ""
        if filter is not None:
            tag_nodes = scanner.filter_tag_nodes_by_source(filter)
        else:
            tag_nodes = scanner.tag_node
        
        for name, node in reversed(tag_nodes.items()):
            retVal += c_gen.visit(node) + ";\n"
        
        return retVal
    
    
    def _create_ast_types(self, scanner: Scanner, c_gen: CGenerator, filter: str = None):
        retVal = ""
        if filter is not None:
            nodes = scanner.filter_nodes_by_source(filter)
        else:
            nodes = scanner.node
        
        for name, node in reversed(nodes.items()):
            if name in scanner.types:
                retVal += c_gen.visit(node) + ";\n"
        
        return retVal
    
    def _create_ast_variable_externs(self, scanner: Scanner, c_gen: CGenerator, filter: str = None):
        retVal = ""
        if filter is not None:
            nodes = scanner.filter_nodes_by_source(filter)
        else:
            nodes = scanner.node
        
        for name, node in reversed(nodes.items()):
            if name in scanner.variables:
                var: Decl = node
                # We'll deal with static variables later:
                if 'static' in var.storage:
                    continue
                # Convert the node into a extern declaration:
                var.storage.insert(0, 'extern')
                var.init = None
                retVal += c_gen.visit(var) + ";\n"
        
        return retVal
    
    def _create_ast_static_variable_externs(self, scanner: Scanner, c_gen: CGenerator, filter: str = None):
        retVal = ""
        if filter is not None:
            nodes = scanner.filter_nodes_by_source(filter)
        else:
            nodes = scanner.node
        
        for name, node in reversed(nodes.items()):
            if name in scanner.variables:
                var: Decl = node
                # We'll deal with static variables later:
                if 'static' not in var.storage:
                    continue
                # Convert the node into a extern declaration:
                var.storage.insert(0, 'extern')
                var.init = None
                retVal += c_gen.visit(var) + ";\n"
        
        return retVal
                
    def _create_ast_function_declarations(self, scanner: Scanner, c_gen: CGenerator, filter: str = None):
        retVal = ""
        if filter is not None:
            nodes = scanner.filter_nodes_by_source(filter)
        else:
            nodes = scanner.node
        
        for name, node in reversed(nodes.items()):
            if name in scanner.functions: # and func_name not in spec.functions:
                if isinstance(node, FuncDef):
                    retVal += c_gen.visit(node.decl) + ";\n"
                else:
                    retVal += c_gen.visit(node) + ";\n"
        
        return retVal
        
    def basic_analysis_only(self, spec: ProjectConfig.FileSpec):
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
        output = f"// Analysis of '{spec.in_file.relative_to(self.config.location)}'\n\n"
        
        # Functions Analyzed:
        output += f"// Functions Analyzed\n"
        for func_name in spec.functions:
            output += f"// - {func_name}\n"
        
        output += f"\n// NOTE: generation is still not perfect. This file may need some modification before it can be used.\n\n"
        
        # Gathering Includes:
        output += f"// Detected includes from original file:\n"
        output += self._create_source_include_code(preproc)
        output += f"\n"
        
        # Gathering Macros:
        output += f"// Detected these macros in the original file:\n"
        output += self._create_source_macro_code(preproc)
        output += f"\n"
        
        output += "\n// The following code is generated from the preprocessed AST,\n" \
            + "// and thus will likely have flattened macros or may not work properly.\n" \
            + "// If you encounter issues with any declaration, try copying the original\n" \
            + "// from the input file. Use CTRL+F with the symbol name to locate it.\n" 
        
        # Gathering Tag Information:
        output += f"// Required tags from original file:\n"
        output += self._create_ast_tag_node_code(scanner, c_gen, spec.in_file)
        output += f"\n"
        
        # Type Declarations: 
        output += f"// Required type declarations from original file:\n"        
        output += self._create_ast_types(scanner, c_gen, spec.in_file)
        output += f"\n"
        
        # Variable Declarations:    
        output += f"// Required variable declarations from original file:\n"        
        output += self._create_ast_static_variable_externs(scanner, c_gen, spec.in_file)
        output += f"\n"
             
        output += f"// The following variables are static. They need to be added to a custtom datasyms file to work correctly:\n"        
        output += self._create_ast_variable_externs(scanner, c_gen, spec.in_file)
        output += f"\n"
        
        # Function Declarations:
        output += f"// Required function declarations from original file:\n"        
        output += self._create_ast_function_declarations(scanner, c_gen, spec.in_file)
        output += f"\n"
        
        spec.out_file.write_text(output)
    
    def preprocess_only(self, spec: ProjectConfig.FileSpec):
        result = subprocess.run(
            [str(self.config.preproc_command_path), str(spec.in_file)]
            + settings.current.preprocessing.default_flags
            + self.config.preproc_flags
            + [f"-I{i}" for i in self.config.includes]
            + ["-o", str(spec.out_file)],
        )

        return result.returncode

    
    # Methods beyond this point are experimental:
    # def ast_only(self, spec: ProjectConfig.FileSpec):
    #     ast = pycparser.parse_file(
    #         spec.in_file,
    #         use_cpp=spec.preprocess,
    #         cpp_path=str(self.config.preproc_command_path),
    #         cpp_args=settings.current.preprocessing.default_flags + self.config.preproc_flags
    #         + [f"-I{i}" for i in self.config.includes]
    #     )

    #     scanner = Scanner(spec.functions)
    #     scanner.exec(ast)
        
    #     out_code = ""
    #     c_gen = self.CustomCGenerator()
        
    #     for name, node in reversed(scanner.node.items()):
    #         out_code += c_gen.visit(node) + ";\n"
            
    #     spec.out_file.write_text(out_code)
            
    # def includes_and_ast(self, spec: ProjectConfig.FileSpec):
    #     ast = pycparser.parse_file(
    #         spec.in_file,
    #         use_cpp=spec.preprocess,
    #         cpp_path=str(self.config.preproc_command_path),
    #         cpp_args=settings.current.preprocessing.default_flags + self.config.preproc_flags
    #         + [f"-I{i}" for i in self.config.includes]
    #     )

    #     scanner = Scanner(spec.functions)
    #     scanner.exec(ast)
        
    #     out_code = ""
    #     c_gen = self.CustomCGenerator()
        
    #     for i in scanner.collect_includes():
    #         print(i)
    #         include_str = str(i).replace("\\\\", "/")
            
    #         out_code += f"#include \"{include_str}\"\n"
            
    #     for name, node in reversed(scanner.filter_tag_nodes_by_source(spec.in_file).items()):
    #         print(f"TAG_NODE: {name}")
    #         out_code += c_gen.visit(node) + ";\n"
        
    #     for name, node in reversed(scanner.filter_nodes_by_source(spec.in_file).items()):
    #         print(f"NODE: {name}")
            
    #         if isinstance(node, FuncDef) and node.decl.name not in spec.functions:
    #             out_code += c_gen.visit(node.decl) + ";\n"
    #         else:
    #             out_code += c_gen.visit(node) + ";\n"
            
    #     spec.out_file.write_text(out_code)
        
