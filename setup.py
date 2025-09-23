from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import os

# Root path to source
src_path = os.path.join("cardiomaton_code", "src", "models")

# List of Cython extensions
extensions = [
    Extension(
        "src.models.cell_new",
        [os.path.join(src_path, "cell_new.pyx")],
        include_dirs=[numpy.get_include(), src_path],
    ),
    Extension(
        "src.models.automaton_new",
        [os.path.join(src_path, "automaton_new.pyx")],
        include_dirs=[numpy.get_include(), src_path],
    ),
]

setup(
    name="automaton_backend",
    package_dir={"": "cardiomaton_code"},
    packages=[
        "cardiomaton_code",
        "cardiomaton_code.src",
        "cardiomaton_code.src.models",
        "cardiomaton_code.src.utils",
        "cardiomaton_code.src.frontend",
        "cardiomaton_code.src.update_strategies",
    ],
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
        include_path=[
            "cardiomaton_code/src",
            "cardiomaton_code/src/models",
        ],
    ),
    zip_safe=False,
)
