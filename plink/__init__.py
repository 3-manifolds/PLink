#!/usr/bin/env python
#
#   Copyright (C) 2007 Marc Culler and others
#
#   This program is distributed under the terms of the 
#   GNU General Public License, version 3 or later, as published by
#   the Free Software Foundation.  See the file gpl-3.0.txt for details.
#   The URL for this program is
#     http://www.math.uic.edu/~t3m/plink
#   A copy of the license file may be found at:
#     http://www.gnu.org/licenses/gpl-3.0.txt
#
#   The development of this program was partially supported by
#   the National Science Foundation under grants DMS0608567,
#   DMS0504975and DMS0204142.
#
#   $Author$ $Date$ $Revision$
#

import os
import sys
import webbrowser
import Tkinter
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
from urllib import pathname2url
from math import sqrt
from random import random

class LinkEditor:
    """
    A graphical link drawing tool based on the one embedded in Jeff Weeks'
    original SnapPea program.
    """
    def __init__(self, callback=None):
        self.callback=callback
        self.initialize()
        self.cursorx = 0
        self.cursory = 0
        self.window = Tkinter.Tk()
        self.window.title('PLink Editor')
        self.palette = Palette()
        # Menus
        menubar = Tkinter.Menu(self.window)
        file_menu = Tkinter.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open File ...', command=self.load)
        file_menu.add_command(label='Save ...', command=self.save)
        print_menu = Tkinter.Menu(menubar, tearoff=0)
        print_menu.add_command(label='monochrome',
                       command=lambda : self.save_image(color_mode='mono'))
        print_menu.add_command(label='color', command=self.save_image)
        file_menu.add_cascade(label='Save Image ...', menu=print_menu)
        export_menu = Tkinter.Menu(menubar, tearoff=0)
        export_menu.add_command(label='DT code', command=self.not_done)
        export_menu.add_command(label='Gauss code', command=self.not_done)
        export_menu.add_command(label='PD code', command=self.not_done)
        file_menu.add_cascade(label='Export ...', menu=export_menu)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.done)
        menubar.add_cascade(label='File', menu=file_menu)
        tools_menu = Tkinter.Menu(menubar, tearoff=0)
        tools_menu.add_command(label='Make alternating',
                       command=self.make_alternating)
        tools_menu.add_command(label='Reflect', command=self.reflect)
        tools_menu.add_command(label='Clear', command=self.clear)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        help_menu = Tkinter.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About PLink...', command=self.about)
        help_menu.add_command(label='Instructions ...', command=self.howto)
        menubar.add_cascade(label='Help', menu=help_menu)
        self.window.config(menu=menubar)
        # Frame and Canvas
        self.frame = Tkinter.Frame(self.window, 
                                   borderwidth=2,
                                   relief=Tkinter.SUNKEN)
        self.canvas = Tkinter.Canvas(self.frame,
                                     bg='#dcecff',
                                     width=600,
                                     height=600)
        self.frame.pack(padx=5, pady=5, fill=Tkinter.BOTH, expand=Tkinter.YES)
        self.canvas.pack(padx=5, pady=5, fill=Tkinter.BOTH, expand=Tkinter.YES)
        # Event bindings
        self.canvas.bind('<Button-1>', self.onebutton)
        self.canvas.bind('<Button-2>', self.mouse2)
        self.canvas.bind('<Motion>', self.mouse_moved)
        self.window.bind('<Key>', self.key_press)
        self.window.protocol("WM_DELETE_WINDOW", self.done)
        # Go
        self.state='start_state'

    def initialize(self):
        self.Edges = []
        self.Vertices = []
        self.Crossings = []
        self.CrossPoints = []
        self.LiveEdge1 = None
        self.LiveEdge2 = None
        self.ActiveVertex = None

    def done(self):
        if self.callback:
            self.callback(self.SnapPea_KLPProjection())
        self.window.destroy()

    def onebutton(self, event):
        """
        Simulates a 3-button mouse for OS X.
        """
        if (event.state & 24 == 8):
            self.mouse3(event)
        elif (event.state & 24 == 16):
            self.mouse2(event)
        else:
            self.mouse1(event)

    def mouse1(self, event):
        """
        Event handler for mouse button 1.
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.state == 'start_state':
            start_vertex = Vertex(x, y, self.canvas, hidden=True)
            if start_vertex in [v for v in self.Vertices if v.is_endpoint()]:
                #print 'clicked on an endpoint'
                start_vertex.erase()
                start_vertex = self.Vertices[self.Vertices.index(start_vertex)]
                x0, y0 = x1, y1 = start_vertex.point()
                if start_vertex.out_edge:
                    start_vertex.reverse_path()
                    self.update_crosspoints()
                    for edge in self.Edges: 
                        edge.draw(self.Crossings)
            elif start_vertex in self.Vertices:
                #print 'clicked on non-endpoint vertex'
                cut_vertex = self.Vertices[self.Vertices.index(start_vertex)]
                cut_vertex.recolor_incoming(palette=self.palette)
                cut_edge = cut_vertex.in_edge
                cut_vertex.in_edge = None
                start_vertex = cut_edge.start
                x1, y1 = cut_vertex.point()
                cut_edge.freeze()
            elif start_vertex in self.CrossPoints:
                #print 'clicked on a crossing'
                crossing = self.Crossings[self.CrossPoints.index(start_vertex)]
                crossing.reverse()
                crossing.under.draw(self.Crossings)
                crossing.over.draw(self.Crossings)
                return
            else:
                #print 'creating a new vertex'
                if not self.generic_vertex(start_vertex):
                    start_vertex.erase()
                    self.window.bell()
                    return
                x1, y1 = start_vertex.point()
                start_vertex.set_color(self.palette.new())
                self.Vertices.append(start_vertex)
            self.ActiveVertex = start_vertex
            self.goto_drawing_state(x1,y1)
            return
        elif self.state == 'drawing':
            next_vertex = Vertex(x, y, self.canvas, hidden=True)
            if next_vertex == self.ActiveVertex:
                #print 'clicked twice'
                next_vertex.erase()
                dead_edge = self.ActiveVertex.out_edge
                if dead_edge:
                    self.destroy_edge(dead_edge)
                self.goto_start_state()
                return
            #print 'setting up a new edge'
            if self.ActiveVertex.out_edge:
                next_edge = self.ActiveVertex.out_edge
                next_edge.set_end(next_vertex)
                next_vertex.in_edge = next_edge
                if not next_edge.frozen:
                    next_edge.hide()
            else:
                this_color = self.ActiveVertex.color
                next_edge = Edge(self.ActiveVertex, next_vertex,
                                 self.canvas, hidden=True,
                                 color=this_color)
                self.Edges.append(next_edge)
            next_vertex.set_color(next_edge.color)
            if next_vertex in [v for v in self.Vertices if v.is_endpoint()]:
                #print 'joining up to another component'
                if not self.generic_edge(next_edge):
                    self.window.bell()
                    return
                next_vertex.erase()
                next_vertex = self.Vertices[self.Vertices.index(next_vertex)]
                if next_vertex.in_edge:
                    next_vertex.reverse_path()
                next_edge.set_end(next_vertex)
                next_vertex.in_edge = next_edge
                if next_vertex.color != self.ActiveVertex.color:
                    self.palette.recycle(self.ActiveVertex.color)
                    next_vertex.recolor_incoming(color = next_vertex.color)
                self.update_crossings(next_edge)
                next_edge.expose(self.Crossings)
                self.goto_start_state()
                return
            # 'just extending a path, as usual'
            self.update_crossings(next_edge)
            self.update_crosspoints()
            if not (self.generic_vertex(next_vertex) and
                    self.generic_edge(next_edge) ):
                self.window.bell()
                return
            next_edge.expose(self.Crossings)
            self.Vertices.append(next_vertex)
            next_vertex.expose()
            self.ActiveVertex = next_vertex
            self.canvas.coords(self.LiveEdge1,x,y,x,y)
            return
        elif self.state == 'dragging_state':
            try:
                self.end_dragging_state()
            except ValueError:
                self.window.bell()

    def mouse2(self, event):
        """
        Event handler for mouse button 2 (dragging).
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        vertex = Vertex(x, y, self.canvas, hidden=True)
        if vertex not in self.Vertices:
            self.canvas.bell()
            return
        if self.state == 'start_state':
            self.state = 'dragging_state'
            self.canvas.config(cursor='circle')
            self.ActiveVertex = self.Vertices[self.Vertices.index(vertex)]
            self.ActiveVertex.freeze()
            x1, y1 = self.ActiveVertex.point()
            if self.ActiveVertex.in_edge:
                x0, y0 = self.ActiveVertex.in_edge.start.point()
                self.ActiveVertex.in_edge.freeze()
                self.LiveEdge1 = self.canvas.create_line(x0,y0,x1,y1,
                                                         fill='red')
            if self.ActiveVertex.out_edge:
                x0, y0 = self.ActiveVertex.out_edge.end.point()
                self.ActiveVertex.out_edge.freeze()
                self.LiveEdge2 = self.canvas.create_line(x0,y0,x1,y1,
                                                         fill='red')
        elif self.state == 'dragging_state':
            try:
                self.end_dragging_state()
            except ValueError:
                self.window.bell()

    def mouse3(self, event):
        """
        Event handler for mouse button 3 (reverses component).
        """
        if self.state != 'start_state':
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        vertex = Vertex(x, y, self.canvas, hidden=True)
        if vertex in self.Vertices:
            match = self.Vertices[self.Vertices.index(vertex)]
            match.reverse_path()
            return
        for edge in self.Edges:
            if edge.too_close(vertex):
                edge.end.reverse_path()
                return
        
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
                self.canvas.config(cursor='hand1')
            elif point in self.CrossPoints:
                self.canvas.config(cursor='exchange')
            else:
                self.canvas.config(cursor='')
        elif self.state == 'drawing':
            x0,y0,x1,y1 = self.canvas.coords(self.LiveEdge1)
            self.canvas.coords(self.LiveEdge1, x0, y0, x, y)
        elif self.state == 'dragging_state':
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.ActiveVertex.x, self.ActiveVertex.y = x, y
            self.ActiveVertex.draw()
            if self.LiveEdge1:
                x0,y0,x1,y1 = self.canvas.coords(self.LiveEdge1)
                self.canvas.coords(self.LiveEdge1, x0, y0, x, y)
            if self.LiveEdge2:
                x0,y0,x1,y1 = self.canvas.coords(self.LiveEdge2)
                self.canvas.coords(self.LiveEdge2, x0, y0, x, y)

    def key_press(self, event):
        """
        Handler for keypress events.
        """
        if event.keysym == 'Delete' or event.keysym == 'BackSpace':
            if self.state == 'drawing':
                last_edge = self.ActiveVertex.in_edge
                if last_edge:
                    dead_edge = self.ActiveVertex.out_edge
                    if dead_edge:
                        self.destroy_edge(dead_edge)
                    self.ActiveVertex = last_edge.start
                    self.ActiveVertex.out_edge = None
                    x0,y0,x1,y1 = self.canvas.coords(self.LiveEdge1)
                    x0, y0 = self.ActiveVertex.point()
                    self.canvas.coords(self.LiveEdge1, x0, y0, x1, y1)
                    self.Crossings = [c for c in self.Crossings
                                      if last_edge not in c]
                    self.Vertices.remove(last_edge.end)
                    self.Edges.remove(last_edge)
                    last_edge.end.erase()
                    last_edge.erase()
                    for edge in self.Edges:
                        edge.draw(self.Crossings)
                if not self.ActiveVertex.in_edge:
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
        event.x, event.y = self.cursorx, self.cursory
        self.mouse_moved(event)

    def goto_start_state(self):
        self.canvas.delete(self.LiveEdge1)
        self.LiveEdge1 = None
        self.canvas.delete(self.LiveEdge2)
        self.LiveEdge2 = None
        self.ActiveVertex = None
        self.update_crosspoints()
        for vertex in self.Vertices:
            vertex.draw()
        for edge in self.Edges: 
            edge.draw(self.Crossings)
        self.canvas.config(cursor='')
        self.state = 'start_state'

    def goto_drawing_state(self, x1,y1):
        self.ActiveVertex.hidden = False
        self.ActiveVertex.draw()
        x0, y0 = self.ActiveVertex.point()
        self.LiveEdge1 = self.canvas.create_line(x0,y0,x1,y1,fill='red')
        self.state = 'drawing'
        self.canvas.config(cursor='pencil')

    def verify_drag(self):
        self.ActiveVertex.update_edges()
        self.update_crossings(self.ActiveVertex.in_edge)
        self.update_crossings(self.ActiveVertex.out_edge)
        self.update_crosspoints()
        return (self.generic_edge(self.ActiveVertex.in_edge) and
                self.generic_edge(self.ActiveVertex.out_edge) )

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
            self.update_crossings(self.ActiveVertex.in_edge)
            self.update_crossings(self.ActiveVertex.out_edge)
        if endpoint is None and not self.generic_vertex(self.ActiveVertex):
            raise ValueError
        self.ActiveVertex.expose()
        if self.ActiveVertex.in_edge:
            self.ActiveVertex.in_edge.expose()
        if self.ActiveVertex.out_edge:
            self.ActiveVertex.out_edge.expose()
        self.goto_start_state()

    def generic_vertex(self, vertex):
        if vertex in [v for v in self.Vertices if v is not vertex]:
            return False
        for edge in self.Edges:
            if edge.too_close(vertex):
                #print 'non-generic vertex'
                return False
        return True

    def generic_edge(self, edge):
        if edge == None:
            return True
        for vertex in self.Vertices:
            if edge.too_close(vertex):
                #print 'edge too close to vertex'
                return False
        for crossing in self.Crossings:
            point = self.CrossPoints[self.Crossings.index(crossing)]
            if edge not in crossing and edge.too_close(point):
                #print 'edge too close to crossing'
                return False
        return True
       
    def destroy_edge(self, edge):
        self.Edges.remove(edge)
        if edge.end:
            edge.end.in_edge = None
        if edge.start:
            edge.start.out_edge = None
        edge.erase()
        self.Crossings = [c for c in self.Crossings if edge not in c]

    def update_crosspoints(self):
        for c in self.Crossings:
            c.locate()
        self.CrossPoints = [Vertex(c.x, c.y, self.canvas, hidden=True)
                                    for c in self.Crossings]

    def update_crossings(self, this_edge):
        if this_edge == None:
            return
        cross_list = [c for c in self.Crossings if this_edge in c]
        damage_list =[]
        find = lambda x: cross_list[cross_list.index(x)]
        for edge in self.Edges:
            if this_edge == edge:
                continue
            new_crossing = Crossing(this_edge, edge)
            if this_edge ^ edge:
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
                    if edge == find(new_crossing).under:
                        damage_list.append(edge)
                    self.Crossings.remove(new_crossing)
        for edge in damage_list:
            edge.draw(self.Crossings)

    def edge_components(self):
        """
        Returns a list of lists of edges, one per component of the diagram.
        An empty list corresponds to a component consisting of one vertex.
        """
        pool = [v.out_edge  for v in self.Vertices if not v.is_endpoint()]
        pool += [v.out_edge for v in self.Vertices if v.in_edge == None]
        result = []
        while len(pool):
            first_edge = pool.pop()
            if first_edge == None:
                result.append([])
                continue
            component = [first_edge]
            while component[-1].end != component[0].start:
                next = component[-1].end.out_edge
                if next == None:
                    break
                pool.remove(next)
                component.append(next)
            result.append(component)
        return result

    def crossing_components(self):
        """
        Returns a list of lists of ECrossings, one per component,
        where the corresponding crossings are ordered consecutively
        through the component.  Requires that all components be closed.
        """
        for vertex in self.Vertices:
            if vertex.is_endpoint():
                raise ValueError
        result = []
        edge_components = self.edge_components()
        for component in edge_components:
            crosses=[]
            for edge in component:
                edge_crosses = [(c.height(edge), c, edge) 
                                for c in self.Crossings if edge in c]
                edge_crosses.sort()
                crosses += edge_crosses
            result.append([ECrossing(c[1],c[2]) for c in crosses]) 
        return result

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
                'All components must be closed to use this tool.')
            return
        for component in crossing_components:
            cross0, edge0 = component[0].pair()
            for ecrossing in component[1:]:
                cross, edge = ecrossing.pair()
                if ( (edge0 == cross0.under and edge == cross.under) or 
                     (edge0 == cross0.over and edge == cross.over) ):
                    if cross.locked:
                        for ecrossing2 in component:
                            if ecrossing2.crossing == cross:
                                break
                            ecrossing2.crossing.reverse()
                    else:
                        cross.reverse()
                cross0, edge0 = cross, edge
            for ecrossing in component:
                ecrossing.crossing.locked = True
        for crossing in self.Crossings:
            crossing.locked = False
        for edge in self.Edges:
            edge.draw(self.Crossings)

    def reflect(self):
        for crossing in self.Crossings:
            crossing.reverse()
        for edge in self.Edges:
            edge.draw(self.Crossings)

    def clear(self):
        for edge in self.Edges:
            edge.erase()
        for vertex in self.Vertices:
            vertex.erase()
        self.canvas.delete('all')
        self.palette.reset()
        self.initialize()
        self.goto_start_state()

    def SnapPea_KLPProjection(self):
        """
        Constructs a python simulation of a SnapPea KLPProjection.
        (See the SnapPea file link_projection.h for definitions.)
        The KLPCrossings are modeled by dictionaries.
        Requires that all components be closed.
        """
        crossing_components = self.crossing_components()
        num_crossings = len(self.Crossings)
        num_free_loops = 0
        num_components = len(crossing_components)
        id = lambda x: self.Crossings.index(x.crossing)
        for component in crossing_components:
            this_component = crossing_components.index(component)
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

    def SnapPea_projection_file(self):
        """
        Returns a string containing the contents of a SnapPea link
        projection file.
        """
        result = ''
        result += '% Link Projection\n'
        components = self.edge_components()
        result += '%d\n'%len(components)
        for component in components:
            first = self.Vertices.index(component[0].start)
            last = self.Vertices.index(component[-1].end)
            result +='%4.1d %4.1d\n'%(first, last)
        result += '%d\n'%len(self.Vertices)
        for vertex in self.Vertices:
            result += '%5.1d %5.1d\n'%vertex.point()
        result += '%d\n'%len(self.Edges)
        for edge in self.Edges:
            start_index = self.Vertices.index(edge.start)
            end_index = self.Vertices.index(edge.end)
            result += '%4.1d %4.1d\n'%(start_index, end_index)
        result += '%d\n'%len(self.Crossings)
        for crossing in self.Crossings:
            under = self.Edges.index(crossing.under)
            over = self.Edges.index(crossing.over)
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
        savefile = tkFileDialog.asksaveasfile(
            mode='w',
            title='Save As Snappea Projection File',
            filetypes=[('Any','*')])
        if savefile:
            savefile.write(self.SnapPea_projection_file())
            savefile.close()

    def save_image(self, color_mode='color'):
        savefile = tkFileDialog.asksaveasfile(
            mode='w',
            title='Save As Postscript Image File (%s)'%color_mode,
            filetypes=[('ps','eps')])
        if savefile:
            savefile.write(self.canvas.postscript(colormode=color_mode))
            savefile.close()

    def load(self):
        loadfile = tkFileDialog.askopenfile(
            mode='r',
            title='Open SnapPea Projection File',
            filetypes=[('Any','*')])
        if loadfile:
            lines = loadfile.readlines()
            num_lines = len(lines)
            if not lines.pop(0).startswith('% Link Projection'):
                tkMessageBox.showwarning(
                    'Bad file',
                    'This is not a SnapPea link projection file')
            else:
                try:
                    num_components = int(lines.pop(0))
                    for n in range(num_components):
                        lines.pop(0) # We don't need this
                    num_vertices = int(lines.pop(0))
                    for n in range(num_vertices):
                        x, y = lines.pop(0).split()
                        X, Y = int(x), int(y)
                        self.Vertices.append(Vertex(X, Y, self.canvas))
                    num_edges = int(lines.pop(0))
                    for n in range(num_edges):
                        s, e = lines.pop(0).split()
                        S, E = self.Vertices[int(s)], self.Vertices[int(e)]
                        self.Edges.append(Edge(S, E, self.canvas))
                    num_crossings = int(lines.pop(0))
                    for n in range(num_crossings):
                        u, o = lines.pop(0).split()
                        U, O = self.Edges[int(u)], self.Edges[int(o)]
                        self.Crossings.append(Crossing(O, U))
                    hot = int(lines.pop(0))
                    loadfile.close()
                    self.goto_start_state()
                    if hot != -1:
                        self.ActiveVertex = self.Vertices[hot]
                        self.goto_drawing_state(*self.canvas.winfo_pointerxy())
                except:
                    tkMessageBox.showwarning(
                        'Bad file',
                        'Could not parse line %d'%(num_lines - len(lines)))


    def about(self):
        InfoDialog(self.window, 'About PLink', About)

    def howto(self):
        doc_file = 'plink_howto.html'
        doc_file2 = os.path.join(__path__[0], doc_file)
        for path in sys.path + [os.path.abspath(os.path.dirname(sys.argv[0]))]:
            doc_path = os.path.join(path, doc_file)
            if os.path.exists(doc_path):
                break
            doc_path = os.path.join(path, doc_file2)
            if os.path.exists(doc_path):
                break
        doc_path = os.path.abspath(doc_path)
        url = 'file:' + pathname2url(doc_path)
        try:
            webbrowser.open(url) 
        except:
            showwarning('Not found!', 'Could not open URL\n(%s)'%url)
  
