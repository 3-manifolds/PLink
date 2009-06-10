#!/usr/bin/env python

# First, bootstrap setuptools

import ez_setup
ez_setup.use_setuptools()

# Now start the main part of setup.py

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

# Set the version

from plink.version import version

setup(name='plink',
      version= version,
      description='Link Projection Editor',
      author='Marc Culler and Nathan Dunfield',
      author_email='culler@math.uic.edu, nmd@illinois.edu',
      url='http://www.math.uic.edu/~t3m',
      packages=['plink'],
      package_data={'plink': doc_files},
      entry_points = {'console_scripts': ['plink = plink.app:main']},
      cmdclass =  {'clean' : clean},
     )

