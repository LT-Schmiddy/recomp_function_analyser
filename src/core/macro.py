import sys, shutil, os
from enum import IntEnum
from .doubly_linked_list import DoublyLinkedList
from copy import deepcopy

class MacroSection(IntEnum):
    WHITESPACE = 0
    NAME = 1
    OPERATOR = 2
    TEXT = 3
    NUMBER = 4
    MISC = 5

MacroExpression = DoublyLinkedList[tuple[MacroSection, str]]
MacroExpressionNode = DoublyLinkedList.Node[tuple[MacroSection, str]]

class MacroSource:
    def __repr__(self):
        raise NotImplementedError()

class ExternalSource(MacroSource):
    def __init__(self, source : str):
        super().__init__()
        self.source = source

    def __repr__(self) -> str:
        return self.source

class CodeSource(MacroSource):
    def __init__(self, file : str, line : int, pos : int):
        super().__init__()
        self.file = file
        self.line = line
        self.pos = pos

    def __repr__(self) -> str:
        return "%s:%d:%d" % (self.file, self.line, self.pos)



class Macro:
    def __init__(self, source : MacroSource):
        super().__init__()
        self.source = source

    def solve(self, macroexpr : MacroExpression, origin_node : MacroExpressionNode):
        raise NotImplementedError()

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
        '?',
        ':',
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

    def __init__(self, source : MacroSource, macros : dict[str, Macro], definition : str):
        super().__init__(source)
        self.macros = macros
        self.contents = self.parse(definition)

    @staticmethod
    def parse(definition : str) -> MacroExpression:
        res : MacroExpression = DoublyLinkedList()

        processed_section = MacroSection.WHITESPACE
        buffer : list[str] = []

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
            elif c in ObjectMacro.operators:
                section = MacroSection.OPERATOR
                if processed_section == MacroSection.OPERATOR:
                    tmp = ''.join(buffer) + c
                    if tmp not in ObjectMacro.operators:
                        res.add_end((processed_section, ''.join(buffer)))
                        buffer = []
            elif c in {'"', "'"}:
                section = MacroSection.TEXT

                res.add_end((processed_section, ''.join(buffer)))
                buffer = [c]
                processed_section = section

                initial = c
                i += 1
                while i < end:
                    c = definition[i]
                    if (c == initial):
                        break
                    buffer += [c]
                    i += 1
            else:
                section = MacroSection.MISC

            if section != processed_section:
                res.add_end((processed_section, ''.join(buffer)))
                buffer = [c]
                processed_section = section
            elif section != MacroSection.WHITESPACE:
                buffer += [c]
            i += 1
        if processed_section != MacroSection.WHITESPACE:
            res.add_end((processed_section, ''.join(buffer)))
        res.pop_begin()
        return res

    @staticmethod
    def _remove_node(contents : MacroExpression, current : MacroExpressionNode):
        contents.remove(current)
        current = current.next
        if current == None:
            return (None, None, None)
        (section, content) = current.val
        return (current, section, content)

    @staticmethod
    def _remove_space(contents : MacroExpression, current : MacroExpressionNode, section : MacroSection, content : str) -> tuple[MacroExpressionNode, MacroSection, str]:
        if section == MacroSection.WHITESPACE:
            return ObjectMacro._remove_node(contents, current)
        return (current, section, content)

    def _solve_perform_concatenation(self, contents : MacroExpression):
        current = contents.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.OPERATOR and content == '##':
                operator = current
                current = current.next
                if current != None:
                    left = current.prev.prev
                    (l_section, l_content) = left.val
                    (left, l_section, l_content) = self._remove_space(contents, left, l_section, l_content)

                    right = current
                    (r_section, r_content) = right.val
                    (right, r_section, r_content) = self._remove_space(contents, right, r_section, r_content)

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

    def _solve_add_arg(self, arg : MacroExpression, args : list[MacroExpression]):
        begin = arg.begin
        if begin != None and begin.val[0] == MacroSection.WHITESPACE:
            arg.remove(begin)

        end = arg.end
        if end != None and end.val[0] == MacroSection.WHITESPACE:
            arg.remove(end)

        args += [arg]

    def _solve_handle_functionMacro(self, used : set[str], macro : Macro, contents : MacroExpression, start : MacroExpressionNode) -> tuple[MacroExpression, MacroExpressionNode]:
        current = start.next
        if current != None:
            (section, content) = current.val
            if section == MacroSection.OPERATOR and content == '(':
                contents.remove(current)
                current = current.next

                parenth_level = 1
                args : list[MacroExpression] = []
                f = current
                t = None
                while current != None:
                    (section, content) = current.val
                    if section == MacroSection.OPERATOR:
                        if content == '(':
                            parenth_level += 1
                            t = current
                        elif content == ')':
                            parenth_level -= 1
                            if parenth_level > 0:
                                t = current
                            else:
                                arg = contents.extract_list(f, t)
                                self._solve_add_arg(arg, args)

                                contents.remove(current)
                                break
                        elif content == ',':
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

    def _solve_replace_macros(self, contents : MacroExpression, used : set[str]) -> MacroExpression:
        current = contents.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.NAME:
                macro = self.macros.get(content)
                if macro != None and content not in used:
                    used.add(content)
                    if isinstance(macro, FunctionMacro):
                        start = current

                        (list, current) = self._solve_handle_functionMacro(used, macro, contents, current)

                        contents.add_list_before(list, current)
                        contents.remove(start)
                    elif isinstance(macro, ObjectMacro):
                        contents.add_list_before(macro._copy_and_solve(used), current)
                    elif isinstance(macro, Macro):
                        macro.solve(contents, current)
                    else:
                        raise Exception("Not a macro!")
                    contents.remove(current)
                    used.remove(content)
            current = current.next

    def _solve(self, contents : MacroExpression, used : set[str]) -> MacroExpression:
        self._solve_perform_concatenation(contents)
        self._solve_replace_macros(contents, used)

    def _copy_and_solve(self, used : set[str]) -> MacroExpression:
        res = deepcopy(self.contents)
        self._solve(res, used)
        return res

    def solve(self) -> MacroExpression:
        return self._copy_and_solve(set())

    @staticmethod
    def contents_to_string(contents : MacroExpression) -> str:
        current = contents.begin
        res = ''
        while current != None:
            content = current.val[1]
            if isinstance(content, bool):
                res += "True" if content else "False"
            else:
                res += content
            current = current.next
        return res

