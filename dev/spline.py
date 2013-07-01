from Tkinter import *

class SmoothKnot:
    def __init__(self, polylines, tightness=1.0):
        self.window = Toplevel()
        self.canvas = Canvas(self.window, width=500, height=500,
                             background='white')
        self.canvas.pack()
        for polyline in polylines:
            for arc in polyline:
                self.draw_arc(arc, tightness)
        
    def draw_arc(self, points, t):
        self.canvas.create_line(*points, width=1, fill='black')
        x0, y0 = points[:2]
        x1, y1 = points[2:4]
        XY = [x0, y0, x0 +t*(x1-x0), y0 + t*(y1-y0)]
        for n in xrange(2,len(points)-2,2):
            x0, y0 = points[n:n+2]
            x1, y1 = points[n+2:n+4]
            x, y = (x0+x1)/2, (y0+y1)/2
            XY += [x0+t*(x-x0), y0+t*(y-y0), x, y, x+t*(x1-x),y+t*(y1-y)]
        x0, y0 = points[-4:-2]
        x1, y1 = points[-2:]
        XY += [x1+t*(x0-x1), y1 + t*(y0-y1), x1, y1]
        self.canvas.create_line(*XY, smooth='raw', width=6,
                                fill='#ffb0b0', splinesteps=100)
        self.canvas.create_line(*XY, smooth='raw', width=5,
                                fill='#ff6060', splinesteps=100)
        self.canvas.create_line(*XY, smooth='raw', width=4,
                                fill='#ff0000', splinesteps=100)

#C.create_line(*PCCP, smooth=True, width=5, fill='blue', splinesteps=60)
def test(M):
    L = link_from_manifold(M)
    PM = snappy.Manifold()
    PM.LE.load_from_spherogram(L, None, False)
    PM.LE.callback()
    PM.zoom_to_fit()
    p = PM.LE.polylines()
    return SmoothKnot(p)

