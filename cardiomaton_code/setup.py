from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import os

# Root path to source
src_path = os.path.join("src", "models")

# List of Cython extensions
extensions = [
    Extension(
        "models.cell_new",
        [os.path.join(src_path, "cell_new.pyx")],
        include_dirs=[numpy.get_include(), src_path],
    ),
    Extension(
        "models.automaton_new",
        [os.path.join(src_path, "automaton_new.pyx")],
        include_dirs=[numpy.get_include(), src_path],
    ),
]

setup(
    name="automaton_backend",
    package_dir={"": "src"},
    packages=[
        "src",
        "src.models",
        "src.utils",
        "src.frontend",
        "src.update_strategies",
    ],
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
        include_path=[
            "src/models",
        ],
    ),
    zip_safe=False,
)
