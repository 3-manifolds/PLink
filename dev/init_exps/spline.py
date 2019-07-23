from Tkinter import *
import sys
sys.path.insert(0, '/home/culler/programs/Spherogram/dev/orthogonal')
from snappy import *
from orthogonal import *

class SmoothKnot:
    def __init__(self, polylines, tightness=0.9, end_tightness=0.9):
        self.window = Toplevel()
        self.canvas = Canvas(self.window, width=500, height=500,
                             background='white')
        self.canvas.pack()
        for polyline in polylines:
            for arc in polyline:
                self.draw_arc(arc, tightness, end_tightness)
        
    def draw_arc(self, points, t, s):
#        self.canvas.create_line(*points, width=1, fill='black')
        x0, y0 = points[:2]
        x1, y1 = points[2:4]
#        self.canvas.create_oval(x0-10,y0-10,x0+10,y0+10, fill='green')
        XY = [x0, y0, x0 +s*(x1-x0), y0 + s*(y1-y0)]
        for n in xrange(2,len(points)-2,2):
            x0, y0 = points[n:n+2]
            x1, y1 = points[n+2:n+4]
            x, y = (x0+x1)/2, (y0+y1)/2
            XY += [x+t*(x0-x), y+t*(y0-y), x, y, x+t*(x1-x),y+t*(y1-y)]
        x1, y1 = points[-4:-2]
        x0, y0 = points[-2:]
        XY += [x0+s*(x1-x0), y0+s*(y1-y1), x0, y0]
#        self.canvas.create_oval(x0-10,y0-10,x0+10,y0+10, fill='purple')
#        self.canvas.create_line(*XY, width=1, fill='blue')
#        self.canvas.create_line(*XY, smooth='raw', width=6,
#                                fill='#ffb0b0', splinesteps=100)
        self.canvas.create_line(*XY, smooth='raw', width=5,
                                fill='#ff6060', splinesteps=100)
#        self.canvas.create_line(*XY, smooth='raw', width=4,
#                                fill='#ff0000', splinesteps=100)

    def Xdraw_arc(self, points, t, s):
        self.canvas.create_line(*points, width=1, fill='black')
        self.canvas.create_line(*points, smooth=True, width=6,
                                fill='#ffb0b0', splinesteps=100)
        self.canvas.create_line(*points, smooth=True, width=5,
                                fill='#ff6060', splinesteps=100)
        self.canvas.create_line(*points, smooth=True, width=4,
                                fill='#ff0000', splinesteps=100)

#C.create_line(*PCCP, smooth=True, width=5, fill='blue', splinesteps=60)
def test(M):
    L = link_from_manifold(M)
    PM = snappy.Manifold()
    PM.LE.load_from_spherogram(L, None, False)
#    PM.LE.callback()
#    PM.zoom_to_fit()
    p = PM.LE.polylines()
    return SmoothKnot(p)

