from cx_Freeze import setup, Executable
import sys

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [Executable("main.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "Robo Consulta TRT2",
    options = options,
    version = "1.0",
    description = '',
    executables = executables
)