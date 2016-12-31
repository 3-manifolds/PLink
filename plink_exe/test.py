#! /usr/bin/env python

import os
os.system('rm -rf build dist')
os.system('pyinstaller PLink.spec')
os.system('start dist/PLink/PLink.exe')
