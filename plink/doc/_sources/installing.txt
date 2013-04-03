.. Installing PLink 

Installing and running PLink
======================================================

Mac OS X
---------------

Simply download `PLink.dmg <http://math.uic.edu/t3m/plink/PLink.dmg>`_
and copy PLink.app to the Applications folder.  Double-click to start
it, just like any other application.

Windows
-------------------

To be improved, but for now the following works: Install `Python
<http://python.org>`_, and then get the source code below and expand
it.  Then double-click the file::

  plink\plink\__init__.py

Linux and other Unixes
-------------------------------------------------------

You will need to have Python (> 2.4), Tk (>= 8.4), and Tkinter
installed to run plink; for instance, if you are using Debian or
Ubuntu, just install the package "python-tk".

If you have root privileges and `setuptools
<http://peak.telecommunity.com/DevCenter/setuptools>`_ installed (the
Linux package is usually called "python-setuptools"), simply do::

  sudo python -m easy_install -f http://math.uic.edu/t3m/plink plink

This installs a shell-command called "plink" which starts PLink.  

If you don't have root privileges, download the source-code below and do::

  tar xfz plink.tar.gz
  cd plink
  python -m plink.app

to start PLink.  

Source code
-----------------------------------

The complete source code for all platforms: `plink.tar.gz <http://math.uic.edu/t3m/plink.tar.gz>`_   

You can also get it straight from the `Mercurial
<http://www.selenic.com/mercurial>`_ repository::

  hg clone static-http://math.uic.edu/t3m/hg/plink





