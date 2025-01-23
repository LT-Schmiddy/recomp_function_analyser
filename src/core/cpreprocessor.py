import sys, shutil, os
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from copy import deepcopy
from pathlib import Path

from .macro import MacroSection, MacroExpression, MacroExpressionNode, Macro, ObjectMacro, FunctionMacro, VariadicMacro, MacroSource, ExternalSource, CodeSource, FUNCTION_MACRO_PREFIX
from .constexpr_evaluator import ConstexprEvaluator

class FunctionDefState(IntEnum):
    OUTSIDE = 0
    WATCHING = 1
    INSIDE = 2

class CodeSection(IntEnum):
    DIRECTIVE = 0
    CODE = 1
    COMMENT = 2
    LINE_COMMENT = 3
    WHITESPACE = 4
    
class StoredSection:
    line: int
    pos: int
    section: CodeSection
    content: str
    code_content: str
    
    def __init__(self, line: int, pos: int, section: CodeSection, content: str, code_content: str):
        self.line = line
        self.pos = pos
        self.section = section
        self.content = content
        self.code_content = code_content
    
    def __str__(self):
        return f"{self.section.name} @ {self.line},{self.pos}"

class Preprocessor:
    forbidden_macro_names = {
        "defined"
    }

    tabsize = 4
    
    cond_st : deque[int]
    include_dirs : list[str]
    recurse_includes: bool
    detected_includes: set[str]
    sections: dict[str, str]
    macros : dict[str, Macro]

    def _add_predefined_macros(self):
        # TODO Implement
        self.new_ObjectMacro("__STDC_VERSION__", ExternalSource("predefined"), "199901L")

    def __init__(self, include_dirs : list[str], standard_c_lib_dir : str, recurse_includes = True):
        super().__init__()

        self.recurse_includes = recurse_includes

        self.include_dirs = []
        self.conditionalSegment = None
        self.cond_st = deque()
        self.inactive_level = 0
        self.macros = {}
        self.detected_includes = set()
        self.sections = {}

        self._add_predefined_macros()

        included = { "" }
        for dir in include_dirs:
            while len(dir) > 0:
                prefix = dir[:2]
                if prefix in { ".", "./" }:
                    dir = dir[2:]
                else:
                    break
            if dir not in included:
                included.add(dir)
                self.include_dirs += [dir]

        if standard_c_lib_dir not in included:
            included.add(dir)
            self.include_dirs += [dir]

    def new_Macro(self, name : str, macro : Macro) -> Macro:
        if name in self.forbidden_macro_names:
            raise Exception("Forbidden macro name!")
        self.macros[name] = macro
        return macro

    def new_ObjectMacro(self, name : str, source : MacroSource, definition : str) -> ObjectMacro:
        return self.new_Macro(name, ObjectMacro(self.macros, source, definition))

    def new_FunctionMacro(self, name : str, source : MacroSource, definition : str, args : list[str]) -> FunctionMacro:
        return self.new_Macro(FUNCTION_MACRO_PREFIX + name, FunctionMacro(self.macros, source, definition, args))

    def new_VariadicMacro(self, name : str, source : MacroSource, definition : str, args : list[str]) -> FunctionMacro:
        return self.new_Macro(FUNCTION_MACRO_PREFIX + name, VariadicMacro(self.macros, source, definition, args))

    def print_macros(self):
        for n, m in self.macros.items():
            print("%s : %s" % (n, ObjectMacro.contents_to_string(m.contents)))
        print("\n")

    class ConditionalSegmentStatus(IntEnum):
        DISABLED = 0
        ACTIVE = 1
        SKIP = 2
        

    def _handle_get_identifier(self, contents : str, start : int, end : int) -> tuple[str, int]:
        i = start
        while i < end:
            c = contents[i]
            if c != ' ':
                break
            i += 1
        pass

        if i >= end:
            raise Exception("Invalid define!")

        c = contents[i]

        if not c.isalpha() and c != '_':
            raise Exception("Invalid macro name!")

        left = i

        i += 1

        while i < end:
            c = contents[i]
            if c == ' ' or c == '(':
                break
            elif not c.isalnum() and c != '_':
                raise Exception("Invalid macro name!")
            i += 1

        name = contents[left:i]
        return (name, i)


    def _handle_get_macro_args(self, contents : str, start : int, end : int) -> tuple[bool, list[str], int]:
        i = start

        args = []
        identifierFound = False
        variadic = False
        while i < end:
            while i < end:
                c = contents[i]
                if c != ' ':
                    break
                i += 1
            pass

            if i >= end:
                raise Exception("Invalid define!")

            c = contents[i]

            if c == ')':
                break
            elif variadic:
                raise Exception("Expected ')'!")
            elif c == ',':
                if identifierFound:
                    identifierFound = False
                    i += 1
                    continue
                raise Exception("Expected identifier!")
            elif identifierFound or (not c.isalpha() and c != '_' and c != '.'):
                raise Exception("Invalid argument name!")

            left = i
            i += 1

            while i < end:
                c = contents[i]
                if c == '.':
                    variadic = True
                elif c in { ' ', ',', ')' }:
                    break
                elif not c.isalnum() and c != '_':
                    raise Exception("Invalid argument name!")
                i += 1

            arg = contents[left:i]
            if not variadic:
                args += [arg]
                identifierFound = True
            elif arg != "...":
                raise Exception("Invalid argument name!")

            if not c in { ' ', ',', ')' }:
                i += 1
        return (variadic, args, i)

    def _is_conditional_segment_inactive(self):
        return (self.conditionalSegment != None) and (self.conditionalSegment[0] != self.ConditionalSegmentStatus.ACTIVE)

    def handle_DEFINE(self, contents : str, source):
        end = len(contents)
        i = 0

        (name, i) = self._handle_get_identifier(contents, i, end)

        args : list[str] = None
        variadic = False
        if i < end:
            c = contents[i]
            if c == '(':
                i += 1
                (variadic, args, i) = self._handle_get_macro_args(contents, i, end)

        definition = contents[i:end]

        if variadic:
            self.new_VariadicMacro(name, source, definition, args)
        elif args == None:
            self.new_ObjectMacro(name, source, definition)
        else:
            self.new_FunctionMacro(name, source, definition, args)

        return None

    def handle_UNDEF(self, contents : str, source):
        end = len(contents)
        i = 0

        (name, i) = self._handle_get_identifier(contents, i, end)

        self.macros.pop(name, None)

    def _handle_check_def(self, contents : str) -> bool:
        (name, i) = self._handle_get_identifier(contents, 0, len(contents))
        return name in self.macros

    def _get_segment_status(self, current : ConditionalSegmentStatus, activate : bool) -> ConditionalSegmentStatus:
        if current == self.ConditionalSegmentStatus.SKIP or current == self.ConditionalSegmentStatus.ACTIVE:
            return self.ConditionalSegmentStatus.SKIP
        elif activate:
            return self.ConditionalSegmentStatus.ACTIVE
        else:
            return self.ConditionalSegmentStatus.DISABLED

    def _handle_ifs(self, contents : str, source, func : function):
        if self.conditionalSegment != None:
            self.cond_st.append(self.conditionalSegment)

        status = self._get_segment_status(self.ConditionalSegmentStatus.DISABLED, func(contents) != 0)
        self.conditionalSegment = (status, source)

    def _handle_defined(self, macroexpr : MacroExpression, origin_node : MacroExpressionNode):
        inParentheses = False

        current = origin_node.next
        (section, content) = current.val

        (current, section, content) = ObjectMacro._remove_space(macroexpr, current, section, content)

        if section == MacroSection.OPERATOR and content == '(':
            inParentheses = True
            (current, section, content) = ObjectMacro._remove_node(macroexpr, current)
            (current, section, content) = ObjectMacro._remove_space(macroexpr, current, section, content)

        if section == MacroSection.NAME:
            origin_node.val = (MacroSection.NUMBER, content in self.macros)
            (current, section, content) = ObjectMacro._remove_node(macroexpr, current)
        else:
            raise Exception("Invalid expression!")

        if inParentheses:
            (current, section, content) = ObjectMacro._remove_space(macroexpr, current, section, content)

            if section == MacroSection.OPERATOR and content == ')':
                (current, section, content) = ObjectMacro._remove_node(macroexpr, current)
            else:
                raise Exception("Invalid expression!")

    def _check_for_defined(self, macroexpr : MacroExpression):
        current = macroexpr.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.NAME and content == "defined":
                self._handle_defined(macroexpr, current)
            current = current.next

    def handle_IF(self, contents : str, source):
        c = ConstexprEvaluator()
        parsed = ObjectMacro.parse(contents)
        self._check_for_defined(parsed)
        ObjectMacro(None, self.macros, "")._solve(parsed, set())
        self._handle_ifs(contents, source, lambda contents: c.eval(parsed))

    def handle_IFDEF(self, contents : str, source):
        self._handle_ifs(contents, source, lambda contents: self._handle_check_def(contents))

    def handle_IFNDEF(self, contents : str, source):
        self._handle_ifs(contents, source, lambda contents: not self._handle_check_def(contents))

    def _handle_elifs(self, contents : str, source, func : function):
        if self.conditionalSegment == None:
            raise Exception("#elif without #if")
        prevStatus = self.conditionalSegment[0]
        status = self._get_segment_status(prevStatus, func(contents) != 0)
        self.conditionalSegment = (status, source)

    def handle_ELIF(self, contents : str, source):
        c = ConstexprEvaluator()
        parsed = ObjectMacro.parse(contents)
        self._check_for_defined(parsed)
        ObjectMacro(None, self.macros, "")._solve(parsed, set())
        self._handle_elifs(contents, source, lambda contents: c.eval(parsed))

    def handle_ELSE(self, contents : str, source):
        if self.conditionalSegment == None:
            raise Exception("#else without #if")
        prevStatus = self.conditionalSegment[0]
        if prevStatus == self.ConditionalSegmentStatus.DISABLED:
            status = self.ConditionalSegmentStatus.ACTIVE
        else:
            status = self.ConditionalSegmentStatus.SKIP
        self.conditionalSegment = (status, source)

    def handle_ENDIF(self, contents : str, source):
        try:
            self.conditionalSegment = self.cond_st.pop()
        except IndexError:
            self.conditionalSegment = None

    def handle_INCLUDE(self, contents : str, source):
        self.detected_includes.add(contents)
        
        end = len(contents)
        if end > 0:
            include_type = contents[0]
            if include_type == '<':
                include_type = '>'
            elif include_type != '"':
                raise Exception("Invalid include directive!")

            i = 1
            while i < end:
                c = contents[i]
                if c == include_type:
                    break
                i += 1

            (path_dir, path_file) = os.path.split(contents[1:i])

            # find the file using the algorithm specified in the standard
            # https://en.cppreference.com/w/c/preprocessor/include

            file : str = None
            if include_type == '"':
                # Search in the directory of the current file
                root = os.path.join(self.current_dir, path_dir)
                if os.path.isdir(root):
                    for item in os.listdir(root):
                        if item == path_file:
                            file = os.path.join(root, path_file)
                            break

            # Search in the standard include directories
            for dir in self.include_dirs:
                root = os.path.join(dir, path_dir)
                if os.path.isdir(root):
                    for item in os.listdir(root):
                        if item == path_file:
                            file = os.path.join(root, path_file)
                            break
                    if file != None:
                        break
            
            if self.recurse_includes:
                text = Path(file).read_text()

                current_dir = self.current_dir
                self.current_dir = os.path.split(file)[0]

                self.read_include(text)

                self.current_dir = current_dir

            return None

        raise Exception("Invalid include directive!")

    def handle_PRAGMA(self, contents : str, source):
        pass

    directives = {
        "define" : handle_DEFINE,
        "undef" : handle_UNDEF,
        "if" : handle_IF,
        "ifdef" : handle_IFDEF,
        "ifndef" : handle_IFNDEF,
        "elif" : handle_ELIF,

        # C23
        # "elifdef" : handle_ELIF,
        # "elifndef" : handle_ELIF,

        "else" : handle_ELSE,
        "endif" : handle_ENDIF,
        "include" : handle_INCLUDE,

        # TODO?
        # "error" : handle_ERROR,

        # C23
        # "warning" : handle_WARNING,

        # TODO?
        "pragma" : handle_PRAGMA,
        # "line" : handle_LINE,

        # C23
        # "embed" : handle_EMBED,
    }

    def handle_directive(self, directive : str, code : str, line : int, pos : int) -> bool:
        end = len(directive)
        (dir, i) = self._handle_get_identifier(directive, 1, end)
        contents = directive[(i + 1) : end]

        try:
            if self._is_conditional_segment_inactive():
                if dir in { "if", "ifdef", "ifndef" }:
                    self.inactive_level += 1
                elif dir == "endif":
                    if self.inactive_level > 0:
                        self.inactive_level -= 1
                    else:
                        file = os.path.join(self.current_dir, self.current_file)
                        self.directives[dir](self, contents, ((line, pos), CodeSource(file, line, pos)))
            else:
                self.directives[dir](self, contents, ((line, pos), code))
        except KeyError:
            raise Exception("Invalid directive!")

    def _check_for_newline(self, c : str, line : int, pos : int) -> tuple[bool, int, int]:
        if c == '\n':
            pos = 1
            line += 1
            return (True, line, pos)
        pos += 1
        return (False, line, pos)

    def _check_for_comment_start(self, code: str, c : str, i : int, end : int, buf : list[str], buf_code : list[str]) -> tuple[bool, CodeSection | int]:
        if c == '/':
            buf_code += [c]
            i += 1
            if i < end:
                _c = code[i]
                if _c == '*':
                    buf_code += [_c]
                    return (True, CodeSection.COMMENT)
                elif _c == '/':
                    buf_code += [_c]
                    return (True, CodeSection.LINE_COMMENT)
                buf += [c]
                return (False, i)
        return (False, i)

    def _read_DIRECTIVE(self, code: str, i : int, end : int, c : str, buf : list[str], buf_code : list[str], line : int, pos : int) -> tuple[bool, CodeSection, int]:
        section = CodeSection.DIRECTIVE
        cont = False
        clear_buf = False
        clear_code_buf = False
        
        (is_comment, res) = self._check_for_comment_start(code, c, i, end, buf, buf_code)
        if is_comment:
            tmp_section = res
            tmp_buf_code = []
            while i < end:
                c = code[i]
                tmp_cont = False
                if res == CodeSection.COMMENT:
                    (tmp_cont, tmp_section, i, line, pos, clear_buf, clear_code_buf) = self._read_COMMENT(code, i, end, c, tmp_buf_code, line, pos)
                else:
                    (tmp_section, line, pos, clear_buf, clear_code_buf) = self._read_LINE_COMMENT(c, tmp_buf_code, line, pos)

                if tmp_section != res:
                    break

                if tmp_cont:
                    continue

                i += 1
        else:
            i = res
            if i < end:
                c = code[i]
                buf_code += [c]

                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if is_newline:
                    self.handle_directive(''.join(buf), ''.join(buf_code), line, pos)
                    section = CodeSection.WHITESPACE
                    clear_buf = True
                    clear_code_buf = True
                elif c == '\\':
                    i += 1
                    if i < end:
                        c = code[i]

                        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                        if is_newline:
                            buf_code += [c]
                            buf += [' ']
                        else:
                            buf += ['\\']
                            cont = True
                elif c == ' ' or c == '\t':
                    buf += [' ']
                else:
                    buf += [c]
        return (cont, section, i, line, pos, clear_buf, clear_code_buf)

    def _read_COMMENT(self, code: str, i : int, end : int, c : str, buf_code : list[str], line : int, pos : int) -> tuple[bool, CodeSection, int, int, int]:
        section = CodeSection.COMMENT
        cont = False
        clear_buf = False
        
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if c == '*':
            i += 1
            if i < end:
                cont = True
                c = code[i]
                buf_code += [c]
                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if c == '/':
                    # TODO Handle Comments
                    section = CodeSection.WHITESPACE
                    # buf_code.clear()
                    clear_buf = True
        return (cont, section, i, line, pos, clear_buf, False)

    def _read_LINE_COMMENT(self, c : str, buf_code : list[str], line : int, pos : int) -> tuple[CodeSection, int, int]:
        section = CodeSection.LINE_COMMENT
        clear_buf = False
        
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if is_newline:
            # TODO Handle Comments
            section = CodeSection.WHITESPACE
            # buf_code.clear()
            clear_buf = True
        return (section, line, pos, clear_buf, False)

    def _read_WHITESPACE(self, code: str, i : int, end : int, c : str, buf : list[str], buf_code : list[str], line : int, pos : int, transition_to_code_allowed : bool) -> tuple[CodeSection, int, int, int]:
        section = CodeSection.WHITESPACE

        tmp_buf = []
        tmp_buf_code = []
        (is_comment, res) = self._check_for_comment_start(code, c, i, end, tmp_buf, tmp_buf_code)
        if is_comment:
            buf_code += tmp_buf_code
            section = res
        elif transition_to_code_allowed and len(buf) > 0:
            # Invalid code
            buf += tmp_buf
            buf_code += tmp_buf_code
            section = CodeSection.CODE
        else:
            i = res
            if i < end:
                c = code[i]

                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if not is_newline:
                    if c == '#':
                        section = CodeSection.DIRECTIVE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
                    elif transition_to_code_allowed:
                        section = CodeSection.CODE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
        return (section, i, line, pos, False, False)

    def _read_CODE(self, code: str, i : int, end : int, c : str, buf : list[str], buf_code : list[str], line : int, pos : int, brace_level: int, parentheses_level: int, func_def_state: FunctionDefState) -> tuple[CodeSection, int, int, int]:
        section = CodeSection.CODE
        clear_buf = False
        clear_code_buf = False
        
        if i < end:
            c = code[i]
            buf += [c]
            buf_code += [c]

            function_ended = False
            # Function Watching:
            if c == "{":
                brace_level += 1
                if func_def_state == FunctionDefState.WATCHING:
                    func_def_state = FunctionDefState.INSIDE

            elif c == "}":
                brace_level -= 1
                if func_def_state == FunctionDefState.INSIDE and brace_level == 0:
                    func_def_state = FunctionDefState.OUTSIDE
                    function_ended = True

            elif c == "(":
                parentheses_level += 1

            elif c == ")":
                if brace_level == 0:
                    func_def_state = FunctionDefState.WATCHING
                parentheses_level -= 1

            elif not c.isspace():
                func_def_state = FunctionDefState.OUTSIDE

            is_newline, line, pos = self._check_for_newline(c, line, pos)
            if not is_newline:
                if (function_ended) or (c == ";" and brace_level == 0):
                    section = CodeSection.WHITESPACE
                    out_str = "".join(buf_code)
                    print("****\n" + out_str)
                    clear_buf = True
                    clear_code_buf = True

        return (section, i, line, pos, brace_level, parentheses_level, func_def_state, clear_buf, clear_code_buf)

    
    def _make_line_pos_string(self, line: int, pos: int) -> str:
        return f"{line},{pos}"
        # return f"{line}"
    
    def _store_section(self, line: int, pos: int, section: CodeSection, buf: list[str], buf_code : list[str]):
        entry = StoredSection(line, pos, section, ''.join(buf), ''.join(buf_code))
        self.sections[self._make_line_pos_string(line, pos)] = entry

    def lookup_section(self, line: int, pos: int = 0) -> StoredSection:
        return self.sections[self._make_line_pos_string(line, pos)]
    
    def read_include(self, code : str) -> list[tuple[CodeSection, str, int, int]]:
        code = code.replace("\r\n", "\n")

        line = 1
        pos = 1
        buf : list[str] = []
        buf_code : list[str] = []
        section = CodeSection.WHITESPACE
        end = len(code)
        
        clear_buf = False
        clear_code_buf = False
        i = 0
        while i < end:
            c = code[i]
            cont = False
            
            if clear_buf:
                buf.clear()
            if clear_code_buf:
                buf_code.clear()
            
            clear_buf = False
            clear_code_buf = False
            
            match section:
                case CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos, clear_buf, clear_code_buf) = self._read_DIRECTIVE(code, i, end, c, buf, buf_code, line, pos)
                case CodeSection.COMMENT:
                    (cont, section, i, line, pos, clear_buf, clear_code_buf) = self._read_COMMENT(code, i, end, c, buf_code, line, pos)
                case CodeSection.LINE_COMMENT:
                    (section, line, pos, clear_buf, clear_code_buf) = self._read_LINE_COMMENT(c, buf_code, line, pos)
                case CodeSection.WHITESPACE:
                    (section, i, line, pos, clear_buf, clear_code_buf) = self._read_WHITESPACE(code, i, end, c, buf, buf_code, line, pos, False)

            if cont:
                continue

            i += 1
        if section == CodeSection.DIRECTIVE:
            self.handle_directive(''.join(buf), ''.join(buf_code), line, pos)
            buf.clear()
            buf_code.clear()

    def read(self, code : str) -> list[tuple[CodeSection, str, int, int]]:
        code = code.replace("\r\n", "\n")

        line = 1
        pos = 1
        brace_level = 0
        parentheses_level = 0
        func_def_state = FunctionDefState.OUTSIDE
        buf : list[str] = []
        buf_code : list[str] = []
        section = CodeSection.WHITESPACE
        end = len(code)
        
        last_section = CodeSection.WHITESPACE
        section_start_line = line
        section_start_pos = pos
        clear_buf = False
        clear_code_buf = False
        i = 0
        while i < end:
            # Do we need to store section buffers?
            if section != last_section and last_section != CodeSection.WHITESPACE:
                self._store_section(section_start_line, section_start_pos, last_section, buf, buf_code)
                section_start_line = line
                section_start_pos = pos

            # Reset the buffers?
            if clear_buf:
                buf.clear()
            if clear_code_buf:
                buf_code.clear()
            
            clear_buf = False
            clear_code_buf = False
                
            last_section = section
            c = code[i]
            cont = False
            
            match section:
                case CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos, clear_buf, clear_code_buf) = self._read_DIRECTIVE(code, i, end, c, buf, buf_code, line, pos)
                case CodeSection.COMMENT:
                    (cont, section, i, line, pos, clear_buf, clear_code_buf) = self._read_COMMENT(code, i, end, c, buf_code, line, pos)
                case CodeSection.LINE_COMMENT:
                    (section, line, pos, clear_buf, clear_code_buf) = self._read_LINE_COMMENT(c, buf_code, line, pos)
                case CodeSection.WHITESPACE:
                    (section, i, line, pos, clear_buf, clear_code_buf) = self._read_WHITESPACE(code, i, end, c, buf, buf_code, line, pos, True)
                case CodeSection.CODE:
                    (section, i, line, pos, brace_level, parentheses_level, func_def_state, clear_buf, clear_code_buf) = \
                        self._read_CODE(code, i, end, c, buf, buf_code, line, pos, brace_level, parentheses_level, func_def_state)

            if cont:
                continue
            i += 1
        if section == CodeSection.DIRECTIVE:
            self.handle_directive(''.join(buf), ''.join(buf_code), line, pos)
            buf.clear()
            buf_code.clear()

    def preprocess(self, code : str):
        # Trigraph replacement
        # Line splicing
        # Tokenization
        # Macro expansion and directive handling
        self.read_include(code)
        # self.files.clear()

    def exec(self, path):
        (dir, file) = os.path.split(path)
        self.current_dir = dir
        self.current_file = file
        self.preprocess(Path(path).read_text())
    
    # Temporary names
    def preprocess2(self, code : str):
        # Trigraph replacement
        # Line splicing
        # Tokenization
        # Macro expansion and directive handling
        self.read(code)
        # self.files.clear()
    
    def exec2(self, path):
        (dir, file) = os.path.split(path)
        self.current_dir = dir
        self.current_file = file
        self.preprocess2(Path(path).read_text())
