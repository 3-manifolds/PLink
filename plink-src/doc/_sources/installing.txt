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

Install `Python <http://python.org>`_ and use `pip
<https://pip.pypa.io/en/latest/>`_ (included in recent versions) to
get plink.  For example::

  pip install plink
  python -m plink.app

-------------------------------------------------------

You will need to have Python (> 2.4), Tk (>= 8.4), and Tkinter
installed to run plink; for instance, if you are using Debian or
Ubuntu, just install the package "python-tk".

If you have root privileges and `pip <https://pip.pypa.io/en/latest/>`_, simply do::

  pip install plink

This installs a shell-command called "plink" which starts PLink.  

If you don't have root privileges, add the "--user" flag to the end of
the above install command.  You can then run plink via::

  python -m plink.app


Source code
-----------------------------------

You can download and browse the source code
`here <https://bitbucket.org/t3m/plink>`_.
