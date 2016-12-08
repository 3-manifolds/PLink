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
This module exports the InfoDialog class, used for displaying information
about the PLink program.
"""
# Hack for when Tkinter is unavailable or broken
from .gui import *

if tkSimpleDialog:
    baseclass = tkSimpleDialog.Dialog
else:
    baseclass = object
    
class InfoDialog(baseclass):
    def __init__(self, parent, title, content=''):
        self.parent = parent
        self.content = content
        Tk_.Toplevel.__init__(self, parent)
        NW = Tk_.N+Tk_.W
        if title:
            self.title(title)
#        self.icon = PhotoImage(data=icon_string)
        canvas = Tk_.Canvas(self, width=58, height=58)
#        canvas.create_image(10, 10, anchor=NW, image=self.icon)
        canvas.grid(row=0, column=0, sticky=NW)
        text = Tk_.Text(self, font='Helvetica 14',
                    width=50, height=16, padx=10)
        text.insert(Tk_.END, self.content)
        text.grid(row=0, column=1, sticky=NW,
                  padx=10, pady=10)
        text.config(state=Tk_.DISABLED)
        self.buttonbox()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.ok)
        self.focus_set()
        self.wait_window(self)

    def buttonbox(self):
        box = Tk_.Frame(self)
        w = Tk_.Button(box, text="OK", width=10, command=self.ok,
                   default=Tk_.ACTIVE)
        w.pack(side=Tk_.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.grid(row=1, columnspan=2)

    def ok(self, event=None):
        self.parent.focus_set()
        self.app = None
        self.destroy()


