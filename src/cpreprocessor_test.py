import sys, shutil, os
from enum import IntEnum
from types import FunctionType as function
from collections import deque
from copy import deepcopy
from pathlib import Path

from core.cpreprocessor import Preprocessor
from core.macro import MacroSection, MacroExpression, MacroExpressionNode, Macro, ObjectMacro, FunctionMacro, VariadicMacro, MacroSource, ExternalSource, CodeSource
from core.constexpr_evaluator import ConstexprEvaluator

standard_c_lib_dir = "mm/include/libc" # I'm not sure if decomp uses compiler's standard C library

def macro_test():
    global standard_c_lib_dir
    print("\nMacro test")

    p = Preprocessor(include_dirs, standard_c_lib_dir)

    #define STR(X) #X
    p.new_FunctionMacro("STR", None, "#X", ["X"])
    #define STRX(X) STR(X)
    p.new_FunctionMacro("STRX", None, "STR(X)", ["X"])
    #define TEST4(_1, _2, _3) STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)
    test4 = p.new_FunctionMacro("TEST4", None, "STRX(_1##_2) STR(_1##_2) STR(_2) STR(_1##_2 _1)", ["_1", "_2", "_3"])

    #define BOOM (5)
    p.new_ObjectMacro("BOOM", None, "(521)")
    #define Bo 5
    p.new_ObjectMacro("BO", None, "5")
    #define OM 6
    p.new_ObjectMacro("OM", None, "6")

    # TEST4(  BO  , OM    BO     ,   OM  )
    m_1 = ObjectMacro.parse("  BO  ")
    m_2 = ObjectMacro.parse(" OM    BO     ")
    m_3 = ObjectMacro.parse("   OM  ")

    # "(521) 5" "BOOM BO" "6 5" "BOOM BO 5"
    print(ObjectMacro.contents_to_string(test4.solve([m_1, m_2, m_3])))

def constexpr_evaluator_test():
    print("\nConstexpr Evaluator test")

    e = ConstexprEvaluator()
    val = e.eval(ObjectMacro.parse("(2 + 2 * 2) * 10 == 6 ? 10 : 7"))
    print(val)

    val = e.eval(ObjectMacro.parse("(1||0)"))
    print(val)

def preprocessor_test():
    global standard_c_lib_dir
    print("\nPreprocessor test")

    p = Preprocessor(include_dirs, standard_c_lib_dir)
    p.exec(file)

    print("OK" if ("MESSAGE_ITEM_NONE" in p.macros) else "ERROR")

def main():
    macro_test()
    constexpr_evaluator_test()
    preprocessor_test()
    print("\nFINISHED")

include_dirs = [
    'mm',
    'mm/src',
    'mm/include',
    'mm/assets',
]

file = 'mm/src/code/z_message.c'

if __name__ == "__main__":
    main()