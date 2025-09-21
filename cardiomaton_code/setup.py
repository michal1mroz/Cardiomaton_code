from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import pathlib

# Base source dir (relative to cardiomaton_code/)
src_dir = pathlib.Path(__file__).parent / "src"
backend_dir = src_dir / "backend"

# Collect all .pyx files recursively
pyx_files = [path for path in backend_dir.rglob("*.pyx")]

# Convert paths to fully qualified module names
extensions = []
for path in pyx_files:
    # e.g. src/backend/models/cell_state.pyx -> backend.models.cell_state
    module_path = path.relative_to(src_dir).with_suffix("")
    module_name = ".".join(module_path.parts)

    extensions.append(
        Extension(
            module_name,
            [str(path)],
        )
    )

extensions = cythonize(
    extensions,
    compiler_directives={"language_level": "3"},
)

setup(
    name="cardiomaton-code",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=extensions,
    zip_safe=False,
)