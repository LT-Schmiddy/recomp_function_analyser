import sys, shutil, os
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from .doubly_linked_list import DoublyLinkedList
from copy import deepcopy
from pathlib import Path
from .macro import MacroExpression, MacroExpressionNode, MacroSection

class ConstexprEvaluator:
    class Associativity(IntEnum):
        LEFT_TO_RIGHT = 0
        RIGHT_TO_LEFT = 1

    def __init__(self):
        super().__init__()
        self.cond_st : deque[int] = deque()

    def handle_single_arg(self, constexpr : MacroExpression, node : MacroExpressionNode, func : function):
        if node.next:
            (symbol, val) = node.next.val
            if symbol == MacroSection.NUMBER:
                node.val = (MacroSection.NUMBER, func(val))
                constexpr.remove(node.next)
                return None
        raise Exception("Invalid expression!")

    def handle_double_arg(self, constexpr : MacroExpression, node : MacroExpressionNode, func : function):
        if node.prev and node.next:
            (l_symbol, l_val) = node.prev.val
            (r_symbol, r_val) = node.next.val
            if l_symbol == MacroSection.NUMBER and r_symbol == MacroSection.NUMBER:
                node.val = (MacroSection.NUMBER, func(l_val, r_val))
                constexpr.remove(node.prev)
                constexpr.remove(node.next)
                return None
            else:
                print(node.prev.val)
                print(node.val)
                print(node.next.val)
        raise Exception("Invalid expression!")

    def handle_PLUS(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_single_arg(constexpr, node, lambda x : x)

    def handle_MINUS(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_single_arg(constexpr, node, lambda x : -x)

    def handle_SUM(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x + y)

    def handle_SUB(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x - y)

    def handle_MUL(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x * y)

    def handle_DIV(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x / y)

    def handle_MOD(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x % y)

    def handle_NOT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_single_arg(constexpr, node, lambda x : not x)

    def handle_CONDL(self, constexpr : MacroExpression, node : MacroExpressionNode):
        try:
            z = self.cond_st.pop()
        except IndexError:
            raise Exception("Invalid expression!")
        self.handle_double_arg(constexpr, node, lambda x, y : y if x else z)

    def handle_CONDR(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_single_arg(constexpr, node, lambda x : self.cond_st.append(x))
        constexpr.remove(node)

    def handle_AND(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x and y)

    def handle_OR(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x or y)

    def handle_EQ(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x == y)

    def handle_NEQ(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x != y)

    def handle_LT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x < y)

    def handle_GT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x > y)

    def handle_LEQ(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x <= y)

    def handle_GEQ(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x >= y)

    def handle_BAND(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x & y)

    def handle_BOR(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x | y)

    def handle_BXOR(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x ^ y)

    def handle_BNOT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_single_arg(constexpr, node, lambda x : ~x)

    def handle_BLSHFT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x << y)

    def handle_BRSHFT(self, constexpr : MacroExpression, node : MacroExpressionNode):
        self.handle_double_arg(constexpr, node, lambda x, y : x >> y)

    operators : dict[str, function] = {
        'u+' : handle_PLUS,
        'u-' : handle_MINUS,
        '+' : handle_SUM,
        '-' : handle_SUB,
        '*' : handle_MUL,
        '/' : handle_DIV,
        '%' : handle_MOD,
        '!' : handle_NOT,
        '?' : handle_CONDL,
        ':' : handle_CONDR,
        '&&' : handle_AND,
        '||' : handle_OR,
        '==' : handle_EQ,
        '!=' : handle_NEQ,
        '<' : handle_LT,
        '>' : handle_GT,
        '<=' : handle_LEQ,
        '>=' : handle_GEQ,
        '&' : handle_BAND,
        '|' : handle_BOR,
        '^' : handle_BXOR,
        '~' : handle_BNOT,
        '<<' : handle_BLSHFT,
        '>>' : handle_BRSHFT,
    }

    precedence : list[tuple[int, set[str]]] = [
        (Associativity.RIGHT_TO_LEFT, {'u+', 'u-', '!', '~'}),
        (Associativity.LEFT_TO_RIGHT, {'*', '/', '%'}),
        (Associativity.LEFT_TO_RIGHT, {'+', '-'}),
        (Associativity.LEFT_TO_RIGHT, {'<<', '>>'}),
        (Associativity.LEFT_TO_RIGHT, {'<', '<=', '>', '>='}),
        (Associativity.LEFT_TO_RIGHT, {'==', '!='}),
        (Associativity.LEFT_TO_RIGHT, {'&'}),
        (Associativity.LEFT_TO_RIGHT, {'^'}),
        (Associativity.LEFT_TO_RIGHT, {'|'}),
        (Associativity.LEFT_TO_RIGHT, {'&&'}),
        (Associativity.LEFT_TO_RIGHT, {'||'}),
        (Associativity.RIGHT_TO_LEFT, {'?', ':'}),
    ]

    def _eval_simplify_constexpr(self, constexpr : MacroExpression):
        current = constexpr.begin
        parenth_level = 0
        f : MacroExpressionNode = None
        t : MacroExpressionNode = None
        while current != None:
            (section, content) = current.val
            if section == MacroSection.OPERATOR:
                if content == '(':
                    if parenth_level == 0:
                        f = current.next
                    parenth_level += 1
                    constexpr.remove(current)
                elif content == ')':
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
                # TODO Support more number formats
                num : int
                try:
                    num = int(content)
                except ValueError:
                    # Temporary solution for suffixes
                    i = len(content)
                    while i > 0:
                        i -= 1
                        c = content[i]
                        if c.isdigit():
                            break
                    updated_content = content[0 : i + 1]
                    num = int(updated_content)
                current.val = (section, num)
            elif section == MacroSection.WHITESPACE:
                constexpr.remove(current)
            current = current.next

    def _eval_detect_unary_plus_minus(self, constexpr : MacroExpression):
        prev = MacroSection.OPERATOR
        current = constexpr.begin
        while current != None:
            (symbol, val) = current.val
            if symbol == MacroSection.OPERATOR and prev == symbol and (val == '+' or val == '-'):
                current.val = (MacroSection.OPERATOR, 'u' + val)
            prev = symbol
            current = current.next

    def _eval_process_operators(self, constexpr : MacroExpression):
        for (associativity, symbol_set) in self.precedence:
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

    def _eval(self, constexpr : MacroExpression) -> int:
        self._eval_simplify_constexpr(constexpr)
        self._eval_detect_unary_plus_minus(constexpr)
        self._eval_process_operators(constexpr)

        if constexpr.begin != constexpr.end:
            raise Exception("Invalid expression!")

        return constexpr.begin.val[1]

    def eval(self, constexpr : MacroExpression) -> int:
        if constexpr.is_empty():
            raise Exception("Expected value in expression!")
        return self._eval(constexpr)