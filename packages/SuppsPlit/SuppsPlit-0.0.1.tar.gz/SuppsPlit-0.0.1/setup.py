"""
File Name: setup.py
Author: Panyi Dong
GitHub: https://github.com/PanyiDong/
Mathematics Department, University of Illinois at Urbana-Champaign (UIUC)

Project: SuppsPlit
Latest Version: <<projectversion>>
Relative Path: /setup.py
File Created: Thursday, 11th September 2025 2:47:14 pm
Author: Panyi Dong (panyid2@illinois.edu)

-----
Last Modified: Wednesday, 17th September 2025 11:02:22 pm
Modified By: Panyi Dong (panyid2@illinois.edu)

-----
MIT License

Copyright (c) 2025 - 2025, Panyi Dong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# setup.py
from setuptools import setup, Extension
import sys
import pybind11
import os

extra_compile_args = []
extra_link_args = []
include_dirs = [
    pybind11.get_include(),
    pybind11.get_include(user=True),
    # add any additional include paths, e.g. path to nanoflann.hpp if needed
    os.path.join(os.path.dirname(__file__), "src"),
]
library_dirs = []
libraries = []

# NOTE: use this on macOS with Homebrew-installed OpenMP
# if sys.platform == "darwin":
#     extra_compile_args += ["-Xpreprocessor", "-fopenmp"]
#     extra_link_args += ["-lomp"]
#     # Homebrew paths (adjust if needed)
#     include_dirs += ["/usr/local/include", "/opt/homebrew/include"]
#     library_dirs += ["/usr/local/lib", "/opt/homebrew/lib"]
#     libraries += ["omp"]
# elif sys.platform != "win32":
if sys.platform != "win32":
    extra_compile_args += ["-O3", "-std=c++14", "-fopenmp"]
    extra_link_args += ["-fopenmp"]

ext_modules = [
    Extension(
        "splitpy",
        sources=["src/sp.cpp", "src/sPlit.cpp", "src/bindings.cpp"],
        include_dirs=include_dirs,
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        library_dirs=library_dirs,
        libraries=libraries,
    )
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SuppsPlit",
    version="0.0.1",
    author="Panyi Dong",
    author_email="panyid2@illinois.edu",
    description="A data splitting based on support points.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PanyiDong/SuppsPlit",
    ext_modules=ext_modules,
    install_requires=["pybind11"],
    setup_requires=["pybind11"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False,
)
