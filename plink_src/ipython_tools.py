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

It also exports a function which will issue an equivalent warning.
"""
import time
import threading
try:
    from tkinter import Tk
except ImportError:
    class Tk:
        pass

try:
    import IPython
    # This will not be None if we are running in an IPython shell.
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
        window_type = kwargs.pop('window_type', '')
        Tk.__init__(self, **kwargs)
        self.message = (
            '\x1b[31mYour new {} window needs an event loop to become visible.\n'
            'Type "%gui tk" below (without the quotes) to start one.\x1b[0m\n'
        ).format(window_type if window_type else self.winfo_class())
        if ip and IPython.version_info < (6,):
            self.message = '\n' + self.message[:-1]
        self._have_loop = False
        self._check_for_tk()

    def _tk_check(self):
        for n in range(4):
            time.sleep(0.25)
            if self._have_loop:
                return
        print(self.message)

    def _check_for_tk(self):
        def set_flag():
            self._have_loop = True
        if ip:
            # Tk will set the flag if it is has an event loop.
            self.after(10, set_flag)
            # This thread will notice if the flag does not get set.
            threading.Thread(target=self._tk_check).start()


def warn_if_necessary(tk_window, window_type=''):
    """
    When running within IPython, this function checks to see if a Tk event
    loop exists and, if not, tells the user how to start one.
    """
    try:
        import IPython
        ip = IPython.get_ipython()
        tk_window._have_loop = False

        def set_flag():
            tk_window._have_loop = True

        def tk_check():
            message = (
                '\x1b[31mYour new {} window needs an event loop to become visible.\n'
                'Type "%gui tk" below (without the quotes) to start one.\x1b[0m\n'
            ).format(window_type if window_type else tk_window.winfo_class())
            if IPython.version_info < (6,):
                message = '\n' + message[:-1]
            for n in range(4):
                time.sleep(0.25)
                if tk_window._have_loop:
                    return
            print(message)

        # Tk will set the flag if it is has an event loop.
        tk_window.after(10, set_flag)
        # This thread will notice if the flag did not get set.
        threading.Thread(target=tk_check).start()

    except ImportError:
        pass
