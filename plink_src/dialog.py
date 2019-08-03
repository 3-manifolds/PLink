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
from .gui import Tk_, ttk, SimpleDialog

if SimpleDialog:
    baseclass = SimpleDialog
else:
    baseclass = object

class InfoDialog(baseclass):
    def __init__(self, parent, title, style, content=''):
        self.parent, self.style, self.content = parent, style, content
        Tk_.Toplevel.__init__(self, parent)
        if title:
            self.title(title)
#        self.icon = PhotoImage(data=icon_string)
#        canvas = Tk_.Canvas(self, width=58, height=58)
#        canvas.create_image(10, 10, anchor=NW, image=self.icon)
#        canvas.grid(row=0, column=0, sticky=NSEWW)
        text = Tk_.Text(self, font=style.font, width=50, height=18, padx=10,
                            relief=Tk_.FLAT, background = style.windowBG,
                            highlightthickness=0)
        text.insert(Tk_.END, self.content)
        #Needed to make the text selectable on macOS
        text.focus_set()
        text.config(state=Tk_.DISABLED)
        text.grid(row=0, column=1, sticky=Tk_.N+Tk_.W, padx=10, pady=10)
        self.buttonbox()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.ok)
        self.focus_set()
        self.wait_window(self)

    def buttonbox(self):
        box = ttk.Frame(self)
        w = ttk.Button(box, text="OK", width=10, command=self.ok,
                   default=Tk_.ACTIVE)
        w.pack(side=Tk_.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.grid(row=1, columnspan=2)

    def ok(self, event=None):
        self.parent.focus_set()
        self.app = None
        self.destroy()
