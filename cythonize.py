from __future__ import with_statement

import os, sys
from os import path
import shutil
import inspect
from hashlib import md5

import subprocess

CYTHONIZE_DIR = '__cythonize_build__'
WAF_FILE = './waf'

def cythonize(func):
    sourcelines, startlinenum = inspect.getsourcelines(func)
    sourcelines = cleansourcelines(sourcelines)
    sourcestr = ''.join(sourcelines)
    m = md5(sourcestr)
    sourcehash = "%s_%s" % (func.__name__, m.hexdigest())
    fname = "%s.pyx" % sourcehash
    dirname = setup(dirname=sourcehash, fname=fname, source=sourcestr)
    compile_extmod(dirname)
    mod = import_extmod(dirname, sourcehash)
    return getattr(mod, func.__name__)

def cleansourcelines(slines):
    return [sl for sl in slines if not sl.startswith('@cythonize')]

def modfromfname(fname):
    if fname.endswith('.pyx'):
        return fname[:-len('.pyx')]
    elif fname.endswith('.py'):
        return fname[:-len('.py')]

def setup(dirname, fname, source):
    dirname = path.join(os.curdir, CYTHONIZE_DIR, dirname)
    modname = modfromfname(fname)
    try:
        os.makedirs(dirname)
    except OSError:
        pass
    full_fname = path.join(dirname, fname)
    with open(full_fname, 'w') as fh:
        fh.write(source)
    # copy waf to dirname
    shutil.copy(WAF_FILE, dirname)
    # write wscript to dirname
    full_wscript = path.join(dirname, 'wscript')
    with open(full_wscript, 'w') as fh:
        fh.write(wscript_src % {'modname' : modname})
    return dirname

def compile_extmod(dirname):
    odir = path.abspath(os.curdir)
    os.chdir(dirname)
    set_cython = 'CYTHON=/Users/ksmith/fwrap/ve-python25/bin/cython'
    exe_str = ' '.join(
                        [set_cython,
                        sys.executable,
                        './waf distclean configure build'])
    try:
        subprocess.check_call(exe_str, shell=True)
    finally:
        os.chdir(odir)

def import_extmod(dirname, modname):
    sys.path.insert(0, os.path.join(dirname, 'build'))
    try:
        mod = __import__(modname)
    finally:
        sys.path.pop(0)
    return mod

wscript_src = '''
top = '.'
out = 'build'

def options(opts):
    opts.load('compiler_c')
    opts.load('python')
    opts.load('cython')

def configure(ctx):
    ctx.load('compiler_c')
    ctx.load('python')
    ctx.check_python_headers()
    ctx.load('cython')

def build(bld):
    bld(
        features = 'c cshlib pyext',
        source   = '%(modname)s.pyx',
        target   = '%(modname)s',
        )
'''
