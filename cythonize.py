from __future__ import with_statement

import os, sys
from os import path
import shutil
import inspect
import imp
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
    mod_dir = get_dirname(sourcehash)
    try:
        mod = import_extmod(mod_dir, sourcehash)
    except ImportError:
        setup(dirname=mod_dir, fname=fname, source=sourcestr)
        cond_compile_extmod(mod_dir)
        mod = import_extmod(mod_dir, sourcehash)
    return getattr(mod, func.__name__)

def cleansourcelines(slines):
    return [sl for sl in slines if not sl.startswith('@cythonize')]

def find_module(name, path):
    old_path = sys.path
    sys.path = [os.path.join(path, 'build')] + old_path
    try:
        return imp.find_module(name)
    finally:
        sys.path = old_path
    return mod

def get_dirname(hsh):
    return path.join(os.curdir, CYTHONIZE_DIR, hsh)

def modfromfname(fname):
    if fname.endswith('.pyx'):
        return fname[:-len('.pyx')]
    elif fname.endswith('.py'):
        return fname[:-len('.py')]

def setup(dirname, fname, source):
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

def cond_compile_extmod(dirname):
    odir = path.abspath(os.curdir)
    os.chdir(dirname)
    set_cython = 'CYTHON=/Users/ksmith/fwrap/ve-python25/bin/cython'
    exe_str = ' '.join(
                        [set_cython,
                        sys.executable,
                        './waf configure build'])
    try:
        subprocess.check_call(exe_str, shell=True)
    finally:
        os.chdir(odir)

def import_extmod(dirname, modname):
    import pdb; pdb.set_trace()
    old_path = sys.path
    sys.path = [os.path.join(dirname, 'build')] + old_path
    try:
        mod = __import__(modname)
    finally:
        sys.path = old_path
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
