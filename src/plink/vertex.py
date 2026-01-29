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
This module exports the class Vertex which represents an endpoint
of a segment in a PL link diagram.
"""

class Vertex:
    """
    A vertex in a PL link diagram.
    """
    epsilon = 8
    scale_factor = 1
    
    @classmethod
    def set_scale(cls, factor):
        cls.scale_factor = factor
        cls.epsilon = 8 * factor

    def __init__(self, x, y, canvas=None, style='normal', color='black'):
        self.x, self.y = float(x), float(y)
        self.in_arrows = []
        self.out_arrows = []
        self.canvas = canvas
        self.color = color
        self.delta = 2
        self.dot = None
        self.style = style

    def __repr__(self):
        return '(%s,%s)'%(self.x, self.y)

    def __eq__(self, other):
        """
        Vertices are equivalent if they are sufficiently close.
        Use the "is" operator to test if they are identical.
        """
        return abs(self.x - other.x) + abs(self.y - other.y) < Vertex.epsilon
    
    def __hash__(self):
        # Since we redefined __eq__ we need to define __hash__
        return id(self)

    def hide(self):
        self.canvas.delete(self.dot)
        self.style = 'hidden'

    @property
    def hidden(self):
        return self.style == 'hidden'
    
    def freeze(self):
        self.style = 'frozen'
    
    @property
    def valence(self):
        return len(self.in_arrows) + len(self.out_arrows)
    
    @property
    def frozen(self):
        return self.style == 'frozen'

    def make_faint(self):
        self.style = 'faint'

    def expose(self, crossings=[]):
        self.style = 'normal'
        self.draw()

    def point(self):
        return self.x, self.y

    def draw(self, skip_frozen=False):
        if self.hidden or (self.frozen and skip_frozen):
            return
        if self.style != 'normal':
            color = 'gray'
        else:
            color = self.color
        delta = self.delta
        x, y = self.point()
        if self.dot:
            self.canvas.delete(self.dot)
        self.dot = self.canvas.create_oval(x-delta , y-delta, x+delta, y+delta,
                                           outline=color,
                                           fill=color,
                                           tags='transformable')
    def set_color(self, color):
        self.color = color
        self.canvas.itemconfig(self.dot, fill=color, outline=color)

    def set_delta(self, delta):
        self.delta = delta
        self.draw()
        
    @property
    def is_endpoint(self):
        return self.valence == 1

    @property
    def is_smooth(self):
        return len(self.in_arrows) == 1 and len(self.out_arrows) == 1

    @property
    def is_isolated(self):
        return self.valence == 0

    def reverse(self):
        self.in_arrows, self.out_arrows = self.out_arrows, self.in_arrows

    def swallow(self, other, palette):
        """
        Join two paths.  Self and other must be endpoints. Other is erased.
        """
        if not self.is_endpoint() or not other.is_endpoint():
            raise ValueError
        if self.in_arrows:
            if other.in_arrows:
                other.reverse_filament()
            if self.color != other.color:
                palette.recycle(self.color)
                self.color = other.color
                self.recolor_incoming(color=other.color)
            self.out_arrows = other.out_arrows
            for arrow in self.out_arrows:
                arrow.set_start(self)
        elif self.out_arrows:
            if other.out_arrows:
                other.reverse_filament()
            if self.color != other.color:
                palette.recycle(other.color)
                other.recolor_incoming(color=self.color)
            self.in_arrows = other.in_arrows
            self.in_arrows[0].set_end(self)
        other.erase()
            
    def reverse_filaments(self, crossings=[]):
        """
        Reverse the arc filaments emanating from this vertex.
        """
        v = self
        for e in v.out_arrows:
            while True:
                e.reverse(crossings)
                v = e.end
                if v == self:
                    return
                if v.valence > 2:
                    break
        self.reverse()
        v = self
        for e in v.out_arrows:
            while True:
                e.reverse(crossings)
                v = e.start
                if v == self:
                    return
                if v.valence > 2:
                    break

    def recolor_incoming(self, palette=None, color=None):
        """
        If this vertex lies in a non-closed filament, recolor its incoming
        filaments.  The old color is not freed.  This vertex is NOT recolored. 
        """
        if not color:
            color = palette.new()
        #print(color)
        v = self
        for e in v.in_arrows:
            while True:
                e.set_color(color)
                v = e.start
                if v == self:
                    return
                if v.valence > 2:
                    break
        
    def update_arrows(self):
        for arrow in self.in_arrows + self.out_arrows:
            arrow.vectorize()

    def erase(self):
        """
        Prepare the vertex for the garbage collector.
        """
        self.in_arrows = []
        self.out_arrows = []
        self.hide()
