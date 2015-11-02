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
This module exports the class LinkViewer.  A LinkViewer object
creates a Tk window for viewing (not editing) a PL or smooth
link diagram.
"""
from .gui import *
from . import smooth
# -*- coding: utf-8 -*-

from .colors import Palette
from .manager import LinkManager

class LinkViewer(LinkManager):
    """
    Simply draws a smooth link diagram on a canvas.  Instantiate with
    a canvas and a pickled link diagram as returned by
    OrthogonalLinkDiagram.plink_data.
    """
    def __init__(self, canvas, data):
        self.initialize()
        self.canvas = canvas
        self.palette = Palette()
        self.smoother = smooth.Smoother(self.canvas)
        self.unpickle(*data)
        self.create_colors()

    def _zoom(self):
        W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
        # To avoid round-off artifacts, compute a floating point bbox
        x0, y0, x1, y1 = self._bbox()
        w, h = x1-x0, y1-y0
        factor = min( (W-40)/w, (H-40)/h )
        # Make sure we get an integer bbox after zooming
        xfactor, yfactor = round(factor*w)/w, round(factor*h)/h
        self.update_crosspoints()
        # Scale the picture, fixing the upper left corner
        for vertex in self.Vertices:
            vertex.x = x0 + xfactor*(vertex.x - x0)
            vertex.y = y0 + yfactor*(vertex.y - y0)
        # Shift into place
        self._shift( 20 - x0, 20 - y0)
        self.update_info()

    def _bbox(self):
        x0 = y0 = float('inf')
        x1 = y1 = float('-inf')
        for vertex in self.Vertices:
            x0, y0 = min(x0, vertex.x), min(y0, vertex.y)
            x1, y1 = max(x1, vertex.x), max(y1, vertex.y)
        return x0, y0, x1, y1

    def _shift(self, dx, dy):
        for vertex in self.Vertices:
            vertex.x += dx
            vertex.y += dy
        self.canvas.move(Tk_.ALL, dx, dy)

    def draw(self):
        # Fit to the canvas
        self._zoom()
        # Hide the polygon image
        for vertex in self.Vertices:
            vertex.hide()
        for arrow in self.Arrows: 
            arrow.hide()
        # draw the smooth image
        self.smoother.clear()
        self.smoother.set_polylines(self.polylines())

    def update_info(self):
        # subclasses can override this method.
        pass

    def save_image(self, file_type='eps', colormode='color', target=None):
        savefile = asksaveasfile(
            mode='w',
            title='Save As %s (%s)'% (file_type.upper(), colormode),
            defaultextension = "." + file_type)
        if savefile:
            file_name = savefile.name
            savefile.close()
            if target is None:
                target = self.smoother
            save_fn = getattr(target, 'save_as_' + file_type)
            save_fn(file_name, colormode)

    def save_as_eps(self, file_name, colormode):
        smooth.save_as_eps(self.canvas, file_name, colormode)

    def save_as_svg(self, file_name, colormode):
        smooth.save_as_svg(self.canvas, file_name, colormode)

    def save_as_pdf(self, file_name, colormode,  width=312.0):
        PDF = smooth.PDFPicture(self.canvas, width)
        for polylines, color in self.polylines(break_at_overcrossings=False):
            style = [pyx.style.linewidth(4), pyx.style.linecap.round,
                     pyx.style.linejoin.round, pyx.color.rgbfromhexstring(color)]
            for lines in polylines:
                lines = [PDF.transform(xy) for xy in lines]
                path_parts = [pyx.path.moveto(* lines[0])] + [pyx.path.lineto(*xy) for xy in lines]
                PDF.canvas.stroke(pyx.path.path(*path_parts), style)
        PDF.save(file_name)

    def build_save_image_menu(self, menubar, parent_menu):
        menu = self.save_image_menu = Tk_.Menu(menubar, tearoff=0)
        save = self.save_image
        for item_name, save_function in [
                ('PostScript (color)', lambda : save('eps', 'color')), 
                ('PostScript (grays)', lambda : save('eps', 'gray')),
                ('SVG', lambda : save('svg', 'color')),
                ('TikZ', lambda : save('tikz', 'color')),
                ('PDF', lambda : save('pdf', 'color'))]:
            menu.add_command(label=item_name, command=save_function)
        self.disable_fancy_save_images()
        self.enable_fancy_save_images()
        parent_menu.add_cascade(label='Save Image...', menu=menu)

    def disable_fancy_save_images(self):
        for i in [3,4]:
            self.save_image_menu.entryconfig(i, state='disabled')

    def enable_fancy_save_images(self):
        fancy = [3,4] if have_pyx else [3]
        for i in fancy:
            self.save_image_menu.entryconfig(i, state='active')

