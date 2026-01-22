import PyInstaller.__main__
import customtkinter
import os
import sys

# Get the location of customtkinter to include its assets (json themes, etc.)
ctk_path = os.path.dirname(customtkinter.__file__)

print(f"Building executable with CustomTkinter from: {ctk_path}")

# arguments for pyinstaller
args = [
    'main.py',
    '--name=CompilationSimulator',
    '--onefile',
    '--noconsole',
    f'--add-data={ctk_path};customtkinter/',  # Windows uses ; for separator
    '--icon=app_icon.ico',
    '--clean',
    '--hidden-import=pkg_resources.extern', # Sometimes needed
]

# Run PyInstaller
PyInstaller.__main__.run(args)
