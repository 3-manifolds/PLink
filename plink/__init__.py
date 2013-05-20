#!/usr/bin/env python
#
#   Copyright (C) 2007-2009 Marc Culler, Nathan Dunfield and others.
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

import os
import sys
import time
import webbrowser
from math import sqrt
from random import random
from colorsys import hls_to_rgb

try:
    import Tkinter as Tk_
    import tkFileDialog
    import tkMessageBox
    import tkSimpleDialog
    from urllib import pathname2url
except ImportError: # Python 3
    import tkinter as Tk_
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    import tkinter.simpledialog as tkSimpleDialog
    from urllib.request import pathname2url

# Make the Tk file dialog work better with file extensions on OX

def asksaveasfile(mode='w',**options):
    """
    Ask for a filename to save as, and returned the opened file.
    Modified from tkFileDialog to more intelligently handle
    default file extensions. 
    """
    if sys.platform == 'darwin':
        if 'defaultextension' in options and not 'initialfile' in options:
            options['initialfile'] = 'untitled' + options['defaultextension']

    return tkFileDialog.asksaveasfile(mode=mode, **options)

if sys.platform == 'linux2':
    def askopenfile():
        return tkFileDialog.askopenfile(
            mode='r',
            title='Open SnapPea Projection File')
else:
    def askopenfile():
        return tkFileDialog.askopenfile(
            mode='r',
            title='Open SnapPea Projection File',
            defaultextension = ".lnk",
            filetypes = [
                ("Link and text files", "*.lnk *.txt", "TEXT"),
                ("All text files", "", "TEXT"),
                ("All files", "")],
            )

