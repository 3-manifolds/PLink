#!/usr/bin/env python

from distutils.core import setup
from distutils.command.install_data import install_data

class my_install_data(install_data):
    """
    Put the data in the package directory, where we can find it.
    """
    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )
setup(name='plink',
      version='1.0',
      description='Link Projection Editor',
      author='Marc Culler',
      author_email='culler@math.uic.edu',
      url='http://www.math.uic.edu/~t3m',
      cmdclass = {"install_data" : my_install_data},
      packages=['plink'],
      data_files=[('plink',['plink_howto.html'])],
      package_data={'plink': ['plink_howto.html']},
      scripts=['bin/plink']
     )

