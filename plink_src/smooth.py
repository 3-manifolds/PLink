#!/usr/bin/env python
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
#
#                 ##############################
#
# This module exports the class Smoother which displays a smoothed
# PLink on a canvas.
#
# Cubic splines are used to draw each arc joining two crossings in the
# PL link diagram.  The segments of the PLink are subdivided by
# introducing vertices at all crossings. The spline knots are chosen
# to lie at overcrossings, near undercrossings, and at the midpoint of
# each PL segment which does not emanate from a crossing.  The spline
# is tangent to the PL link at each knot.  Consecutive splines are
# joined together at the overcrossing points so that the tangents at
# overcrossings can be adjusted together, e.g. in an SVG editor.  Thus
# the spline curves correspond to the arcs used in a Wirtinger
# presentation.  Endpoints of the splines occur near undercrossing
# points, leaving a small gap to indicate the undercrossing in the
# usual way.
#
# The speeds at the spline knots are chosen using Hobby's algorithm from:
#
#   * Hobby, John D., "Smooth, easy to compute interpolating splines,"
#     Discrete and Computational Geometry 1:123-140 (1986).
#
# with caps on the velocities to remove some unnecessary inflection points.

import sys

try: 
    if sys.version_info[0] < 3:
        import Tkinter as Tk_
    else:
        import tkinter as Tk_
    from . import canvasvg
except ImportError:  # Tk unavailable or misconfigured
    Tk_, canvasvg= None, None

try:
    import pyx
except ImportError:
    pass

from math import sqrt, cos, sin, atan2, pi


def in_twos(L):
    assert len(L) % 2 == 0
    return [L[i:i+2] for i in range(0, len(L), 2)]        

class TwoVector(tuple):
    def __new__(cls, x, y):
        return tuple.__new__(cls, (x,y))

    def __add__(self, other):
        return TwoVector(self[0]+other[0], self[1]+other[1])

    def __sub__(self, other):
        return TwoVector(self[0]-other[0], self[1]-other[1])

    def __rmul__(self, scalar):
        return TwoVector(scalar*self[0], scalar*self[1])

    def __xor__(self, other):
        return self[0]*other[1] - self[1]*other[0]

    def __abs__(self):
        return sqrt(self[0]*self[0]+self[1]*self[1])

    def angle(self):
        return atan2(self[1], self[0])

    def unit(self):
        return (1/abs(self))*self