class LinkEditor:
    """
    A graphical link drawing tool based on the one embedded in Jeff Weeks'
    original SnapPea program.
    """
    def __init__(self, root=None, no_arcs=False, callback=None, cb_menu='',
                 title='PLink Editor'):
        self.no_arcs = no_arcs
        self.callback = callback
        self.cb_menu = cb_menu
        self.title = title
        self.initialize()
        self.cursorx = 0
        self.cursory = 0
        self.colors = []
        self.color_keys = []
        if root is None:
            self.window = root = Tk_.Tk(className='plink')
        else:
            self.window = Tk_.Toplevel(root)
        if sys.platform == 'linux2':
            root.tk.call('namespace', 'import', '::tk::dialog::file::')
            root.tk.call('set', '::tk::dialog::file::showHiddenBtn',  '1')
            root.tk.call('set', '::tk::dialog::file::showHiddenVar',  '0')

        self.window.title(title)
        self.palette = Palette()
        # Frame and Canvas
        self.frame = Tk_.Frame(self.window, 
                               borderwidth=0,
                               relief=Tk_.FLAT,
                               background='#dcecff')
        self.canvas = Tk_.Canvas(self.frame,
                                 bg='#dcecff',
                                 width=500,
                                 height=500,
                                 highlightthickness=0)
        self.infoframe = Tk_.Frame(self.window, 
                                   borderwidth=2,
                                   relief=Tk_.FLAT,
                                   background='#ffffff')
        self.infotext_contents = Tk_.StringVar()
        self.infotext = Tk_.Entry(self.infoframe,
                                  state='readonly',
                                  font='Helvetica 16',
                                  textvariable=self.infotext_contents,
                                  readonlybackground='#ffffff',
                                  relief=Tk_.FLAT,
                                  highlightthickness=0)
        #spacer = Tk_.Frame(self.window,
        #                   height=16,
        #                   background='#dcecff')
        #spacer.pack(side=Tk_.BOTTOM)
        self.infoframe.pack(padx=0, pady=0, fill=Tk_.X, expand=Tk_.NO,
                            side=Tk_.BOTTOM)
        self.frame.pack(padx=0, pady=0, fill=Tk_.BOTH, expand=Tk_.YES)
        self.canvas.pack(padx=0, pady=0, fill=Tk_.BOTH, expand=Tk_.YES)
        self.infotext.pack(padx=5, pady=0, fill=Tk_.X, expand=Tk_.NO)
        self.show_DT_var = Tk_.IntVar(self.window)
        self.info_var = Tk_.IntVar(self.window)
        self.current_info = 0
        self.has_focus = True
        # Menus
        self.build_menus()
        # Event bindings
        self.canvas.bind('<Button-1>', self.single_click)
        self.canvas.bind('<Double-Button-1>', self.double_click)
        self.canvas.bind('<Motion>', self.mouse_moved)
        self.window.bind('<FocusIn>', self.focus_in)
        self.window.bind('<FocusOut>', self.focus_out)
        self.window.bind('<Key>', self.key_press)
        self.infotext.bind('<<Copy>>', lambda event : None)
        self.window.protocol("WM_DELETE_WINDOW", self.done)
        # Go
        self.flipcheck = None
        self.state='start_state'
    
    # Subclasses may want to overide this method.
    def build_menus(self):
        menubar = Tk_.Menu(self.window)
        file_menu = Tk_.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open File ...', command=self.load)
        file_menu.add_command(label='Save ...', command=self.save)
        print_menu = Tk_.Menu(menubar, tearoff=0)
        print_menu.add_command(label='monochrome',
                       command=lambda : self.save_image(color_mode='mono'))
        print_menu.add_command(label='color', command=self.save_image)
        file_menu.add_cascade(label='Save Image', menu=print_menu)
        file_menu.add_separator()
        if self.callback:
            file_menu.add_command(label=self.cb_menu, command=self.do_callback)
            file_menu.add_command(label='Close', command=self.done)
        else:
            file_menu.add_command(label='Exit', command=self.done)
        menubar.add_cascade(label='File', menu=file_menu)
        export_menu = Tk_.Menu(menubar, tearoff=0)
        info_menu = Tk_.Menu(menubar, tearoff=0)
        info_menu.add_radiobutton(label='DT code', var=self.info_var,
                                  command=self.set_info, value=1)
        info_menu.add_radiobutton(label='Alphabetical DT', var=self.info_var,
                                  command=self.set_info, value=2)
        info_menu.add_radiobutton(label='Gauss code', var=self.info_var,
                                  command=self.set_info, value=3)
        info_menu.add_radiobutton(label='PD code', var=self.info_var,
                                  command=self.set_info, value=4)
        info_menu.add_radiobutton(label='BB framing', var=self.info_var,
                                  command=self.set_info, value=5)
        info_menu.add_separator()
        info_menu.add_checkbutton(label='DT labels', var=self.show_DT_var,
                                  command = self.update_info)
        menubar.add_cascade(label='Info', menu=info_menu)
        tools_menu = Tk_.Menu(menubar, tearoff=0)
        tools_menu.add_command(label='Make alternating',
                       command=self.make_alternating)
        tools_menu.add_command(label='Reflect', command=self.reflect)
        tools_menu.add_command(label='Clear', command=self.clear)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        help_menu = Tk_.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About PLink...', command=self.about)
        help_menu.add_command(label='Instructions ...', command=self.howto)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.window.config(menu=menubar)

    def initialize(self):
        self.Arrows = []
        self.Vertices = []
        self.Crossings = []
        self.CrossPoints = []
        self.LiveArrow1 = None
        self.LiveArrow2 = None
        self.ActiveVertex = None
        self.DTlabels = []

    def alert(self):
        background = self.canvas.cget('bg')
        def reset_bg():
            self.canvas.config(bg=background)
        self.canvas.config(bg='#ffffff')
        self.canvas.after(100, reset_bg)

    def warn_arcs(self):
        if self.no_arcs:
            for vertex in self.Vertices:
                if vertex.is_endpoint():
                    if tkMessageBox.askretrycancel('Warning',
                         'This link has non-closed components!\n'
                         'Click "retry" to continue editing.\n'
                         'Click "cancel" to quit anyway.\n'
                         '(The link projection may be useless.)'):
                        return 'oops'
                    else:
                        break

    def done(self):
        if self.callback is not None:
            self.window.withdraw()
            return
        if self.warn_arcs() == 'oops':
            return
        else:
            self.window.destroy()

    def do_callback(self):
        if self.warn_arcs() == 'oops':
            return
        self.callback()

    def reopen(self):
        self.window.deiconify()

    def focus_in(self, event):
        self.window.after(100, self.notice_focus) 
    
    def notice_focus(self):
        self.has_focus = True
               
    def focus_out(self, event):
        self.has_focus = False

    def single_click(self, event):
        """
        Event handler for mouse clicks.
        """
        if not self.has_focus:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.clear_text()
        start_vertex = Vertex(x, y, self.canvas, hidden=True)
        if self.state == 'start_state':
            if start_vertex in self.Vertices:
                #print 'single click on a vertex'
                self.state = 'dragging_state'
                self.hide_DT()
                self.canvas.config(cursor='circle')
                self.ActiveVertex = self.Vertices[
                    self.Vertices.index(start_vertex)]
                self.ActiveVertex.freeze()
                x1, y1 = self.ActiveVertex.point()
                if self.ActiveVertex.in_arrow:
                    x0, y0 = self.ActiveVertex.in_arrow.start.point()
                    self.ActiveVertex.in_arrow.freeze()
                    self.LiveArrow1 = self.canvas.create_line(x0,y0,x1,y1,
                                                             fill='red')
                if self.ActiveVertex.out_arrow:
                    x0, y0 = self.ActiveVertex.out_arrow.end.point()
                    self.ActiveVertex.out_arrow.freeze()
                    self.LiveArrow2 = self.canvas.create_line(x0,y0,x1,y1,
                                                             fill='red')
                return
            elif start_vertex in self.CrossPoints:
                #print 'single click on a crossing'
                crossing = self.Crossings[self.CrossPoints.index(start_vertex)]
                crossing.reverse()
                self.update_info()
                crossing.under.draw(self.Crossings)
                crossing.over.draw(self.Crossings)
                return
            elif self.clicked_on_arrow(start_vertex):
                #print 'clicked on an arrow.'
                return
            else:
                #print 'creating a new vertex'
                if not self.generic_vertex(start_vertex):
                    start_vertex.erase()
                    self.alert()
                    return
            x1, y1 = start_vertex.point()
            start_vertex.set_color(self.palette.new())
            self.Vertices.append(start_vertex)
            self.ActiveVertex = start_vertex
            self.goto_drawing_state(x1,y1)
            return
        elif self.state == 'drawing_state':
            next_vertex = Vertex(x, y, self.canvas, hidden=True)
            if next_vertex == self.ActiveVertex:
                #print 'clicked the same vertex twice'
                next_vertex.erase()
                dead_arrow = self.ActiveVertex.out_arrow
                if dead_arrow:
                    self.destroy_arrow(dead_arrow)
                self.goto_start_state()
                return
            #print 'setting up a new arrow'
            if self.ActiveVertex.out_arrow:
                next_arrow = self.ActiveVertex.out_arrow
                next_arrow.set_end(next_vertex)
                next_vertex.in_arrow = next_arrow
                if not next_arrow.frozen:
                    next_arrow.hide()
            else:
                this_color = self.ActiveVertex.color
                next_arrow = Arrow(self.ActiveVertex, next_vertex,
                                 self.canvas, hidden=True,
                                 color=this_color)
                self.Arrows.append(next_arrow)
            next_vertex.set_color(next_arrow.color)
            if next_vertex in [v for v in self.Vertices if v.is_endpoint()]:
                #print 'melding vertices'
                if not self.generic_arrow(next_arrow):
                    self.alert()
                    return
                next_vertex.erase()
                next_vertex = self.Vertices[self.Vertices.index(next_vertex)]
                if next_vertex.in_arrow:
                    next_vertex.reverse_path()
                next_arrow.set_end(next_vertex)
                next_vertex.in_arrow = next_arrow
                if next_vertex.color != self.ActiveVertex.color:
                    self.palette.recycle(self.ActiveVertex.color)
                    next_vertex.recolor_incoming(color = next_vertex.color)
                self.update_crossings(next_arrow)
                next_arrow.expose(self.Crossings)
                self.goto_start_state()
                return
            #print 'just extending a path, as usual'
            self.update_crossings(next_arrow)
            self.update_crosspoints()
            if not (self.generic_vertex(next_vertex) and
                    self.generic_arrow(next_arrow) ):
                self.alert()
                return
            next_arrow.expose(self.Crossings)
            self.Vertices.append(next_vertex)
            next_vertex.expose()
            self.ActiveVertex = next_vertex
            self.canvas.coords(self.LiveArrow1,x,y,x,y)
            return
        elif self.state == 'dragging_state':
            try:
                self.end_dragging_state()
            except ValueError:
                self.alert()

    def double_click(self, event):
        """
        Event handler for mouse double-clicks.
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.clear_text()
        vertex = Vertex(x, y, self.canvas, hidden=True)
        #print 'double-click in %s'%self.state
        if self.state == 'dragging_state':
            self.end_dragging_state()
            # The first click on a vertex put us in dragging state.
            if vertex in [v for v in self.Vertices if v.is_endpoint()]:
                #print 'double-clicked on an endpoint'
                vertex.erase()
                vertex = self.Vertices[self.Vertices.index(vertex)]
                x0, y0 = x1, y1 = vertex.point()
                if vertex.out_arrow:
                    self.update_crosspoints()
                    vertex.reverse_path()
            elif vertex in self.Vertices:
                #print 'double-clicked on a non-endpoint vertex'
                cut_vertex = self.Vertices[self.Vertices.index(vertex)]
                cut_vertex.recolor_incoming(palette=self.palette)
                cut_arrow = cut_vertex.in_arrow
                cut_vertex.in_arrow = None
                vertex = cut_arrow.start
                x1, y1 = cut_vertex.point()
                cut_arrow.freeze()
            self.ActiveVertex = vertex
            self.goto_drawing_state(x1,y1)
            return
        elif self.state == 'drawing_state':
            #print 'double-click while drawing'
            dead_arrow = self.ActiveVertex.out_arrow
            if dead_arrow:
                self.destroy_arrow(dead_arrow)
            self.goto_start_state()
        
    def mouse_moved(self,event):
        """
        Handler for mouse motion events.
        """
        self.cursorx, self.cursory = event.x, event.y
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.state == 'start_state':
            point = Vertex(x, y, self.canvas, hidden=True)
            if point in self.Vertices:
                self.flipcheck=None
                self.canvas.config(cursor='hand1')
            elif point in self.CrossPoints:
                self.flipcheck=None
                self.canvas.config(cursor='exchange')
            elif self.cursor_on_arrow(point):
                now = time.time()
                if self.flipcheck is None:
                    self.flipcheck = now
                elif now - self.flipcheck > 0.5:
                    self.canvas.config(cursor='double_arrow')
            else:
                self.flipcheck=None
                self.canvas.config(cursor='')
        elif self.state == 'drawing_state':
            x0,y0,x1,y1 = self.canvas.coords(self.LiveArrow1)
            self.canvas.coords(self.LiveArrow1, x0, y0, x, y)
        elif self.state == 'dragging_state':
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.ActiveVertex.x, self.ActiveVertex.y = x, y
            self.ActiveVertex.draw()
            if self.LiveArrow1:
                x0,y0,x1,y1 = self.canvas.coords(self.LiveArrow1)
                self.canvas.coords(self.LiveArrow1, x0, y0, x, y)
            if self.LiveArrow2:
                x0,y0,x1,y1 = self.canvas.coords(self.LiveArrow2)
                self.canvas.coords(self.LiveArrow2, x0, y0, x, y)

    def key_press(self, event):
        """
        Handler for keypress events.
        """
        if event.keysym == 'Delete' or event.keysym == 'BackSpace':
            if self.state == 'drawing_state':
                last_arrow = self.ActiveVertex.in_arrow
                if last_arrow:
                    dead_arrow = self.ActiveVertex.out_arrow
                    if dead_arrow:
                        self.destroy_arrow(dead_arrow)
                    self.ActiveVertex = last_arrow.start
                    self.ActiveVertex.out_arrow = None
                    x0,y0,x1,y1 = self.canvas.coords(self.LiveArrow1)
                    x0, y0 = self.ActiveVertex.point()
                    self.canvas.coords(self.LiveArrow1, x0, y0, x1, y1)
                    self.Crossings = [c for c in self.Crossings
                                      if last_arrow not in c]
                    self.Vertices.remove(last_arrow.end)
                    self.Arrows.remove(last_arrow)
                    last_arrow.end.erase()
                    last_arrow.erase()
                    for arrow in self.Arrows:
                        arrow.draw(self.Crossings)

                if not self.ActiveVertex.in_arrow:
                    self.Vertices.remove(self.ActiveVertex)
                    self.ActiveVertex.erase()
                    self.goto_start_state()
        dx, dy = 0, 0
        if event.keysym == 'Down':
            dx, dy = 0, 5
        elif event.keysym == 'Up':
            dx, dy = 0, -5
        elif event.keysym == 'Right':
            dx, dy = 5, 0
        elif event.keysym == 'Left':
            dx, dy = -5, 0
        if dx or dy:
            for vertex in self.Vertices:
                vertex.x += dx
                vertex.y += dy
            self.update_crosspoints()
            self.canvas.move('all', dx, dy)
            self.adjust_colors()
        event.x, event.y = self.cursorx, self.cursory
        self.mouse_moved(event)

    def clicked_on_arrow(self, vertex):
        for arrow in self.Arrows:
            if arrow.too_close(vertex):
                arrow.end.reverse_path(self.Crossings)
                self.update_info()
                return True
        return False

    def cursor_on_arrow(self, point):
        for arrow in self.Arrows:
            if arrow.too_close(point):
                return True
        return False

    def goto_start_state(self):
        self.canvas.delete(self.LiveArrow1)
        self.LiveArrow1 = None
        self.canvas.delete(self.LiveArrow2)
        self.LiveArrow2 = None
        self.ActiveVertex = None
        self.update_crosspoints()
        self.state = 'start_state'
        self.update_info()
        self.adjust_colors()
        for vertex in self.Vertices:
            vertex.draw()
#        for arrow in self.Arrows: 
#            arrow.draw(self.Crossings)
        self.canvas.config(cursor='')

    def goto_drawing_state(self, x1,y1):
        self.ActiveVertex.hidden = False
        self.ActiveVertex.draw()
        x0, y0 = self.ActiveVertex.point()
        self.LiveArrow1 = self.canvas.create_line(x0,y0,x1,y1,fill='red')
        self.state = 'drawing_state'
        self.canvas.config(cursor='pencil')
        self.hide_DT()
        self.clear_text()

    def verify_drag(self):
        self.ActiveVertex.update_arrows()
        self.update_crossings(self.ActiveVertex.in_arrow)
        self.update_crossings(self.ActiveVertex.out_arrow)
        self.update_crosspoints()
        return (self.generic_arrow(self.ActiveVertex.in_arrow) and
                self.generic_arrow(self.ActiveVertex.out_arrow) )

    def end_dragging_state(self):
        if not self.verify_drag():
            raise ValueError
        endpoint = None
        if self.ActiveVertex.is_endpoint():
            other_ends = [v for v in self.Vertices if
                          v.is_endpoint() and v is not self.ActiveVertex]
            if self.ActiveVertex in other_ends:
                endpoint = other_ends[other_ends.index(self.ActiveVertex)]
                self.ActiveVertex.swallow(endpoint, self.palette)
                self.Vertices = [v for v in self.Vertices if v is not endpoint]
            self.update_crossings(self.ActiveVertex.in_arrow)
            self.update_crossings(self.ActiveVertex.out_arrow)
        if endpoint is None and not self.generic_vertex(self.ActiveVertex):
            raise ValueError
        self.ActiveVertex.expose()
        if self.ActiveVertex.in_arrow:
            self.ActiveVertex.in_arrow.expose()
        if self.ActiveVertex.out_arrow:
            self.ActiveVertex.out_arrow.expose()
        self.goto_start_state()

    def generic_vertex(self, vertex):
        if vertex in [v for v in self.Vertices if v is not vertex]:
            return False
        for arrow in self.Arrows:
            if arrow.too_close(vertex):
                #print 'non-generic vertex'
                return False
        return True

    def generic_arrow(self, arrow):
        if arrow == None:
            return True
        for vertex in self.Vertices:
            if arrow.too_close(vertex):
                #print 'arrow too close to vertex'
                return False
        for crossing in self.Crossings:
            point = self.CrossPoints[self.Crossings.index(crossing)]
            if arrow not in crossing and arrow.too_close(point):
                #print 'arrow too close to crossing'
                return False
        return True
       
    def destroy_arrow(self, arrow):
        self.Arrows.remove(arrow)
        if arrow.end:
            arrow.end.in_arrow = None
        if arrow.start:
            arrow.start.out_arrow = None
        arrow.erase()
        self.Crossings = [c for c in self.Crossings if arrow not in c]

    def update_crosspoints(self):
        for c in self.Crossings:
            c.locate()
        self.CrossPoints = [Vertex(c.x, c.y, self.canvas, hidden=True)
                                    for c in self.Crossings]

    def update_crossings(self, this_arrow):
        if this_arrow == None:
            return
        cross_list = [c for c in self.Crossings if this_arrow in c]
        damage_list =[]
        find = lambda x: cross_list[cross_list.index(x)]
        for arrow in self.Arrows:
            if this_arrow == arrow:
                continue
            new_crossing = Crossing(this_arrow, arrow)
            if this_arrow ^ arrow:
                if new_crossing in cross_list:
                    #print 'keeping %s'%new_crossing
                    find(new_crossing).locate()
                    continue
                else:
                    #print 'adding %s'%new_crossing
                    self.Crossings.append(new_crossing)
                    new_crossing.locate()
            else:
                #print 'removing %s'%new_crossing
                if new_crossing in self.Crossings:
                    if arrow == find(new_crossing).under:
                        damage_list.append(arrow)
                    self.Crossings.remove(new_crossing)
        for arrow in damage_list:
            arrow.draw(self.Crossings)

    def arrow_components(self, include_isolated_vertices=False):
        """
        Returns a list of components, given as lists of arrows.
        The closed components are sorted in DT order if they have
        been marked.  The others are sorted by age.
        """
        pool = [v.out_arrow for v in self.Vertices if v.in_arrow is None]
        pool += [v.out_arrow  for v in self.Vertices if v.in_arrow is not None]
        closed, nonclosed = [], []
        while len(pool):
            first_arrow = pool.pop(0)
            if first_arrow == None:
                continue
            component = [first_arrow]
            while component[-1].end != component[0].start:
                next_arrow = component[-1].end.out_arrow
                if next_arrow is None:
                    break
                pool.remove(next_arrow)
                component.append(next_arrow)
            if next_arrow is None:
                nonclosed.append(component)
            else:
                closed.append(component)
        if include_isolated_vertices:
            for vertex in [v for v in self.Vertices if v.is_isolated()]:
                nonclosed.append([Arrow(vertex, vertex, color=vertex.color)])
        def oldest_vertex(component):
            def oldest(arrow):
                return min([self.Vertices.index(v)
                            for v in [arrow.start, arrow.end] if v])
            return min( [len(self.Vertices)] +  [oldest(a) for a in component])
        closed.sort(key=lambda x : (x[0].component, oldest_vertex(x)))
        nonclosed.sort(key=oldest_vertex)
        return closed + nonclosed

    def crossing_components(self):
        """
        Returns a list of lists of ECrossings, one per component,
        where the corresponding crossings are ordered consecutively
        through the component.  Requires that all components be closed.
        """
        for vertex in self.Vertices:
            if vertex.is_endpoint():
                raise ValueError('All components must be closed.')
        result = []
        arrow_components = self.arrow_components()
        for component in arrow_components:
            crosses=[]
            for arrow in component:
                arrow_crosses = [(c.height(arrow), c, arrow) 
                                for c in self.Crossings if arrow in c]
                arrow_crosses.sort()
                crosses += arrow_crosses
            result.append([ECrossing(c[1],c[2]) for c in crosses]) 
        return result

    def adjust_colors(self):
        """
        Recolors and redraws all components, in DT order, and displays
        the legend linking colors to cusp indices.
        """
        components = self.arrow_components(include_isolated_vertices=True)
        self.colors = []
        for key in self.color_keys:
            self.canvas.delete(key)
        self.color_keys = []
        x, y, n = 10, 24, 0
        self.palette.reset()
        for component in components:
            color = self.palette.new()
            self.colors.append(color)
            component[0].start.color = color
            for arrow in component:
                arrow.color = color
                arrow.end.color = color
                arrow.draw(self.Crossings)
            self.color_keys.append(
                self.canvas.create_text(x, y,
                                        text=str(n),
                                        fill=color,
                                        anchor=Tk_.SW,
                                        font='Helvetica 16 bold'))
            x, n = x+16, n+1
        for vertex in self.Vertices:
            vertex.draw()

    def set_info(self):
        self.clear_text()
        which_info = self.info_var.get()
        if which_info == self.current_info:
            # toggle
            self.info_var.set(0)
            self.current_info = 0
        else:
            self.current_info = which_info
            self.update_info()

    def clear_text(self):
        self.infotext_contents.set('')
        self.window.focus_set()

    def write_text(self, string):
        self.infotext_contents.set(string)

    def make_alternating(self):
        """
        Changes crossings to make the projection alternating.
        Requires that all components be closed.
        """
        try:
            crossing_components = self.crossing_components()
        except ValueError:
            tkMessageBox.showwarning(
                'Error',
                'Please close up all components first.')
            return
        for component in crossing_components:
            if len(component) == 0:
                continue
            cross0, arrow0 = component[0].pair()
            for ecrossing in component[1:]:
                cross, arrow = ecrossing.pair()
                if ( (arrow0 == cross0.under and arrow == cross.under) or 
                     (arrow0 == cross0.over and arrow == cross.over) ):
                    if cross.locked:
                        for ecrossing2 in component:
                            if ecrossing2.crossing == cross:
                                break
                            ecrossing2.crossing.reverse()
                    else:
                        cross.reverse()
                cross0, arrow0 = cross, arrow
            for ecrossing in component:
                ecrossing.crossing.locked = True
        for crossing in self.Crossings:
            crossing.locked = False
        self.clear_text()
        self.update_info()
        for arrow in self.Arrows:
            arrow.draw(self.Crossings)

    def reflect(self):
        for crossing in self.Crossings:
            crossing.reverse()
        self.clear_text()
        self.update_info()
        for arrow in self.Arrows:
            arrow.draw(self.Crossings)

    def clear(self):
        for arrow in self.Arrows:
            arrow.erase()
        for vertex in self.Vertices:
            vertex.erase()
        self.canvas.delete('all')
        self.palette.reset()
        self.initialize()
        self.show_DT_var.set(0)
        self.info_var.set(0)
        self.clear_text()
        self.goto_start_state()


    def update_info(self):
        self.hide_DT()
        self.clear_text()
        if self.state != 'start_state':
            return
        if self.show_DT_var.get():
            dt = self.DT_code()
            if dt is not None:
                self.show_DT()
        info_value = self.info_var.get()
        if info_value == 1:
            self.DT_normal()
        elif info_value == 2:
            self.DT_alpha()
        elif info_value == 3:
            self.Gauss_info()
        elif info_value == 4:
            self.PD_info()
        elif info_value == 5:
            self.BB_info()

    def sorted_components(self):
        """
        Returns a list of crossing components which have been sorted
        and cyclically permuted, following the scheme used in "standard"
        DT codes.

        The sorting process also sets the hit counters on all
        crossings, for use in computing DT and Gauss codes, and
        sets the component attribute of each arrow in each
        component.

        Requires that all components be closed.

        """
        try:
            components = self.crossing_components()
            components.sort(key=lambda x:len(x))
        except ValueError:
            return None
        for crossing in self.Crossings:
            crossing.clear_marks()
        # Mark which components each crossing belongs to.
        for component in components:
            for ecrossing in component:
                ecrossing.crossing.mark_component(component)
        sorted_components = []
        count = 1
        while len(components) > 0:
            this_component = components.pop()
            sorted_components.append(this_component)
            # Choose the first crossing on this component by Morwen's
            # rule: If any crossings on this component have been hit,
            # find the first one with an odd label and then start at
            # its predecessor.
            odd_hits = [ec for ec in this_component if ec.crossing.hit1%2 == 1]
            if len(odd_hits) > 0:
                odd_hits.sort(key=lambda x : x.crossing.hit1)
                n = this_component.index(odd_hits[0])
                this_component = this_component[n-1:] + this_component[:n-1]
            # Count the crossings on this component and remember any
            # odd-numbered crossings which are shared with an
            # unfinished component.
            touching = []
            for ec in this_component:
                crossing = ec.crossing
                if crossing.DT_hit(count, ec):
                    if crossing.comp2 in components:
                        touching.append((crossing, crossing.comp2))
                    elif crossing.comp1 in components:
                        touching.append((crossing, crossing.comp1))
                count += 1
            # Choose the next component, by Morwen's rule: Use the
            # component containing the partner of the first
            # odd-numbered crossing that is shared with another
            # commponent (if there are any shared crossings).
            if len(touching) > 0:
                touching.sort(key=lambda x : x[0].hit1)
                next_component = touching[0][1]
                components.remove(next_component)
                components.append(next_component)
        for arrow in self.Arrows:
            arrow.component = None
        for n, component in enumerate(sorted_components):
            if len(component) == 0:
                continue
            arrow = first_arrow = component[0].arrow
            while True:
                arrow.component = n
                arrow = arrow.end.out_arrow
                if arrow == first_arrow:
                    break
        return sorted_components

    def SnapPea_KLPProjection(self):
        """
        Constructs a python simulation of a SnapPea KLPProjection
        (Kernel Link Projection) structure.  See Jeff Weeks' SnapPea
        file link_projection.h for definitions.  Here the KLPCrossings
        are modeled by dictionaries.  This method requires that all
        components be closed.  A side effect is that the KLP attributes
        of all crossings are updated.

        The following excerpt from link_projection.h describes the
        main convention:

        If you view a crossing (from above) so that the strands go in the
        direction of the positive x- and y-axes, then the strand going in
        the x-direction is the KLPStrandX, and the strand going in the
        y-direction is the KLPStrandY.  Note that this definition does not
        depend on which is the overstrand and which is the understrand:
        
        ::

                             KLPStrandY
                                 ^
                                 |
                             ----+---> KLPStrandX
                                 |
                                 |

        \ 
        """
        try:
            sorted_components = self.sorted_components()
        except ValueError:
            return None
        num_crossings = len(self.Crossings)
        num_free_loops = 0
        num_components = len(sorted_components)
        id = lambda x: self.Crossings.index(x.crossing)
        for component in sorted_components:
            this_component = sorted_components.index(component)
            N = len(component)
            for n in range(N):
                this = component[n]
                previous = component[n-1]
                next = component[(n+1)%N]
                this.crossing.KLP['sign'] = sign = this.crossing.sign()
                if this.strand == 'X':
                    this.crossing.KLP['Xbackward_neighbor'] = id(previous)
                    this.crossing.KLP['Xbackward_strand'] = previous.strand
                    this.crossing.KLP['Xforward_neighbor']  = id(next)
                    this.crossing.KLP['Xforward_strand'] = next.strand
                    this.crossing.KLP['Xcomponent'] = this_component
                else:
                    this.crossing.KLP['Ybackward_neighbor'] = id(previous)
                    this.crossing.KLP['Ybackward_strand'] = previous.strand
                    this.crossing.KLP['Yforward_neighbor']  = id(next)
                    this.crossing.KLP['Yforward_strand'] = next.strand
                    this.crossing.KLP['Ycomponent'] = this_component
            if N == 0:
                num_free_loops += 1
        KLP_crossings = [crossing.KLP for crossing in self.Crossings]
        return num_crossings, num_free_loops, num_components, KLP_crossings

    def PD_code(self):
        """
        Return the PD (Planar Diagram) code for the link projection,
        as a list of 4-tuples.
        """
        # We view an ecrossing as corresponding to the outgoing arc
        # of the diagram at the ecrossing.crossing.
        try:
            sorted_components = self.sorted_components()
        except ValueError:
            return None
        ecrossings = [ ec for component in sorted_components
                       for ec in component ]
        counter = dict( (ec, k+1) for k, ec in enumerate(ecrossings) )
        over_dict, under_dict = {}, {}
        for component in sorted_components:
            N = len(component)
            for n, ec in enumerate(component):
                incoming = counter[component[n-1]]
                outgoing = counter[component[n]]
                D = over_dict if ec.goes_over() else under_dict
                D[ec.crossing] = (incoming, outgoing)
        PD = []
        for crossing in self.Crossings:
            under, over = under_dict[crossing], over_dict[crossing]
            if crossing.sign() =='RH':
                PD.append( (under[0], over[1], under[1], over[0]) )
            else:
                PD.append( (under[0], over[0], under[1], over[1]) )
        return PD

    def DT_code(self, alpha=False, signed=True, return_sizes=False):
        """
        Return the Dowker-Thistlethwaite code as a list of tuples of
        even integers.  Requires that all components be closed.

        If alpha is set to True, this method returns the alphabetical
        Dowker-Thistlethwaite code as used in Oliver Goodman's Snap
        and in the tabulations by Jim Hoste and Morwen Thistlethwaite.

        If return_sizes is set to True, a list of the number of crossings
        in each component is returned (this is for use by Gauss_code).
        """
        sorted_components = self.sorted_components()
        if sorted_components is None or len(sorted_components) == 0:
            return (None, None) if return_sizes else None
        component_sizes = [len(c) for c in sorted_components]
        DT_chunks, S = [], 0
        for size in component_sizes:
            DT_chunks.append((size+1)//2 if S%2 != 0 else size//2)
            S += size
        # Now build the Dowker-Thistlethwaite code
        even_codes = [None]*len(self.Crossings)
        flips = [None]*len(self.Crossings)
        for crossing in self.Crossings:
            if crossing.hit1%2 != 0:
                n = (crossing.hit1 - 1)//2
                even_codes[n] = crossing.hit2
            else:
                n = (crossing.hit2 - 1)//2
                even_codes[n] = crossing.hit1
            flips[n] = int(crossing.flipped)
        if not alpha:
            dt = []
            for chunk in DT_chunks:
                dt.append(tuple(even_codes[:chunk]))
                even_codes = even_codes[chunk:]
            result = [dt]
            if signed:
                result.append(flips)
        else:
            prefix_ints = [len(self.Crossings), len(sorted_components)]
            prefix_ints += DT_chunks
            if prefix_ints[0] > 26:
                tkMessageBox.showwarning(
                    'Error',
                    'Alphabetical DT codes require fewer than 26 crossings.')
                return None
            alphacode = ''.join(tuple([DT_alphabet[n>>1] for n in even_codes]))
            prefix = ''.join(tuple([DT_alphabet[n] for n in prefix_ints]))
            if signed:
                alphacode += '.' + ''.join([str(f) for f in flips])
            result=[prefix + alphacode]
        if return_sizes:
            result.append(component_sizes)
        return tuple(result)

    def Gauss_code(self):
        """
        Return a Gauss code for the link.  The Gauss code is computed
        from a DT code, so the Gauss code will use the same indexing
        of crossings as is used for the DT code.  Requires that all
        components be closed.
        """
        dt, sizes = self.DT_code(signed=False, return_sizes=True)
        if dt is None:
            return None
        evens = [y for x in dt for y in x]
        size = 2*len(evens)
        counts = [None]*size
        for odd, N in zip(range(1, size, 2), evens):
            even = abs(N)
            if even < odd:
                counts[even-1] = -N
                counts[odd-1] = N 
            else:
                O = odd if N > 0 else -odd
                counts[even-1] = -O
                counts[odd-1] = O
        gauss = []
        start = 0
        for size in sizes:
            end = start + size
            gauss.append(tuple(counts[start:end]))
            start = end
        return gauss
                                         
    def BB_framing(self):
        """
        Return the standard meridian-longitude coordinates of the
        blackboard longitude (i.e. the peripheral element obtained
        by following the top of a tubular neighborhood of the knot).
        """
        try:
            components = self.sorted_components()
        except ValueError:
            return None
        framing = []
        for component in components:
            m = 0
            for ec in component:
                crossing = ec.crossing
                # Only consider self crossings
                if crossing.comp1 == crossing.comp2 == component:
                    if ec.crossing.sign() == 'RH':
                        m += 1
                    elif ec.crossing.sign() == 'LH':
                        m -= 1
            # Each crossing got counted twice.
            framing.append( (m/2, 1) )
        return framing
        
    def DT_normal(self):
        """
        Displays a Dowker-Thistlethwaite code as a list of tuples of
        signed even integers.
        """
        code = self.DT_code()
        if code:
            self.write_text(('DT: %s,  %s'%code).replace(', ',','))

    def DT_alpha(self):
        """
        Displays an alphabetical Dowker-Thistlethwaite code, as used in
        the knot tabulations.
        """
        code = self.DT_code(alpha=True)
        if code:
            self.write_text('DT: %s'%code)

    def Gauss_info(self):
        """
        Displays a Gauss code as a list of tuples of signed
        integers.
        """
        code = self.Gauss_code()
        if code:
            self.write_text(('Gauss: %s'%code).replace(', ',','))

    def PD_info(self):
        """
        Displays a PD code as a list of 4-tuples.
        """
        code = self.PD_code()
        if code:
            self.write_text(('PD: %s'%code).replace(', ',','))

    def BB_info(self):
        """
        Displays the meridian-longitude coordinates of the blackboard
        longitudes of the components of the link
        """
        framing = self.BB_framing()
        if framing:
            self.write_text(('BB framing:  %s'%framing).replace(', ',','))

    def show_DT(self):
        """
        Display the DT hit counters next to each crossing.  Crossings
        that need to be flipped for the planar embedding have an
        asterisk.
        """
        for crossing in self.Crossings:
            crossing.locate()
            yshift = 0
            for arrow in crossing.over, crossing.under:
                arrow.vectorize()
                if abs(arrow.dy) < .3*abs(arrow.dx):
                    yshift = 8
            flip = ' *' if crossing.flipped else ''
            self.DTlabels.append(self.canvas.create_text(
                    (crossing.x - 10, crossing.y - yshift),
                    anchor=Tk_.E,
                    text=str(crossing.hit1)
                    ))
            self.DTlabels.append(self.canvas.create_text(
                    (crossing.x + 10, crossing.y - yshift),
                    anchor=Tk_.W,
                    text=str(crossing.hit2) + flip
                    ))

    def hide_DT(self):
        for text_item in self.DTlabels:
            self.canvas.delete(text_item)
        self.DTlabels = []

    def SnapPea_projection_file(self):
        """
        Returns a string containing the contents of a SnapPea link
        projection file.
        """
        result = ''
        result += '% Link Projection\n'
        components = self.arrow_components()
        result += '%d\n'%len(components)
        for component in components:
            first = self.Vertices.index(component[0].start)
            last = self.Vertices.index(component[-1].end)
            result +='%4.1d %4.1d\n'%(first, last)
        result += '%d\n'%len(self.Vertices)
        for vertex in self.Vertices:
            result += '%5.1d %5.1d\n'%vertex.point()
        result += '%d\n'%len(self.Arrows)
        for arrow in self.Arrows:
            start_index = self.Vertices.index(arrow.start)
            end_index = self.Vertices.index(arrow.end)
            result += '%4.1d %4.1d\n'%(start_index, end_index)
        result += '%d\n'%len(self.Crossings)
        for crossing in self.Crossings:
            under = self.Arrows.index(crossing.under)
            over = self.Arrows.index(crossing.over)
            result += '%4.1d %4.1d\n'%(under, over)
        if self.ActiveVertex:
            result += '%d\n'%self.Vertices.index(self.ActiveVertex)
        else:
            result += '-1\n'
        return result

    def not_done(self):
        tkMessageBox.showwarning(
            'Not implemented',
            'Sorry!  That feature has not been written yet.')

    def save(self):
        savefile = asksaveasfile(
            mode='w',
            title='Save As Snappea Projection File',
            defaultextension = '.lnk',
            filetypes = [
                ("Link and text files", "*.lnk *.txt", "TEXT"),
                ("All text files", "", "TEXT"),
                ("All files", "")],
            )
        if savefile:
            savefile.write(self.SnapPea_projection_file())
            savefile.close()

    def save_image(self, color_mode='color'):
        savefile = asksaveasfile(
            mode='w',
            title='Save As Postscript Image File (%s)'%color_mode,
            defaultextension = ".eps", 
            filetypes=[('ps','eps')])
        if savefile:
            savefile.write(self.canvas.postscript(colormode=color_mode))
            savefile.close()

    def load(self, file_name=None):
        if file_name:
            loadfile = open(file_name, "r")
        else:
            loadfile = askopenfile()
        if loadfile:
            lines = [line for line in loadfile.readlines() if len(line) > 1]
            num_lines = len(lines)
            if not lines.pop(0).startswith('% Link Projection'):
                tkMessageBox.showwarning(
                    'Bad file',
                    'This is not a SnapPea link projection file')
            else:
                self.clear()
                self.clear_text()
                try:
                    num_components = int(lines.pop(0))
                    for n in range(num_components):
                        lines.pop(0) # We don't need this
                    num_vertices = int(lines.pop(0))
                    for n in range(num_vertices):
                        x, y = lines.pop(0).split()
                        X, Y = int(x), int(y)
                        self.Vertices.append(Vertex(X, Y, self.canvas))
                    num_arrows = int(lines.pop(0))
                    for n in range(num_arrows):
                        s, e = lines.pop(0).split()
                        S, E = self.Vertices[int(s)], self.Vertices[int(e)]
                        self.Arrows.append(Arrow(S, E, self.canvas))
                    num_crossings = int(lines.pop(0))
                    for n in range(num_crossings):
                        u, o = lines.pop(0).split()
                        U, O = self.Arrows[int(u)], self.Arrows[int(o)]
                        self.Crossings.append(Crossing(O, U))
                    hot = int(lines.pop(0))
                except:
                    tkMessageBox.showwarning(
                        'Bad file',
                        'Failed while parsing line %d'%(num_lines - len(lines)))
                loadfile.close()
                self.create_colors()
                self.goto_start_state()
                if hot != -1:
                    self.ActiveVertex = self.Vertices[hot]
                    self.goto_drawing_state(*self.canvas.winfo_pointerxy())

    def create_colors(self):
        components = self.arrow_components()
        for component in components:
            color = self.palette.new()
            component[0].start.set_color(color)
            for arrow in component:
                arrow.set_color(color)
                arrow.end.set_color(color)

    def about(self):
        InfoDialog(self.window, 'About PLink', About)

    def howto(self):
        doc_file = os.path.join(os.path.dirname(__file__), 'doc', 'index.html')
        doc_path = os.path.abspath(doc_file)
        url = 'file:' + pathname2url(doc_path)
        try:
            webbrowser.open(url) 
        except:
            tkMessageBox.showwarning('Not found!', 'Could not open URL\n(%s)'%url)
  
class Vertex:
    """
    A vertex in a PL link diagram.
    """
    epsilon = 6

    def __init__(self, x, y, canvas, hidden=False,color='black'):
        self.x, self.y = int(x), int(y)
        self.in_arrow = None
        self.out_arrow = None
        self.canvas = canvas
        self.color = color
        self.dot = None
        self.hidden = hidden
        self.frozen = False
        self.draw()

    def __repr__(self):
        return '(%d,%d)'%(self.x, self.y)

    def __eq__(self, other):
        """
        Vertices are equivalent if they are sufficiently close.
        Use the "is" operator to test if they are identical.
        """
        return abs(self.x - other.x) + abs(self.y - other.y) < Vertex.epsilon

    def hide(self):
        self.canvas.delete(self.dot)
        self.hidden = True
    
    def freeze(self):
        self.frozen = True
    
    def expose(self, crossings=[]):
        self.hidden = False
        self.frozen = False
        self.draw()

    def point(self):
        return self.x, self.y

    def draw(self):
        if self.hidden or self.frozen:
            return
        delta = 2
        x, y = self.point()
        if self.dot:
            self.canvas.delete(self.dot)
        self.dot = self.canvas.create_oval(x-delta , y-delta, x+delta, y+delta,
                                           outline=self.color,
                                           fill=self.color)
    def set_color(self, color):
        self.color = color
        self.canvas.itemconfig(self.dot, fill=color, outline=color)
        
    def is_endpoint(self):
        return self.in_arrow == None or self.out_arrow == None
    
    def is_isolated(self):
        return self.in_arrow == None and self.out_arrow == None

    def reverse(self):
        self.in_arrow, self.out_arrow = self.out_arrow, self.in_arrow

    def swallow(self, other, palette):
        """
        Join two paths.  Self and other must be endpoints. Other is erased.
        """
        if not self.is_endpoint() or not other.is_endpoint():
            raise ValueError
        if self.in_arrow is not None:
            if other.in_arrow is not None:
                other.reverse_path()
            if self.color != other.color:
                palette.recycle(self.color)
                self.color = other.color
                self.recolor_incoming(color = other.color)
            self.out_arrow = other.out_arrow
            self.out_arrow.set_start(self)
        elif self.out_arrow is not None:
            if other.out_arrow is not None:
                other.reverse_path()
            if self.color != other.color:
                palette.recycle(other.color)
                other.recolor_incoming(color = self.color)
            self.in_arrow = other.in_arrow
            self.in_arrow.set_end(self)
        other.erase()
            
    def reverse_path(self, crossings=[]):
        """
        Reverse all vertices and arrows of this vertex's component.
        """
        v = self
        while True:
            e = v.in_arrow
            v.reverse()
            if not e: break
            e.reverse(crossings)
            v = e.end
            if v == self: return
        self.reverse()
        v = self
        while True:
            e = v.out_arrow
            v.reverse()
            if not e: break
            e.reverse(crossings)
            v = e.start
            if v == self: return

    def recolor_incoming(self, palette=None, color=None):
        """
        If this vertex lies in a non-closed component, recolor its incoming
        path.  The old color is not freed.  This vertex is NOT recolored. 
        """
        v = self
        while True:
            e = v.in_arrow
            if not e:
                break
            v = e.start
            if v == self:
                return
        if not color:
            color = palette.new()
        #print color
        v = self
        while True:
            e = v.in_arrow
            if not e:
                break
            e.set_color(color)
            v = e.start
            v.set_color(color)
        
    def update_arrows(self):
        if self.in_arrow: self.in_arrow.vectorize()
        if self.out_arrow: self.out_arrow.vectorize()

    def erase(self):
        """
        Prepare the vertex for the garbage collector.
        """
        self.in_arrow = None
        self.out_arrow = None
        self.hide()

class Arrow:
    """
    An arrow in a PL link diagram.
    """
    epsilon = 12
    
    def __init__(self, start, end, canvas=None, hidden=False, color='black'):
        self.start, self.end = start, end
        self.canvas = canvas
        self.color = color
        self.component = None
        self.hidden = hidden
        self.frozen = False
        self.lines = []
        self.cross_params = []
        if self.start != self.end:
            self.start.out_arrow = self
            self.end.in_arrow = self
            self.vectorize()
            self.draw()
        
    def __repr__(self):
        return '%s-->%s'%(self.start, self.end)

    def __xor__(self, other):
        """
        Returns the barycentric coordinate at which self crosses other.
        """
        D = float(other.dx*self.dy - self.dx*other.dy)
        if D == 0:
            return None
        xx = other.start.x - self.start.x
        yy = other.start.y - self.start.y
        s = (yy*self.dx - xx*self.dy)/D
        t = (yy*other.dx - xx*other.dy)/D
        if 0 < s < 1 and 0 < t < 1:
            return t
        else:
            return None

    def vectorize(self):
        self.dx = float(self.end.x - self.start.x)
        self.dy = float(self.end.y - self.start.y)
        self.length = sqrt(self.dx*self.dx + self.dy*self.dy) 

    def reverse(self, crossings=[]):
        self.end, self.start = self.start, self.end
        self.vectorize()
        self.draw(crossings)

    def hide(self):
        for line in self.lines:
            self.canvas.delete(line)
        self.hidden = True

    def freeze(self):
        for line in self.lines:
            self.canvas.itemconfig(line, fill='gray')
        self.frozen = True
    
    def expose(self, crossings=[]):
        self.hidden = False
        self.frozen = False
        self.draw(crossings)

    def draw(self, crossings=[], recurse=True):
        if self.hidden or self.frozen:
            return
        self.vectorize()
        gap = 9.0/self.length
        for line in self.lines:
            self.canvas.delete(line)
        self.lines = []
        cross_params = []
        over_arrows = [c.over for c in crossings if c.under == self]
        for arrow in over_arrows: 
            t = self ^ arrow
            if t:
                cross_params.append(t)
        cross_params.sort()
        x0, y0 = x00, y00 = self.start.point()
        for s in cross_params:
            x1 = x00 + (s-gap)*self.dx 
            y1 = y00 + (s-gap)*self.dy
            self.lines.append(self.canvas.create_line(
                    x0, y0, x1, y1,
                    width=3, fill=self.color))
            x0, y0 = x1 + 2*gap*self.dx, y1 + 2*gap*self.dy
        x1, y1 = self.end.point()
        self.lines.append(self.canvas.create_line(
                x0, y0, x1, y1,
                arrow=Tk_.LAST,
                width=3, fill=self.color))
        if recurse:
            under_arrows = [c.under for c in crossings if c.over == self]
            for arrow in under_arrows:
                arrow.draw(crossings, recurse=False)
    
    def set_start(self, vertex, crossings=[]):
        self.start = vertex
        if self.end:
            self.vectorize()
            self.draw(crossings)

    def set_end(self, vertex, crossings=[]):
        self.end = vertex
        if self.start:
            self.vectorize()
            self.draw(crossings)

    def set_color(self, color):
        self.color = color
        for line in self.lines:
            self.canvas.itemconfig(line, fill=color)
            
    def erase(self):
        """
        Prepare the arrow for the garbage collector.
        """
        self.start = None
        self.end = None
        self.hide()

    def too_close(self, vertex):
        if vertex == self.start or vertex == self.end:
            return False
        try:
            e = Arrow.epsilon
            Dx = vertex.x - self.start.x
            Dy = vertex.y - self.start.y
            A = (Dx*self.dx + Dy*self.dy)/self.length
            B = (Dy*self.dx - Dx*self.dy)/self.length
            return -e < A < self.length + e and -e < B < e
        except:
            #print vertex
            return False

class Crossing:
    """
    A pair of crossing arrows in a PL link diagram.
    """
    def __init__(self, over, under):
        self.over = over
        self.under = under
        self.locked = False
        self.KLP = {}    # See the SnapPea file link_projection.h
        self.hit1 = None # For computing DT codes
        self.hit2 = None
        self.comp1 = None
        self.comp2 = None
        self.flipped = None

    def __repr__(self):
        return '%s over %s at (%d,%d)'%(self.over, self.under, self.x, self.y)

    def __eq__(self, other):
        """
        Crossings are equivalent if they involve the same arrows.
        """
        if self.over in other and self.under in other:
            return True
        else:
            return False

    def __hash__(self):
        # Since we redefined __eq__ we need to define __hash__
        return id(self)
        
    def __contains__(self, arrow):
        if arrow == None or arrow == self.over or arrow == self.under:
            return True
        else:
            return False
        
    def locate(self):
        t = self.over ^ self.under
        if t:
            self.x = int(self.over.start.x + t*self.over.dx)
            self.y = int(self.over.start.y + t*self.over.dy)
        else:
            self.x, self.y = None, None

    def sign(self):
        try:
            D = self.under.dx*self.over.dy - self.under.dy*self.over.dx
            if D > 0: return 'RH'
            if D < 0: return 'LH'
        except:
            return 0

    def strand(self, arrow):
        sign = self.sign()
        if arrow not in self:
            return None
        elif ( (arrow == self.over and sign == 'RH') or
               (arrow == self.under and sign =='LH') ):
            return 'X'
        else:
            return 'Y'

    def reverse(self):
        self.over, self.under = self.under, self.over

    def height(self, arrow):
        if arrow == self.under:
            return self.under ^ self.over
        elif arrow == self.over:
            return self.over ^ self.under
        else:
            return None

    def DT_hit(self, count, ecrossing):
        """
        Count the crossing, using DT conventions.  Return True on the
        first hit if the count is odd and the crossing is shared by
        two components of the diagram.  As a side effect, set the
        flipped attribute on the first hit.
        """
        over = ecrossing.goes_over()
        if count%2 == 0 and over:
            count = -count
        if self.hit1 == 0:
            self.hit1 = count
            sign = self.sign()
            if sign:
                self.flipped = over ^ (sign == 'RH')
            if count%2 != 0 and self.comp1 != self.comp2:
                return True
        elif self.hit2 == 0:
            self.hit2 = count
        else:
            raise ValueError('Too many hits!')

    def mark_component(self, component):
        if self.comp1 is None:
            self.comp1 = component
        elif self.comp2 is None:
            self.comp2 = component
        else:
            raise ValueError('Too many component hits!')

    def clear_marks(self):
        self.hit1= self.hit2 = 0
        self.flipped = self.comp1 = self.comp2 = None

class ECrossing:
    """
    A pair: (Crossing, Arrow), where the Arrow is involved in the Crossing.
    The ECrossings correspond 1-1 with edges of the link diagram.
    """ 
    def __init__(self, crossing, arrow):
        if arrow not in crossing:
            raise ValueError
        self.crossing = crossing
        self.arrow = arrow
        self.strand = self.crossing.strand(self.arrow)

    def pair(self):
        return (self.crossing, self.arrow)

    def goes_over(self):
        if self.arrow == self.crossing.over:
            return True
        return False

DT_alphabet = '_abcdefghijklmnopqrstuvwxyzZYXWVUTSRQPONMLKJIHGFEDCBA'

class Palette:
    """
    Dispenses colors.
    """
    def __init__(self):
        self.colorizer = Colorizer()
        self.reset()

    def reset(self):
        self.free_colors = [self.colorizer(n) for n in range(6)]
        self.active_colors = []

    def new(self):
        if len(self.free_colors) == 0:
            for n in range(10):
                color = self.colorizer(len(self.active_colors))
                if color not in self.free_colors + self.active_colors:
                    self.free_colors.append(color)
        try:
            color = self.free_colors.pop(0)
            self.active_colors.append(color)
            return color
        except IndexError:
            self.active_colors.append('black')
            return 'black'

    def recycle(self, color):
        self.active_colors.remove(color)
        self.free_colors.append(color)

# Pure python version of the Colorizer class from snappy.CyOpenGL
class Colorizer:
    """
    Callable class which returns an RGB color string when passed an
    index.  Uses the same algorithm as the SnapPea kernel.
    """
    def __init__(self, lightness=0.5, saturation=0.7):
        self.base_hue = [0,4,2,3,5,1]
        self.lightness = lightness
        self.saturation = saturation

    def __call__(self, index):
        hue = (self.base_hue[index%6] + self.index_to_hue(index//6)) / 6.0
        rgb = hls_to_rgb(hue, self.lightness, self.saturation)  
        return '#%.2x%.2x%.2x'%tuple(int(x*255) for x in rgb)

    def index_to_hue(self, index):
        num, den= 0, 1
        while index:
            num = num<<1
            den = den<<1
            if index & 0x1:
                num += 1
            index = index>>1
        return float(num)/float(den)

class InfoDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title, content=''):
        self.parent = parent
        self.content = content
        Tk_.Toplevel.__init__(self, parent)
        NW = Tk_.N+Tk_.W
        if title:
            self.title(title)
#        self.icon = PhotoImage(data=icon_string)
        canvas = Tk_.Canvas(self, width=58, height=58)
#        canvas.create_image(10, 10, anchor=NW, image=self.icon)
        canvas.grid(row=0, column=0, sticky=NW)
        text = Tk_.Text(self, font='Helvetica 14',
                    width=50, height=16, padx=10)
        text.insert(Tk_.END, self.content)
        text.grid(row=0, column=1, sticky=NW,
                  padx=10, pady=10)
        text.config(state=Tk_.DISABLED)
        self.buttonbox()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.ok)
        self.focus_set()
        self.wait_window(self)

    def buttonbox(self):
        box = Tk_.Frame(self)
        w = Tk_.Button(box, text="OK", width=10, command=self.ok,
                   default=Tk_.ACTIVE)
        w.pack(side=Tk_.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.grid(row=1, columnspan=2)

    def ok(self, event=None):
        self.parent.focus_set()
        self.app = None
        self.destroy()

try:
    import version
except ImportError: # Python 3
    from . import version

About = """PLink version %s

PLink draws piecewise linear links.

Written in Python by Marc Culler and Nathan Dunfield.

Comments to: culler@math.uic.edu, nmd@illinois.edu
Download at http://www.math.uic.edu/~t3m
Distributed under the GNU General Public License.

Development supported by the National Science Foundation.

Inspired by SnapPea (written by Jeff Weeks) and
LinkSmith (written by Jim Hoste and Morwen Thistlethwaite).
""" % version.version

if __name__ == '__main__':
    LE = LinkEditor()
    LE.window.mainloop()
