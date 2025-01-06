import sys, shutil, os
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from .doubly_linked_list import DoublyLinkedList
from copy import deepcopy


class MacroSection(IntEnum):
    WHITESPACE = 0
    NAME = 1
    OPERATOR = 2
    TEXT = 3
    NUMBER = 4
    MISC = 5

class FunctionDefState(IntEnum):
    OUTSIDE = 0
    WATCHING = 1
    INSIDE = 2    

class Preprocessor:
    class ConstexprEvaluator:
        class Associativity(IntEnum):
            LEFT_TO_RIGHT = 0
            RIGHT_TO_LEFT = 1

        def __init__(self):
            super().__init__()
            self.cond_st: deque[int] = deque()

        def handle_single_arg(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
            func: function,
        ):
            if node.next:
                (symbol, val) = node.next.val
                if symbol == MacroSection.NUMBER:
                    node.val = (MacroSection.NUMBER, func(val))
                    constexpr.remove(node.next)
                    return None
            raise Exception("Invalid expression!")

        def handle_double_arg(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
            func: function,
        ):
            if node.prev and node.next:
                (l_symbol, l_val) = node.prev.val
                (r_symbol, r_val) = node.next.val
                if l_symbol == MacroSection.NUMBER and r_symbol == MacroSection.NUMBER:
                    node.val = (MacroSection.NUMBER, func(l_val, r_val))
                    constexpr.remove(node.prev)
                    constexpr.remove(node.next)
                    return None
            raise Exception("Invalid expression!")

        def handle_PLUS(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_single_arg(constexpr, node, lambda x: x)

        def handle_MINUS(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_single_arg(constexpr, node, lambda x: -x)

        def handle_SUM(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x + y)

        def handle_SUB(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x - y)

        def handle_MUL(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x * y)

        def handle_DIV(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x / y)

        def handle_MOD(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x % y)

        def handle_NOT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_single_arg(constexpr, node, lambda x: not x)

        def handle_CONDL(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            try:
                z = self.cond_st.pop()
            except IndexError:
                raise Exception("Invalid expression!")
            self.handle_double_arg(constexpr, node, lambda x, y: y if x else z)

        def handle_CONDR(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_single_arg(constexpr, node, lambda x: self.cond_st.append(x))
            constexpr.remove(node)

        def handle_AND(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x and y)

        def handle_OR(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x or y)

        def handle_EQ(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x == y)

        def handle_NEQ(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x != y)

        def handle_LT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x < y)

        def handle_GT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x > y)

        def handle_LEQ(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x <= y)

        def handle_GEQ(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x >= y)

        def handle_BAND(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x & y)

        def handle_BOR(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x | y)

        def handle_BXOR(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x ^ y)

        def handle_BNOT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_single_arg(constexpr, node, lambda x: ~x)

        def handle_BLSHFT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x << y)

        def handle_BRSHFT(
            self,
            constexpr: DoublyLinkedList[tuple[MacroSection, str]],
            node: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ):
            self.handle_double_arg(constexpr, node, lambda x, y: x >> y)

        operators: dict[str, function] = {
            "u+": handle_PLUS,
            "u-": handle_MINUS,
            "+": handle_SUM,
            "-": handle_SUB,
            "*": handle_MUL,
            "/": handle_DIV,
            "%": handle_MOD,
            "!": handle_NOT,
            "?": handle_CONDL,
            ":": handle_CONDR,
            "&&": handle_AND,
            "||": handle_OR,
            "==": handle_EQ,
            "!=": handle_NEQ,
            "<": handle_LT,
            ">": handle_GT,
            "<=": handle_LEQ,
            ">=": handle_GEQ,
            "&": handle_BAND,
            "|": handle_BOR,
            "^": handle_BXOR,
            "~": handle_BNOT,
            "<<": handle_BLSHFT,
            ">>": handle_BRSHFT,
        }

        precedence: list[tuple[int, set[str]]] = [
            (Associativity.RIGHT_TO_LEFT, {"u+", "u-", "!", "~"}),
            (Associativity.LEFT_TO_RIGHT, {"*", "/", "%"}),
            (Associativity.LEFT_TO_RIGHT, {"+", "-"}),
            (Associativity.LEFT_TO_RIGHT, {"<<", ">>"}),
            (Associativity.LEFT_TO_RIGHT, {"<", "<=", ">", ">="}),
            (Associativity.LEFT_TO_RIGHT, {"==", "!="}),
            (Associativity.LEFT_TO_RIGHT, {"&"}),
            (Associativity.LEFT_TO_RIGHT, {"^"}),
            (Associativity.LEFT_TO_RIGHT, {"|"}),
            (Associativity.LEFT_TO_RIGHT, {"&&"}),
            (Associativity.LEFT_TO_RIGHT, {"||"}),
            (Associativity.RIGHT_TO_LEFT, {"?", ":"}),
        ]

        def _eval_simplify_constexpr(
            self, constexpr: DoublyLinkedList[tuple[MacroSection, str]]
        ):
            current = constexpr.begin
            parenth_level = 0
            f: DoublyLinkedList.Node[tuple[MacroSection, str]] = None
            t: DoublyLinkedList.Node[tuple[MacroSection, str]] = None
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR:
                    if content == "(":
                        if parenth_level == 0:
                            f = current.next
                        parenth_level += 1
                        constexpr.remove(current)
                    elif content == ")":
                        parenth_level -= 1
                        if parenth_level == 0:
                            if f == current:
                                raise Exception("Expected value in expression!")
                            t = current.prev

                            constexpr = constexpr.extract_list(f, t)
                            current.val = (MacroSection.NUMBER, self._eval(constexpr))
                        elif parenth_level < 0:
                            raise Exception("Invalid expression!")
                        else:
                            constexpr.remove(current)
                elif section == MacroSection.NUMBER:
                    current.val = (section, int(content))
                elif section == MacroSection.WHITESPACE:
                    constexpr.remove(current)
                current = current.next

        def _eval_detect_unary_plus_minus(
            self, constexpr: DoublyLinkedList[tuple[MacroSection, str]]
        ):
            prev = MacroSection.OPERATOR
            current = constexpr.begin
            while current != None:
                (symbol, val) = current.val
                if (
                    symbol == MacroSection.OPERATOR
                    and prev == symbol
                    and (val == "+" or val == "-")
                ):
                    current.val = (MacroSection.OPERATOR, "u" + val)
                prev = symbol
                current = current.next

        def _eval_process_operators(
            self, constexpr: DoublyLinkedList[tuple[MacroSection, str]]
        ):
            for associativity, symbol_set in self.precedence:
                if associativity == self.Associativity.LEFT_TO_RIGHT:
                    current = constexpr.begin
                else:
                    current = constexpr.end

                while current != None:
                    (symbol, val) = current.val
                    if symbol == MacroSection.OPERATOR and val in symbol_set:
                        self.operators[val](self, constexpr, current)
                    if associativity == self.Associativity.LEFT_TO_RIGHT:
                        current = current.next
                    else:
                        current = current.prev

            if len(self.cond_st) > 0:
                raise Exception("Invalid expression!")

        def _eval(self, constexpr: DoublyLinkedList[tuple[MacroSection, str]]) -> int:
            self._eval_simplify_constexpr(constexpr)
            self._eval_detect_unary_plus_minus(constexpr)
            self._eval_process_operators(constexpr)

            if constexpr.begin != constexpr.end:
                raise Exception("Invalid expression!")

            return constexpr.begin.val[1]

        def eval(self, constexpr: DoublyLinkedList[tuple[MacroSection, str]]) -> int:
            if constexpr.is_empty():
                raise Exception("Expected value in expression!")
            return self._eval(constexpr)

    class Macro:
        def get_string(self) -> str:
            pass

        def solve(self) -> DoublyLinkedList[tuple[MacroSection, str]]:
            pass

    class ObjectMacro(Macro):
        operators = {
            "++",
            "--",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            ".",
            "->",
            "+",
            "-",
            "!",
            "~",
            "*",
            "&",
            "/",
            "%",
            "<<",
            ">>",
            "<",
            "<=",
            ">",
            ">=",
            "==",
            "!=",
            "^",
            "|",
            "&&",
            "||",
            "?",
            ":",
            "=",
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "<<=",
            ">>=",
            "&=",
            "^=",
            "|=",
            ",",
            "#",
            "##",
        }

        concatenation_res = {
            (MacroSection.NAME, MacroSection.NAME): MacroSection.NAME,
            (MacroSection.NAME, MacroSection.NUMBER): MacroSection.NAME,
            (MacroSection.NUMBER, MacroSection.NAME): MacroSection.NUMBER,
            (MacroSection.NUMBER, MacroSection.NUMBER): MacroSection.NUMBER,
            (MacroSection.OPERATOR, MacroSection.OPERATOR): MacroSection.OPERATOR,
        }

        def __init__(self, source, definition: str):
            super().__init__()
            self.source = source
            self.contents = self.parse(definition)

        @staticmethod
        def parse(definition: str) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res: DoublyLinkedList[tuple[MacroSection, str]] = DoublyLinkedList()

            processed_section = MacroSection.WHITESPACE
            buffer = ""

            end = len(definition)
            i = 0
            while i < end:
                c = definition[i]
                section = processed_section
                if c.isalpha() or c == "_":
                    if section != MacroSection.NUMBER:
                        section = MacroSection.NAME
                elif c.isspace():
                    section = MacroSection.WHITESPACE
                elif c.isnumeric():
                    if section != MacroSection.NAME:
                        section = MacroSection.NUMBER
                elif c in Preprocessor.ObjectMacro.operators:
                    section = MacroSection.OPERATOR
                    if processed_section == MacroSection.OPERATOR:
                        tmp = buffer + c
                        if tmp not in Preprocessor.ObjectMacro.operators:
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
                        if c == initial:
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

        def _solve_remove_space(
            self,
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            current: DoublyLinkedList.Node[tuple[MacroSection, str]],
            section: MacroSection,
            content: str,
        ) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            if section == MacroSection.WHITESPACE:
                contents.remove(current)
                current = current.next
                (section, content) = current.val
                return (current, section, content)
            return (current, section, content)

        def _solve_perform_concatenation(
            self, contents: DoublyLinkedList[tuple[MacroSection, str]]
        ):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == "##":
                    operator = current
                    current = current.next
                    if current != None:
                        left = current.prev.prev
                        (l_section, l_content) = left.val
                        (left, l_section, l_content) = self._solve_remove_space(
                            contents, left, l_section, l_content
                        )

                        right = current
                        (r_section, r_content) = right.val
                        (right, r_section, r_content) = self._solve_remove_space(
                            contents, right, r_section, r_content
                        )

                        res_content = l_content + r_content
                        res_section = self.concatenation_res[(l_section, r_section)]
                        if res_section != None and (
                            res_section != MacroSection.OPERATOR
                            or res_content in self.operators
                        ):
                            right.val = (res_section, res_content)
                            contents.remove(left)
                            contents.remove(operator)

                            current = right
                        else:
                            raise Exception(
                                ('Pasting formed "%s", an invalid preprocessing token!')
                                % (res_content)
                            )
                    else:
                        break
                current = current.next

        def _solve_add_arg(
            self,
            arg: DoublyLinkedList[tuple[MacroSection, str]],
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
        ):
            begin = arg.begin
            if begin != None and begin.val[0] == MacroSection.WHITESPACE:
                arg.remove(begin)

            end = arg.end
            if end != None and end.val[0] == MacroSection.WHITESPACE:
                arg.remove(end)

            args += [arg]

        def _solve_handle_functionMacro(
            self,
            used: set[str],
            macro,
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            start: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ) -> tuple[
            DoublyLinkedList[tuple[MacroSection, str]],
            DoublyLinkedList.Node[tuple[MacroSection, str]],
        ]:
            current = start.next
            if current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == "(":
                    contents.remove(current)
                    current = current.next

                    parenth_level = 1
                    args: list[DoublyLinkedList[tuple[MacroSection, str]]] = []
                    f = current
                    t = None
                    while current != None:
                        (section, content) = current.val
                        if section == MacroSection.OPERATOR:
                            if content == "(":
                                parenth_level += 1
                                t = current
                            elif content == ")":
                                parenth_level -= 1
                                if parenth_level > 0:
                                    t = current
                                else:
                                    arg = contents.extract_list(f, t)
                                    self._solve_add_arg(arg, args)

                                    contents.remove(current)
                                    break
                            elif content == ",":
                                if parenth_level > 0:
                                    t = current
                                else:
                                    arg = contents.extract_list(f, t)
                                    self._solve_add_arg(arg, args)

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
                    return (macro._copy_and_solve(args, used), current)
                return (None, current)
            return (None, current)

        def _solve_replace_macros(
            self, contents: DoublyLinkedList[tuple[MacroSection, str]], used: set[str]
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.NAME:
                    macro = Preprocessor.macros.get(content)
                    if macro != None and content not in used:
                        used.add(content)
                        if isinstance(macro, Preprocessor.FunctionMacro):
                            start = current

                            (list, current) = self._solve_handle_functionMacro(
                                used, macro, contents, current
                            )

                            contents.add_list_before(list, current)
                            contents.remove(start)
                        elif isinstance(macro, Preprocessor.ObjectMacro):
                            contents.add_list_before(
                                macro._copy_and_solve(used), current
                            )
                        else:
                            contents.add_list_before(macro.solve(), current)
                        contents.remove(current)
                        used.remove(content)
                current = current.next

        def _solve(
            self, contents: DoublyLinkedList[tuple[MacroSection, str]], used: set[str]
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            self._solve_perform_concatenation(contents)
            self._solve_replace_macros(contents, used)

        def _copy_and_solve(
            self, used: set[str]
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res = deepcopy(self.contents)
            self._solve(res, used)
            return res

        def solve(self) -> DoublyLinkedList[tuple[MacroSection, str]]:
            return self._copy_and_solve(set())

        @staticmethod
        def contents_to_string(
            contents: DoublyLinkedList[tuple[MacroSection, str]]
        ) -> str:
            current = contents.begin
            res = ""
            while current != None:
                content = current.val[1]
                res += content
                current = current.next
            return res

    class FunctionMacro(ObjectMacro):
        def __init__(self, source, definition: str, args: list[str]):
            super().__init__(source, definition)
            self.args = {arg: i for (i, arg) in enumerate(args)}

        def _solve_get_arg(
            self, args: list[DoublyLinkedList[tuple[MacroSection, str]]], name: str
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            pos = self.args.get(name)
            if pos != None:
                try:
                    arg = args[pos]
                    return arg
                except IndexError:
                    return None
            return None

        def _solve_remove_space(
            self,
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            current: DoublyLinkedList.Node[tuple[MacroSection, str]],
            section: MacroSection,
            content: str,
        ) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            if section == MacroSection.WHITESPACE:
                contents.remove(current)
                current = current.next
                (section, content) = current.val
                return (current, section, content)
            return (current, section, content)

        def _solve_perform_stringification(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
        ):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == "#":
                    current = current.next
                    if current != None:
                        (section, content) = current.val
                        (current, section, content) = self._solve_remove_space(
                            contents, current, section, content
                        )

                        if section == MacroSection.NAME:
                            arg = self._solve_get_arg(args, content)
                            if arg != None:
                                contents.remove(current.prev)
                                current.val = (
                                    MacroSection.TEXT,
                                    '"' + self.contents_to_string(arg) + '"',
                                )
                            else:
                                raise Exception(
                                    "'#' is not followed by a macro parameter!"
                                )
                    else:
                        break
                current = current.next

        def _solve_perform_concatenation_get_left_arg(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            current: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            left = current.prev.prev
            (l_section, l_content) = left.val
            (left, l_section, l_content) = self._solve_remove_space(
                contents, left, l_section, l_content
            )

            if l_section == MacroSection.NAME:
                arg = self._solve_get_arg(args, l_content)
                if arg != None:
                    if arg.is_empty():
                        left = None
                    else:
                        contents.add_list_before(deepcopy(arg), left)
                        contents.remove(left)
                        left = left.prev
                        (l_section, l_content) = left.val
            return (left, l_section, l_content)

        def _solve_perform_concatenation_get_right_arg(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            current: DoublyLinkedList.Node[tuple[MacroSection, str]],
        ) -> tuple[DoublyLinkedList.Node[tuple[MacroSection, str]], MacroSection, str]:
            right = current
            (r_section, r_content) = right.val
            (right, r_section, r_content) = self._solve_remove_space(
                contents, right, r_section, r_content
            )

            end = right

            if r_section == MacroSection.NAME:
                arg = self._solve_get_arg(args, r_content)
                if arg != None:
                    if arg.is_empty():
                        right = None
                    else:
                        arg = deepcopy(arg)
                        end = arg.end

                        contents.add_list_after(arg, right)
                        contents.remove(right)
                        right = right.next
                        (r_section, r_content) = right.val
            return (right, r_section, r_content, end)

        def _solve_perform_concatenation_f(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
        ):
            current = contents.begin
            while current != None:
                (section, content) = current.val
                if section == MacroSection.OPERATOR and content == "##":
                    operator = current
                    current = current.next
                    if current != None:
                        (left, l_section, l_content) = (
                            self._solve_perform_concatenation_get_left_arg(
                                args, contents, current
                            )
                        )
                        (right, r_section, r_content, end) = (
                            self._solve_perform_concatenation_get_right_arg(
                                args, contents, current
                            )
                        )

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
                            if res_section != None and (
                                res_section != MacroSection.OPERATOR
                                or res_content in self.operators
                            ):
                                right.val = (res_section, res_content)
                                contents.remove(left)
                                contents.remove(operator)

                                current = end
                            else:
                                raise Exception(
                                    (
                                        'Pasting formed "%s", an invalid preprocessing token!'
                                    )
                                    % (res_content)
                                )
                    else:
                        break
                current = current.next

        def _solve_replace_args(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            used: set[str],
        ):
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

        def _solve(
            self,
            args: list[DoublyLinkedList[tuple[MacroSection, str]]],
            contents: DoublyLinkedList[tuple[MacroSection, str]],
            used: set[str],
        ):
            self._solve_perform_stringification(args, contents)
            self._solve_perform_concatenation_f(args, contents)
            self._solve_replace_args(args, contents, used)
            super()._solve_replace_macros(contents, used)

        def _copy_and_solve(
            self, args: list[DoublyLinkedList[tuple[MacroSection, str]]], used: set[str]
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            res = deepcopy(self.contents)
            self._solve(args, res, used)
            return res

        def solve(
            self, args: list[DoublyLinkedList[tuple[MacroSection, str]]]
        ) -> DoublyLinkedList[tuple[MacroSection, str]]:
            return self._copy_and_solve(args, set())

    tabsize = 4
    macros: dict[str, Macro] = {}
    include: list[str]

    def __init__(self, include_dirs: list[str]):
        super().__init__()

        self.include = []

        included = {""}
        for dir in include_dirs:
            while len(dir) > 0:
                prefix = dir[:2]
                print(prefix)
                if prefix in {".", "./"}:
                    dir = dir[2:]
                else:
                    break
            if dir not in included:
                included.add(dir)
                self.include += [dir]

        print(self.include)

    def add_ObjectMacro(self, name: str, source, definition: str) -> ObjectMacro:
        macro = self.ObjectMacro(source, definition)
        Preprocessor.macros[name] = macro
        return macro

    def add_FunctionMacro(
        self, name: str, source, definition: str, args: list[str]
    ) -> FunctionMacro:
        macro = self.FunctionMacro(source, definition, args)
        Preprocessor.macros[name] = macro
        return macro

    class CodeSection(IntEnum):
        DIRECTIVE = 0
        CODE = 1
        COMMENT = 2
        LINE_COMMENT = 3
        WHITESPACE = 4

    def handle_DEFINE(self, contents: str):
        pass

    def handle_UNDEF(self, contents: str):
        pass

    def handle_IFDEF(self, contents: str):
        pass

    def handle_IFNDEF(self, contents: str):
        pass

    def handle_ELIF(self, contents: str):
        pass

    def handle_ELSE(self, contents: str):
        pass

    def handle_ENDIF(self, contents: str):
        pass

    def handle_INCLUDE(self, contents: str):
        pass

    def handle_PRAGMA(self, contents: str):
        pass

    directives = {
        "#define": handle_DEFINE,
        "#undef": handle_UNDEF,
        "#if": handle_IFDEF,
        "#ifdef": handle_IFDEF,
        "#ifndef": handle_IFNDEF,
        "#elif": handle_ELIF,
        # C23
        # "#elifdef" : handle_ELIF,
        # "#elifndef" : handle_ELIF,
        "#else": handle_ELSE,
        "#endif": handle_ENDIF,
        "#include": handle_INCLUDE,
        # TODO?
        # "#error" : handle_ERROR,
        # C23
        # "#warning" : handle_WARNING,
        # TODO?
        "#pragma": handle_PRAGMA,
        # "#line" : handle_LINE,
        # C23
        # "#embed" : handle_EMBED,
    }

    def handle_directive(self, directive: str, code: str, line: int, pos: int):
        split = directive.split(" ", 1)
        dir = split[0]
        if len(split) > 1:
            contents = split[1]
        else:
            contents = ""

        print("%s\nwith contents %s\nat %d, %d\n" % (dir, contents, line, pos))
        try:
            self.directives[dir](self, contents)
        except KeyError:
            raise Exception("Invalid directive!")

    def _check_for_newline(self, c: str, line: int, pos: int) -> tuple[bool, int, int]:
        if c == "\n":
            pos = 1
            line += 1
            return (True, line, pos)
        pos += 1
        return (False, line, pos)

    def _check_for_comment_start(
        self, code: str, c: str, i: int, end: int, buf: list[str], buf_code: list[str]
    ) -> tuple[bool, CodeSection | int]:
        if c == "/":
            buf_code += [c]
            i += 1
            if i < end:
                _c = code[i]
                if _c == "*":
                    buf_code += [_c]
                    return (True, self.CodeSection.COMMENT)
                elif _c == "/":
                    buf_code += [_c]
                    return (True, self.CodeSection.LINE_COMMENT)
                buf += [c]
                return (False, i)
        return (False, i)

    def _read_DIRECTIVE(
        self,
        code: str,
        i: int,
        end: int,
        c: str,
        buf: list[str],
        buf_code: list[str],
        line: int,
        pos: int,
    ) -> tuple[bool, CodeSection, int]:
        section = self.CodeSection.DIRECTIVE
        cont = False
        (is_comment, res) = self._check_for_comment_start(
            code, c, i, end, buf, buf_code
        )
        if is_comment:
            section = res
        else:
            i = res
            if i < end:
                c = code[i]
                buf_code += [c]

                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if is_newline:
                    self.handle_directive("".join(buf), "".join(buf_code), line, pos)
                    section = self.CodeSection.WHITESPACE
                    buf.clear()
                    buf_code.clear()
                elif c == "\\":
                    i += 1
                    if i < end:
                        c = code[i]

                        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                        if is_newline:
                            buf_code += [c]
                            buf += [" "]
                        else:
                            buf += ["\\"]
                            cont = True
                elif c == " " or c == "\t":
                    buf += [c]
                else:
                    buf += [c]
        return (cont, section, i, line, pos)

    def _read_COMMENT(
        self,
        code: str,
        i: int,
        end: int,
        c: str,
        buf_code: list[str],
        line: int,
        pos: int,
    ) -> tuple[CodeSection, int, int, int]:
        section = self.CodeSection.COMMENT
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if c == "*":
            i += 1
            if i < end:
                c = code[i]
                buf_code += [c]
                (is_newline, line, pos) = self._check_for_newline(c, line, pos)
                if c == "/":
                    # TODO Handle Comments
                    section = self.CodeSection.WHITESPACE
                    buf_code.clear()
        return (section, i, line, pos)

    def _read_LINE_COMMENT(
        self, c: str, buf_code: list[str], line: int, pos: int
    ) -> tuple[CodeSection, int, int]:
        section = self.CodeSection.LINE_COMMENT
        buf_code += [c]
        (is_newline, line, pos) = self._check_for_newline(c, line, pos)
        if is_newline:
            # TODO Handle Comments
            section = self.CodeSection.WHITESPACE
            buf_code.clear()
        return (section, line, pos)

    def _read_WHITESPACE(
        self,
        code: str,
        i: int,
        end: int,
        c: str,
        buf: list[str],
        buf_code: list[str],
        line: int,
        pos: int,
        transition_to_code_allowed: bool,
    ) -> tuple[CodeSection, int, int, int]:
        section = self.CodeSection.WHITESPACE

        tmp_buf = []
        tmp_buf_code = []
        (is_comment, res) = self._check_for_comment_start(
            code, c, i, end, tmp_buf, tmp_buf_code
        )
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
                    if c == "#":
                        section = self.CodeSection.DIRECTIVE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
                    elif transition_to_code_allowed:
                        section = self.CodeSection.CODE
                        buf += tmp_buf + [c]
                        buf_code += tmp_buf_code + [c]
        return (section, i, line, pos)

    def _read_CODE(
        self,
        code: str,
        i: int,
        end: int,
        c: str,
        buf: list[str],
        buf_code: list[str],
        line: int,
        pos: int,
        brace_level: int,
        parentheses_level: int,
        watch_for_func_def: bool,
        is_func_def: bool,
    ) -> tuple[bool, CodeSection, int]:
        section = self.CodeSection.CODE
        cont = False

        if i < end:
            c = code[i]
            buf += [c]
            buf_code += [c]

            function_ended = False
            # Function Watching:
            if c == "{":
                brace_level += 1
                if watch_for_func_def:
                    watch_for_func_def = False
                    is_func_def = True

            elif c == "}":
                brace_level -= 1
                if is_func_def and brace_level == 0:
                    is_func_def = False
                    function_ended = True

            elif c == "(":
                parentheses_level += 1

            elif c == ")":
                if brace_level == 0:
                    watch_for_func_def = True
                parentheses_level -= 1

            elif not c.isspace():
                watch_for_func_def = False

            (is_newline, line, pos) = self._check_for_newline(c, line, pos)
            if not is_newline:
                if (function_ended) or (c == ";" and brace_level == 0):
                    section = self.CodeSection.WHITESPACE
                    out_str = "".join(buf_code)
                    print("****\n" + out_str)
                    buf.clear()
                    buf_code.clear()
        return (
            cont,
            section,
            i,
            line,
            pos,
            brace_level,
            parentheses_level,
            watch_for_func_def,
            is_func_def,
        )

    def read_include(self, code: str) -> list[tuple[CodeSection, str, int, int]]:
        sections: list[tuple[int, int, self.CodeSection, str]] = []

        line = 1
        pos = 1

        buf: list[str] = []
        buf_code: list[str] = []

        section = self.CodeSection.WHITESPACE
        end = len(code)
        i = 0
        while i < end:
            c = code[i]
            match section:
                case self.CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos) = self._read_DIRECTIVE(
                        code, i, end, c, buf, buf_code, line, pos
                    )
                    if cont:
                        continue
                case self.CodeSection.COMMENT:
                    (section, i, line, pos) = self._read_COMMENT(
                        code, i, end, c, buf_code, line, pos
                    )
                case self.CodeSection.LINE_COMMENT:
                    (section, line, pos) = self._read_LINE_COMMENT(
                        c, buf_code, line, pos
                    )
                case self.CodeSection.WHITESPACE:
                    (section, i, line, pos) = self._read_WHITESPACE(
                        code, i, end, c, buf, buf_code, line, pos, False
                    )
            i += 1

    def read(self, code: str) -> list[tuple[CodeSection, str, int, int]]:
        sections: list[tuple[int, int, self.CodeSection, str]] = []

        line = 1
        pos = 1

        buf: list[str] = []
        buf_code: list[str] = []

        # Level handling and function definition processing.
        brace_level = 0
        parentheses_level = 0

        watch_for_func_def = False
        is_func_def = False

        section = self.CodeSection.WHITESPACE
        end = len(code)
        i = 0
        while i < end:
            c: str = code[i]

            match section:
                case self.CodeSection.DIRECTIVE:
                    (cont, section, i, line, pos) = self._read_DIRECTIVE(
                        code, i, end, c, buf, buf_code, line, pos
                    )
                    if cont:
                        continue
                case self.CodeSection.COMMENT:
                    (section, i, line, pos) = self._read_COMMENT(
                        code, i, end, c, buf_code, line, pos
                    )
                case self.CodeSection.LINE_COMMENT:
                    (section, line, pos) = self._read_LINE_COMMENT(
                        c, buf_code, line, pos
                    )
                case self.CodeSection.WHITESPACE:
                    (section, i, line, pos) = self._read_WHITESPACE(
                        code, i, end, c, buf, buf_code, line, pos, True
                    )
                case self.CodeSection.CODE:
                    (
                        cont,
                        section,
                        i,
                        line,
                        pos,
                        brace_level,
                        parentheses_level,
                        watch_for_func_def,
                        is_func_def,
                    ) = self._read_CODE(
                        code,
                        i,
                        end,
                        c,
                        buf,
                        buf_code,
                        line,
                        pos,
                        brace_level,
                        parentheses_level,
                        watch_for_func_def,
                        is_func_def,
                    )
                    if cont:
                        continue
            i += 1
        if brace_level != 0:
            print("BRACE_MISMATCH!")

    def preprocess(self, code: str):
        code = code.replace("\r\n", "\n")
        # Trigraph replacement
        # Line splicing
        # Tokenization
        # Macro expansion and directive handling
        # self.read_include(code)
        self.read(code)

    def exec(self, file):
        f = open(file)
        self.preprocess(f.read())
        f.close()

    @staticmethod
    def print_macros():
        for n, m in Preprocessor.macros.items():
            print(
                "%s : %s" % (n, Preprocessor.ObjectMacro.contents_to_string(m.contents))
            )
        print("\n")


if __name__ == "__main__":
    include_dirs = [
        "mm",
        "mm/include",
        "mm/assets",
        ".",
        "./",
        "./mm",
    ]

    file = "mm/src/code/z_message.c"

    p = Preprocessor(include_dirs)

    # Macro test

    # define STR(X) #X
    p.add_FunctionMacro("STR", None, "#X", ["X"])
    # define STRX(X) STR(X)
    p.add_FunctionMacro("STRX", None, "STR(X)", ["X"])
    # define TEST4(_1, _2, _3) STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)
    test4 = p.add_FunctionMacro(
        "TEST4",
        None,
        "STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)",
        ["_1", "_2", "_3"],
    )

    # define BOOM (5)
    p.add_ObjectMacro("BOOM", None, "(521)")
    # define Bo 5
    p.add_ObjectMacro("BO", None, "5")
    # define OM 6
    p.add_ObjectMacro("OM", None, "6")

    # TEST4(  BO  , OM    BO     ,   OM  )
    m_1 = Preprocessor.ObjectMacro.parse("  BO  ")
    m_2 = Preprocessor.ObjectMacro.parse(" OM    BO     ")
    m_3 = Preprocessor.ObjectMacro.parse("   OM  ")

    # "(521) 5" "BOOM BO" "6 5" "BOOM BO 5"
    print(Preprocessor.ObjectMacro.contents_to_string(test4.solve([m_1, m_2, m_3])))

    # ConstexprEvaluator test

    e = Preprocessor.ConstexprEvaluator()
    val = e.eval(Preprocessor.ObjectMacro.parse("(2 + 2 * 2) * 10 == 6 ? 10 : 7"))
    print(val)

    # Preprocessor test
    p.exec(file)
