from setuptools import setup, Command
from pkg_resources import load_entry_point
import os, re, site, shutil, subprocess, sys, sysconfig, glob

pjoin = os.path.join
src = 'plink_src'
doc_path = pjoin(src, 'doc')

# A real clean

class PLinkClean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        for dir in ['build', 'dist', 'plink.egg-info']:
            shutil.rmtree(dir, ignore_errors=True)
        for file in glob.glob('*.pyc'):
            if os.path.exists(file):
                os.remove(file)

# Building the documentation

class PLinkBuildDocs(Command):
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

class PLinkBuildAll(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        python = sys.executable
        subprocess.call([python, 'setup.py', 'build'])
        build_lib_dir = os.path.join('build','lib')
        subprocess.call([python, 'setup.py', 'build_docs'])
        subprocess.call([python, 'setup.py', 'build'])

def check_call(args):
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError:
        executable = args[0]
        command = [a for a in args if not a.startswith('-')][-1]
        raise RuntimeError(command + ' failed for ' + executable)

class PLinkRelease(Command):
    user_options = [('install', 'i', 'install the release into each Python')]
    def initialize_options(self):
        self.install = False
    def finalize_options(self):
        pass
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')

        pythons = os.environ.get('RELEASE_PYTHONS', sys.executable).split(',')
        for python in pythons:
            check_call([python, 'setup.py', 'build_all'])
            if self.install:
                check_call([python, 'setup.py', 'pip_install'])

        # Build sdist/universal wheels using the *first* specified Python
        check_call([pythons[0], 'setup.py', 'sdist'])
        check_call([pythons[0], 'setup.py', 'bdist_wheel', '--universal'])

class PLinkPipInstall(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        python = sys.executable
        check_call([python, 'setup.py', 'bdist_wheel', '--universal'])
        egginfo = 'plink.egg-info'
        if os.path.exists(egginfo):
            shutil.rmtree(egginfo)
        wheels = glob.glob('dist' + os.sep + '*.whl')
        new_wheel = max(wheels, key=os.path.getmtime)            
        check_call([python, '-m', 'pip', 'install', '--upgrade',
                    '--upgrade-strategy', 'only-if-needed',
                    new_wheel])

# We need to collect the names of the Sphinx-generated documentation files to add

if not os.path.exists(doc_path):
    os.mkdir(doc_path)
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
      install_requires=['future'],
      entry_points = {'console_scripts': ['plink = plink.app:main']},
      cmdclass =  {'clean': PLinkClean,
                   'build_docs': PLinkBuildDocs,
                   'build_all': PLinkBuildAll,
                   'release': PLinkRelease,
                   'pip_install':PLinkPipInstall,
      },
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