class Vertex:
    """
    A vertex in a PL link diagram.
    """
    epsilon = 6

    def __init__(self, x, y, canvas, hidden=False,color='black'):
        self.x, self.y = int(x), int(y)
        self.in_edge = None
        self.out_edge = None
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
        return self.in_edge == None or self.out_edge == None
    
    def reverse(self):
        self.in_edge, self.out_edge = self.out_edge, self.in_edge

    def swallow(self, other, palette):
        """
        Join two paths.  Self and other must be endpoints. Other is erased.
        """
        if not self.is_endpoint() or not other.is_endpoint():
            raise ValueError
        if self.in_edge is not None:
            if other.in_edge is not None:
                other.reverse_path()
            if self.color != other.color:
                palette.recycle(self.color)
                self.color = other.color
                self.recolor_incoming(color = other.color)
            self.out_edge = other.out_edge
            self.out_edge.set_start(self)
        elif self.out_edge is not None:
            if other.out_edge is not None:
                other.reverse_path()
            if self.color != other.color:
                palette.recycle(other.color)
                other.recolor_incoming(color = self.color)
            self.in_edge = other.in_edge
            self.in_edge.set_end(self)
        other.erase()
            
    def reverse_path(self):
        """
        Reverse all vertices and edges of this vertex's component.
        """
        v = self
        while True:
            e = v.in_edge
            v.reverse()
            if not e: break
            e.reverse()
            v = e.end
            if v == self: return
        self.reverse()
        v = self
        while True:
            e = v.out_edge
            v.reverse()
            if not e: break
            e.reverse()
            v = e.start
            if v == self: return

    def recolor_incoming(self, palette=None, color=None):
        """
        If this vertex lies in a non-closed component, recolor its incoming
        path.  The old color is not freed.  This vertex is NOT recolored. 
        """
        v = self
        while True:
            e = v.in_edge
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
            e = v.in_edge
            if not e:
                break
            e.set_color(color)
            v = e.start
            v.set_color(color)
        
    def update_edges(self):
        if self.in_edge: self.in_edge.vectorize()
        if self.out_edge: self.out_edge.vectorize()

    def erase(self):
        """
        Prepare the vertex for the garbage collector.
        """
        self.in_edge = None
        self.out_edge = None
        self.hide()

