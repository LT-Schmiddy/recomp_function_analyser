import sys, shutil
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from constexpr_evaluator import ConstexprEvaluator
from doubly_linked_list import DoublyLinkedList
from copy import deepcopy

class MacroSection(IntEnum):
    WHITESPACE = 0
    NAME = 1
    OPERATOR = 2
    TEXT = 3
    NUMBER = 4
    MISC = 5

class Preprocessor:
    class Macro:
        def get_string(self) -> str:
            pass

        def solve(self) -> DoublyLinkedList[tuple[MacroSection, str]]:
            pass

    class ObjectMacro(Macro):
        operators = {
            '++',
            '--',
            '(',
            ')',
            '[',
            ']',
            '{',
            '}',
            '.',
            '->',
            '+',
            '-',
            '!',
            '~',
            '*',
            '&',
            '/',
            '%',
            '<<',
            '>>',
            '<',
            '<=',
            '>',
            '>=',
            '==',
            '!=',
            '^',
            '|',
            '&&',
            '||',
            '?:',
            '=',
            '+=',
            '-=',
            '*=',
            '/=',
            '%=',
            '<<=',
            '>>=',
            '&=',
            '^=',
            '|=',
            ',',
            '#',
            '##',
        }

        concatenation_res = {
            (MacroSection.NAME, MacroSection.NAME) : MacroSection.NAME,
            (MacroSection.NAME, MacroSection.NUMBER) : MacroSection.NAME,
            (MacroSection.NUMBER, MacroSection.NAME) : MacroSection.NUMBER,
            (MacroSection.NUMBER, MacroSection.NUMBER) : MacroSection.NUMBER,
            (MacroSection.OPERATOR, MacroSection.OPERATOR) : MacroSection.OPERATOR,
        }

        def __init__(self, source, definition : str):
            super().__init__()
            self.source = source
            self.contents = self.parse(definition)

        def parse(self, definition : str) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res : DoublyLinkedList[tuple[MacroSection, str]] = DoublyLinkedList()

            processed_section = MacroSection.WHITESPACE
            buffer = ''

            end = len(definition)
            i = 0
            while i < end:
                c = definition[i]
                section = processed_section
                if c.isalpha() or c == '_':
                    if section != MacroSection.NUMBER:
                        section = MacroSection.NAME
                elif c.isspace():
                    section = MacroSection.WHITESPACE
                elif c.isnumeric():
                    if section != MacroSection.NAME:
                        section = MacroSection.NUMBER
                elif c in self.operators:
                    section = MacroSection.OPERATOR
                    if processed_section == MacroSection.OPERATOR:
                        tmp = buffer + c
                        if tmp not in self.operators:
                            res.add_end((processed_section, buffer))
                            buffer = c
                elif c in {'"', "'"}:
                    section = MacroSection.TEXT

                    res += [(processed_section, buffer)]
                    buffer = c
                    processed_section = section

                    initial = c
                    i += 1
                    while i < end:
                        c = definition[i]
                        if (c == initial):
                            break
                        buffer += c
                        i += 1
                else:
                    section = MacroSection.MISC

                if section != processed_section:
                    res.add_end((processed_section, buffer))
                    buffer = c
                    processed_section = section
                elif section != MacroSection.WHITESPACE:
                    buffer += c
                i += 1
            if section != MacroSection.WHITESPACE:
                res.add_end((processed_section, buffer))
            res.pop_begin()
            return res

        def _solve_remove_space(self, contents : DoublyLinkedList[tuple[MacroSection, str]], current : DoublyLinkedList.Node[tuple[MacroSection, str]], section : MacroSection, content : str) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            if section == MacroSection.WHITESPACE:
                contents.remove(current)
                current = current.next
                (section, content) = current.val
                return (current, section, content)
            return (current, section, content)

        def _solve_perform_concatenation(self, contents : DoublyLinkedList[tuple[MacroSection, str]]):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == '##':
                    operator = current
                    current = current.next
                    if current != None:
                        left = current.prev.prev
                        (l_section, l_content) = left.val
                        (left, l_section, l_content) = self._solve_remove_space(contents, left, l_section, l_content)

                        right = current
                        (r_section, r_content) = right.val
                        (right, r_section, r_content) = self._solve_remove_space(contents, right, r_section, r_content)

                        res_content = l_content + r_content
                        res_section = self.concatenation_res[(l_section, r_section)]
                        if res_section != None and (res_section != MacroSection.OPERATOR or res_content in self.operators):
                            right.val = (res_section, res_content)
                            contents.remove(left)
                            contents.remove(operator)

                            current = right
                        else:
                            raise Exception(("Pasting formed \"%s\", an invalid preprocessing token!") % (res_content))
                    else:
                        break
                current = current.next

        def _solve_handle_functionMacro(self, used : set[str], macro, contents : DoublyLinkedList[tuple[MacroSection, str]], start : DoublyLinkedList.Node[tuple[MacroSection, str]]) -> tuple[DoublyLinkedList[tuple[MacroSection, str]], DoublyLinkedList.Node[tuple[MacroSection, str]]]:
            current = start.next
            if current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == '(':
                    contents.remove(current)
                    current = current.next

                    parenth_level = 0
                    args : list[DoublyLinkedList[tuple[MacroSection, str]]] = []
                    f = current
                    t = None
                    while current != None:
                        (section, content) = current.val
                        if section == MacroSection.OPERATOR:
                            if content == '(':
                                t = current
                                parenth_level += 1
                            elif content == ')':
                                if parenth_level > 0:
                                    t = current
                                    parenth_level -= 1
                                else:
                                    args += contents.extract_list(f, t)

                                    contents.remove(current)
                                    break
                            elif content == ',':
                                if parenth_level > 0:
                                    t = current
                                else:
                                    arg = contents.extract_list(f, t)

                                    begin = arg.begin
                                    if begin != None and begin.val[0] == MacroSection.WHITESPACE:
                                        arg.remove(begin)

                                    end = arg.end
                                    if end != None and end.val[0] == MacroSection.WHITESPACE:
                                        arg.remove(end)

                                    args += arg

                                    contents.remove(current)
                                    current = current.next

                                    f = current
                                    t = None
                                    continue
                            else:
                                t = current
                        else:
                            t = current
                        current = current.next

                    if parenth_level > 0:
                        raise Exception("unterminated function-like macro invocation")

                    return (macro._replace(args, used), current)
                return (None, current)
            return (None, current)

        def _solve_replace_macros(self, contents : DoublyLinkedList[tuple[MacroSection, str]], used : set[str]) -> DoublyLinkedList[tuple[MacroSection, str]]:
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.NAME:
                    macro = Preprocessor.macros[content]
                    if macro != None and content not in used:
                        used.add(content)
                        if isinstance(macro, Preprocessor.FunctionMacro):
                            (list, current) = self._copy_and_solve(used, macro, contents, current)
                            contents.add_list_before(list, current)
                        elif isinstance(macro, Preprocessor.ObjectMacro):
                            contents.add_list_before(macro._copy_and_solve(used), current)
                        else:
                            contents.add_list_before(macro.solve(), current)
                        contents.remove(current)
                        used.remove(content)
                current = current.next

        def _solve(self, contents : DoublyLinkedList[tuple[MacroSection, str]], used : set[str]) -> DoublyLinkedList[tuple[MacroSection, str]]:
            self._solve_perform_concatenation(contents)
            self._solve_replace_macros(contents, used)

        def _copy_and_solve(self, used : set[str]) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res = deepcopy(self.contents)
            self._solve(res, used)
            return res

        def solve(self) -> DoublyLinkedList[tuple[MacroSection, str]]:
            return self._copy_and_solve(set())

        @staticmethod
        def contents_to_string(contents : DoublyLinkedList[tuple[MacroSection, str]]) -> str:
            current = contents.begin
            res = ''
            while current != None:
                content = current.val[1]
                res += content
                current = current.next
            return res

    class FunctionMacro(ObjectMacro):
        def __init__(self, source, definition : str, args : list[str]):
            super().__init__(source, definition)
            self.args = {arg: i for (i, arg) in enumerate(args)}

        def _solve_get_arg(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], name : str) -> DoublyLinkedList[tuple[MacroSection, str]]:
            pos = self.args[name]
            if pos != None:
                return args[pos]
            return None

        def _solve_remove_space(self, contents : DoublyLinkedList[tuple[MacroSection, str]], current : DoublyLinkedList.Node[tuple[MacroSection, str]], section : MacroSection, content : str) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            if section == MacroSection.WHITESPACE:
                contents.remove(current)
                current = current.next
                (section, content) = current.val
                return (current, section, content)
            return (current, section, content)

        def _solve_perform_stringification(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], contents : DoublyLinkedList[tuple[MacroSection, str]]):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == '#':
                    current = current.next
                    if current != None:
                        (section, content) = current.val
                        (current, section, content) = self._solve_remove_space(contents, current, section, content)

                        if section == MacroSection.NAME:
                            arg = self._solve_get_arg(args, content)
                            if arg != None:
                                contents.remove(current.prev)
                                current.val = (MacroSection.TEXT, '"' + self.contents_to_string(arg) + '"')
                            else:
                                raise Exception("'#' is not followed by a macro parameter!")
                    else:
                        break
                current = current.next

        def _solve_perform_concatenation(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], contents : DoublyLinkedList[tuple[MacroSection, str]]):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == '##':
                    operator = current
                    current = current.next
                    if current != None:
                        left = current.prev.prev
                        (l_section, l_content) = left.val
                        (left, l_section, l_content) = self._solve_remove_space(contents, left, l_section, l_content)

                        if l_section == MacroSection.NAME:
                            arg = self._solve_get_arg(args, l_content)
                            if arg != None:
                                if arg.is_empty():
                                    left = None
                                else:
                                    contents.add_list_before(arg, left)
                                    contents.remove(left)
                                    left = left.prev

                        right = current
                        (r_section, r_content) = right.val
                        (right, r_section, r_content) = self._solve_remove_space(contents, right, r_section, r_content)

                        end = right

                        if r_section == MacroSection.NAME:
                            arg = self._solve_get_arg(args, r_content)
                            if arg != None:
                                if arg.is_empty():
                                    right = None
                                else:
                                    end = arg.end

                                    contents.add_list_after(arg, right)
                                    contents.remove(right)
                                    right = right.next

                        if left == None:
                            contents.remove(left)
                            contents.remove(operator)
                            if right == None:
                                contents.remove(right)
                            current = right
                        elif right == None:
                            contents.remove(operator)
                            contents.remove(right)
                            current = left
                        else:
                            res_content = l_content + r_content
                            res_section = self.concatenation_res[(l_section, r_section)]
                            if res_section != None and (res_section != MacroSection.OPERATOR or res_content in self.operators):
                                right.val = (res_section, res_content)
                                contents.remove(left)
                                contents.remove(operator)

                                current = end
                            else:
                                raise Exception(("Pasting formed \"%s\", an invalid preprocessing token!") % (res_content))
                    else:
                        break
                current = current.next


        def _solve_replace_args(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], contents : DoublyLinkedList[tuple[MacroSection, str]], used : set[str]):
            for arg in args:
                super()._solve(arg, used)

            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.NAME:
                    arg = self._solve_get_arg(args, content)
                    if arg != None:
                        contents.add_list_before(deepcopy(arg), current)
                        contents.remove(current)
                current = current.next

        def _solve(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], contents: DoublyLinkedList[tuple[MacroSection, str]], used : set[str]):
            self._solve_perform_stringification(args, contents)
            self._solve_perform_concatenation(args, contents)
            self._solve_replace_args(args, contents, used)
            super()._solve_replace_macros(contents, used)

        def _copy_and_solve(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]], used : set[str]) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res = deepcopy(self.contents)
            self._solve(args, res, used)
            return res

        def solve(self, args : list[DoublyLinkedList[tuple[MacroSection, str]]]) -> DoublyLinkedList[tuple[MacroSection, str]]:
            return self._copy_and_solve(args, set())

    macros : dict[str, Macro] = {}
    include_paths : list[str]

    def __init__(self, include_paths):
        super().__init__()
        self.include_paths = include_paths

    def add_ObjectMacro(self, name : str, source, definition : str):
        macro = self.ObjectMacro(source, definition)
        self.macros[name] = macro
        return macro

    def add_FunctionMacro(self, name : str, source, definition : str, args : list[str]):
        macro = self.FunctionMacro(source, definition, args)
        self.macros[name] = macro
        return macro

    class CodeSection(IntEnum):
        DIRECTIVE = 0
        CODE = 1
        COMMENT = 2
        WHITESPACE = 3

    def split_code(self, code : str) -> list[tuple[CodeSection, str, int, int]]:
        sections : list[tuple[int, int, self.CodeSection, str]] = []

        line : int = 0
        char : int = 0
        pos : int = 0
        # while(len(code) > 0):

    def preprocess(self, code : str):
        code = code.replace("\r\n", "\n")
        # Trigraph replacement
        # Line splicing
        # Tokenization
        # Macro expansion and directive handling
        print(code)

    def exec(self, file):
        f = open(file)
        self.preprocess(f.read())
        f.close()



