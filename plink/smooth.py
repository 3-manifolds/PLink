#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (C) 2007-2013 Marc Culler, Nathan Dunfield and others.
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
# PLink in a separate window.
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
#   * Hobby, John D., "Smooth, easy to compute interpolating splines,"
#     Discrete and Computational Geometry 1:123-140 (1986).
#

try:
    import Tkinter as Tk_
except ImportError: # Python 3
    import tkinter as Tk_

try:
    import pyx
except ImportError:
    pass

from math import sqrt, cos, sin, atan2, pi
from . import canvasvg

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

    def _extend(self, other):
        if ( self.color != other.color or
             self.spline_knots[-1] != other.spline_knots[0] or
             abs(self.tangents[-1].unit()-other.tangents[0].unit())>.000001):
            raise ValueError('Splines do not match.')
        self.spline_knots += other.spline_knots[1:]
        self.tangents = self.tangents[:-1] + other.tangents
        self.vertices += other.vertices[1:]

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
            
    def tk_draw(self, thickness=5):
        XY = self.bezier()
        self.tk_clear()
        self.canvas_items.append(self.canvas.create_line(
            *XY, smooth='raw', width=thickness, fill=self.color,
             splinesteps=100, tags='smooth'))

    def pyx_draw(self, canvas):
        XY = self.bezier()
        arc_parts = [pyx.path.moveto(XY[0][0], -XY[0][1])]
        for i in xrange(1, len(XY), 3):
            arc_parts.append(pyx.path.curveto(
                    XY[i][0], -XY[i][1], XY[i+1][0],
                    -XY[i+1][1], XY[i+2][0], -XY[i+2][1]))
            style = [pyx.style.linewidth(4), pyx.style.linecap.round,
                     pyx.color.rgbfromhexstring(self.color)]
            path = pyx.path.path(*arc_parts)
            canvas.stroke(path, style)
        
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

    def _extend(self, other):
        raise RuntimeError('SmoothLoops are not extendable.')

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
                    try: # join arcs at overcrossings
                        curves[-1]._extend(A)
                    except (IndexError, ValueError):
                        curves.append(A)
            self.polygons.append(polygon)
            if len(curves) - n > 1:
                try: # join the first to the last if possible
                    curves[-1]._extend(self.curves[n])
                    curves.pop(n)
                except ValueError:
                    pass

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
        Save the link diagram as an encapsulated postscript file.
        Accepts options colormode and width.
        The colormode must be 'color', 'gray', or 'mono'; default is 'color'.
        The width option sets the width of the figure in points.
        The default width is 312pt = 4.33in = 11cm .
        """
        ulx, uly, lrx, lry = self.canvas.bbox(Tk_.ALL)
        scale = float(width)/(lrx - ulx)
        pyx.unit.set(uscale=scale, wscale=scale, defaultunit='pt')
        # Currently ignoring colormode
        canvas = pyx.canvas.canvas()
        for curve in self.curves:
            curve.pyx_draw(canvas)
        canvas.writePDFfile(file_name)

    def save_as_eps(self, file_name, colormode='color', width=312.0):
        """
        Save the link diagram as an encapsulated postscript file.
        Accepts options colormode and width.
        The colormode must be 'color', 'gray', or 'mono'; default is 'color'.
        The width option sets the width of the figure in points.
        The default width is 312pt = 4.33in = 11cm .
        """
        ulx, uly, lrx, lry = self.canvas.bbox(Tk_.ALL)
        self.canvas.postscript(file=file_name, x=ulx, y=uly,
                               width=lrx-ulx, height=lry-uly,
                               colormode=colormode,
                               pagewidth=width)

    def save_as_svg(self, file_name, colormode='color', width=None):
        """
        Save the link diagram as an encapsulated postscript file.
        Accepts options colormode and width.
        The colormode must be 'color', 'gray', or 'mono'; default is 'color'.
        The width option is ignored for svg images.
        """
        # Currently ignoring colormode
        canvasvg.saveall(
            file_name, self.canvas,
            items=self.canvas.find_withtag('smooth'))