class Edge:
    """
    An edge in a PL link diagram.
    """
    epsilon = 12
    
    def __init__(self, start, end, canvas, hidden=False, color='black'):
        self.start, self.end = start, end
        self.start.out_edge = self
        self.end.in_edge = self
        self.canvas = canvas
        self.color = color
        self.hidden = hidden
        self.frozen = False
        self.lines = []
        self.cross_params = []
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

    def reverse(self):
        self.end, self.start = self.start, self.end
        self.vectorize()
        self.draw()

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
        over_edges = [c.over for c in crossings if c.under == self]
        for edge in over_edges: 
            t = self ^ edge
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
                arrow=Tkinter.LAST,
                width=3, fill=self.color))
        if recurse:
            under_edges = [c.under for c in crossings if c.over == self]
            for edge in under_edges:
                edge.draw(crossings, recurse=False)

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
        Prepare the edge for the garbage collector.
        """
        self.start = None
        self.end = None
        self.hide()

    def too_close(self, vertex):
        if vertex == self.start or vertex == self.end:
            return False
        try:
            e = Edge.epsilon
            Dx = vertex.x - self.start.x
            Dy = vertex.y - self.start.y
            comp1 = (Dx*self.dx + Dy*self.dy)/self.length
            comp2 = (Dy*self.dx - Dx*self.dy)/self.length
            return -e < comp1 < self.length + e and -e < comp2 < e
        except:
            print vertex
            return False

class Crossing:
    """
    A pair of crossing edges in a PL link diagram.
    """
    def __init__(self, over, under):
        self.over = over
        self.under = under
        self.locked = False
        self.KLP = {}
        # See the SnapPea file link_projection.h

    def __repr__(self):
        return '%s over %s at (%d,%d)'%(self.over, self.under, self.x, self.y)

    def __eq__(self, other):
        """
        Crossings are equivalent if they involve the same edges.
        """
        if self.over in other and self.under in other:
            return True
        else:
            return False
        
    def __contains__(self, edge):
        if edge == None or edge == self.over or edge == self.under:
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

    def strand(self, edge):
        sign = self.sign()
        if edge not in self:
            return None
        elif ( (edge == self.over and sign == 'RH') or
               (edge == self.under and sign =='LH') ):
            return 'X'
        else:
            return 'Y'

    def reverse(self):
        self.over, self.under = self.under, self.over

    def height(self, edge):
        if edge == self.under:
            return self.under ^ self.over
        elif edge == self.over:
            return self.over ^ self.under
        else:
            return None

class ECrossing:
    """
    A pair: (Crossing, Edge).
    """ 
    def __init__(self, crossing, edge):
        if edge not in crossing:
            raise ValueError
        self.crossing = crossing
        self.edge = edge
        self.strand = self.crossing.strand(self.edge)

    def pair(self):
        return (self.crossing, self.edge)

class Palette:
    """
    Dispenses colors.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.free_colors = ['#e0e', '#0e0', '#ee0', '#00e', '#e00']
        self.active_colors = []

    def new(self):
        if len(self.free_colors) == 0:
            for n in range(10):
                R = int(random()*230)
                G = int(random()*230)
                B = int(random()*230)
                color = '#%.2x%.2x%.2x'%(R,G,B)
                if color not in self.free_colors + self.active_colors:
                    self.free_colors.append(color)
        try:
            color = self.free_colors.pop()
            self.active_colors.append(color)
            return color
        except:
            self.active_colors.append('black')
            return 'black'

    def recycle(self, color):
        self.active_colors.remove(color)
        self.free_colors.append(color)

class InfoDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title, content=''):
        self.parent = parent
        self.content = content
        Tkinter.Toplevel.__init__(self, parent)
        NW = Tkinter.N+Tkinter.W
        if title:
            self.title(title)
#        self.icon = PhotoImage(data=icon_string)
        canvas = Tkinter.Canvas(self, width=58, height=58)
#        canvas.create_image(10, 10, anchor=NW, image=self.icon)
        canvas.grid(row=0, column=0, sticky=NW)
        text = Tkinter.Text(self, font='Helvetica 14',
                    width=50, height=16, padx=10)
        text.insert(Tkinter.END, self.content)
        text.grid(row=0, column=1, sticky=NW,
                  padx=10, pady=10)
        text.config(state=Tkinter.DISABLED)
        self.buttonbox()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.ok)
        self.focus_set()
        self.wait_window(self)

    def buttonbox(self):
        box = Tkinter.Frame(self)
        w = Tkinter.Button(box, text="OK", width=10, command=self.ok,
                   default=Tkinter.ACTIVE)
        w.pack(side=Tkinter.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.grid(row=1, columnspan=2)

    def ok(self, event=None):
        self.parent.focus_set()
        self.app = None
        self.destroy()

About = """PLink version 1.0

PLink draws piecewise linear links.

Written in Python by Marc Culler.

Comments to: culler@math.uic.edu
Download at http://www.math.uic.edu/~t3m/plink
Distributed under the GNU General Public License.

Development supported by the National Science Foundation.

Inspired by SnapPea, by Jeff Weeks, and LinkSmith by
Jim Hoste and Morwen Thistlethwaite.
"""

if __name__ == '__main__':
    LE = LinkEditor()
    LE.window.mainloop()
