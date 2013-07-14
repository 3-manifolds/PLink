"""
Comparing the two methods for chosing the velocites.  To using interactively in a Sage notebook, do:

@interact
def _(x=(0.5, (-0.7, 1.7)), y=(0.3, (0,1.5)), t=(0.6,(0,1))):
    draw_bezier_possibilities(x, y, t).show()

or

@interact
def _(x=(0.5, (-0.7, 1.7)), y=(0.3, (0,1.5)), t=(0.1,(0,0.3))):
    subproblem.draw_better_bezier_possibilities(x, y, t).show()

"""

import math
from sage.all import *

def good_bezier(p1, angle1, angle2, p2, tension1=1.0, tension2=1.0):
    """
    Compute a nice curve from p1 to p2 with specified tangents
    """
    def polar(r, phi):
        return vector(RR, [r*cos(phi), r*sin(phi)])

    def to_polar((x,y)):
        r = sqrt(x**2+y**2)
        phi = 0 if r == 0 else RR(math.atan2(y,x))
        return r, phi
    
    l, psi = to_polar(p2-p1)
    ctheta, stheta = polar(1.0, angle1-psi)
    cphi,   sphi   = polar(1.0, psi-angle2)
    a = sqrt(2.0)
    b = 1.0/16.0
    c = (3.0 - sqrt(5.0))/2.0
    alpha = a*(stheta - b*sphi) * (sphi - b*stheta) * (ctheta - cphi)
    rho = (2 + alpha) / (1 + (1-c)*ctheta + c*cphi) / tension1
    sigma = (2 - alpha) / (1 + (1-c)*cphi + c*ctheta) / tension2
    return (p1 + polar(l*rho/3, angle1), p2 - polar(l*sigma/3, angle2))

def great_bezier(p1, angle1, angle2, p2, min_gap, apex):
    """
    Compute a nice curve from p1 to p2 with specified tangents
    """
    def polar(r, phi):
        return vector(RR, [r*cos(phi), r*sin(phi)])

    def to_polar((x,y)):
        r = sqrt(x**2+y**2)
        phi = 0 if r == 0 else RR(math.atan2(y,x))
        return r, phi
    
    l, psi = to_polar(p2-p1)
    ctheta, stheta = polar(1.0, angle1-psi)
    cphi,   sphi   = polar(1.0, psi-angle2)
    a = sqrt(2.0)
    b = 1.0/16.0
    c = (3.0 - sqrt(5.0))/2.0
    alpha = a*(stheta - b*sphi) * (sphi - b*stheta) * (ctheta - cphi)
    rho = (2 + alpha) / (1 + (1-c)*ctheta + c*cphi) 
    sigma = (2 - alpha) / (1 + (1-c)*cphi + c*ctheta)

    def normalize_velocity(proposed, side_length):
        ans = min(proposed, side_length*(1 - min_gap))
        return max(side_length*min_gap, ans)

    v1 = normalize_velocity(l*rho/3, norm(p1 - apex))
    v2 = normalize_velocity(l*sigma/3, norm(p2 - apex))
    
    return (p1 + polar(v1, angle1), p2 - polar(v2, angle2))

def great_bezier2(p1, angle1, angle2, p2, min_gap, apex):
    """
    Compute a nice curve from p1 to p2 with specified tangents
    """
    def polar(r, phi):
        return vector(RR, [r*cos(phi), r*sin(phi)])

    def to_polar((x,y)):
        r = sqrt(x**2+y**2)
        phi = 0 if r == 0 else RR(math.atan2(y,x))
        return r, phi
    
    l, psi = to_polar(p2-p1)
    ctheta, stheta = polar(1.0, angle1-psi)
    cphi,   sphi   = polar(1.0, psi-angle2)
    a = sqrt(2.0)
    b = 1.0/16.0
    c = (3.0 - sqrt(5.0))/2.0
    alpha = a*(stheta - b*sphi) * (sphi - b*stheta) * (ctheta - cphi)
    rho = (2 + alpha) / (1 + (1-c)*ctheta + c*cphi) 
    sigma = (2 - alpha) / (1 + (1-c)*cphi + c*ctheta)

    v1, v2 = l*rho/3, l*sigma/3
    tension = max( [1.0, v1/norm(p1-apex), v2/norm(p2-apex)] )
    v1, v2 = v1/tension, v2/tension
    
    return (p1 + polar(v1, angle1), p2 - polar(v2, angle2))

def angle(v):
    return math.atan2(v[1], v[0])

def draw_bezier_possibilities(x, y, tightness=0.6):
    V = VectorSpace(RR, 2)
    a, b, c = V( (0,0) ), V( (x,y) ), V( (1,0) )
    G = line( [a, b, c], color='grey', linestyle='--')
    G += point( [a, b, c], color='grey', size=20)

    t = tightness
    culler =  [t*b + (1-t)*a, t*b + (1-t)*c]
    u, v = b - a, b - c
    hobby = good_bezier(a, angle(u), angle(-v), c)

    for (c0, c1), color in [(culler, 'red'), (hobby, 'blue')]:
        G += bezier_path([[a, c0, c1, c]], color=color, thickness=1.5)
        G += point([c0,c1], color=color, size=30)
    
    G.set_aspect_ratio(1.0)
    G.axes(False)
    G.set_axes_range(-0.7, 1.7, -0.2, 1.5)
    return G

def draw_better_bezier_possibilities(x, y, min_gap):
    V = VectorSpace(RR, 2)
    a, b, c = V( (0,0) ), V( (x,y) ), V( (1,0) )
    G = line( [a, b, c], color='grey', linestyle='--')
    G += point( [a, b, c], color='grey', size=20)

    u, v = b - a, b - c
    hobby = good_bezier(a, angle(u), angle(-v), c)
    capped = great_bezier(a, angle(u), angle(-v), c, min_gap, b)
    alt_capped = great_bezier2(a, angle(u), angle(-v), c, min_gap, b)
    
    for (c0, c1), color in [(capped, 'red'), (alt_capped, 'green'), (hobby, 'blue')]:
        G += bezier_path([[a, c0, c1, c]], color=color, thickness=1.5)
        G += point([c0,c1], color=color, size=30)
    
    G.set_aspect_ratio(1.0)
    G.axes(False)
    G.set_axes_range(-0.7, 1.7, -0.2, 1.5)
    return G
    
