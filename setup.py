#!/usr/bin/env python

from setuptools import setup, Command
import os


# A real clean

class clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system("rm -rf build dist *.pyc")
        os.system("rm -rf plink*.egg-info")

# We need to collect the names of the Sphinx-generated documentation files to add

pjoin = os.path.join
doc_path = pjoin('plink', 'doc')
doc_files = [pjoin('doc', file) for file in os.listdir(doc_path) if file[0] != "_"]
for dir_name in [file for file in os.listdir(doc_path) if file[0] == "_"]:
    doc_files += [pjoin('doc', dir_name, file) for file in os.listdir(pjoin('plink', 'doc', dir_name))]

# Get version number:

exec(open('plink/version.py').read())

setup(name='plink',
      version=version,
      summary='Link Projection Editor',
      description='A full featured Tk-based knot and link editor', 
      author='Marc Culler and Nathan Dunfield',
      author_email='culler@math.uic.edu, nmd@illinois.edu',
      url='http://www.math.uic.edu/~t3m',
      packages=['plink'],
      package_data={'plink': doc_files},
      entry_points = {'console_scripts': ['plink = plink.app:main']},
      cmdclass =  {'clean' : clean},
      license = 'GPL v2+',
      keywords = 'knot link editor',
      platform = 'Linux, OS X, other Unixes, Windows', 
      zip_safe = False, 
     )

with open('version.txt', 'w') as output:
    output.write(version)
