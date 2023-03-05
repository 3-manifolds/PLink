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
Imports objects and defines constants used in common by different
components of the graphical user interface for PLink.
"""
import sys, platform

try:
    import tkinter as Tk_
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    import tkinter.ttk as ttk
    from . import canvasvg
    from tkinter.simpledialog import Dialog as SimpleDialog
except ImportError:
    # Tk is unavailable or misconfigured.
    # This allows running tests when there is no tkinter module.
    print('Plink failed to import tkinter.')
    Tk_ = ttk = tkFileDialog = tkMessageBox = SimpleDialog = None

from urllib.request import pathname2url

try:
    import pyx
    have_pyx = True
except ImportError:
    have_pyx = False


if sys.platform == 'linux2' or sys.platform == 'linux':
    closed_hand_cursor = 'fleur'
    open_hand_cursor = 'hand1'
elif sys.platform == 'darwin':
    closed_hand_cursor = 'closedhand'
    open_hand_cursor = 'openhand'
else:
    closed_hand_cursor = 'hand2'
    open_hand_cursor = 'hand1'

class PLinkStyle:
    """
    Provide platform specific thematic constants for use by Tk widgets.
    NOTE: A Tk interpreter must be created before instantiating an
    object in this class.
    """
    def __init__(self):
        self.ttk_style = ttk_style = ttk.Style()
        self.windowBG = ttk_style.lookup('Tframe', 'background')
        if sys.platform == 'darwin':
            self.font = 'Helvetica 16'
        else:
            self.font = 'Helvetica 12'

# Make the Tk file dialog work better with file extensions on macOS

def asksaveasfile(mode='w',**options):
    """
    Ask for a filename to save as, and returned the opened file.
    Modified from tkFileDialog to more intelligently handle
    default file extensions.
    """
    if sys.platform == 'darwin':
        if platform.mac_ver()[0] < '10.15.2':
            options.pop('parent', None)
        if 'defaultextension' in options and not 'initialfile' in options:
            options['initialfile'] = 'untitled' + options['defaultextension']

    return tkFileDialog.asksaveasfile(mode=mode, **options)

if sys.platform == 'linux2':
    def askopenfile(parent=None):
        return tkFileDialog.askopenfile(
            parent=parent,
            mode='r',
            title='Open SnapPea Projection File')
else:
    def askopenfile(parent=None):
        if sys.platform == 'darwin' and platform.mac_ver()[0] < '10.15.2':
            parent=None
        return tkFileDialog.askopenfile(
            parent=parent,
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