class SmoothArc:
    """
    A Bezier spline that is tangent at the midpoints of segments in
    the PL path given by specifying a list of vertices.  Speeds
    at the spline knots are chosen by using Hobby's scheme.
    """
    def __init__(self, canvas, vertices, color='black',
                 tension1=1.0, tension2=1.0):
        self.canvas = canvas
        self.vertices = V = [TwoVector(*p) for p in vertices]
        self.tension1, self.tension2 = tension1, tension2
        self.color = color
        self.canvas_items = []
        self.spline_knots = K = (
            [ V[0] ] +
            [ 0.5*(V[k] + V[k+1]) for k in xrange(1, len(V)-2) ] +
            [ V[-1] ] )
        self.tangents = (
            [ V[1]-K[0] ] +
            [ V[k+1]-K[k] for k in xrange(1, len(V)-2) ] +
            [ V[-1]-V[-2] ])
        assert len(self.spline_knots) == len(self.tangents)

    def _polar_to_vector(self, r, phi):
        """
        Return a TwoVector with specified length and angle.
        """
        return TwoVector(r*cos(phi), r*sin(phi))

    def _curve_to(self, k):
        """
        Compute the two control points for a nice cubic curve from the
        kth spline knot to the next one.  Return the kth spline knot
        and the two control points.  We do not allow the speed at the
        spline knots to exceed the distance to the interlacing vertex
        of the PL curve; this avoids extraneous inflection points.
        """
        A, B = self.spline_knots[k:k+2]
        vA, vB = self.tangents[k:k+2]
        A_speed_max, B_speed_max = abs(vA), abs(vB)
        base = B - A
        l, psi = abs(base), base.angle()
        theta, phi = vA.angle() - psi, psi - vB.angle()
        ctheta, stheta = cos(theta), sin(theta)
        cphi, sphi = cos(phi), sin(phi)
        a = sqrt(2.0)
        b = 1.0/16.0
        c = (3.0 - sqrt(5.0))/2.0
        alpha = a*(stheta - b*sphi) * (sphi - b*stheta) * (ctheta - cphi)
        rho = (2 + alpha) / ((1 + (1-c)*ctheta + c*cphi) * self.tension1 )
        sigma = (2 - alpha) / ((1 + (1-c)*cphi + c*ctheta) * self.tension2 )
        A_speed = min(l*rho/3, A_speed_max)
        B_speed = min(l*sigma/3, B_speed_max)
        return [ A,
                 A + self._polar_to_vector(A_speed, psi+theta),
                 B - self._polar_to_vector(B_speed, psi-phi) ]

    def bezier(self):
        """
        Return a list of spline knots and control points for the Bezier
        spline, in format [ ... Knot, Control, Control, Knot ...]
        """
        path = []
        for k in xrange(len(self.spline_knots)-1):
            path += self._curve_to(k)
        path.append(self.spline_knots[-1])
        return path

    def tk_clear(self):
        for item in self.canvas_items:
            self.canvas.delete(item)
            
    def tk_draw(self, thickness=4):
        XY = self.bezier()
        self.tk_clear()
        self.canvas_items.append(self.canvas.create_line(
            *XY, smooth='raw', width=thickness, fill=self.color,
             capstyle=Tk_.ROUND, splinesteps=100,
             tags=('smooth','transformable')))

    def pyx_draw(self, canvas, transform):
        XY = [transform(xy) for xy in self.bezier()]
        arc_parts = [pyx.path.moveto(*XY[0])]
        for i in xrange(1, len(XY), 3):
            arc_parts.append(pyx.path.curveto(XY[i][0], XY[i][1],
                XY[i+1][0], XY[i+1][1], XY[i+2][0], XY[i+2][1]))
            style = [pyx.style.linewidth(4), pyx.style.linecap.round,
                     pyx.color.rgbfromhexstring(self.color)]
            path = pyx.path.path(*arc_parts)
            canvas.stroke(path, style)

    def tikz_draw(self, file, transform):
        points = ['(%.2f, %.2f)' % transform(xy) for xy in self.bezier()]
        file.write(self.color, '    \\draw %s .. controls %s and %s .. ' % tuple(points[:3]))
        for i in range(3, len(points) - 3, 3):
            file.write(self.color, '\n' + 10*' ' + '%s .. controls %s and %s .. ' % tuple(points[i:i+3]))
        file.write(self.color, points[-1] + ';\n')
        
class SmoothLoop(SmoothArc):
    """
    A Bezier spline that is tangent at the midpoints of segments in a
    PL loop given by specifying a list of vertices.  Speeds at
    the spline knots are chosen by using Hobby's scheme.
    """    
    def __init__(self, canvas, vertices, color='black',
                 tension1=1.0, tension2=1.0):
        self.canvas = canvas
        if vertices[0] != vertices[-1]:
            vertices.append(vertices[0])
        vertices.append(vertices[1])
        self.vertices = V = [TwoVector(*p) for p in vertices]
        self.tension1, self.tension2 = tension1, tension2
        self.color = color
        self.canvas_items = []
        self.spline_knots = [0.5*(V[k] + V[k+1]) for k in xrange(len(V)-1)]
        self.spline_knots.append(self.spline_knots[0])
        self.tangents = [(V[k+1] - V[k]) for k in xrange(len(V)-1)]
        self.tangents.append(self.tangents[0])
        assert len(self.spline_knots) == len(self.tangents)

