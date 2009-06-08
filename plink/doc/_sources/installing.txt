.. Installing PLink 

Installing and running PLink
======================================================

Mac OS X:
---------------

Simply download `PLink.dmg <http://math.uic.edu/~t3m/plink/PLink.dmg>`_
and copy PLink.app to the Applications folder.  Double-click to start
it, just like any other application.

Windows:
-------------------


Linux and other Unixes
-------------------------------------------------------

You will need to have Python (> 2.4), Tk (>= 8.4), and Tkinter
installed to run plink; for instance, if you are using Debian or
Ubuntu, install the package "python-tk".

If you have root privileges and `distutils
<http://peak.telecommunity.com/DevCenter/setuptools>`_ installed (the
Linux package is usually called "python-setuptools") and simply do::

  sudo easy_install plink

This installs a shell-command called "plink" which starts PLink.  

If you don't have root privileges, download the source-code below and do::

  tar xfz PLink.tar.gz
  cd PLink
  python -m plink.app

to start PLink.  

Source code
-----------------------------------

The complete source code for all platforms: `plink.tar.gz <http://math.uic.edu/~t3m/plink/plink.tar.gz>`_ 



