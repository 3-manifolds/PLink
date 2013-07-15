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
# This module exports the class SmoothLink which displays a smoothed
# PLink in a separate window.
#
# Cubic splines are used to draw each arc joining two crossings in the
# link diagram.  The segments of the PLink are subdivided by
# introducing vertices at all crossings and the splines are chosen to
# interpolate the midpoints of all subdivision segments, except those
# emanating from a crossing, in such a way that the smooth arc is
# tangent to the segment at the midpoint.  The bezier arc are drawn with
# a gap near the crossing to indicate which strand goes under.
#
# The speeds at the midpoint are chosen using Hobby's algorithm from:
#   * Hobby, John D., "Smooth, easy to compute interpolating splines,"
#     Discrete and Computational Geometry 1:123-140 (1986).
#

try:
    import Tkinter as Tk_
except ImportError: # Python 3
    import tkinter as Tk_
from math import sqrt, cos, sin, atan2, pi

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
    the PL path determined by specifying a list of vertices.  Speeds
    at the nodes are chosen by using Hobby's scheme.
    """
    def __init__(self, points, color='black', tension1=1.0, tension2=1.0):
        self.points = P = [TwoVector(*p) for p in points]
        self.tension1, self.tension2 = tension1, tension2
        self.color = color
        self.tk_line = None
        self.spline_knots =  (
            [P[0]] +
            [0.5*(P[k] + P[k+1]) for k in xrange(1, len(P)-1)] +
            [P[-1]])
        self.tangents = [(P[k+1] - P[k]).unit()
                         for k in xrange(len(P)-1)]

    def _polar_to_vector(self, r, phi):
        """
        Return a TwoVector with specified length and angle.
        """
        return TwoVector(r*cos(phi), r*sin(phi))

    def _control_points(self, k):
        """
        Compute the two control points for a nice cubic curve from the
        kth spline knot to the next one.  Return the first knot and the
        two control points.  We do not allow the speeds to exceed the
        distance from the midpoint to the vertex.
        """
        p1, p2 = self.spline_knots[k:k+2]
        v = self.points[k+1]
        speed1_max = abs(v-p1)
        speed2_max = abs(v-p2)
        u1, u2 = self.tangents[k:k+2]
        base = p2 - p1
        l, psi = abs(base), base.angle()
        theta, phi = u1.angle() - psi, psi - u2.angle()
        ctheta, stheta = self._polar_to_vector(1.0, theta)
        cphi, sphi = self._polar_to_vector(1.0, phi)
        a = sqrt(2.0)
        b = 1.0/16.0
        c = (3.0 - sqrt(5.0))/2.0
        alpha = a*(stheta - b*sphi) * (sphi - b*stheta) * (ctheta - cphi)
        rho = (2 + alpha) / ((1 + (1-c)*ctheta + c*cphi) * self.tension1 )
        sigma = (2 - alpha) / ((1 + (1-c)*cphi + c*ctheta) * self.tension2 )
        speed1 = min(l*rho/3, speed1_max)
        speed2 = min(l*sigma/3, speed2_max)
        return [p1, 
                p1 + self._polar_to_vector(speed1, psi+theta),
                p2 - self._polar_to_vector(speed2, psi-phi)]

    def bezier(self):
        """
        Return a list of spline knots and control points for the Bezier
        spline, in format [ ... Knot, Control, Control, Knot ...]
        """
        path = []
        if len(self.spline_knots) == 2:
            A, B = self.spline_knots
            M = 0.5*(A+B)
            return [A, M, M, B]
        for k in xrange(len(self.spline_knots)-2 ):
            path += self._control_points(k)
        path.append(self.spline_knots[-1])
        return path

    def tk_draw(self, canvas):
        XY = self.bezier()
        self.tk_line = canvas.create_line(*XY, smooth='raw', width=5,
                                fill=self.color, splinesteps=100)

    def pyx_draw(self, canvas):
        import pyx
        XY = self.bezier()
        arc_parts = [pyx.path.moveto(XY[0][0], -XY[0][1])]
        for i in range(1, len(XY), 3):
            arc_parts.append(pyx.path.curveto(
                XY[i][0], -XY[i][1], XY[i+1][0], -XY[i+1][1], XY[i+2][0], -XY[i+2][1]))

        style = [pyx.style.linewidth(4), pyx.style.linecap.round,
                 pyx.color.rgbfromhexstring(self.color)]
        path = pyx.path.path(*arc_parts)
        canvas.stroke(path, style)
        
class SmoothLoop(SmoothArc):
    """
    A Bezier spline that is tangent at the midpoints of segments in a
    PL loop determined by specifying a list of vertices.  Speeds at
    the nodes are chosen by using Hobby's scheme.
    """    
    def __init__(self, points, color='black', tension1=1.0, tension2=1.0):
        if points[0] != points[-1]:
            points = points[:] +[points[0]]
        points = points[:] +[points[1]]
        self.points = P = [TwoVector(*p) for p in points]
        self.tension1, self.tension2 = tension1, tension2
        self.color = color
        self.tk_line = None
        self.spline_knots = [0.5*(P[k] + P[k+1]) for k in xrange(len(P)-1)]
        self.spline_knots.append(self.spline_knots[0])
        self.tangents = [(P[k+1] - P[k]).unit()
                         for k in xrange(len(P)-1)]
   
class SmoothLink:
    """
    A Tk window that displays a smooth link image inscribed in a PLink.
    """
    def __init__(self, polylines, width=500, height=500,
                 tension1=1.0, tension2=1.0):
        self.polylines = polylines
        self.tension1 = tension1
        self.tension2 = tension2
        self.window = window = Tk_.Toplevel()
        self.window.title('PLink smoother')
        top_frame = Tk_.Frame(window)
        self.t_scale = Tk_.Scale(top_frame, from_=0.0, to=2.0,
                                 resolution=0.01,
                                 orient=Tk_.HORIZONTAL,
                                 length=300,
                                 command=self.set_tension1)
        self.t_scale.set(tension1)
        Tk_.Label(top_frame, text='tension1:').grid(
            row=0, column=0, sticky=Tk_.SE)
        self.t_scale.grid(row=0, column=1)
        self.s_scale = Tk_.Scale(top_frame, from_=0.0, to=2.0,
                                 resolution=0.01,
                                 orient=Tk_.HORIZONTAL,
                                 length=300,
                                 command=self.set_tension2)
        self.s_scale.set(tension2)
        Tk_.Label(top_frame, text='tension2:').grid(
            row=1, column=0, sticky=Tk_.SE)
        self.s_scale.grid(row=1, column=1)
        top_frame.pack(expand=True, fill=Tk_.X)
        self.canvas = Tk_.Canvas(self.window, width=width, height=height,
                             background='white')
        self.canvas.pack(expand=True, fill=Tk_.BOTH)
        self.curves = []
        self.draw()

    def set_tension1(self, value):
        self.tension1 = float(value)
        self.draw()

    def set_tension2(self, value):
        self.tension2 = float(value)
        self.draw()

    def draw(self):
        # Clear existing curves in case we've changed the tensions.
        for curve in self.curves:
            if curve.tk_line:
                self.canvas.delete(curve.tk_line)
        self.curves = []
      
        for polyline, color in self.polylines:
            if len(polyline) == 1 and polyline[0][0] == polyline[0][-1]:
                L = SmoothLoop(polyline[0], color, self.tension1, self.tension2)
                self.curves.append(L)
            else:
                for arc in polyline:
                    A = SmoothArc(arc, color, self.tension1, self.tension2)
                    self.curves.append(A)

        for curve in self.curves:
            curve.tk_draw(self.canvas)
        
    def save(self, file_name):
        import pyx
        pyx.unit.set(defaultunit='pt')
        canvas = pyx.canvas.canvas()
        for curve in self.curves:
            curve.pyx_draw(canvas)
        canvas.writePDFfile(file_name)
