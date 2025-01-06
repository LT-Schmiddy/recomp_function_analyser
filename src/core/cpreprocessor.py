import sys, shutil
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from copy import deepcopy
from pathlib import Path

from macro import MacroSection, MacroExpression, MacroExpressionNode, Macro, ObjectMacro, FunctionMacro, VariadicMacro, MacroSource, ExternalSource, CodeSource
from constexpr_evaluator import ConstexprEvaluator

class Preprocessor:
    forbidden_macro_names = {
        "defined"
    }

    tabsize = 4
    include : list[str]

    def _add_predefined_macros(self):
        # TODO Implement
        self.new_ObjectMacro("__STDC_VERSION__", ExternalSource("predefined"), "199901L")

    def __init__(self, include_dirs : list[str]):
        super().__init__()
        self.include_paths = include_paths

        self.include = []
        self.conditionalSegment = None
        self.cond_st : deque[int] = deque()
        self.inactive_level = 0
        self.macros : dict[str, Macro] = {}
        self.files : dict[str, str] = {}

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
                self.include += [dir]

    def add_Macro(self, name : str, macro : Macro) -> Macro:
        if name in self.forbidden_macro_names:
            raise Exception("Forbidden macro name!")
        self.macros[name] = macro
        return macro

    def new_ObjectMacro(self, name : str, source : MacroSource, definition : str) -> ObjectMacro:
        return self.add_Macro(name, ObjectMacro(self.macros, source, definition))

    def new_FunctionMacro(self, name : str, source : MacroSource, definition : str, args : list[str]) -> FunctionMacro:
        return self.add_Macro(name, FunctionMacro(self.macros, source, definition, args))

    def new_VariadicMacro(self, name : str, source : MacroSource, definition : str, args : list[str]) -> FunctionMacro:
        return self.add_Macro(name, VariadicMacro(self.macros, source, definition, args))

    def print_macros(self):
        for n, m in self.macros.items():
            print("%s : %s" % (n, ObjectMacro.contents_to_string(m.contents)))
        print("\n")

    class ConditionalSegmentStatus(IntEnum):
        DISABLED = 0
        ACTIVE = 1
        SKIP = 2

    class CodeSection(IntEnum):
        DIRECTIVE = 0
        CODE = 1
        COMMENT = 2
        WHITESPACE = 3

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
        # return None

        end = len(contents)
        if end > 0:
            if contents in self.files:
                text = self.files[contents]
            else:
                print(contents)
                t = contents[0]
                if t == '<':
                    t = '>'
                elif t != '"':
                    raise Exception("Invalid include directive!")

                i = 1
                while i < end:
                    c = contents[i]
                    if c == t:
                        break
                    i += 1

                name = contents[1:i]
                split = name.rsplit('/', 1)
                if len(split) > 1:
                    name_dir = split[0]
                    name_file = split[1]
                else:
                    name_dir = ""
                    name_file = split[0]

                # find the file using the algorithm specified in the standard
                # https://en.cppreference.com/w/c/preprocessor/include
                file : str = None
                for dir in include_dirs:
                    path = os.path.join(dir, name_dir)
                    for root, dir, files in os.walk(path):
                        if name_file in files:
                            file = os.path.join(root, name_file)
                            break

                if file == None:
                    # TODO
                    return FileNotFoundError("Included file doesn't exit!")

                text = Path(file).read_text()
                self.files[contents] = text


            cond_st = self.cond_st
            inactive_level = self.inactive_level

            self.cond_st : deque[int] = deque()
            self.inactive_level = 0

            self.read_include(text)

            self.cond_st = cond_st
            self.inactive_level = inactive_level

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
                        # print("%s\nwith contents %s\nat %d, %d\n" % (dir, contents, line, pos))
                        self.directives[dir](self, contents, ((line, pos), code))
            else:
                # print("%s\nwith contents %s\nat %d, %d\n" % (dir, contents, line, pos))
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
                    return (True, self.CodeSection.COMMENT)
                elif _c == '/':
                    buf_code += [_c]
                    return (True, self.CodeSection.LINE_COMMENT)
                buf += [c]
                return (False, i)
        return (False, i)

    def _read_DIRECTIVE(self, code: str, i : int, end : int, c : str, buf : list[str], buf_code : list[str], line : int, pos : int) -> tuple[bool, CodeSection, int]:
        section = self.CodeSection.DIRECTIVE
        cont = False
        (is_comment, res) = self._check_for_comment_start(code, c, i, end, buf, buf_code)
        if is_comment:
            tmp_section = res
            tmp_buf_code = []
            while i < end:
                c = code[i]
                if res == self.CodeSection.COMMENT:
                    (tmp_section, i, line, pos) = self._read_COMMENT(code, i, end, c, tmp_buf_code, line, pos)
                else:
                    (tmp_section, line, pos) = self._read_LINE_COMMENT(c, tmp_buf_code, line, pos)

                if tmp_section != res:
                    break
                i += 1
        else:
            i = res
            if i < end:
                c = code[i]
                buf_code += [c]

                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if is_newline:
                    self.handle_directive(''.join(buf), ''.join(buf_code), line, pos)
                    section = self.CodeSection.WHITESPACE
                    buf.clear()
                    buf_code.clear()
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
        return (cont, section, i, line, pos)

    def _read_COMMENT(self, code: str, i : int, end : int, c : str, buf_code : list[str], line : int, pos : int) -> tuple[CodeSection, int, int, int]:
        section = self.CodeSection.COMMENT
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if c == '*':
            i += 1
            if i < end:
                c = code[i]
                buf_code += [c]
                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if c == '/':
                    # TODO Handle Comments
                    section = self.CodeSection.WHITESPACE
                    buf_code.clear()
        return (section, i, line, pos)

    def _read_LINE_COMMENT(self, c : str, buf_code : list[str], line : int, pos : int) -> tuple[CodeSection, int, int]:
        section = self.CodeSection.LINE_COMMENT
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if is_newline:
            # TODO Handle Comments
            section = self.CodeSection.WHITESPACE
            buf_code.clear()
        return (section, line, pos)

    def _read_WHITESPACE(self, code: str, i : int, end : int, c : str, buf : list[str], buf_code : list[str], line : int, pos : int, transition_to_code_allowed : bool) -> tuple[CodeSection, int, int, int]:
        section = self.CodeSection.WHITESPACE

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
            section = self.CodeSection.CODE
        else:
            i = res
            if i < end:
                c = code[i]

                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if not is_newline:
                    if c == '#':
                        section = self.CodeSection.DIRECTIVE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
                    elif transition_to_code_allowed:
                        section = self.CodeSection.CODE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
        return (section, i, line, pos)

    def read_include(self, code : str) -> list[tuple[CodeSection, str, int, int]]:
        code = code.replace("\r\n", "\n")

        line = 1
        pos = 1

        buf : list[str] = []
        buf_code : list[str] = []

        section = self.CodeSection.WHITESPACE
        end = len(code)
        i = 0
        while i < end:
            c = code[i]
            match section:
                case self.CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos) = self._read_DIRECTIVE(code, i, end, c, buf, buf_code, line, pos)
                    if cont:
                        continue
                case self.CodeSection.COMMENT:
                    (section, i, line, pos) = self._read_COMMENT(code, i, end, c, buf_code, line, pos)
                case self.CodeSection.LINE_COMMENT:
                    (section, line, pos) = self._read_LINE_COMMENT(c, buf_code, line, pos)
                case self.CodeSection.WHITESPACE:
                    (section, i, line, pos) = self._read_WHITESPACE(code, i, end, c, buf, buf_code, line, pos, False)
            i += 1

    def read(self, code : str) -> list[tuple[CodeSection, str, int, int]]:
        code = code.replace("\r\n", "\n")

        line = 1
        pos = 1

        buf : list[str] = []
        buf_code : list[str] = []

        section = self.CodeSection.WHITESPACE
        end = len(code)
        i = 0
        while i < end:
            c = code[i]
            match section:
                case self.CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos) = self._read_DIRECTIVE(code, i, end, c, buf, buf_code, line, pos)
                    if cont:
                        continue
                # case self.CodeSection.CODE:
                case self.CodeSection.COMMENT:
                    (section, i, line, pos) = self._read_COMMENT(code, i, end, c, buf_code)
                case self.CodeSection.LINE_COMMENT:
                    (section, line, pos) = self._read_LINE_COMMENT(c, buf_code)
                case self.CodeSection.WHITESPACE:
                    (section, i, line, pos) = self._read_WHITESPACE(code, i, end, c, buf, buf_code, line, pos, True)

            i += 1

    def preprocess(self, code : str):
        # Trigraph replacement
        # Line splicing
        # Tokenization
        # Macro expansion and directive handling
        self.read_include(code)
        # self.files.clear()

    def exec(self, file):
        self.preprocess(Path(file).read_text())