class Smoother:
    """
    An object that displays a smooth link image on a Tk canvas.
    """
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas_items = []
        self.curves = []

    def _build_curves(self):
        self.curves = curves = []
        self.polygons = []
        for polyline, color in self.polylines:
            n = len(curves)
            polygon = []
            for arc in polyline:
                polygon += arc[1:-1]
                if arc[0] == arc[-1]:
                    A = SmoothLoop(self.canvas, arc, color,
                        tension1=self.tension1, tension2=self.tension2)
                    curves.append(A)
                else:
                    A = SmoothArc(self.canvas, arc, color,
                        tension1=self.tension1, tension2=self.tension2)
                    curves.append(A)
            self.polygons.append(polygon)

    def set_polylines(self, polylines, thickness=5,
                      tension1=1.0, tension2=1.0):
        self.clear()
        self.polylines = polylines
        self.vertices = []
        self.tension1 = tension1
        self.tension2 = tension2
        self._build_curves()
        self.draw(thickness=thickness)

    def draw(self, thickness=5):
        for curve in self.curves:
            curve.tk_draw(thickness=thickness)

    def clear(self):
        for curve in self.curves:
            curve.tk_clear()
        
    def save_as_pdf(self, file_name, colormode='color', width=312.0):
        """
        Save the smooth link diagram as a PDF file.
        Accepts options colormode and width.
        The colormode (currently ignored) must be 'color', 'gray', or 'mono'; default is 'color'.
        The width option sets the width of the figure in points.
        The default width is 312pt = 4.33in = 11cm .
        """
        PDF = PDFPicture(self.canvas, width)
        for curve in self.curves:
            curve.pyx_draw(PDF.canvas, PDF.transform)
        PDF.save(file_name)
      
    def save_as_eps(self, file_name, colormode='color', width=312.0):
        """
        Save the link diagram as an encapsulated postscript file.
        Accepts options colormode and width.
        The colormode must be 'color', 'gray', or 'mono'; default is 'color'.
        The width option sets the width of the figure in points.
        The default width is 312pt = 4.33in = 11cm .
        """
        save_as_eps(self.canvas, file_name, colormode, width)

    def save_as_svg(self, file_name, colormode='color', width=None):
        """
        The colormode (currently ignored) must be 'color', 'gray', or 'mono'.
        The width option is ignored for svg images.
        """
        save_as_svg(self.canvas, file_name, colormode, width)

    def save_as_tikz(self, file_name, colormode='color', width=282.0):
        colors = [pl[-1] for pl in self.polylines]
        tikz = TikZPicture(self.canvas, colors, width)
        for curve in self.curves:
            curve.tikz_draw(tikz, tikz.transform)
        tikz.save(file_name)



#----- Code for saving various file types ------

def save_as_eps(canvas, file_name, colormode='color', width=312.0):
    """
    The colormode must be 'color', 'gray', or 'mono'; default is 'color'.
    The width option sets the width of the figure in points.  The
    default width is 312pt = 4.33in = 11cm .
    """
    ulx, uly, lrx, lry = canvas.bbox(Tk_.ALL)
    canvas.postscript(file=file_name, x=ulx, y=uly, width=lrx-ulx, height=lry-uly,
                               colormode=colormode, pagewidth=width)
    
    
def save_as_svg(canvas, file_name, colormode='color', width=None):
    """
    Width is ignored for SVG images; colormode is currently ignored.
    """
    canvasvg.saveall(file_name, canvas, items=canvas.find_withtag(Tk_.ALL))

class PDFPicture:
    def __init__(self, canvas, width):
        ulx, uly, lrx, lry = canvas.bbox(Tk_.ALL)        
        scale = float(width)/(lrx - ulx)
        pyx.unit.set(uscale=scale, wscale=scale, defaultunit='pt')
        self.transform = lambda xy: (xy[0]-ulx,-xy[1]+lry)
        self.canvas = pyx.canvas.canvas()

    def save(self, file_name):
        page = pyx.document.page(self.canvas,  bboxenlarge=3.5* pyx.unit.t_pt)
        doc = pyx.document.document([page])
        doc.writePDFfile(file_name)

class TikZPicture:
    def __init__(self, canvas, raw_colors, width=282.0):
        self.string = ''
        ulx, uly, lrx, lry = canvas.bbox(Tk_.ALL)
        pt_scale = float(width)/(lrx - ulx)
        cm_scale = 0.0352777778*pt_scale
        self.transform = lambda xy: (cm_scale*(-ulx+xy[0]), cm_scale*(lry-xy[1]))

        self.colors = dict()
        for i, hex_color in enumerate(raw_colors):
            self.colors[hex_color] = i
            rgb = [int(c,16)/255.0 for c in in_twos(hex_color[1:])]
            self.string += '\\definecolor{linkcolor%d}' % i + '{rgb}{%.2f, %.2f, %.2f}\n' % tuple(rgb)
        self.string += '\\begin{tikzpicture}[line width=%.1f, line cap=round, line join=round]\n' % (pt_scale*4)
        self.curcolor = None

    def write(self, color, line):
        if color != self.curcolor:
            if self.curcolor is not None:
                self.string += '  \\end{scope}\n'
            self.string += '  \\begin{scope}[color=linkcolor%d]\n' % self.colors[color]
            self.curcolor = color
        self.string += line
        
    def save(self, file_name):
        file = open(file_name, 'w')
        file.write(self.string + '  \\end{scope}\n\\end{tikzpicture}\n')
        file.close()
    
