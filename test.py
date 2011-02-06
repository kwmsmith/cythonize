from cythonize import cythonize

@cythonize
# @cython.locals(a=cython.int, b=cython.int)
def foo(a, b):
    return a +b

print foo(3, 4)
