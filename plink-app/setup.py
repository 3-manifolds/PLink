"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup, Command
import os

APP = ['PLink.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'plink.icns',
    'semi_standalone' : False,
    'packages' : 'plink',
    }

class clean(Command):
    user_options = []

    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
    
    def run(self):
        os.system("rm -rf build dist")
    
    
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    cmdclass   = {'clean' : clean},
)