if __name__ == "__main__":
    include_dirs = [
        'mm',
        'mm/include',# p = Preprocessor(include_dirs)

        'mm/assets',
    ]

    l = [0, 1, 0, 0, 0]

    lp = l
    for index, val in reversed(list(enumerate(lp))):
        if val == 0:
            l[index] = 2

    print(l)

    # file = 'mm/src/code/z_message.c'
    file = 'test/test.c'

    # e = ConstexprEvaluator()
    # val = e.eval("(2 + 2 * 2) * 10 == 6 ? 10 : 7")
    # print(val)


    p = Preprocessor(include_dirs)
    # p.exec(file)

    #define STR(X) #X
    p.add_FunctionMacro("STR", None, "#X", ["X"])
    #define STRX(X) STR(X)
    p.add_FunctionMacro("STRX", None, "STR(X)", ["X"])
    #define TEST4(_1, _2, _3) STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)
    macro = p.add_FunctionMacro("STRX", None, "STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)", ["_1", "_2", "_3"])

    #define NAWIAS (5)
    p.add_ObjectMacro("NAWIAS", None, "(5)")
    #define NA 5
    p.add_ObjectMacro("NA", None, "5")
    #define WIAS 6
    p.add_ObjectMacro("WIAS", None, "6")

    # TEST4( NA, WIAS NA, WIAS)
    m_1 = p.add_ObjectMacro("_1", None, " NA")
    m_2 = p.add_ObjectMacro("_2", None, " WIAS NA")
    m_3 = p.add_ObjectMacro("_3", None, " WIAS")

    print(Preprocessor.ObjectMacro.contents_to_string(macro.solve([m_1.contents, m_2.contents, m_3.contents])))