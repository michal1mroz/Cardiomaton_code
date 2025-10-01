from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import pathlib

src_dir = pathlib.Path(__file__).parent

pyx_files = [path for path in src_dir.rglob("*.pyx")]
extensions = []
for path in pyx_files:
    module_path = path.relative_to(src_dir)
    module_name = ".".join(module_path.with_suffix("").parts)

    extensions.append(
        Extension(
            module_name,
            [module_path]
        )
    )

# extensions = [
#         Extension("src.backend.models.c_cell", ["src/backend/models/c_cell.pyx"]),
#         Extension("src.backend.models.cell_state", ["src/backend/models/cell_state.pyx"]),
#         Extension("src.backend.models.cell_type", ["src/backend/models/cell_type.pyx"]),
#         Extension("src.backend.models.automaton", ["src/backend/models/automaton.pyx"]),
#         Extension("src.backend.utils.charge_update", ["src/backend/utils/charge_update.pyx"]),

#     ]
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