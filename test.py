from cythonize import cythonize

@cythonize
def foo(a, b):
    return a +b

def foo_slow(a, b):
    return a + b

print foo(1, 2)
print foo_slow(1, 2)
