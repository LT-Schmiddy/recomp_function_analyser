import pycparser
from pycparser.c_generator import CGenerator

from project import ProjectConfig
import settings

from core.scanner import Scanner
from core.cpreprocessor import Preprocessor

class PatchGenerator:
    config: ProjectConfig
    
    class CustomCGenerator(CGenerator):
        def _make_indent(self):
            return ' ' * self.indent_level
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        
    def ast_only(self):
        for spec in self.config.process_specs:
            ast = pycparser.parse_file(
                spec.in_file,
                use_cpp=spec.preprocess,
                cpp_path=self.config.preproc_command_path,
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
            
    def includes_and_ast(self):
        for spec in self.config.process_specs:
            ast = pycparser.parse_file(
                spec.in_file,
                use_cpp=spec.preprocess,
                cpp_path=self.config.preproc_command_path,
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
                out_code += c_gen.visit(node) + ";\n"
                
            spec.out_file.write_text(out_code)
        
    def scanner_and_cpreprocessor(self):
        for spec in self.config.process_specs:
            p = Preprocessor([str(i) for i in self.config.includes], False)
            p.read(spec.in_file.read_text())
            
            print(p.files.keys())