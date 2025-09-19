from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
from setuptools import setup


ext_modules = [
    Pybind11Extension(
        "bigwig_io",
        sources=[
            "bigwig_io/python_binding.cpp",
        ],
        include_dirs=[
            "bigwig_io/",
            pybind11.get_include(),
        ],
        libraries=["curl", "z"],
        language="c++",
        cxx_std=17,
    ),
]


setup(
    name="bigwig_io",
    version="0.0.1",
    author="Arthur Gouhier",
    author_email='ajgouhier@gmail.com',
    license="MIT",
    description="Read and write bigwig/bigbed files",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "pybind11",
    ],
)
