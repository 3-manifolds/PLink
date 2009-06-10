#! /usr/bin/env python
"""
This script builds everything, except the Windows binary, for the
PLink project.  It should be run under OS X with a Framework version
of Python 2.5 and Python 2.6 installed.
"""
import os, sys, re, glob

# We build the thing and install it twice to make sure the
# documentation is up to date.

def build_module_and_eggs():
    os.chdir("../")
    os.system("python2.6 setup.py clean")
    os.system("python2.6 setup.py install")
    os.chdir("doc-source")
    os.system("make install")
    os.chdir("../")
    os.system("python2.6 setup.py install")
    os.system("python2.5 setup.py install")

# Now build the .app

def build_app():
    os.chdir("plink-app")
    os.system("python2.6 setup.py clean py2app")
    # Make things a little smaller.
    os.system("rm -rf dist/PLink.app/Contents/Frameworks/Tcl.framework/Versions/8.4/Resources/English.lproj/ActiveTcl-8.4")
    os.system("rm -rf dist/PLink.app/Contents/Frameworks/Tk.framework/Versions/8.4/Resources/Scripts/demos")

def build_disk_image():
    os.chdir("dmg-maker")
    os.system("./dmg-maker.py")

# Now put it on the webpage:

def upload_files():
    user = os.environ['USER']
    if user in ['nmd', 'dunfield']:
        print "Hi there Nathan..."
        address = "t3m@shell.math.uic.edu"
    if user == 'culler':
        print "Hi there Marc..."
        address = "culler@shell.math.uic.edu"


    eggs = glob.glob("../../dist/plink-*.egg")
    os.system("scp PLink.dmg %s %s:~t3m/public_html/plink/" % (" ".join(eggs), address))
    os.system("ssh %s update_plink.py" % address)

if __name__ == "__main__":
    build_module_and_eggs()
    build_app()
    build_disk_image()
    upload_files()

