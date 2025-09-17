from setuptools import setup, Extension, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import os

# Ensure we're in the right directory
here = os.path.abspath(os.path.dirname(__file__))

ext_modules = [
    Pybind11Extension(
        "qss_integrator.qss_py",  # Full module path
        [
            "qss_integrator/src/qss_python.cpp",
            "qss_integrator/src/qss_integrator.cpp",
        ],
        include_dirs=[
            "qss_integrator/src",
            pybind11.get_include(),
        ],
        cxx_std=17,
        define_macros=[('VERSION_INFO', '"dev"')],
    ),
]

setup(
    name="qss-integrator",
    packages=["qss_integrator"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.16.0",
    ],
)