from polylinesample import polylines
from collections import *
import hobby

def direction(p, q):
    return hobby.to_polar(q-p)[1]

def get_polylines():
    import plink
    LE = plink.LinkEditor(file_name='test.lnk')
    return LE.polylines(gapsize=None,break_at_overcrossings=True)
    
class HobbySegment(list):
    def __init__(self, points):
        points = [vector(RR, p) for p in points]
        midpoints =  [(points[k+1] + points[k])/2 for k in range(1, len(points) - 2)]
        list.__init__(self, [points[0]] + midpoints+ [points[-1]])
        self.original_tangents = [direction(*points[:2])]+ [direction(*points[k:k+2] ) for k in range(1, len(points)-2)] + [direction(*points[-2:])]
        self.orig_points = points
        assert len(self) == len(self.original_tangents)
        
    def bezier_spec(self, tension=1.0):
        a, b= self.original_tangents[0], self.original_tangents[-1]
        dirs = hobby.hobby_dirs(self, a, b)
        dirs = self.original_tangents
        path = []
        for k in range(len(self)-1):
            c0, c1 = hobby.good_bezier(self[k], dirs[k], dirs[k+1], self[k+1],
                                       tension, tension)
            if k == 0:
                path.append([self[0], c0, c1, self[1]])
            else:
                path.append([c0, c1, self[k+1]])

        return path


class SimpleSegment:
    def __init__(self, points):
        points = [vector(RR, p) for p in points]
        midpoints =  [(points[k+1] + points[k])/2 for k in range(len(points) - 1)] 
        points = [points[0]] + midpoints + [points[-1]]
        list.__init__(self, points)
        self.init_tangent = hobby.to_polar(self[1] - self[0])[1]
        self.final_tangent = hobby.to_polar(self[-1] - self[-2])[1]

    

    

def basic_draw():
    G = Graphics()
    G.set_aspect_ratio(1.0)
    for segments, color in polylines:
        for segment in segments:
            G += line(segment, color=color, thickness=3)
    return G

def fancy_draw(segtype, torsion=1.0, polylines=polylines):
    G = Graphics()
    G.set_aspect_ratio(1.0)
    for segments, color in polylines:
        c = Color(color)
        for i, segment in enumerate(segments):
            S = segtype(segment)
            x = 0.5 if i % 2 == 0 else 0.0
            G += bezier_path(S.bezier_spec(torsion), color=c.lighter(x), thickness=3)
            G += point(S, color=c, size=30)
            G += line(segment, color=c.lighter(0.7), thickness=1)
            #G += line(S, color=c.lighter(0.7), thickness=1)
    return G