class FunctionMacro(ObjectMacro):
    def __init__(self, source : MacroSource, macros : dict[str, Macro], definition : str, args : list[str]):
        super().__init__(macros, source, definition)
        self.args = {arg: i for (i, arg) in enumerate(args)}

    def _solve_get_arg(self, args : list[MacroExpression], name : str) -> MacroExpression:
        pos = self.args.get(name)
        if pos != None:
            try:
                arg = args[pos]
                return arg
            except IndexError:
                return None
        return None

    def _solve_stringify_arg(self, args : list[MacroExpression], contents : MacroExpression, origin_node : MacroExpressionNode, content : str):
        arg = self._solve_get_arg(args, content)
        if arg != None:
            contents.remove(origin_node.prev)
            origin_node.val = (MacroSection.TEXT, '"' + self.contents_to_string(arg) + '"')
        else:
            raise Exception("'#' is not followed by a macro parameter!")

    def _solve_perform_stringification(self, args : list[MacroExpression], contents : MacroExpression):
        current = contents.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.OPERATOR and content == '#':
                current = current.next
                if current != None:
                    (section, content) = current.val
                    (current, section, content) = self._remove_space(contents, current, section, content)

                    if section == MacroSection.NAME:
                        self._solve_stringify_arg(args, contents, current, content)
                else:
                    break
            current = current.next

    def _solve_perform_concatenation_get_left_arg(self, args : list[MacroExpression], contents : MacroExpression, current : MacroExpressionNode) -> tuple[MacroExpressionNode, MacroSection, str]:
        left = current.prev.prev
        (l_section, l_content) = left.val
        (left, l_section, l_content) = self._remove_space(contents, left, l_section, l_content)

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

    def _solve_perform_concatenation_get_right_arg(self, args : list[MacroExpression], contents : MacroExpression, current : MacroExpressionNode) -> tuple[MacroExpressionNode, MacroSection, str]:
        right = current
        (r_section, r_content) = right.val
        (right, r_section, r_content) = self._remove_space(contents, right, r_section, r_content)

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

    def _solve_perform_concatenation_f(self, args : list[MacroExpression], contents : MacroExpression):
        current = contents.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.OPERATOR and content == '##':
                operator = current
                current = current.next
                if current != None:
                    (left, l_section, l_content) = self._solve_perform_concatenation_get_left_arg(args, contents, current)
                    (right, r_section, r_content, end) = self._solve_perform_concatenation_get_right_arg(args, contents, current)

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

    def _solve_replace_arg(self, args : list[MacroExpression], contents : MacroExpression, origin_node : MacroExpressionNode, content : str):
        arg = self._solve_get_arg(args, content)
        if arg != None:
            contents.add_list_before(deepcopy(arg), origin_node)
            contents.remove(origin_node)

    def _solve_replace_args(self, args : list[MacroExpression], contents : MacroExpression, used : set[str]):
        for arg in args:
            super()._solve(arg, used)

        current = contents.begin
        while current != None:
            (section, content) = current.val
            if section == MacroSection.NAME:
                self._solve_replace_arg(args, contents, current, content)
            current = current.next

    def _solve(self, args : list[MacroExpression], contents: MacroExpression, used : set[str]):
        self._solve_perform_stringification(args, contents)
        self._solve_perform_concatenation_f(args, contents)
        self._solve_replace_args(args, contents, used)
        super()._solve_replace_macros(contents, used)

    def _copy_and_solve(self, args : list[MacroExpression], used : set[str]) -> MacroExpression:
        res = deepcopy(self.contents)
        self._solve(args, res, used)
        return res

    def solve(self, args : list[MacroExpression]) -> MacroExpression:
        return self._copy_and_solve(args, set())

