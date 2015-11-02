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
Tools for dealing with colors, including the class Palette.
"""
from colorsys import hls_to_rgb

class Palette:
    """
    Dispenses colors.
    """
    def __init__(self):
        self.colorizer = Colorizer()
        self.reset()

    def reset(self):
        self.free_colors = [self.colorizer(n) for n in range(6)]
        self.active_colors = []

    def new(self):
        if len(self.free_colors) == 0:
            for n in range(10):
                color = self.colorizer(len(self.active_colors))
                if color not in self.free_colors + self.active_colors:
                    self.free_colors.append(color)
        try:
            color = self.free_colors.pop(0)
            self.active_colors.append(color)
            return color
        except IndexError:
            self.active_colors.append('black')
            return 'black'

    def recycle(self, color):
        self.active_colors.remove(color)
        self.free_colors.append(color)

# Pure python version of the Colorizer class from snappy.CyOpenGL
class Colorizer:
    """
    Callable class which returns an RGB color string when passed an
    index.  Uses the same algorithm as the SnapPea kernel.
    """
    def __init__(self, lightness=0.5, saturation=0.7):
        self.base_hue = [0,4,2,3,5,1]
        self.lightness = lightness
        self.saturation = saturation

    def __call__(self, index):
        hue = (self.base_hue[index%6] + self.index_to_hue(index//6)) / 6.0
        rgb = hls_to_rgb(hue, self.lightness, self.saturation)  
        return '#%.2x%.2x%.2x'%tuple(int(x*255) for x in rgb)

    def index_to_hue(self, index):
        num, den= 0, 1
        while index:
            num = num<<1
            den = den<<1
            if index & 0x1:
                num += 1
            index = index>>1
        return float(num)/float(den)
