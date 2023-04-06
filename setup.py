#######################################################################
#
#  See setup.cfg for most of the settings, this is just some custom
#  commands related to the Sphinx docs and previous versions of our
#  build system.
#
#######################################################################


from setuptools import setup, Command
from pkg_resources import load_entry_point
from wheel.bdist_wheel import bdist_wheel
import os, re, shutil, subprocess, sys, glob

doc_path = 'plink_src/doc'

# A real clean

class PLinkClean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        for dir in ['build', 'dist', 'plink.egg-info', '__pycache__', doc_path]:
            shutil.rmtree(dir, ignore_errors=True)
        os.mkdir(doc_path)
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
        sphinx_cmd = load_entry_point('sphinx>=1.7', 'console_scripts', 'sphinx-build')
        sphinx_args = ['-a', '-E', '-d', 'doc_source/_build/doctrees',
                       'doc_source', 'plink_src/doc']
        sphinx_cmd(sphinx_args)


def check_call(args):
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError:
        executable = args[0]
        command = [a for a in args if not a.startswith('-')][-1]
        raise RuntimeError(command + ' failed for ' + executable)

class PlinkBuildWheel(bdist_wheel):
    def run(self):
        python = sys.executable
        check_call([python, 'setup.py', 'build'])
        check_call([python, 'setup.py', 'build_docs'])
        check_call([python, 'setup.py', 'build'])
        bdist_wheel.run(self)

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
        check_call([pythons[0], 'setup.py', 'bdist_wheel'])

class PLinkPipInstall(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        python = sys.executable
        check_call([python, 'setup.py', 'bdist_wheel'])
        egginfo = 'plink.egg-info'
        if os.path.exists(egginfo):
            shutil.rmtree(egginfo)
        wheels = glob.glob('dist' + os.sep + '*.whl')
        new_wheel = max(wheels, key=os.path.getmtime)
        check_call([python, '-m', 'pip', 'uninstall', '-y', 'plink'])
        check_call([python, '-m', 'pip', 'install',
                    '--upgrade-strategy', 'only-if-needed',
                    new_wheel])


setup(cmdclass={'clean': PLinkClean,
                'build_docs': PLinkBuildDocs,
                'bdist_wheel': PlinkBuildWheel,
                'pip_install':PLinkPipInstall})
