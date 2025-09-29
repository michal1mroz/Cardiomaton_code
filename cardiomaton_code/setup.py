from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize


extensions = [
        Extension("src.backend.models.c_cell", ["src/backend/models/c_cell.pyx"]),
        Extension("src.backend.models.cell_state", ["src/backend/models/cell_state.pyx"]),
        Extension("src.backend.models.cell_type", ["src/backend/models/cell_type.pyx"]),
        Extension("src.backend.models.cell", ["src/backend/models/cell.pyx"]),
        Extension("src.backend.models.automaton", ["src/backend/models/automaton.pyx"]),
        Extension("src.backend.utils.charge_update", ["src/backend/utils/charge_update.pyx"]),

    ]
extensions = cythonize(
    extensions,
    compiler_directives={"language_level": "3"},
)

setup(
    name="cardiomaton-code",
    packages=find_packages(where=""),
    package_dir={"": ""},
    ext_modules=extensions,
    zip_safe=False,
)