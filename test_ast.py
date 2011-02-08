import ast

src = """
@cython.locals(a=cython.int, b=cython.int)
def func(a, b):
    return a+b
"""

func_ast = compile(src, "<string>", "exec", flags=ast.PyCF_ONLY_AST)

import pdb; pdb.set_trace()
