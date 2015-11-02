from setuptools import setup, Command
from pkg_resources import load_entry_point
import os

pjoin = os.path.join
src = 'plink_src'
doc_path = pjoin(src, 'doc')

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

# Building the documentation

class build_docs(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        sphinx_cmd = load_entry_point('Sphinx>=0.6.1', 'console_scripts', 'sphinx-build')
        sphinx_args = ['sphinx', '-a', '-E', '-d', 'doc_source/_build/doctrees',
                       'doc_source', doc_path]
        sphinx_cmd(sphinx_args)

# We need to collect the names of the Sphinx-generated documentation files to add

doc_files = [pjoin('doc', file) for file in os.listdir(doc_path) if file[0] != "_"]
for dir_name in [file for file in os.listdir(doc_path) if file[0] == "_"]:
    doc_files += [pjoin('doc', dir_name, file) for file in os.listdir(pjoin(src, 'doc', dir_name))]

# Get version number.
exec(open('plink_src/version.py').read())

# Get long description from README
long_description = open('README').read().split('License')[0]

setup(name='plink',
      version=version,
      packages=['plink'],
      package_dir = {'plink': src}, 
      package_data={'plink': doc_files},
      entry_points = {'console_scripts': ['plink = plink.app:main']},
      cmdclass =  {'clean': clean, 'build_docs': build_docs},
      zip_safe = False,

      description='A full featured Tk-based knot and link editor', 
      long_description = long_description,
      author = 'Marc Culler and Nathan M. Dunfield',
      author_email = 'culler@uic.edu, nathan@dunfield.info',
      license='GPLv2+',
      url = 'http://www.math.uic.edu/t3m/plink/doc/',
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
        keywords = 'knot, link, editor, SnapPy',
     )
