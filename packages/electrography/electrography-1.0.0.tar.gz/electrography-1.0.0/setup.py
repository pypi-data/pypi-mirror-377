#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, Extension
from Cython.Build import cythonize
from Cython.Compiler import Options

extensions = [
    Extension(
        "electrography.data_helper_functions",
        ["src/zippy_cython_functions/data_helper_functions.pyx"], \
        ),
    ]

setup(
    name='electrography',
    ext_modules = cythonize(extensions, \
        compiler_directives={"language_level":3, "profile": False}),
    )

