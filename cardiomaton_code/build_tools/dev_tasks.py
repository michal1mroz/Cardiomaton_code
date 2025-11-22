import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"

def clean():
    """
    Remove build artifacts: .c/.so/.pyd files, build/, dist/, *.egg-info
    """
    for d in ["build", "dist"]:
        shutil.rmtree(ROOT / d, ignore_errors=True)

    for egg in ROOT.glob("*.egg-info"):
        shutil.rmtree(egg, ignore_errors=True)

    for ext in ("*.c", "*.so", "*.pyd"):
        for f in SRC_DIR.rglob(ext):
            try:
                f.unlink()
            except Exception as e:
                print(f"Could not remove {f}: {e}", file=sys.stderr)

    print("✨ Cleaned build artifacts.")

def build():
    """
    Compile all Cython modules in src/ using setup.py build_ext --inplace
    """
    try:
        import Cython  
    except ImportError:
        print("Cython not installed. Please run: poetry add --dev cython", file=sys.stderr)
        sys.exit(1)

    subprocess.check_call([sys.executable, "setup.py", "build_ext", "--inplace"], cwd=ROOT)
    print("🚀 Built Cython extensions.")