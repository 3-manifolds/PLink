# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
Imports objects and defines constants used in common by different
components of the graphical user interface for PLink.
""" 
import sys

try: 
    if sys.version_info[0] < 3:
        import Tkinter as Tk_
        import tkFileDialog
        import tkMessageBox
        import tkSimpleDialog
    else:
        import tkinter as Tk_
        import tkinter.filedialog as tkFileDialog
        import tkinter.messagebox as tkMessageBox
        import tkinter.simpledialog as tkSimpleDialog
    from . import canvasvg
except ImportError:  # Tk unavailable or misconfigured
    Tk_, tkFileDialog, tkMessageBox, tkSimpleDialog, canvasvg = None, None, None, None, None

try:
    from urllib import pathname2url
except:  # Python 3
    from urllib.request import pathname2url

try:
    import pyx
    have_pyx = True
except ImportError:
    have_pyx = False

if sys.platform == 'linux2':
    closed_hand_cursor = 'fleur'
    open_hand_cursor = 'hand1'
elif sys.platform == 'darwin':
    closed_hand_cursor = 'closedhand'
    open_hand_cursor = 'openhand'
else:
    closed_hand_cursor = 'hand2'
    open_hand_cursor = 'hand1'
    
# Make the Tk file dialog work better with file extensions on OX

def asksaveasfile(mode='w',**options):
    """
    Ask for a filename to save as, and returned the opened file.
    Modified from tkFileDialog to more intelligently handle
    default file extensions. 
    """
    if sys.platform == 'darwin':
        if 'defaultextension' in options and not 'initialfile' in options:
            options['initialfile'] = 'untitled' + options['defaultextension']

    return tkFileDialog.asksaveasfile(mode=mode, **options)

if sys.platform == 'linux2':
    def askopenfile():
        return tkFileDialog.askopenfile(
            mode='r',
            title='Open SnapPea Projection File')
else:
    def askopenfile():
        return tkFileDialog.askopenfile(
            mode='r',
            title='Open SnapPea Projection File',
            defaultextension = ".lnk",
            filetypes = [
                ("Link and text files", "*.lnk *.txt", "TEXT"),
                ("All text files", "", "TEXT"),
                ("All files", "")],
            )

# Keyboard shortcuts
scut = {
    'Left'   : '←',
    'Up'     : '↑',
    'Right'  : '→',
    'Down'   : '↓'}

# Shift vectors
canvas_shifts = {
    'Down'  : (0, 5),
    'Up'    : (0, -5),
    'Right' : (5, 0),
    'Left'  : (-5, 0)
    }
vertex_shifts = {
    'Down'  : (0, 1),
    'Up'    : (0, -1),
    'Right' : (1, 0),
    'Left'  : (-1, 0)
    }

