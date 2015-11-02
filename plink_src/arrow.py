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
This module exports the class Arrow which represents a (directed)
line segment in a PL link diagram.
"""
from math import sqrt
from gui import *
default_gap_size = 9.0

class Arrow:
    """
    An arrow in a PL link diagram.
    """
    epsilon = 8
    
    def __init__(self, start, end, canvas=None, style='normal', color='black'):
        self.start, self.end = start, end
        self.canvas = canvas
        self.color = color
        self.component = None
        self.style = 'normal'
        self.lines = []
        self.dots = []
        self.cross_params = []
        if self.start != self.end:
            self.start.out_arrow = self
            self.end.in_arrow = self
            self.vectorize()
        
    def __repr__(self):
        return '%s-->%s'%(self.start, self.end)

    def __xor__(self, other):
        """
        Returns the barycentric coordinate at which self crosses other.
        """
        D = other.dx*self.dy - self.dx*other.dy
        if D == 0:
            return None
        xx = other.start.x - self.start.x
        yy = other.start.y - self.start.y
        s = (yy*self.dx - xx*self.dy)/D
        t = (yy*other.dx - xx*other.dy)/D
        if 0 < s < 1 and 0 < t < 1:
            return t
        else:
            return None

    def vectorize(self):
        self.dx = float(self.end.x - self.start.x)
        self.dy = float(self.end.y - self.start.y)
        self.length = sqrt(self.dx*self.dx + self.dy*self.dy) 

    def reverse(self, crossings=[]):
        self.end, self.start = self.start, self.end
        self.vectorize()
        self.draw(crossings)

    def hide(self):
        for line in self.lines:
            self.canvas.delete(line)
            self.style = 'hidden'

    @property
    def hidden(self):
        return self.style == 'hidden'

    def freeze(self):
        for line in self.lines:
            self.canvas.itemconfig(line, fill='gray')
        self.style = 'frozen'

    @property
    def frozen(self):
        return self.style == 'frozen'

    def make_faint(self):
        for line in self.lines:
            self.canvas.itemconfig(line, fill='gray', width=1)
        self.style = 'faint'

    def expose(self, crossings=[]):
        self.style = 'normal'
        self.draw(crossings)

    def find_segments(self, crossings, include_overcrossings=False,
                      gapsize=default_gap_size):
        """
        Return a list of segments that make up this arrow, each
        segment being a list of 4 coordinates [x0,y0,x1,y1].  The
        first segment starts at the start vertex, and the last one
        ends at the end vertex.  Otherwise, endpoints are near
        crossings where this arrow goes under, leaving a gap between
        the endpoint and the crossing point.  If the
        include_overcrossings flag is True, then the segments are
        also split at overcrossings, with no gap.
        """
        segments = []
        self.vectorize()
        cross_params = [(0.0,False), (1.0,False)]
        for c in crossings:
            if c.under == self:
                t = self ^ c.over
                if t:
                    cross_params.append((t, not c.is_virtual))
            if c.over == self and include_overcrossings:
                t = self ^ c.under
                if t:
                    cross_params.append((t, False))
        cross_params.sort()
        
        def r(t):
            "Affine parameterization of the arrow with domain [0,1]."
            if t == 1.0:
                return list(self.end.point())
            x, y = self.start.point()
            return [x + t*self.dx, y + t*self.dy]

        def gap(dt):
            "A suitable gap for r restricted to a subinterval of length dt"
            return min(gapsize/self.length, 0.2*dt)

        segments = []
        for i in range(len(cross_params)-1):
            a, has_gap_a = cross_params[i]
            b, has_gap_b = cross_params[i+1]
            gap_a = gap(b-a) if has_gap_a else 0
            gap_b = gap(b-a) if has_gap_b else 0
            segments.append( (a + gap_a, b - gap_b) )
        return [r(a) + r(b) for a, b in segments]

    def draw(self, crossings=[], recurse=True, skip_frozen=True):
        if self.hidden or (self.frozen and skip_frozen):
            return
        if self.style == 'frozen':
            color = 'gray'
            thickness = 3
        elif self.style == 'faint':
            color = 'gray'
            thickness = 1
        else:
            color = self.color
            thickness = 3
        segments = self.find_segments(crossings)
        for line in self.lines:
            self.canvas.delete(line)
        for dot in self.dots:
            self.canvas.delete(dot)
        for x0, y0, x1, y1 in segments[:-1]:
            self.lines.append(self.canvas.create_line(
                    x0, y0, x1, y1,
                    width=thickness, fill=color, tags='transformable'))
        x0, y0, x1, y1 = segments[-1]
        self.lines.append(self.canvas.create_line(
                x0, y0, x1, y1,
                arrow=Tk_.LAST,
                width=thickness, fill=color, tags='transformable'))
        if recurse:
            under_arrows = [c.under for c in crossings if c.over == self]
            for arrow in under_arrows:
                arrow.draw(crossings, recurse=False)
        for c in crossings:
            if self == c.under and c.is_virtual:
                self.dots.append(self.canvas.create_oval(
                        c.x-5, c.y-5, c.x+5, c.y+5,
                        fill='black', outline='black',
                        tags=('dot', 'transformable')))
        self.canvas.tag_raise('dot', Tk_.ALL)
    
    def set_start(self, vertex, crossings=[]):
        self.start = vertex
        if self.end:
            self.vectorize()
            self.draw(crossings)

    def set_end(self, vertex, crossings=[]):
        self.end = vertex
        if self.start:
            self.vectorize()
            self.draw(crossings)

    def set_color(self, color):
        self.color = color
        for line in self.lines:
            self.canvas.itemconfig(line, fill=color)
            
    def erase(self):
        """
        Prepare the arrow for the garbage collector.
        """
        self.start = None
        self.end = None
        self.hide()

    def too_close(self, vertex, tolerance=None):
        if vertex == self.start or vertex == self.end:
            return False
        e = tolerance if tolerance else Arrow.epsilon
        Dx = vertex.x - self.start.x
        Dy = vertex.y - self.start.y
        A = (Dx*self.dx + Dy*self.dy)/self.length
        B = (Dy*self.dx - Dx*self.dy)/self.length
        return (-e < A < self.length + e and -e < B < e)

