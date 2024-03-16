import sys
from cx_Freeze import setup, Executable
import subprocess

sys.setrecursionlimit(100000000)

# PACKAGES = ['import_name', ('import_name', 'package_name')]
PACKAGES  = [
        "os",
        "sys",
        "copy",
        "time",
        "math",
        "datetime",
        "tkinter",
        ("PIL", "Image"),
        ("PIL", "ImageTk"),
        "yaml",
        "pandas",
        "schedule",
        ("multiprocessing", "Process"),
        ("multiprocessing", "Array"),
        ("multiprocessing", "Array"),
        "pygame",
        "vgamepad",
]
INCLUDE_PACKAGES = [pkg if type(pkg) == str else pkg[0] for pkg in PACKAGES]

installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
installed_packages = installed_packages.split('\r\n')
EXCLUDES_PACKAGES = {pkg.split('==')[0] for pkg in installed_packages if pkg != ''}

for pkg in PACKAGES:
    need_pkg = pkg if type(pkg) == str else pkg[1]
    if need_pkg in EXCLUDES_PACKAGES:
        EXCLUDES_PACKAGES.remove(need_pkg)

build_exe_options = {
    "packages": INCLUDE_PACKAGES,
    "excludes": EXCLUDES_PACKAGES,
    "include_files": [
        "image/",
    ],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gamepad Recorder",
    version="0.1",
    description="Record Gamepad Inputs and Replay Input as a Virtual Gamepad",
    options={
        "build_exe": build_exe_options,
    },
    executables=[
        Executable(
            script="gamepad_recorder.py",
            base=base,
        ),
    ],
)