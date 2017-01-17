from setuptools import setup, Command
from pkg_resources import load_entry_point
import os, re, site, shutil, subprocess, sys, sysconfig
from glob import glob
from distutils.command.build import build

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
        junkdirs = (glob('build/lib*') + glob('build/bdist*') + glob('plink*.egg-info') +
                    ['__pycache__', doc_path])
        for dir in junkdirs:
            try:
                shutil.rmtree(dir)
            except OSError:
                pass
        junkfiles = glob('*/*.pyc') 
        for file in junkfiles:
            try:
                os.remove(file)
            except OSError:
                pass

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
        
class PLinkBuild(build):
    def run(self, *args, **kwargs):
        subprocess.call(['python', 'setup.py', 'build_docs'])
        build.run(self)

if sys.platform == 'win32':
    pythons = [
        r'C:\Python27\python.exe',
        r'C:\Python27-x64\python.exe',
# Appveyor has these:
#        r'C:\Python34\python.exe',
#        r'C:\Python34-x64\python.exe',
#        r'C:\Python35\python.exe',
#        r'C:\Python35-x64\python.exe',
#        r'C:\Python36\python.exe',
#        r'C:\Python36-x64\python.exe',
        ]
elif sys.platform == 'darwin':
    pythons = [
        'python2.7',
        'python3.4',
        'python3.5',
        'python3.6',
        ]
elif site.__file__.startswith('/opt/python/cp'):
    pythons = [
        'python2.7',
        'python3.4',
        'python3.5',
        'python3.6',
        ]
else:
    pythons = [
        'python2.7',
        'python3.5'
    ]

class PLinkRelease(Command):
    # The -rX option modifies the wheel name by adding rcX to the version string.
    # This is for uploading to testpypi, which will not allow uploading two
    # wheels with the same name.
    user_options = [('rctag=', 'r', 'index for rc tag to be appended to version (e.g. -r2 -> rc2)')]
    def initialize_options(self):
        self.rctag = None
    def finalize_options(self):
        if self.rctag:
            self.rctag = 'rc%s'%self.rctag
    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        for python in pythons:
            try:
                subprocess.check_call([python, 'setup.py', 'build'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Build failed for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'build_docs'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Failed to build documentation for %s.'%python)
                sys.exit(1)
            try:
                subprocess.check_call([python, 'setup.py', 'bdist_wheel'])
            except subprocess.CalledProcessError:
                raise RuntimeError('Error building wheel for %s.'%python)
        if self.rctag:
            version_tag = re.compile('-([^-]*)-')
            for wheel_name in [name for name in os.listdir('dist') if name.endswith('.whl')]:
                new_name = wheel_name
                new_name = version_tag.sub('-\g<1>%s-'%self.rctag, new_name, 1)
                os.rename(os.path.join('dist', wheel_name), os.path.join('dist', new_name))

        try:
            subprocess.check_call(['python', 'setup.py', 'sdist'])
        except subprocess.CalledProcessError:
            raise RuntimeError('Error building sdist archive for %s.'%python)
        sdist_version = re.compile('-([^-]*)(.tar.gz)|-([^-]*)(.zip)')
        for archive_name in [name for name in os.listdir('dist')
                             if name.endswith('tar.gz') or name.endswith('.zip')]:
            if self.rctag:
                new_name = sdist_version.sub('-\g<1>%s\g<2>'%self.rctag, archive_name, 1)
                os.rename(os.path.join('dist', archive_name), os.path.join('dist', new_name))

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
      entry_points = {'console_scripts': ['plink = plink.app:main']},
      cmdclass =  {'clean': PLinkClean,
                   'build_docs': PLinkBuildDocs,
                   'build': PLinkBuild,
                   'release': PLinkRelease},
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
