# This module provides the function set_scale_factor, which
# monkey-patches the classes Vertex, Arrow and SmoothArc by setting
# their scale_factor attribute to an appropriate value depending on
# the screen resolution.  It must be called after the Tk interpreter
# has been created by instantiating the tkinter.Tk class.

try:
    import tkinter
except ImportError:
    pass

import sys

scale_set = False

def set_scale_factor(scale_factor='auto'):
    global scale_set
    if scale_set and scale_factor == 'auto':
        return

    interp = tkinter._default_root
    if scale_factor != 'auto':
        scale_factor = int(scale_factor)
    elif interp is None:
        scale_factor = 1
    elif tkinter.TkVersion >= 9.0:
        scale_factor = round(3 * interp.call('tk', 'scaling') / 4)
    elif sys.platform == 'linux':
        scale_factor = 2 if interp.winfo_screenheight() > 1600 else 1
    else:
        scale_factor = 1

    from .vertex import Vertex
    Vertex.set_scale(scale_factor)
    from .arrow import Arrow
    Arrow.set_scale(scale_factor)
    from .smooth import SmoothArc, PDFPicture, TikZPicture
    SmoothArc.set_scale(scale_factor)
    PDFPicture.set_scale(scale_factor)
    TikZPicture.set_scale(scale_factor)
    scale_set = True
