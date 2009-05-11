#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install_data import install_data
import os

# We need to collect the names of the Sphinx-generated documenation files to add

pjoin = os.path.join
doc_path = pjoin('plink', 'doc')
doc_files = [pjoin('doc', file) for file in os.listdir(doc_path) if file[0] != "_"]
for dir_name in [file for file in os.listdir(doc_path) if file[0] == "_"]:
    doc_files += [pjoin('doc', dir_name, file) for file in os.listdir(pjoin('plink', 'doc', dir_name))]


setup(name='plink',
      version='1.0',
      description='Link Projection Editor',
      author='Marc Culler',
      author_email='culler@math.uic.edu',
      url='http://www.math.uic.edu/~t3m',
      packages=['plink'],
      package_data={'plink': doc_files},
      scripts=['bin/plink']
     )