if __name__ == "__main__":
    include_dirs = [
        'mm',
        'mm/include',# p = Preprocessor(include_dirs)

        'mm/assets',
    ]

    # file = 'mm/src/code/z_message.c'
    file = 'test/test.c'

    p = Preprocessor(include_dirs)
    # p.exec(file)

    # # Macro test

    # #define STR(X) #X
    # p.add_FunctionMacro("STR", None, "#X", ["X"])
    # #define STRX(X) STR(X)
    # p.add_FunctionMacro("STRX", None, "STR(X)", ["X"])
    # #define TEST4(_1, _2, _3) STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)
    # test4 = p.add_FunctionMacro("TEST4", None, "STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)", ["_1", "_2", "_3"])

    # #define BOOM (5)
    # p.add_ObjectMacro("BOOM", None, "(521)")
    # #define Bo 5
    # p.add_ObjectMacro("BO", None, "5")
    # #define OM 6
    # p.add_ObjectMacro("OM", None, "6")

    # # TEST4(  BO  , OM    BO     ,   OM  )
    # m_1 = ObjectMacro.parse("  BO  ")
    # m_2 = ObjectMacro.parse(" OM    BO     ")
    # m_3 = ObjectMacro.parse("   OM  ")

    # # "(521) 5" "BOOM BO" "6 5" "BOOM BO 5"
    # print(ObjectMacro.contents_to_string(test4.solve([m_1, m_2, m_3])))


    #ConstexprEvaluator test

    # e = ConstexprEvaluator()
    # val = e.eval(ObjectMacro.parse("(2 + 2 * 2) * 10 == 6 ? 10 : 7"))
    # print(val)

    # val = e.eval(ObjectMacro.parse("(1||0)"))
    # print(val)

    # Preprocessor test
    p.exec(file)

    print("WORKS" if ("MESSAGE_ITEM_NONE" in p.macros) else "DOESN'T WORK")

    print("FINISHED")
