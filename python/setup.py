#!/usr/bin/env python

# Stolen from Shapely's setup.py
#

import logging
import platform
import sys
from distutils.version import StrictVersion

import numpy
from setuptools import setup
from setuptools.extension import Extension as DistutilsExtension

logging.basicConfig()
log = logging.getLogger(__file__)

DEBUG = True
USE_CYTHON = False
try:

    from Cython.Build import cythonize
    import cython

    if not StrictVersion(cython.__version__) < StrictVersion("0.24"):
        USE_CYTHON = True

except ImportError:
    pass

ext = ".pyx" if USE_CYTHON else ".cpp"

# python -W all setup.py ...
if "all" in sys.warnoptions:
    log.level = logging.DEBUG

# Get the version from the lazperf module
module_version = None
with open("lazperf/__init__.py", "r") as fp:
    for line in fp:
        if line.startswith("__version__"):
            module_version = StrictVersion(line.split("=")[1].strip().strip("\"'"))
            break

if not module_version:
    raise ValueError("Could not determine lazperf's version")

# Handle UTF-8 encoding of certain text files.
open_kwds = {}
if sys.version_info >= (3,):
    open_kwds["encoding"] = "utf-8"

with open("VERSION.txt", "w", **open_kwds) as fp:
    fp.write(str(module_version))

with open("README.rst", "r", **open_kwds) as fp:
    readme = fp.read()

with open("CHANGES.rst", "r", **open_kwds) as fp:
    changes = fp.read()

long_description = readme + "\n\n" + changes

include_dirs = ["."]

library_dirs = []
libraries = []
extra_link_args = []
extra_compile_args = []


# Here we assume everyone on windows uses the MSVC compiler
if platform.system() != "Windows":
    extra_compile_args = ["-std=c++11"]
    if DEBUG:
        extra_compile_args += ["-g", "-O0"]
else:
    include_dirs = ['..']

include_dirs.append(numpy.get_include())


sources = [
    "lazperf/pylazperfapi" + ext,
    "lazperf/PyLazperf.cpp",
    "lazperf/PyVlrCompressor.cpp",
]
extensions = [
    DistutilsExtension(
        "lazperf.pylazperfapi",
        sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c++",
    )
]

if USE_CYTHON and "clean" not in sys.argv:
    from Cython.Build import cythonize

    extensions = cythonize(extensions, language="c++")

setup_args = dict(
    name="lazperf",
    version=str(module_version),
    install_requires=["numpy >=1.11"],
    description="Point cloud data compression",
    license="LGPL",
    keywords="point cloud compression",
    author="Howard Butler",
    author_email="howard@hobu.co",
    maintainer="Howard Butler",
    maintainer_email="howard@hobu.co",
    url="https://github.com/hobu/laz-perf",
    long_description=long_description,
    test_suite="test",
    include_package_data=True,
    packages=["lazperf"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
setup(ext_modules=extensions, **setup_args)
