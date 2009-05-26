#! /usr/bin/env python

import os, sys, re

# We build the thing twice to make sure the documentation is up to
# date.

os.chdir("../")
os.system("python setup.py install")
os.chdir("doc-source")
os.system("make install")
os.chdir("../")
os.system("python setup.py install")
os.chdir("plink-app")
os.system("python setup.py clean py2app")
os.chdir("dmg-maker")
os.system("dmg-maker.py")
os.system("scp PLink.dmg t3m@shell.math.uic.edu:public_html/")
