# -*- coding: utf-8 -*-
#
#   Copyright (C) 2007-present Marc Culler, Nathan Dunfield and others.
#
#   This program is distributed under the terms of the
#   GNU General Public License, version 2 or later, as published by
#   the Free Software Foundation.  See the file gpl-2.0.txt for details.
#   The URL for this program is
#     http://www.math.uic.edu/~t3m/plink
#   A copy of the license file may be found at:
#     http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#
#   The development of this program was partially supported by
#   the National Science Foundation under grants DMS0608567,
#   DMS0504975 and DMS0204142.
"""
This module exports a subclass IPythonTkRoot of tkinter.Tk that
warns its user to type %gui Tk if it instantiates itself in an IPython
shell which does not have a running Tk event loop.
"""
import time, threading
from tkinter import Tk

try:
    import IPython
    # This will not be None if we are runnning in an IPython shell.
    ip = IPython.get_ipython()
except:
    ip = None

class IPythonTkRoot(Tk):
    """
    A Tk root window intended for use in an IPython shell.

    Because of the way that IPython overloads the Python inputhook, it
    is necessary to start a Tk event loop by running the magic command
    %gui tk in order for Tk windows to actually appear on the screen.
    An IPythonRoot detects whether there is a Tk event loop
    running and, if not, reminds the user to type %gui tk.
    """

    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        self.message = (
            '\x1b[31mYour new {} window needs an event loop to become visible.\n'
            'Type "%gui tk" below (without the quotes) to start one.\x1b[0m\n'
        ).format(self.winfo_class())
        self._have_loop = False
        self._check_for_tk()

    def _tk_check(self):
        """Thread target function."""
        time.sleep(0.5)
        if not self._have_loop:
            if IPython.version_info < (6,):
                print('\n' + self.message[:-1])
            else:
                print(self.message)

    def _check_for_tk(self):
        def set_flag():
            self._have_loop = True
        if ip:
            # Tk will set the flag if it is has an event loop.
            self.after(100, set_flag)
            # This thread will notice if the flag did not get set.
            threading.Thread(target=self._tk_check).start()

