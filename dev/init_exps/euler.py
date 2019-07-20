from spiro_curves.clothoid import solve_clothoid
from spiro_curves.cornu import eval_cornu
import math
from sage.all import *

def transformation(p0, p1, q0, q1):
    """
    Return the similarity sending (p0, p1) -> (q0, q1)
    """
    R = matrix([(0, -1), (1, 0)])
    u, v = p1 - p0, q1 - q0
    A = matrix([u, R*u]).transpose()
    B = matrix([v, R*v]).transpose()
    C = B*A.inverse()
    d = -C*p0 + q0
    def T(x):
        return C*vector(x) + d
    return T


a0, a1 = vector( (0,0) ), vector( (1, 0))

def scaled_cornu(theta0, theta1, q0=a0, q1=a1):
    k0, k1 = solve_clothoid(theta0, theta1)
    sqrk1 = sqrt(2 * abs(k1))
    p0 = vector(eval_cornu((k0 - 0.5*k1)/sqrk1))
    p1 = vector(eval_cornu((k0 + 0.5*k1)/sqrk1))
    T = transformation(p0, p1, q0, q1)

    def path(s):
        return T(eval_cornu((k0 + k1*(s-0.5))/sqrk1))
    return path

def plot_cornu(theta0, theta1, color='green'):
    f = scaled_cornu(theta0, theta1)
    pts = [f(x/100.0) for x in range(0, 101)]
    if pts[50][1] < 0:
        pts = [ (x[0], -x[1]) for x in pts]
    G = line(pts, color=color) 
    G.set_aspect_ratio(1.0)
    return G



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

    c0, c1 = hobby
    G += bezier_path([[a, c0, c1, c]], color='blue', thickness=1.5)
    G += point([c0,c1], color='blue', size=30)
    G += plot_cornu(angle(u), RR.pi() - angle(v))
    
        
    G.set_aspect_ratio(1.0)
    G.axes(False)
    G.set_axes_range(-0.7, 1.7, -0.2, 1.5)
    return G
