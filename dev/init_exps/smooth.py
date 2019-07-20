from polylinesample import test_link, bends
from collections import *
import hobby, math, numpy

def get_polylines(file_name='test.lnk'):
    import plink
    LE = plink.LinkEditor(file_name=file_name)
    return LE.polylines(gapsize=None,break_at_overcrossings=True)

class Direction(list):
    """
    An angle/unit vector in R^2
    """
    def __init__(self, spec):
        try:
            x, y = spec
            r = RR(sqrt(x**2 + y**2))
            u = (x/r, y/r)
        except:
            u = (cos(spec), sin(spec))
        list.__init__(self, u)

    def angle(self):
        return math.atan2(self[1], self[0])

    def vector(self):
        return vector(RR, self)

def hobby_bezier(p, q, u, v):
    a, b = hobby.good_bezier(p, u.angle(), v.angle(), q, 1.0, 1.0)
    return [p, a, b, q]

def culler_bezier(p, q, u, v, tightness=0.6):
    u, v = u.vector(), v.vector()
    A = matrix(RR, [u, v]).transpose()
    if abs(A.det()) < 0.00001:
        s = t = 0
    else:
        s, t = numpy.linalg.solve(A.numpy(), q - p)
    return [p, p + tightness*s*u, q - tightness*t*v, q]
    
class PL_Arc(list):
    def __init__(self, points, color='black'):
        self.color = color
        self.orig_points = points = [vector(RR, p) for p in points]
        midpoints =  [(points[k+1] + points[k])/2 for k in range(1, len(points) - 2)]
        list.__init__(self, [points[0]] + midpoints+ [points[-1]])
        def direct(k):
            return Direction(points[k] - points[k-1])
        self.orig_tangents = [direct(1)] + [direct(k) for k in range(2, len(points)-1)] + [direct(-1)]
        assert len(self) == len(self.orig_tangents)
        self.hobby()

    def hobby(self):
        a, b = self.orig_tangents[0], self.orig_tangents[-1]
        dirs = hobby.hobby_dirs(self, a.angle(), b.angle())
        self.hobby_tangents = [Direction(angle) for angle in dirs]

    def bezier(self, bezier=hobby_bezier, tangents='orig'):
        tangents = self.orig_tangents if tangents.startswith('orig') else self.hobby_tangents
        path = [bezier(self[0], self[1], tangents[0], tangents[1])]
        for k in range(1, len(self) - 1):
            path.append( bezier(self[k], self[k+1], tangents[k], tangents[k+1])[1:] )
        return bezier_path(path, color=self.color, thickness=3)

    def overlay(self):
        color = self.color
        ans = line(self.orig_points, color=color.lighter(0.7), thickness=1)
        ans += point(self, color=color, size=30)
        return ans
        

class PL_Arcs(list):
    def __init__(self, polylines=None, arcs=None):
        if polylines:
            arcs = []
            for segments, color in polylines:
                for seg in segments:
                    arcs.append(PL_Arc(seg, Color(str(color))))

        list.__init__(self, arcs)

    def show(self, bezier=culler_bezier, tangents='orig', overlay=True):
        G = Graphics()
        for arc in self:
            G += arc.bezier(bezier, tangents)
            if overlay:
                G += arc.overlay()

        G.set_aspect_ratio(1.0)
        return G
    
    
def quick_fix(arcs):
    ans = []
    for arc in arcs:
        if arc.color == Color(str('#26d826')) and len(arc) == 3:
            if tuple(arc.orig_points[1]) == (377, 109):
                arc.hobby_tangents[1] = arc.orig_tangents[1]