class VariadicMacro(FunctionMacro):
    def _generate_va_args(self, args : list[MacroExpression]) -> MacroExpression:
        res = DoublyLinkedList()

        i = len(self.args)
        end = len(args)
        if i < end:
            res.add_begin(None)
            while i < end - 1:
                res.add_list_after(deepcopy(args[i]), res.end)
                res.add_end((MacroSection.WHITESPACE, ','))
                i += 1
            res.add_list_after(deepcopy(args[i]), res.end)
            res.pop_begin()
        self.va_args = res

    def _solve(self, args : list[MacroExpression], contents: MacroExpression, used : set[str]):
        self._generate_va_args(args)
        super()._solve(contents, used)

    def _solve_stringify_arg(self, args : list[MacroExpression], contents : MacroExpression, origin_node : MacroExpressionNode, content : str):
        if content == "__VA_ARGS__":
            contents.remove(origin_node.prev)
            origin_node.val = (MacroSection.TEXT, '"' + self.contents_to_string(self.va_args) + '"')
        else:
            super()._solve_stringify_arg(args, contents, origin_node, content)

    def _solve_replace_arg(self, args : list[MacroExpression], contents : MacroExpression, origin_node : MacroExpressionNode, content : str):
        if content == "__VA_ARGS__":
            contents.add_list_before(deepcopy(self.va_args), origin_node)
            contents.remove(origin_node)
        else:
            super()._solve_replace_arg(args, contents, origin_node, content)