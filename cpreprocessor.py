import sys, shutil
from enum import IntEnum
from types import FunctionType as function
from typing import Generic, TypeVar
from collections import deque

T = TypeVar('T')

class DoublyLinkedList(Generic[T]):
    class Node(Generic[T]):
        def __init__(self, val : T, prev, next):
            super().__init__()
            self.val = val
            self.prev = prev
            self.next = next

    def __init__(self):
        super().__init__()
        self.begin = None
        self.end = None

    def add_begin(self, val : T) -> Node[T]:
        new = self.Node(val, None, self.begin)
        if self.begin is not None:
            self.begin.prev = new
        self.begin = new
        if self.end is None:
            self.end = new
        return new

    def add_end(self, val : T) -> Node[T]:
        new = self.Node(val, self.end, None)
        if self.end is not None:
            self.end.next = new
        self.end = new
        if self.begin is None:
            self.begin = new
        return new

    def remove(self, node : Node[T]):
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.end = node.prev

        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.begin = node.next

class ConstexprEvaluator:
    class Symbol(IntEnum):
        CONST = 0
        OPERATOR = 1

    class Associativity(IntEnum):
        LEFT_TO_RIGHT = 0
        RIGHT_TO_LEFT = 1

    def __init__(self):
        super().__init__()
        self.symbols : DoublyLinkedList[tuple[self.Symbol, int | str]] = DoublyLinkedList()
        self.cond_s : deque[int] = deque()

    def handle_single_arg(self, node : DoublyLinkedList.Node[tuple[Symbol, str]], func : function):
        if node.next:
            (symbol, val) = node.next.val
            if symbol == self.Symbol.CONST:
                node.val = (self.Symbol.CONST, func(val))
                self.symbols.remove(node.next)
                return None
        raise Exception("Invalid Expression!")

    def handle_double_arg(self, node : DoublyLinkedList.Node[tuple[Symbol, str]], func : function):
        if node.prev and node.next:
            (l_symbol, l_val) = node.prev.val
            (r_symbol, r_val) = node.next.val
            if l_symbol == self.Symbol.CONST and r_symbol == self.Symbol.CONST:
                node.val = (self.Symbol.CONST, func(l_val, r_val))
                self.symbols.remove(node.prev)
                self.symbols.remove(node.next)
                return None
        raise Exception("Invalid Expression!")

    def handle_PLUS(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_single_arg(node, lambda x : x)

    def handle_MINUS(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_single_arg(node, lambda x : -x)

    def handle_SUM(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x + y)

    def handle_SUB(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x - y)

    def handle_MUL(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x * y)

    def handle_DIV(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x / y)

    def handle_MOD(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x % y)

    def handle_NOT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_single_arg(node, lambda x : not x)

    def handle_CONDL(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        try:
            z = self.cond_s.pop()
        except IndexError:
            raise Exception("Invalid Expression!")
        self.handle_double_arg(node, lambda x, y : y if x else z)

    def handle_CONDR(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_single_arg(node, lambda x : self.cond_s.append(x))
        self.symbols.remove(node)

    def handle_AND(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x and y)

    def handle_OR(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x or y)

    def handle_EQ(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x == y)

    def handle_NEQ(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x != y)

    def handle_LT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x < y)

    def handle_GT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x > y)

    def handle_LEQ(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x <= y)

    def handle_GEQ(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x >= y)

    def handle_BAND(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x & y)

    def handle_BOR(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x | y)

    def handle_BXOR(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x ^ y)

    def handle_BNOT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_single_arg(node, lambda x : ~x)

    def handle_BLSHFT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x << y)

    def handle_BRSHFT(self, node : DoublyLinkedList.Node[tuple[Symbol, str]]):
        self.handle_double_arg(node, lambda x, y : x >> y)

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

    def eval(self, constexpr : str) -> int:
        end = len(constexpr)
        (eval, endpos) = self._eval(constexpr, 0, end)
        if endpos < end:
            raise('Invalid Expression!')
        return eval

    def _eval(self, constexpr : str, start : int, end : int) -> tuple[int, int]:
        # Parse Symbols
        c : str
        i = start
        while i < end:
            c = constexpr[i]
            if c == ')':
                break
            elif c == '(':
                e = ConstexprEvaluator()
                (eval, i) = e._eval(constexpr, i + 1, end)
                if i == end:
                    raise Exception("Invalid Expression!")
                self.symbols.add_end((self.Symbol.CONST, eval))
            elif c.isnumeric():
                j = i + 1
                while j < end:
                    c = constexpr[j]
                    if not c.isnumeric():
                        break
                    j += 1
                self.symbols.add_end((self.Symbol.CONST, int(constexpr[i:j])))
                i = j
                continue
            elif i + 1 < end and c in {'&', '|', '=', '!', '<', '>'}:
                i += 1
                _c = constexpr[i]
                cc = c + _c
                if cc in {'&&', '||', '==', '!=', '<=', '>=', '<<', '>>'}:
                    self.symbols.add_end((self.Symbol.OPERATOR, cc))
                else:
                    self.symbols.add_end((self.Symbol.OPERATOR, c))
                    if not _c.isspace():
                        self.symbols.add_end((self.Symbol.OPERATOR, _c))
            elif not c.isspace():
                self.symbols.add_end((self.Symbol.OPERATOR, c))
            i += 1

        # Detect unary + and -
        prev = self.Symbol.OPERATOR
        current = self.symbols.begin
        while current is not None:
            (symbol, val) = current.val
            if symbol == self.Symbol.OPERATOR and prev == symbol and (val == '+' or val == '-'):
                current.val = (self.Symbol.OPERATOR, 'u' + val)
            prev = symbol
            current = current.next

        # Process symbols
        for (associativity, symbol_set) in self.precedence:
            if associativity == self.Associativity.LEFT_TO_RIGHT:
                current = self.symbols.begin
            else:
                current = self.symbols.end

            while current is not None:
                (symbol, val) = current.val
                if symbol == self.Symbol.OPERATOR and val in symbol_set:
                    self.operators[val](self, current)
                if associativity == self.Associativity.LEFT_TO_RIGHT:
                    current = current.next
                else:
                    current = current.prev

        if len(self.cond_s) > 0:
            raise Exception("Invalid Expression!")

        current = self.symbols.begin
        if current.next is not None:
            raise Exception("Invalid Expression!")

        return (self.symbols.begin.val[1], i)

class Preprocessor:
    include_paths : list[str]

    def __init__(self, include_paths):
        self.include_paths = include_paths

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
        'mm/include',
        'mm/src',
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

    e = ConstexprEvaluator()
    val = e.eval("(2 + 2 * 2) * 10 == 6 ? 10 : 7")
    print(val)
    # p = Preprocessor(include_dirs)
    # p.exec(file)